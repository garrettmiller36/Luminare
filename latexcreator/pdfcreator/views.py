"""
All your views aka. your template endpoints go here.
There are two ways to create a view.
1. Create a new Subclass inheriting from one of the flask_template_master views
2. Use the view-factory function flask_template_master.views.create_template_endpoint

Each view requires an 1 (and 2 optional) things:
1. An environment: The environment provides the templates and handles all options of how templates are rendered
2. (optional) An global provider: A global provider provides variables that are accessible in all templates of the endpoint
3. (optional) An compiler: The compiler gets the rendered template and can handle a postprocessing step and controls the
    data that is returned. This can e.g. be used to run a Latex compilation.
"""
import jinja2
from flask import Flask
from ..models import LatexCompiler, BaseTemplateView, create_template_endpoint, DictGlobalProvider, LATEX_TEMPLATE_CONFIG
from latexcreator import Api
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
import pandas as pd
bp = Blueprint('latexcreator', __name__,template_folder='templates')
import datetime
api = Api()  # create an instance of an flask-restfull API. Always required!


class TestView(BaseTemplateView):
    """This is an example of a view created as a subclass.

    This is a simple view using a Dict loader to provide all template strings inline.
    It does not use a compile step and simply returns the rendered template string on POST.

    It passes one value as a global variable. This can be seen in template b.
    The global variable will be overwritten, if a variable with the same name is passed by the POST request
    """

    # The environment needs to be a jinja environment with a loader
    ENVIRONMENT = jinja2.Environment(loader=jinja2.DictLoader({'a': '{{ test }}', 'b': '{{ test }} {{ global }}'}))
    GLOBAL_PROVIDER = DictGlobalProvider({'global': 'This is a global value'})
class Test2(BaseTemplateView):
    ENVIRONMENT = jinja2.Environment(loader=jinja2.DictLoader({'c':'{{ foo }}', 'd': ' {{ bar }} {{ poo }}'}))
    GLOBAL_PROVIDER = DictGlobalProvider({'poo':'The quick brown fox'})

# This registers '/class_test/' for the overview and '/class_test/<template_name> for the individual templates
TestView.add_as_resource(api, '/class_test/')
Test2.add_as_resource(api,'/wafer/')

# This is an example on how to use the factory function

# Setting up the jinja2 enviroemnt using a file loader with LaTex config
environment = jinja2.Environment(loader=jinja2.FileSystemLoader('latexcreator/pdfcreator/templates'), **LATEX_TEMPLATE_CONFIG)
compiler = LatexCompiler()
create_template_endpoint(api, '/factory_test/', environment=environment, compiler=compiler)


environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),**LATEX_TEMPLATE_CONFIG)
compiler = LatexCompiler()
create_template_endpoint(api,'/footest/',environment=environment,compiler=compiler)

