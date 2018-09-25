#!/usr/bin/python
import argparse
import os
import json
import jinja2
import yaml
import requests


# creates visualizations over kibana by reading meta data file.
# global vars:
# args: contains command line arguments.
# @deprecated:
# validateQuery(): not using it currently.

def main(args):
    # vars used:
    # dcos_elk_url: contains elastic search url of a given env.
    # visual_json: contains the json of visualizations (List).
    # tmp_dir: contains the directory where the files are stored.
    # id: contains the visual id.
    # visual: name of the visual json file.
    # payload: contains the actual json we need to put over kibana.
    # request_result: contains the response after PUT our visual to kibana.

    dcos_elk_url = fetchClusterName(args.dcos_cluster_name)

    if dcos_elk_url is None:
        print(">>Invalid DCOS Cluster url")
        return
    visuals_json, tmp_dir = load_config(args)
    if len(visuals_json) is 0:
        print ">>There are no visualisations to create."
        return
    for id, visual in visuals_json:
        print id, visual
        elk_url = dcos_elk_url + "visualization/" + id
        print elk_url
        with open(tmp_dir + '/' + visual, 'r') as json_file:
            payload = json.load(json_file)
            request_result = json.loads(requests.put(elk_url, json=payload).content)
            print ">>status of visualisation: " + id + " :"
            print request_result
    return


def validateQuery(config, dcos_cluster):
    query_url = dcos_cluster + '_doc/_validate/query?'
    response = json.loads(requests.get(query_url, json=config['query']).content)
    if response['valid'] is True:
        return True
    else:
        return False


def fetchClusterName(dcos_cluster_name):
    # fetches the name of the cluster
    # dcos_cluster_name: contains the name of the cluster we are to work with
    #                    defined through cl arguments.
    if "rigel" in dcos_cluster_name:
        return "http://monit-es-rigel.storefrontremote.com/.kibana/"
    elif "saturn" in dcos_cluster_name:
        return "http://elk-saturn.storefrontremote.com/.kibana/"
    elif "neptune" in dcos_cluster_name:
        return "neptune"
    elif "jupiter" in dcos_cluster_name:
        return "jupiter"


def create_bundle_conf_file(args, config, tmp_dir):
    # creates the visual json from meta data
    # config: contains the meta data of visual
    # tmp_dir: directory where we want to put the visual json.
    # file_name: contains the name of visualizations json.
    # path_conf: contains the directory where we have the template file stored.
    # filename_conf: contains the meta data file name.
    # templateFilePath_conf: A File System Loader.
    # jinjaEnv_conf: Environment config'd with loader.
    # jTemplate_conf: contains the env specific meta data.
    # outputFile_conf: contins the json file where we are writing the env specific
    #                  visual json.
    # returns: visual_id , file_name.
    file_name = config['id'] + "-visualization.json"
    path_conf, filename_conf = os.path.split(args.template_conf)
    templateFilePath_conf = jinja2.FileSystemLoader(path_conf or './')
    jinjaEnv_conf = jinja2.Environment(loader=templateFilePath_conf,
                                       trim_blocks=True,
                                       lstrip_blocks=True)
    jTemplate_conf = jinjaEnv_conf.get_template(filename_conf).render(config)

    outFile_conf = open(tmp_dir + '/' + file_name, 'w')
    outFile_conf.write(jTemplate_conf)
    outFile_conf.close()
    return config['id'], file_name


def load_config(args):
    # loads the meta data and creates list of visuals to load.
    # config: contains the visual config file.
    # tmp_dir: contains the directory to store the visuals.
    # file_locations: a List of visual jsons to load.
    # returns: file locations and directory where all the visuals are stored.

    with open(args.config) as config:
        config = yaml.load(config)

    tmp_dir = "tmp-visual-config-dir"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    file_locations = []

    for visual in config['visuals']:
        visual['title'] = visual['title']
        visual['id'] = visual['id'].lower()
        file_locations.append(create_bundle_conf_file(args, visual, tmp_dir))
        # if validateQuery(visual, fetchClusterName(args.dcos_cluster_name)):
        #
        # else:
        #     print ">>Visual: " + visual['id']
        #     print "Has wrong query."
    return file_locations, tmp_dir


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Jinja2 template configuration yaml file')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    parser.add_argument('-u', '--dcos_cluster_name', type=str, required=True,
                        help='Cluster where these visualisations are needed')
    args = parser.parse_args()
    return args


args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
