import os
import json
import jinja2
import yaml


class JinjaTemplate():

    def __init__(self, template_location):
        self.template_file_path = template_location
        self.path_conf, self.conf_file = os.path.split(self.template_file_path)

        self.jinja_filepath_conf = jinja2.FileSystemLoader(self.path_conf or './')

        self.jinjaEnv_conf = jinja2.Environment(loader=self.jinja_filepath_conf,
                                                trim_blocks=True,
                                                lstrip_blocks=True)

    def make_file(self, meta_data):
        return self.jinjaEnv_conf.get_template(self.conf_file).render(meta_data)

    def load_from_string(self, template, **kwargs):
        template_loader = jinja2.Environment(loader=jinja2.BaseLoader)\
            .from_string(template)
        return template_loader.render(**kwargs)