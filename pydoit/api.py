# JSON RPC: https://en.wikipedia.org/wiki/JSON-RPC
# i-doit JSON RPC: https://kb.i-doit.com/pages/viewpage.action?pageId=37355644
# List of available methods: https://kb.i-doit.com/display/en/Methods

'''
Wrapper around the i-doit JSON RPC API
'''

import requests
import pprint

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


    def _req(self, method, req_id, **params):
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

        if response.status_code == 200:
            if "result" in response.json():
                return response.json()["result"]
            elif "error" in response.json():
                error = response.json()["error"]
                raise IdoitRequestError(error["code"], error["message"], error["data"])
        else:
            raise IdoitRequestError("-1", "Unknown Error", None)


    # -----------------------
    # --- NAMESPACE IDOIT ---
    # -----------------------
     # special method
    def login(self, req_id=1):
        """Login and create a session_id for further API calls"""

        if self.username and self.password:
            if self.session_id == None:
                result = self._req("idoit.login", req_id=req_id)
                self.session_id = result["session-id"]
            else:
                raise IdoitAlreadyLoggedInError
        else:
            raise IdoitMissingCredentialsError

    # special method
    def logout(self, req_id=1): 
        """Logout of current session"""
        self._req("idoit.logout", req_id=req_id)
        self.session_id = None

    def version(self, req_id=1):
        """Fetch information about i-doit and the current user

        Returns:
            dict: Dictionary containing information
        """
        res = self._req("idoit.version", req_id=req_id)
        return res

    def search(self, q, req_id=1):
        """Search in i-doit

        Args:
            q (str): Query string

        Returns:
            list: List containig search results
        """
        res = self._req("idoit.search", q=q, req_id=req_id)
        return res

    def constants(self, req_id=1):
        """Fetch defined constants from i-doit

        Returns:
            dict: Dictionary containing all constants
        """
        res = self._req("idoit.constants", req_id=req_id)
        return res

    # ----------------------
    # --- NAMESPACE CMDB ---
    # ----------------------
    def object_create(self, obj_type, title, category=None, purpose=None, cmdb_status=None, description=None, req_id=1):
        """Create new object with some optional information

        Args:
            obj_type (str|int): Object type constant string or type identifier as integer
            title (str): Object Title
            category (int, optional): Attribute Category in category Global. Defaults to None.
            purpose (int, optional): Attribute Purpose in category Global. Defaults to None.
            cmdb_status (int, optional): Attribute CMDB status in category Global by identifier as integer. Defaults to None.
            description (str, optional): Attribute Description in category Global. Defaults to None.

        Returns:
            dict: Dictionary containing info about the creation
        """
        res = self._req(
            "cmdb.object.create",
            type=obj_type,
            title=title,
            category=category,
            purpose=purpose,
            cmdb_status=cmdb_status,
            description=description,
            req_id=req_id
        )
        return res

    def object_read(self, obj_id, req_id=1):
        """Read common information about an object

        Args:
            obj_id (int): Object identifier as integer

        Returns:
            dict: Dict with information
        """
        res = self._req("cmdb.object.read", id=obj_id, req_id=req_id)
        return res

    def object_update(self, obj_id, title, req_id=1):
        """Update an object

        Args:
            obj_id (int): Object identifier as integer
            title (str): New title

        Returns:
            dict: Result as dict
        """
        res = self._req("cmdb.object.update", id=obj_id, title=title, req_id=req_id)
        return res

    def object_delete(self, obj_id, status, req_id=1):
        """Delete an object

        Args:
            obj_id (int): Object identifier as integer
            status (str): Status constant: C__RECORD_STATUS__ARCHIVED, C__RECORD_STATUS__DELETED, C__RECORD_STATUS__PURGE

        Returns:
            dict: Result dict
        """
        res = self._req("cmdb.object.delete", id=obj_id, status=status, req_id=req_id)
        return res

    def object_recycle(self, obj_id, req_id=1):
        """Recycles an object

        Args:
            obj_id (int): Object identifier as integer

        Returns:
            dict: Result dict
        """
        res = self._req("cmdb.object.recycle", object=obj_id, req_id=req_id)
        return res

    def object_archive(self, obj_id, req_id=1):
        """Archives an object

        Args:
            obj_id (int): Object identifier as integer

        Returns:
            dict: Result dict
        """
        res = self._req("cmdb.object.archive", object=obj_id, req_id=req_id)
        return res

    def object_purge(self, obj_id, req_id=1):
        """Purges an object

        Args:
            obj_id (int): Object identifier as integer

        Returns:
            dict: Result dict
        """
        res = self._req("cmdb.object.purge", object=obj_id, req_id=req_id)
        return res

    def object_mark_as_template(self, obj_id, req_id=1):
        """Set the Object condition as a Template

        Args:
            obj_id (int): Object identifier as integer

        Returns:
            dict: REsult dict
        """
        res = self._req("cmdb.object.markAsTemplate", object=obj_id, req_id=req_id)
        return res


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
    def __init__(self, code, msg, data):
        self.code = code,
        self.msg = msg,
        self.data = data

    def __str__(self):
        return str(f"code: {self.code}, msg: {self.msg}, data: {self.data}")
