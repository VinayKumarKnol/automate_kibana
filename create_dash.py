#!/usr/bin/python
import argparse
import os
import jinja2
import yaml
import requests
import json


def main(args):
    dcos_cluster_name = fetchClusterName(args.dcos_cluster_url)

    if dcos_cluster_name is None:
        print(">>Invalid DCOS Cluster url")
        return

    dashboard_jsons, tmp_dir = load_config(args)
    if len(dashboard_jsons) is 0:
        print ">>There are no dashboards to put on kibana."
        return
    for id, dashboard in dashboard_jsons:
        elk_url = "http://monit-es-" + args.dcos_cluster_url + \
                  ".storefrontremote.com/.kibana/dashboard/" \
                  + id
        with open(tmp_dir + '/' + dashboard, 'r') as json_file:
            payload = json.load(json_file)
            response = json.loads(requests.put(elk_url, json=payload).content)
            print ">>status of dashboard: " + id + " :"
            print response
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


def load_config(args):
    # print args.config

    with open(args.config) as config:
        config = yaml.load(config)
    tmp_dir = "tmp-dashboard-config-dir"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    file_location = []
    for dashboard in config['dashboard']:
        file_location.append(create_dash_configs(args, dashboard, tmp_dir))
    return file_location, tmp_dir


def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Configuration Yaml File for J2 Templates')
    parser.add_argument('-u', '--dcos_cluster_url', type=str, required=True,
                        help='dcos cluster where dashboards are needed.')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    args = parser.parse_args()
    print args
    return args


def create_dash_configs(args, dashboard, tmp_dir):
    # print dashboard
    file_name = dashboard['id'] + "-dashboard.json"
    path_conf, filename_conf = os.path.split(args.template_conf)
    templateFilePath_conf = jinja2.FileSystemLoader(path_conf or './')
    jinjaEnv_conf = jinja2.Environment(loader=templateFilePath_conf, trim_blocks=True,
                                       lstrip_blocks=True)
    jTemplate_conf = jinjaEnv_conf.get_template(filename_conf).render(dashboard)
    outFile_conf = open(tmp_dir + '/' + file_name, 'w')
    outFile_conf.write(jTemplate_conf)
    outFile_conf.close()
    return dashboard['id'], file_name


args = parseArgs()
if __name__ == '__main__':
    exit(main(args))
