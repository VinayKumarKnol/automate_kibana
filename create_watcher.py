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
    watchers_json, tmp_dir = load_config(args)
    if len(watchers_json) is 0:
        print ">>There are no visualisations to create."
        return
    for id, watcher in watchers_json:
        # print id, watcher
        elk_url = "http://monit-es-" + dcos_cluster_name + \
                  ".storefrontremote.com/_xpack/watcher/watch/" + id
        # print elk_url
        print watcher
        with open(tmp_dir + '/' + watcher, 'r') as json_file:
            payload = json.load(json_file)
            # print payload
            request_result = json.loads(requests.put(elk_url, json=payload).content)
            print ">>status of visualisation: " + id + " :"
            print request_result
    return


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
    file_name = config['id'] + "-watcher.json"
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

    tmp_dir = "tmp-watchers-config-dir"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    file_locations = []

    for watcher in config['watchers']:
        watcher['email_subject'] = watcher['email_subject'] + \
                                   args.dcos_cluster_url.upper()
        file_locations.append(create_bundle_conf_file(args, watcher, tmp_dir))

    return file_locations, tmp_dir


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Jinja2 template configuration yaml file')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    parser.add_argument('-u', '--dcos_cluster_url', type=str, required=True,
                        help='Cluster whose Kibana will be targeted')
    args = parser.parse_args()
    return args


args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
