import os
import json
import jinja2
import yaml
import requests
import time
import traceback


class IsElasticsearch():

    def __init__(self, index):
        self.index = index

    def put_json(self, url, id, payload):
        if self.check_url(url) is True:
            put_request_url = url + '/' + self.index + id
            response_json = json.loads(
                requests.put(put_request_url, json=payload).content)
            message = time.strftime("%Y-%m-%d %H:%M:%S") + \
                      ' : ' + id + ' : ' + str(response_json)

            return response_json, message

    @staticmethod
    def check_url(url):
        return requests.head(url).status_code == 200
