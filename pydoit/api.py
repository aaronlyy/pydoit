import requests

class Idoit:
    def __init__(self, url, username, password, apikey):
        self.username = username
        self.password = password
        self.auth = (username, password)
        self.apikey = apikey
        self.session = None
        self.url = url

    def login(self):
        '''Creates a session-id that can be used for further api calls'''
        if self.session == None:
            headers = {"Content-Type": "application/json", "X-RPC-Auth-Username": f"{self.username}", "X-RPC-Auth-Password": f"{self.password}"}
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

            if res.status_code == 200:
                self.session = res.json()["result"]["session-id"]
            else:
                print(res.json())
                exit(1)
        else:
            # raise error already logged in
            pass
        

    def _make_request(self, method, req_id=1, lang="en", **params):
        """Make an API Call with passed in method and params

        Args:
            method (str): A String with the name of the method to be invoked
            req_id (int, optional): The id of the request it is responding to. Defaults to 1.
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
                "language": lang,
            },
            "id": req_id
        }

        headers = {"Content-Type": "application/json"} # standard header

        if self.session != None:
            headers["X-RPC-Auth-Session"] = self.session # add seesion-id to header if exists
            response = requests.post(self.url, headers=headers, json=body) # auth with session-id
        else:
            response = requests.post(self.url, headers=headers, json=body, auth=self.auth) # auth with http basic auth

        return response

    def get_version(self):
        res = self._make_request("idoit.version")
        print(res.text)