from flask import Flask
from flask_restplus import Api, Resource, fields
import requests
import json
api = Api(app)
ACCESS_TOKEN = "4698f4c543d948d0f351984b084acacc5e574514ce98ab50"
expect_for_query = api.model('query', {'query': fields.String('Convert 50 Dollars to Rupees')})


    @api.expect(expect_for_signup)
    def post(self):
        username = api.payload["username"]
        password = api.payload["password"]
        email = api.payload["email"]
        if username == "":
            return {"response": "Username cannot be left empty"}
        elif password == "":
            return {"response": "Password cannot be left empty"}
        elif email == "":
            return {"response": "Email cannot be left empty"}
        url = "https://auth.hundred76.hasura-app.io/v1/signup"

        # This is the json payload for the query
        requestPayload = {
            "provider": "username",
            "data": {
                "username": username,
                "password": password
            }
        }

        # Setting headers
        headers = {
        "Content-Type": "application/json"
         }

        # Make the query and store response in resp
        resp = requests.request("POST", url, data=json.loads(requestPayload), headers=headers)
        response = resp.content
        print(response)
        if resp.status_code == 200:
            hasura_id = response["hasura_id"]
            url_ = "https://data.hundred76.hasura-app.io/v1/query"

        # This is the json payload for the query
            requestPayload_ = {
                "type": "insert",
                "args": {
                    "table": "email",
                    "objects": [
                       {
                        "hasura_id": hasura_id,
                        "email": email,
                        "username": username
                       }
                    ]
                }
            }
            # Make the query and store response in resp
            resp_ = requests.request("POST", url_, json=requestPayload_, headers=headers)
        if resp.status_code == 200:
            return {"response": "user added"}
        elif resp.status_code == 400:
            return {"response": "user exists"}
        else:
            return {"response": "Internal server error"}


@api.route('/login')
class Todo(Resource):
    @api.expect(expect_for_login)
    def post(self):
        username = api.payload["username"]
        password = api.payload["password"]
        if username == "":
            return {"response": "Username cannot be left empty"}
        elif password == "":
            return {"response": "Password cannot be left empty"}
        # This is the url to which the query is made
        url = "https://auth.hundred76.hasura-app.io/v1/login"

        # This is the json payload for the query
        requestPayload = {
            "provider": "username",
            "data": {
                "username": username,
                "password": password
            }
        }

        # Setting headers
        headers= {
        "Content-Type": "application/json"
         }

        # Make the query and store response in resp
        resp = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)
        response = resp.json()
        auth_token = response["auth_token"]
        url_ = "https://data.hundred76.hasura-app.io/v1/query"

        requestPayload_ = {
            "type": "insert",
            "args": {
                "table": "Auth",
                "objects": [
                    {
                        "auth_token": auth_token,
                        "username": username
                    }
                ]
            }
        }
        # Make the query and store response in resp
        requests.request("POST", url_, data=json.dumps(requestPayload_), headers=headers)
        # resp.content contains the json response.
        if resp.status_code == 200:
            return {"response": "user logged in"}
        elif resp.status_code == 400:
            return {"response": "Invalid credentials"}
        else:
            return {"response": "Internal server error"}


@api.route('/query')
class Todo(Resource):
    @api.expect(expect_for_query)
    def post(self):
        query = api.payload["query"]
        if query == "":
            return {"response": "You can't enter an empty query"}
        headers = {
            "Authorization": "Bearer " + ACCESS_TOKEN,
            "Content - Type": "application / json"
        }
        body = {
         "lang": "en",
         "query": query,
         "sessionId": "ed49f385-decb-4859-bebd-1dd6b842ac1c",
         "timezone": "America/Los_Angeles"
         }
        send_request = requests.post("https://api.dialogflow.com/v1/query?v=20150910", json=body, headers=headers)
        response = send_request.json()
        output = response["result"]["fulfillment"]["speech"]
        payload = {"response": output}
        print(response)
        return payload


@api.route('/webhook')
class Todo(Resource):
    def post(self):
        data = api.payload
        if data is None:
            return {}
        result = data["result"]
        action = result["action"]
        if action != "Action":
            return {}
        parameters = result["parameters"]
        currency_from = parameters["currency-from"]
        currency_to = parameters["currency-to"]
        amount = float(parameters["amount"])
        req = requests.get("https://api.fixer.io/latest?base=" + currency_from)
        abc = req.json()
        rate = float(abc["rates"][currency_to])
        converted_amount = str(amount * rate)
        speech = "The converted amount is : " + converted_amount + " " + currency_to
        response = {
            "speech": speech,
            "displayText": speech,
            "source": "Conversion.py"
        }
        return response


@api.route('/logout')
class Todo(Resource):
    @api.expect(expect_for_logout)
    def post(self):
        username = api.payload["username"]
        url = "https://data.hundred76.hasura-app.io/v1/query"

        # This is the json payload for the query
        requestPayload = {
            "type": "select",
            "args": {
                "table": "Auth",
                "columns": [
                    "auth_token"
                ],
                "where": {
                    "username": username
                }
            }
        }

        # Setting headers
        headers = {
        "Content-Type": "application/json"
          }

        # Make the query and store response in resp
        resp = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)
        response = resp.json()
        # resp.content contains the json response.
        auth_token = response[0]["auth_token"]
        # This is the url to which the query is made
        url_ = "https://auth.hundred76.hasura-app.io/v1/user/logout"
        # This is the json payload for the query
        # Setting headers
        headers_ = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "+auth_token
        }

        # Make the query and store response in resp
        resp_ = requests.request("POST", url_, headers=headers_)

        # resp.content contains the json response.
        if resp_.status_code == 200:
            return {"response": "user logged out"}

        elif resp_.status_code == 401:
            return {"response": "Invalid authorization token or user does not exist"}

        else:
            return {"response": "Internal server error"}


if __name__ == '__main__':
    app.run()
