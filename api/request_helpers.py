import requests
from requests.auth import HTTPBasicAuth
import json
import time




class RequestHelpers:

    def __init__(self, url = None, params = None):
        self.url = url
        self.params = params
        self.headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJyb2xlX25hbWUiOiJBZG1pbmlzdHJhdG9yIiwiZnVsbF9uYW1lIjoiSG_DoG5nIMSQ4bupYyBExaluZyIsInJvbGUiOiIxIiwidXNlcl9pZCI6IjEiLCJwZXJtaXNzaW9ucyI6WyJ2aWV3X3RlbXBsYXRlcyIsInZpZXdfbW9wcyIsInJ1bl9tb3BzIiwidmlld19jb21tYW5kcyIsImNyZWF0ZV9jb21tYW5kcyIsImVkaXRfY29tbWFuZHMiLCJ2aWV3X2FjdGlvbnMiLCJjcmVhdGVfYWN0aW9ucyIsImVkaXRfYWN0aW9ucyIsImNyZWF0ZV90ZW1wbGF0ZXMiLCJlZGl0X3RlbXBsYXRlcyIsImNyZWF0ZV9tb3BzIiwiZWRpdF9tb3BzIiwidmlld191c2VycyIsImNyZWF0ZV91c2VycyIsImVkaXRfdXNlcnMiLCJ2aWV3X3Blcm1pc3Npb25zIiwiY3JlYXRlX3Blcm1pc3Npb25zIiwiZWRpdF9wZXJtaXNzaW9ucyJdLCJuYW1lIjoiYnViaSIsImRlcGFydG1lbnQiOiJOaMOibiBz4buxIiwiZXhwIjoxNTIzMjQ4Nzg0LCJpYXQiOjE0OTczMjg3ODR9.O4f_CP-P7v_AnRpW5-kDRKLSamnG6W_lOeyBN1CLxoJ28KnqoTIhs9shluCqyneEk2seXyls32nz2xocpv5DeF8M3wdUEGreq_5LXnijolnN16chGHdWRlRGAkHOdpu5p1H3qNZzvGYaVzXMH6ZxKUIBzQ9einy8SIqiuZ2mf-uh-kSMP1iQjQft4mtD9tP9_DqXnXKfdvF93a-IE-OJXvBI7BKmaYVxIXzWJSQCwmIi4QO2KwU28YQAbCFxMJpsQVprvdaBR84bdnBt-CTmLlq1v7dRBcX0Le2qAsKCoRIJ72U9WowZ8tSdcaiiD9k3gnzGLlmbcY7E-zsZzqZUdw=="}
        self.username = 'bubi'
        self.password = '123456'



    def get(self):
        if self.params is not None:
            res = requests.get(self.url, params=self.params)
            res.raise_for_status()
            return res
        else:
            res = requests.get(self.url, params=self.params)
            res.raise_for_status()
            return res

    def get_test(self):
        if self.params is not None:
            res = requests.get(self.url, params=self.params)
            res.raise_for_status()
            return res
        else:
            res = requests.get(self.url, headers = self.headers, auth=HTTPBasicAuth(self.username, self.password))
            res.raise_for_status()
            return res

    def post(self):
        return requests.post(self.url, data=json.dumps(self.params))


    def put(self):
        return requests.put(self.url, data=json.dumps(self.params))
