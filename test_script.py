import jinja_configure
import argparse
import os
import json
import jinja2
import yaml
import requests
import time
import traceback
from string import Template


def main(args):
    config = ''
    with open(args.config) as config_yaml:
        config = yaml.load(config_yaml)

    tmp_path = args.template_conf

    jConfigure = jinja_configure.JinjaTemplate(tmp_path)
    for visual in config['visuals']:
        generic_json = jConfigure.make_file(visual)
    for env in visual['target_environments']:
        fixed_json = jConfigure.load_from_string(template=generic_json, env=env)



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
