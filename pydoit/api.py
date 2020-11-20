
# https://en.wikipedia.org/wiki/JSON-RPC
# https://kb.i-doit.com/pages/viewpage.action?pageId=37355644
# https://kb.i-doit.com/display/en/Methods

import requests

class Idoit:
    def __init__(self, url: str, apikey: str):
        self.url = url
        self.apikey = apikey
        self.session = None
        self.use_auth = False

    def login(self, username: str, password: str):
        '''
        Login with username and password and create a session-id that is saved and used for further api calls
        ---
        It may prove useful to use the API method idoit.login for a single authentication if a lot of requests (meaning thousands) are sent from a client.\n
        Otherwise it is possible that too many sessions are created in a very small time frame but are not terminated.\n
        This could result in the fact that i-doit stops working until the sessions have been terminated.

        https://kb.i-doit.com/display/en/Methods#Methods-idoit.login
        '''
        if self.use_auth == False:
            if self.session == None:
                headers = {"Content-Type": "application/json", "X-RPC-Auth-Username": f"{username}", "X-RPC-Auth-Password": f"{password}"}
                body = {
                    "version": "2.0",
                    "method": "idoit.login",
                    "params": {
                        "apikey": f"{self.apikey}",
                        "language": "en"
                    },
                    "id": 1
                }

                res = requests.post(self.url, headers=headers, json=body)
                self.session = res.json()["result"]["session-id"]
                return res.json()
            else:
                print("Can not log in. Already logged in. Call .logout() to logout.")
        else:
            print("Can not log in. HTTP Basic Auth is enabled. (.set_auth())")
    
    def logout(self):
        """
        Logout and delete session-id from current i-doit instance

        https://kb.i-doit.com/display/en/Methods#Methods-idoit.logout
        """
        self.session = None
        response = self._make_request("idoit.logout")
        return response.json()
    
    def set_auth(self, username: str, password: str):
        """
        Use HTTP Basic Auth for every API Call
        """
        if self.session == None:
            self.use_auth = True
            self.auth = (username, password)
        else:
            print("Can not set credentials. Already logged in with session-id.")
        

    def _make_request(self, method: str, req_id: "any" = 1, lang: "en/de" = "en", **params):
        """Make an API Call with passed in method and params

        Args:
            method (str): A String with the name of the method to be invoked
            req_id (any, optional): The id of the request it is responding to. Defaults to 1.
            lang (str, optional): Change language. Defaults to "en".

        Returns:
            Response: A Response Object (requests)
        """
        body = {
            "version": "2.0",
            "method": method,
            "params": {
                **params,
                "apikey": self.apikey,
            },
            "id": req_id
        }

        headers = {"Content-Type": "application/json"} # standard header

        if self.session != None:
            headers["X-RPC-Auth-Session"] = self.session # add session-id to header if exists
            response = requests.post(self.url, headers=headers, json=body) # auth with session-id
        elif self.use_auth:
            response = requests.post(self.url, headers=headers, json=body, auth=self.auth) # auth with http basic auth
        else:
            response = requests.post(self.url, headers=headers, json=body) # request without any authentification

        if response.status_code == 200:
            return response.json()
        else:
            # raise error
            print(response.text)
            exit(1)

    def version(self):
        """
        Get various information about i-doit itself and the current user.

        https://kb.i-doit.com/display/en/Methods#Methods-idoit.version

        Response (JSON Object):
            login - Array - Information about the user who has performed the request
            login.userid - String - Object identifier (as numeric string)
            login.name - String - Object title
            login.mail - String - E-mail address (see category Persons → Master Data)
            login.username - String - User name (see category Persons → Login)
            login.mandator - String - Tenant name
            login.language - String - Language: "en" or "de"
            version - String - Version of installed i-doit
            step - String - Dev, alpha or beta release
            type - String - Release variant: "OPEN" or "PRO"
        """
        res = self._make_request("idoit.version")
        return res

    def search(self, q: str):
        """
        Search in i-doit

        https://kb.i-doit.com/display/en/Methods#Methods-idoit.search

        q : Query

        Response (JSON Object) (Can also be an array):
            documentID - String - Identifier
            key - String - Attribute which relates to query
            value - String - Value which relates to query
            type - String - Add-on or core feature
            link - String - Relative URL which directly links to search result
            score - Integer - Scoring (deprecated)

        
        """
        res = self._make_request("idoit.search", q=q)
        return res

    def constants(self):
        """
        Fetch defined constants from i-doit

        https://kb.i-doit.com/display/en/Methods#Methods-idoit.constants

        Response (JSON Object):
            objectTypes - Object - List of object types:
                Keys: object type constants
                Values: translated object type titles
            categories - Object - List of global and specific categories
            categories.g - Object - List of global categories
                Keys: category constants
                Values: translated category titles
            categories.s - Object - List of specific categories
                Keys: category constants
                Values: translated category titles
        """
        res = self._make_request("idoit.constants")
        return res

    def cmdb_object_create(self, objtype: "str|int", title: str, category: str = None, purpose: str = None, cmdb_status: "str|int" = None, description: str = None):
        """
        Create new object with some optional information


        https://kb.i-doit.com/display/en/Methods#Methods-cmdb.object.create

        Args:
            objtype (str|int): Object type constant as string, for example: "C__OBJTYPE__SERVER" or identifier as int
            title (str): Object title
            category (str, optional): Attribute Category in category Global. Defaults to "".
            purpose (str, optional): Attribute Purpose in category Global. Defaults to "".
            cmdb_status (str|int, optional): Attribute CMDB status in category Global by its constant or identifier as int. Defaults to "".
            description (str, optional): Attribute Description in category Global. Defaults to "".

        Returns:
            Response:
                    id - String - Object identifier (as numeric string)
                    message - String - Some information
                    success - Boolean - Should always be true
        """

        res = self._make_request(
            "cmdb.object.create",
            type=objtype,
            title=title,
            category=category,
            purpose=purpose,
            cmdb_status=cmdb_status,
            description=description
        )
        return res