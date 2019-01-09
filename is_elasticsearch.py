import requests
import json


class ElasticSearch:

    def __init__(self, url, index):
        self.url = url
        self.index = index

    def put_data(self, content):
        dcos_elk_url = self.url + '/' + self.index + '/_doc/'
        if self.check_if_valid(self.url) is True:
            response = json.loads(requests.put(dcos_elk_url, json=content).content)
            return response

    def get_data(self, query):
        dcos_elk_url = self.url + '/' + self.index +

    def check_if_valid(self, url):
        return requests.head(url).ok

    def check_index(self, index):
        if requests.head(self.url + '/' + index).ok:
            return True
        elif requests.head(self.url + '/' + '.kibana').ok:
            self.index = '.kibana'
            return True
        else:
            return False
