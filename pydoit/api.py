# JSON RPC: https://en.wikipedia.org/wiki/JSON-RPC
# i-doit JSON RPC: https://kb.i-doit.com/pages/viewpage.action?pageId=37355644
# List of available methods: https://kb.i-doit.com/display/en/Methods

'''
Wrapper around the i-doit JSON RPC API
'''

import requests

class Idoit:
    def __init__(self, url, api_key, username=None, password=None):
        """

        Args:
            url (str): URL to API Endpoint
            key (str): API Key
            username (str, optional): Username. Defaults to None.
            password (str, optional): Password. Defaults to None.
        """
        self.url = url
        self.api_key = api_key
        self.username = username
        self.password = password

        self.session_id = None


    def req(self, method, req_id=1, headers=None, **params):
        """Make a request to the API

        Args:
            method (str): RPC method
            req_id (int, optional): Request id to identify req/res. Defaults to 1.
            headers (dict, optional): Overrides the headers. Defaults to None.

        Raises:
            IdoitRequestError: Raised if an request error happens
            IdoitError: Unknown Error

        Returns:
            dict: RPC result
        """
        if headers == None:
            headers = {
                "Content-Type": "application/json"
            }

            if self.session_id: # add the session if exists
                headers["X-RPC-Auth-Session"] = self.session_id
            elif self.username and self.password: # use http basic auth if no session exists
                headers["X-RPC-Auth-Username"] = self.username
                headers["X-RPC-Auth-Password"] = self.password

            # if none of the above is added the api call will happen without authentification

        body = {
            "version": "2.0",
            "method": method,
            "params": {
                **params,
                "apikey": self.api_key
            },
            "id": req_id
        }

        response = requests.post(self.url, headers=headers, json=body)

        if "result" in response.json():
            return response.json()["result"]
        elif "error" in response.json():
            raise IdoitRequestError(response.json()["error"])
        else:
            raise IdoitError


    def login(self):
        """Login and create a session_id for further API calls"""

        if self.username and self.password:
            if self.session_id == None:
                result = self.req("idoit.login")
                print(result)
                self.session_id = result["session-id"]
            else:
                raise IdoitAlreadyLoggedInError
        else:
            raise IdoitMissingCredentialsError

    def logout(self):
        """Logout of current session"""
        self.req("idoit.logout")
        self.session_id = None


# --- Exceptions ---
class IdoitError(Exception):
    """Base idoit error"""

class IdoitMissingCredentialsError(IdoitError):
    """Missing credentials"""
    def __init__(self): pass
    def __str__(self): return "Missing credentials"

class IdoitAlreadyLoggedInError(IdoitError):
    """Already logged in"""
    def __init__(self): pass
    def __str__(self): return "Already logged in"

class IdoitRequestError(IdoitError):
    def __init__(self, msg): self.msg = msg
    def __str__(self): return str(self.msg)