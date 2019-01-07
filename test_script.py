import jinja_configure
import argparse
import os
import json
import jinja2
import yaml
import requests
import time
import traceback

def main(args):
    config = ''
    with open(args.config) as config_yaml:
        config = yaml.load(config_yaml)

    tmp_path = args.template_conf
    print tmp_path

    jConfigure = jinja_configure.JinjaTemplate(tmp_path)
    for visual in config['visuals']:
        print jConfigure.make_file(visual)



def parseArgs():
    parser = argparse.ArgumentParser(description='Python template engine using jinja2')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Jinja2 template configuration yaml file')
    parser.add_argument('-tc', '--template_conf', type=str, required=True,
                        help='Jinja2 template file for config')
    args = parser.parse_args()
    return args


args = parseArgs()
if __name__ == '__main__':
    exit(main(args))