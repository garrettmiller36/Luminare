import subprocess
import os
from tempfile import gettempdir
from io import BytesIO
from flask import send_file
from flask_restful import Resource
from flask import request
import fnmatch
from jinja2 import meta
import re
import jinja2
import shutil


class BaseCompiler:
    def compile(self, template_name, document):
        raise NotImplementedError()


class SendFileCompiler(BaseCompiler):
    """A simple compiler that tries to send the compiled template as a file instead of a simple request content."""
    FILE_EXTENSION = None
    FILE_PREFIX = None
    FILE_POSTFIX = None

    def __init__(self, file_extension=None, file_prefix=None, file_postfix=None):
        self.FILE_EXTENSION = file_extension or self.FILE_EXTENSION
        self.FILE_PREFIX = file_prefix or self.FILE_PREFIX
        self.FILE_POSTFIX = file_postfix or self.FILE_POSTFIX

    def _build_file_name(self, template_name):
        file_name = ''
        extension = '.' + self.FILE_EXTENSION if self.FILE_EXTENSION else None
        for part in [self.FILE_PREFIX, template_name, self.FILE_POSTFIX, extension]:
            if part:
                file_name += part
        return file_name

    def _create_file(self, template_name, document):
        buffer = BytesIO()
        buffer.write(document.encode('utf-8'))
        buffer.seek(0)
        return buffer

    def compile(self, template_name, document):
        file = self._create_file(template_name, document)
        return send_file(file, attachment_filename=self._build_file_name(template_name),
                         as_attachment=True)


class LatexCompiler(SendFileCompiler):
    LATEX_COMMAND = 'pdflatex -interaction=nonstopmode'
    FILE_EXTENSION = 'pdf'

    _OUT_DIR = gettempdir()
    _TEMP_OUT_NAME = 'temp'

    def __init__(self, file_extension=None, file_prefix=None, file_postfix=None, latex_command=None):
        self.LATEX_COMMAND = latex_command or self.LATEX_COMMAND
        super().__init__(file_extension=file_extension, file_prefix=file_prefix, file_postfix=file_postfix)

    def _create_file(self, template_name, document):
        tempfile = os.path.join(self._OUT_DIR, self._TEMP_OUT_NAME)
        temp_tex = tempfile + '.tex'
        with open(temp_tex, 'wb') as f:
            f.write(document.encode('utf-8'))
        proc = subprocess.Popen([*self.LATEX_COMMAND.split(' '), temp_tex], cwd=self._OUT_DIR)
        return_code = proc.wait()
        if return_code != 0:
            raise SystemError()  # TODO: Make this a proper error
        return tempfile + '.' + self.FILE_EXTENSION
        
LATEX_TEMPLATE_CONFIG = {
    'block_start_string': '\BLOCK{',
    'block_end_string': '}',
    'variable_start_string': '\VAR{',
    'variable_end_string': '}',
    'comment_start_string': '\#{',
    'comment_end_string': '}',
    'line_statement_prefix': '%%',
    'line_comment_prefix': '%#',
    'trim_blocks': True,
    'autoescape': False
}

class BaseGlobalProvider:
    def get_globals(self):
        """Get a dictionary of global values."""
        raise NotImplementedError()


class DictGlobalProvider(BaseGlobalProvider):
    GLOBALS = None

    def __init__(self, global_variables):
        self.GLOBALS = global_variables

    def get_globals(self):
        return self.GLOBALS

class BaseTemplateView(Resource):
    """Base View To Provide Templates.

    Attributes:
        GLOBAL_PROVIDER: A Class instance that handels global variables
        ENVIRONMENT: A jinja2 Environment providing a template loader that supports list_templates
        COMPILER: A class instance that handles optionally compiling documents after the templating step
    """
    ENVIRONMENT = None
    GLOBAL_PROVIDER = None
    COMPILER = None

    def get(self, template_name=None):
        """Return list of templates or details of a single template"""
        if not template_name:
            match_filter = request.args.get('filter', default='*', type=str)
            return {
                'templates': self.ENVIRONMENT.list_templates(filter_func=lambda x: fnmatch.fnmatch(x, match_filter))}
        source = str(self.ENVIRONMENT.loader.get_source(self.ENVIRONMENT, template_name)[0])
        return_dict = {
            'template_name': template_name,
            'source': source,
            'vars': list(meta.find_undeclared_variables(self.ENVIRONMENT.parse(source)))
        }
        if self.GLOBAL_PROVIDER:
            return_dict['globals'] = self.GLOBAL_PROVIDER.get_globals()
        return return_dict

    def post(self, template_name):
        """Post data to a template and return a rendered template."""
        if request.is_json:
            vars = request.get_json().get('vars', {})
        else:
            vars = {}
        if self.GLOBAL_PROVIDER:
            vars = {**self.GLOBAL_PROVIDER.get_globals(), **vars}
        document = self.ENVIRONMENT.get_template(template_name).render(**vars)
        if self.COMPILER:
            return self.COMPILER.compile(template_name, document)
        return document

    @classmethod
    def add_as_resource(cls, api, base_route, argument=None):
        argument = argument or '<string:template_name>'
        api.add_resource(cls, base_route, base_route + argument)


def create_template_endpoint(api, base_route, argument=None, environment=None, global_provider=None, compiler=None,
                             view_class=BaseTemplateView):
    class_dict = {
        'ENVIRONMENT': environment,
        'GLOBAL_PROVIDER': global_provider,
        'COMPILER': compiler
    }
    # Dynamically create a new Class (Not a class Instance of the BaseTemplateView
    class_view = type(''.join(e for e in base_route if e.isalnum()), (view_class,), class_dict)
    class_view.add_as_resource(api, base_route, argument)
    return class_view
    
    
PARAMETERS = {
    'BAAtemplate':{'parameter_1':'Covered Entity','parameter_2':'Job Title','parameter_3':'Full Name'},
    'MOUtemplate':{'parameter_1':'Company Full Name','parameter_2':'Company Short Name','parameter_3':'Time Period','parameter_4':'Job Title','parameter_5':'Full Name'},
    'NDAtemplate':{'parameter_1':'Full Company Name','parameter_2':'Short Company Name','parameter_3':'Name','parameter_4':'Address','parameter_5':'City','parameter_6':'State','parameter_7':'Zip'},    
    'PilotAgreement':{'parameter_2':'Company Full Name','parameter_3':'Street','parameter_4':'City','parameter_5':'State','parameter_6':'Zip','parameter_7':'Time Period','parameter_8':'Company Short Name','parameter_9':'Title','parameter_10':'Full Name'}
    }