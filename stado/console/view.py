"""Command: view"""

import threading
import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True

import os
from . import Command
from .build import Build
from .. import config
from .. import log
import time



class View(Command):
    """Build and serve site using development server."""

    name = 'view'

    usage = "view [site] [options]"
    summary = "Build the site and start the development web server."
    description = ''
    options = [
        ["-p, --port", "Specify the port to listen on. (default: {})".format(
            config.port)],
        ["-h, --host", "Specify the host to listen on. (default: {})".format(
            config.host)],
        Build.options[0]
    ]


    def __init__(self, user_interface):
        Command.__init__(self, user_interface)

        self.server =  DevelopmentServer()
        self.cwd = os.getcwd()


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site')
        parser.add_argument('--port', '-p', type=int, default=config.port)
        parser.add_argument('--host', '-h', default=config.host)
        parser.add_argument('--output', '-o', default=None)
        parser.set_defaults(function=self.run)


    def run(self, site, host, port, output=None, wait=True, build=True):
        """Command-line interface will execute this method if user type 'view'
        command."""


        # Path pointing to current working directory.
        self.cwd = os.getcwd()

        # Build site.
        if build:
            self.console.build(site, output)

        # Server will serve files from current working directory.
        # So change current working directory to site output.
        if output:
            os.chdir(output)
        else:
            os.chdir(os.path.join(self.cwd, site, config.build_dir))

        log.debug('Starting development server...')
        log.debug('\tPath: {}'.format(os.getcwd()))
        self.server.start(host, port)


        log.info('You can view site at: http://{}:{}'.format(host, port))

        # Waiting loop.
        if wait: self.event('before_waiting')

        while not self.server.stopped and wait is True:
            time.sleep(config.wait_interval)

        return True


    def stop(self):
        """Stops command (stops development server)."""

        log.debug('Stopping development server...')

        # Change current working directory to previous directory.
        os.chdir(self.cwd)
        self.server.stop()

        log.debug('Done!')



class DevelopmentServer:
    """Development server using python build-in server."""

    def __init__(self):

        self.stopped = True     # Server status.
        self.server = None      # TCPServer object.

        self.host = None
        self.port = None


    def restart(self):
        """Restarts development server."""

        # Stop server if not already stopped.
        if not self.stopped:
            self.stop()

        # Server objects.
        Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((self.host, self.port), Handler)

        # Start a thread with the server.
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates.
        server_thread.daemon = True
        server_thread.start()

        self.stopped = False


    def start(self, host, port):
        """Starts development server.

        Arguments:
            port: Port number.
            host: Host name.
            threaded: If True, server will be run in another thread.
        Returns:
            True if started successfully, False if already running.

        """

        if not self.stopped:
            return False

        self.host = host
        self.port = port

        self.restart()
        return True


    def stop(self):
        """Stops development server."""

        if self.server is not None:

            self.stopped = True
            self.server.shutdown()
            self.server.server_close()
