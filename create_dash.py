#!/usr/bin/python
import argparse
import os
import jinja2
import yaml
import requests
import json
import time
import traceback


# puts dashboards on kibana by reading from meta data.
# global vars:
# args: contain command line arguments.

def main(args):
    # vars used:
    # dcos_elk_url: contains elastic search url of a given env.
    # dashboard_jsons: contains the json of dashboards (List).
    # tmp_dir: contains the directory where the files are stored.
    # id: contains the dashboard id.
    # dashboard: name of the dashboard json file.
    # payload: contains the actual json we need to put over kibana.
    # response: contains the response after PUT our dashboard to kibana.
    exit_status = 0
    failed_ids = []
    elk_url = fetchClusterName(args.dcos_cluster_name)

    if elk_url is None:
        print(">>Invalid DCOS Cluster url")
        return

    log_file_location = 'log/dashboard_logs.log'
    log_file_dir, _ = os.path.split(log_file_location)
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)

    dashboard_jsons, tmp_dir = load_config(args)
    if len(dashboard_jsons) is 0:
        print ">>There are no dashboards to put on kibana."
        return
    for id, dashboard in dashboard_jsons:
        elk_url = elk_url + \
                  "dashboard:" + id
        print elk_url
        with open(tmp_dir + '/' + dashboard, 'r') as json_file:
            try:
                payload = json.load(json_file)
                print payload
                response = json.loads(requests.put(elk_url, json=payload).content)
                print ">>status of dashboard: " + id + " :"
                print response
                logStatus(id, response, log_file_location)
            except:
                exit_status += 1
                failed_ids.append(id)
                logStatus(id, traceback.format_exc(), log_file_location)

    if exit_status is not 0:
        print '>>Following Ids FAILED:'
        print '========================'
        for id in failed_ids:
            print id
        print '========================'
        exit("There's error while processing your meta-data and jsons. Check logs.")
    else:
        exit(0)


def fetchClusterName(dcos_cluster_name):
    # gets the name of the elastic search cluster.
    if "rigel" in dcos_cluster_name:
        return "http://monit-es-rigel.storefrontremote.com/.kibana/doc/"
    elif "saturn" in dcos_cluster_name:
        return "http://elk-saturn.storefrontremote.com/.kibana/doc/"
    elif "neptune" in dcos_cluster_name:
        return "neptune"
    elif "jupiter" in dcos_cluster_name:
        return "jupiter"


def logStatus(dashboard_id, response, log_file_location):
    # logs the output to put request we have thrown over kibana
    # dashboard_id: contains the dashboard_id of the dashboard.
    # response: json which contains the result of the request we have made.
    # log_file_location: represents the location of the log file.

    with open(log_file_location, 'a') as log_file:
        message = time.strftime("%Y-%m-%d %H:%M:%S") + \
                  ' : ' + dashboard_id + ' : ' + str(response)
        log_file.write(message + '\n')


def load_config(args):
    # loads the meta data and creates list of dashboards to load.
    # config: contains the dashboard config file.
    # env_config: contains the env specific meta data.
    # config: yaml dumped env_config.
    # tmp_dir: directory where all the dashboards are stored.
    # file_location: A list of dashboards to load over kibana.
    # returns: location of files and directory where the files are stored.
    with open(args.config) as config:
        env_config = jinja2.Template(config.read()).render(env=args.environment)
        config = yaml.load(env_config)
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
    parser.add_argument('-u', '--dcos_cluster_name', type=str, required=True,
                        help='dcos cluster where dashboards are needed.')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    parser.add_argument('-e', '--environment', type=str, required=True,
                        help='environment to make dashboard for.')

    args = parser.parse_args()
    print args
    return args


def create_dash_configs(args, dashboard, tmp_dir):
    # creates the dashboard json from meta data
    # dashboard: contains the meta data of dashboard.
    # tmp_dir: directory where we want to put the dashboard json.
    # file_name: contains the name of dashboard json.
    # path_conf: contains the directory where we have the template file stored.
    # filename_conf: contains the meta data file name.
    # templateFilePath_conf: A File System Loader.
    # jinjaEnv_conf: Environment config'd with loader.
    # jTemplate_conf: contains the env specific meta data.
    # outputFile_conf: contains the json file where we are writing the env specific
    #                  dashboard json.
    # returns: dashboard_id , file_name.
    file_name = dashboard['id'] + "_dashboard.json"
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
