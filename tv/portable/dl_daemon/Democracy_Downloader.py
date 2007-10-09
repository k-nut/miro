# Miro - an RSS based video player application
# Copyright (C) 2005-2007 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

# Democracy download daemon - background process

def launch():
    # Make all output flush immediately.
    # Don't add extra import statements here.  If there's a problem importting
    # something we want to see the error in the log.
    import sys
    import os
    import util
    import logging
    util.inDownloader = True
    logPath = os.environ.get('DEMOCRACY_DOWNLOADER_LOG')
    if logPath is not None:
        if os.environ.get('DEMOCRACY_DOWNLOADER_FIRST_LAUNCH') == '1':
            logMode = 'w'
        else:
            logMode = 'a'
        log = open(logPath, logMode)
        sys.stdout = sys.stderr = log

    sys.stdout = util.AutoflushingStream(sys.stdout)
    sys.stderr = util.AutoflushingStream(sys.stderr)

    import platformutils
    platformutils.setupLogging(inDownloader=True)
    util.setupLogging()
    platformutils.initializeLocale()

    if os.environ.get('DEMOCRACY_DOWNLOADER_FIRST_LAUNCH') != '1':
        logging.info ("*** Starting new downloader log ***")
    else:
        logging.info ("*** Launching Downloader Daemon ****")


    # Start of normal imports
    import threading

    from dl_daemon import daemon
    # This isn't used here, we just want to load it sooner.
    from dl_daemon import download
    import eventloop
    import httpclient

    port = int(os.environ['DEMOCRACY_DOWNLOADER_PORT'])
    server = daemon.DownloaderDaemon(port)

    # remove the limits for the connection pool, we limit them
    # ourselves in the downloader code.  Don't try to pipeline
    # requests, it doesn't make sense when the download size is so
    # large.
    httpclient.HTTPConnectionPool.MAX_CONNECTIONS_PER_SERVER = sys.maxint
    httpclient.HTTPConnectionPool.MAX_CONNECTIONS = sys.maxint
    httpclient.PIPELINING_ENABLED = False
    httpclient.SOCKET_READ_TIMEOUT = 300
    httpclient.SOCKET_INITIAL_READ_TIMEOUT = 30

    download.downloadUpdater.startUpdates()
    eventloop.startup()

    # Hack to init gettext after we can get config information
    #
    # See corresponding hack in gtcache.py
    import gtcache
    gtcache.init()
    logging.info ("*** Daemon ready ***")

if __name__ == "__main__":
    launch()
