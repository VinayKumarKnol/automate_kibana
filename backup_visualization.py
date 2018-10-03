#!/usr/bin/python
import argparse
import json
import requests
import os
import jinja2
from string import Template
import re
import time


# creates back up of visualizations
# global vars:
# args: contains all the command line arguments
# query_json: contains templatized query json to get env specific visualization.
# yam_template: contains tamplatized meta data.
#
# @deprecated
# yaml_header: only used if we are creating a file from scratch
#

def main(args):
    # args: contain command line arguments
    # vars used
    # path_conf: contains the name of the directory where config is placed.
    # filename_conf: contains the name of the config file name.
    # backup_file:  we are using backup file to stand our visuals.
    # id: contains the unique id associated with each visual.
    path_conf, filename_conf = os.path.split(args.backup_file)

    if not os.path.exists(path_conf):
        os.makedirs(path_conf)

    with open(path_conf + '/' + filename_conf, 'w') as backup_file:
        backup_file.write(yaml_header)
        for id in getAllTheVisualizations(args):
            backup_file.write(loadVisualizationJSON(args, id))
            print "done: " + id
    modifyBackupTemplate(args)


def modifyBackupTemplate(args):
    # modifies the jinja Templated metafile to env specific meta file.
    # vars used:
    # tmp_dir  : the name of the directory to store the env specific meta file.
    # file_name: name of the backup file (has time stamp appended).
    # path_conf: contains the name of the directory where config is placed.
    # filename_conf: contains the name of the config file name.
    # templateFilePath_conf: loader to load the jinja2 template.
    # jinjaEnv_conf: Environment configured with loader to get template.
    # jTemplate_conf: env specific meta file is contained here.
    # outFile_conf: the file which is written with env specific meta data.
    tmp_dir = 'config'
    file_name = ('backup_file_' +
                 time.strftime("%Y-%m-%d %H:%M:%S") +
                 '.yaml').replace(' ', '_')
    path_conf, filename_conf = os.path.split(args.backup_file)
    templateFilePath_conf = jinja2.FileSystemLoader(path_conf or './')
    jinjaEnv_conf = jinja2.Environment(loader=templateFilePath_conf,
                                       trim_blocks=True,
                                       lstrip_blocks=True)
    jTemplate_conf = jinjaEnv_conf.get_template(filename_conf).render(env=args.modify_env)
    outFile_conf = open(tmp_dir + '/' + file_name, 'w')
    outFile_conf.write(jTemplate_conf)
    outFile_conf.close()


def getAllTheVisualizations(args):
    # we curl the .kibana index for all the visualizations
    # elk_url: contains the query suffixed to the base url
    #          found by fetchElasticURL(args.dcos_cluster_url)
    # total_visualizations: contains total number visualizations to get.
    # search_result: json content having details of the all the visualizations.
    # query_json: a global var containing templated query which can work to get
    #             multiple environments visualizations.
    # visual_json: contains only the visualizations to extract id from (json)
    # visual_id: an array of visualization ids

    elk_url = fetchElasticURL(args.dcos_cluster_url) + \
              "_search?pretty&&size=" + total_visualizations
    search_result = requests \
        .get(elk_url,
             json=json.loads(query_json.substitute(backup_env=args.backup_env))) \
        .json()
    visuals_jsons = search_result['hits']['hits']
    visual_ids = []
    for visual in visuals_jsons:
        visual_ids.append(visual['_id'])

    return visual_ids


def loadVisualizationJSON(args, visual_index):
    # here we convert the environment specific meta data to generic templated data.
    # visual_index: contains the id of the visualization to get and convert.
    # env_replace: converts all occurences of backup_env to {{ env }}
    # visual_url: contains the link to curl from
    # visual_json: contains the result after we curl the visual_url.
    # visual_id: a modified id which has title lowercased
    #            and whitespaces converted to '_'
    # yaml_template: contains general template of meta data which will be loaded with
    #                visualization's data.
    elk_url = fetchElasticURL(args.dcos_cluster_url)
    env_replace = re.compile(re.escape(args.backup_env), re.IGNORECASE)
    visual_url = elk_url + visual_index
    visual_json = requests.get(visual_url).json()
    visual_id = re.sub(r'\W+', '_', visual_json['_source']['title']).lower().rstrip('_')
    return yaml_template.substitute(
        id=env_replace.sub('{{ env }}', visual_id),
        title=env_replace.sub('{{ env }}', visual_json['_source']['title']),
        env='{{ env }}',
        visState=json.dumps(env_replace.
                            sub('{{ env }}', visual_json['_source']['visState'])
                            ).strip('"').replace("'", "''"),
        uiStateJSON=json.dumps(env_replace.sub('{{ env }}',
                                                visual_json['_source']['uiStateJSON'])
                               ).strip('"'),
        searchSourceJSON=json.dumps(env_replace.sub('{{ env }}', visual_json['_source']
        ['kibanaSavedObjectMeta']
        ['searchSourceJSON'])
                                    )
            .strip('"')
    )


def fetchElasticURL(dcos_cluster_url):
    # fetches Elasticsearch url for each environment.
    # dcos_cluster_url: contains the dcos cluster we are working on.
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
    parser.add_argument('-e', '--backup_env', type=str, required=True,
                        help='Visualisation environment to take backup of')
    parser.add_argument('-m', '--modify_env', type=str, required=True,
                        help='Visualisation environment to take backup of')
    args = parser.parse_args()
    return args


total_visualizations = '100'
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
    uiStateJSON: '$uiStateJSON'
    searchSourceJSON: '$searchSourceJSON'
    ''')

query_json = Template('''
{            
  "query" : {
    "multi_match" : {
      "query": "$backup_env",
      "fields": ["title", "query"]
     }
  }
}
''')

args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
