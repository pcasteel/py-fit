
#!/usr/bin/python
import cherrypy
import json
import sys
import threading
import traceback
import webbrowser
import pprint
import argparse

from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError


class OAuth2Server:
    def __init__(self, client_id, client_secret,
                 redirect_uri='http://127.0.0.1:8080/'):
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            timeout=10,
        )

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """
        Receive a Fitbit response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                self.fitbit.client.fetch_access_token(code)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("base_date", help="Base date in yyyy-MM-dd format")
    parser.add_argument("detail_level", help="Detail level with value of 1sec or 1min")
    parser.add_argument("output_file", help="Path to output JSON file")
    parser.add_argument("--start_time", help="Start time in format HH:mm")
    parser.add_argument("--end_time", help="End time in format HH:mm")
    args = parser.parse_args()

    credentials = json.load(open(".fitbit"))

    # Authenticate through fitbit
    server = OAuth2Server(credentials["clientID"], credentials["clientSecret"])
    server.browser_authorize()
    try:
        print "\nRetrieving heartrate data..."
        result = server.fitbit.intraday_time_series("activities/heart", 
                                                    base_date=args.base_date, 
                                                    detail_level=args.detail_level, 
                                                    start_time=args.start_time if args.start_time else None,
                                                    end_time=args.end_time if args.end_time else None)
        print "Writing data to " + args.output_file + "..."
        file = open(args.output_file, "w")
        file.write(json.dumps(result, indent=2))
        file.close()
        print "Done."
    except Exception as e:
        print "Error retrieving data: "+ str(e)