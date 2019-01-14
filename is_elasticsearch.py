import requests
import json


class ElasticSearch:

    def __init__(self, url, index):
        self.url = url
        self.index = index

    def put_data(self, content, id):
        dcos_elk_url = self.url + '/' + self.index + '/doc/' + id
        if self.check_if_valid(self.url) is True:
            if self.check_index(self.index) is True:
                print ">>status of visualisation: " + id + " :"
                response = json.loads(requests.post(dcos_elk_url, json=content).content)
                return response
            else:
                print '\n>>The Index used is Invalid.'
                return None
        else:
            print '\n>>The URL used is Invalid.'
            return None

    def get_data(self, query):
        # query = 'q=type:visualization&q=visualization.title=green&size=150'
        dcos_elk_url = self.url + '/' + self.index + '/doc/_search/?' + query
        if self.check_if_valid(self.url) is True:
            if self.check_index(self.index) is True:
                return json.loads(requests.get(url=dcos_elk_url).content)
            else:
                print '\n>>The Index used is invalid.'
                return None
        else:
            print '\n>>This URL used is Invalid.'
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
