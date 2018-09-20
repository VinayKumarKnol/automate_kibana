#!/usr/bin/python
import argparse
import json
import requests
import yaml
import os
from string import Template


def main(args):
    config_location = 'config'
    file_name = args.backup_file

    if not os.path.exists(config_location):
        os.makedirs(config_location)

    with open(config_location + '/' + file_name, 'w') as backup_file:
        backup_file.write(yaml_header)
        for id in getAllTheVisualizations(args):
            backup_file.write(loadVisualizationJSON(args, id))
            print "done: " + id


def getAllTheVisualizations(args):
    elk_url = fetchElasticURL(args.dcos_cluster_url) + \
              "_search?pretty&&size=" + total_visualizations
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
    return yaml_template.substitute(
        id=visual_json['_id'],
        title=visual_json['_source']['title'],
        env='all',
        visState=json.dumps(visual_json['_source']['visState']).strip('"'),
        uiStateJSON=json.dumps(visual_json['_source']['uiStateJSON']).strip('"'),
        searchSourceJSON=visual_json['_source']
        ['kibanaSavedObjectMeta']
        ['searchSourceJSON']
            .replace('"', '\\"')
    )


def fetchElasticURL(dcos_cluster_url):
    if "rigel" in dcos_cluster_url:
        return "http://monit-es-rigel.storefrontremote.com/.kibana/visualization/"
    elif "saturn" in dcos_cluster_url:
        return "http://elk-saturn.storefrontremote.com/.kibana/visualization/"
    elif "neptune" in dcos_cluster_url:
        return "neptune"
    elif "jupiter" in dcos_cluster_url:
        return "jupiter"


# def visualExists(visual_id):
#     with open('config/visual_conf_duplicate.yaml', 'r') as meta_file:
#         meta_yaml = yaml.load(meta_file)
#         visualIds = []
#         if meta_yaml['visuals'] is None:
#             return False
#         for visual in meta_yaml['visuals']:
#             visualIds.append(visual['id'])
#
#         return visual_id in visualIds


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-u', '--dcos_cluster_url', type=str, required=True,
                        help='Cluster where these visualisations are needed')
    parser.add_argument('-b', '--backup_file', type=str, required=True,
                        help='Name of backup file  in YAML')
    args = parser.parse_args()
    return args


total_visualizations = '1'
yaml_header = '''
---
visuals:

'''
yaml_template = Template('''
  -
    id: $id
    title: $title
    env: $env
    visState: '$visState'
    uiStateJSON: $uiStateJSON
    searchSourceJSON: '$searchSourceJSON'
    ''')

args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
