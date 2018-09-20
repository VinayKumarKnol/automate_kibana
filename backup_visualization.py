#!/usr/bin/python
import argparse
import json
import requests
import yaml
from string import Template


def main(args):
    for id in getAllTheVisualizations(args):
        meta_data = loadVisualizationJSON(args, id)
        if len(meta_data) is not 0 and not visualExists(id):
            with open('config/visual_conf_duplicate.yaml', 'a') as meta_yaml:
                meta_yaml.write(yaml_template.substitute(
                    id=meta_data['id'],
                    title=meta_data['title'].rsplit(' ', 1)[0],
                    env=meta_data['env'].upper(),
                    filter=meta_data['filter'],
                    index=meta_data['index'],
                    Axis_Y=meta_data['Axis_Y'],
                    query=meta_data['query']
                ))


def getAllTheVisualizations(args):
    elk_url = fetchElasticURL(args.dcos_cluster_url) + \
              "_search"
    search_result = requests.get(elk_url).json()
    visuals_jsons = search_result['hits']['hits']
    visual_ids = []
    for visual in visuals_jsons:
        visual_ids.append(visual['_id'])

    return visual_ids


def loadVisualizationJSON(args, visual_index):
    elk_url = fetchElasticURL(args.dcos_cluster_url)
    visual_url = elk_url + visual_index
    visual_json = requests.get(visual_url).json()
    if visual_json['found']:
        meta_data = {'id': visual_index,
                     'title': visual_json['_source']['title'],
                     'env': visual_index.split('_')[-1].upper(),
                     'filter': '',
                     'index': '',
                     'Axis_Y': '',
                     'query': ''}
        visState_json = json.loads(visual_json['_source']['visState'])
        searchSource_json = json.loads(visual_json['_source']['kibanaSavedObjectMeta']['searchSourceJSON'])

        meta_data['Axis_Y'] = json.dumps(visState_json['aggs'][0]['params']).replace('"', '\\"')
        meta_data['index'] = searchSource_json['index']
        meta_data['filter'] = json.dumps(searchSource_json['filter'][0]).replace('"', '\\"')
        meta_data['query'] = json.dumps(searchSource_json['query']).replace('"', '\\"')

        return meta_data

    else:
        return {}


def fetchElasticURL(dcos_cluster_url):
    if "rigel" in dcos_cluster_url:
        return "http://monit-es-rigel.storefrontremote.com/.kibana/visualization/"
    elif "saturn" in dcos_cluster_url:
        return "saturn"
    elif "neptune" in dcos_cluster_url:
        return "neptune"
    elif "jupiter" in dcos_cluster_url:
        return "jupiter"


def visualExists(visual_id):
    with open('config/visual_conf_duplicate.yaml', 'r') as meta_file:
        meta_yaml = yaml.load(meta_file)
        visualIds = []
        if meta_yaml['visuals'] is None:
            return False
        for visual in meta_yaml['visuals']:
            visualIds.append(visual['id'])

        return visual_id in visualIds


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-u', '--dcos_cluster_url', type=str, required=True,
                        help='Cluster where these visualisations are needed')
    parser.add_argument('-e', '--environment', type=str, required=True,
                        help='Environment who visualisations needs backup.')
    args = parser.parse_args()
    return args


yaml_template = Template('''
  -
    id: $id
    title: $title
    env: $env
    filter: '$filter'
    index: $index
    Axis_Y: '$Axis_Y'
    query: '$query'
        ''')

args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
