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
        # query = 'q=type:visualization&q=visualization.title=green&size=150'
        dcos_elk_url = self.url + '/' + self.index + '/doc/_search/?' + query
        if self.check_if_valid(self.url) is True:
            if self.check_index(self.index) is True:
                return json.loads(requests.get(url=dcos_elk_url).content)
            else:
                return None
        else:
            return None

    @staticmethod
    def check_if_valid(url):
        return requests.head(url).ok

    def check_index(self, index):
        if requests.head(self.url + '/' + index).ok:
            return True
        elif requests.head(self.url + '/' + '.kibana').ok:
            self.index = '.kibana'
            return True
        else:
            return False
