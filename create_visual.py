#!/usr/bin/python
import argparse
import os
import json
import jinja2
import yaml
import requests


def main(args):
    dcos_cluster_name = fetchClusterName(args.dcos_cluster_url)

    if dcos_cluster_name is None:
        print(">>Invalid DCOS Cluster url")
        return
    visuals_json, tmp_dir = load_config(args)
    if len(visuals_json) is 0:
        print ">>There are no visualisations to create."
        return
    for id, visual in visuals_json:
        print id, visual
        elk_url = "http://monit-es-" + dcos_cluster_name + \
                  ".storefrontremote.com/.kibana/visualization/" + id
        print elk_url
        with open(tmp_dir + '/' + visual, 'r') as json_file:
            payload = json.load(json_file)
            request_result = json.loads(requests.put(elk_url, json=payload).content)
            print ">>status of visualisation: " + id + " :"
            print request_result
    return


def validateQuery(config, dcos_cluster):
    query_url = 'http://monit-es-' + dcos_cluster + \
                '.storefrontremote.com/.kibana/_doc/_validate/query?q=\"' + \
                config['query'] + "\""
    response = json.loads(requests.get(query_url).content)
    if response['valid'] is True:
        return True
    else:
        return False


def fetchClusterName(dcos_cluster_url):
    if "rigel" in dcos_cluster_url:
        return "rigel"
    elif "saturn" in dcos_cluster_url:
        return "saturn"
    elif "neptune" in dcos_cluster_url:
        return "neptune"
    elif "jupiter" in dcos_cluster_url:
        return "jupiter"


def create_bundle_conf_file(args, config, tmp_dir):
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
    with open(args.config) as config:
        config = yaml.load(config)

    tmp_dir = "tmp-visual-config-dir"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    file_locations = []

    for visual in config['visuals']:
        visual['title'] = visual['title'] + " " + visual['env']
        visual['id'] = visual['id'].lower() + "_" + visual['env'].lower()
        if validateQuery(visual, fetchClusterName(args.dcos_cluster_url)):
            file_locations.append(create_bundle_conf_file(args, visual, tmp_dir))
        else:
            print ">>Visual: " + visual['id']
            print "Has wrong query."
    return file_locations, tmp_dir


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Jinja2 template configuration yaml file')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    parser.add_argument('-u', '--dcos_cluster_url', type=str, required=True,
                        help='Cluster where these visualisations are needed')
    args = parser.parse_args()
    return args


args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
