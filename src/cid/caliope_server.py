#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#system, and standard library
import os
import getopt
import sys
import logging
from logging import getLogger

#gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey


#flask
from flask import Flask, render_template, send_from_directory
from jinja2 import FileSystemLoader

#Blueprints
from api.views import api
from server_notifications.views import server_notifications
from file_uploader.views import file_uploader

#Apps import
from utils.fileUtils import loadJSONFromFile

#: Gevent to patch all TCP/IP connections
monkey.patch_all()
app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(app.config['STATIC_PATH'], 'index.html')
    #return render_template('index.html')


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['STATIC_PATH'], filename)


def main(argv):
    _init_flask_app()
    config_file = _parseCommandArguments(argv)
    _configureServer(config_file)
    _configure_logger("conf/logger.json")
    _run_server()


def _init_flask_app():
    app.secret_key = os.urandom(24)
    #: Disable internal debugger
    app.use_debbuger = False
    app.use_reloader = False
    #: Register Blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(server_notifications, url_prefix='/event_from_server')
    app.register_blueprint(file_uploader, url_prefix='/upload')


def _parseCommandArguments(argv):
    config_file = "conf/caliope_server.json"
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        print 'caliope_server.py -c <configfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'caliope_server.py -c <configfile>'
            sys.exit()
        elif opt in ("-c", "--config"):
            config_file = arg
    return config_file


def _configureServer(config_file):
    config = loadJSONFromFile(config_file)
    if 'address' in config['server']:
        app.config['address'] = config['server']['address']
    else:
        app.config['address'] = 'localhost'
    if 'port' in config['server']:
        app.config['port'] = int(config['server']['port'])
    else:
        app.config['port'] = 8000
    if 'static' in config['server']:
        app.config['STATIC_PATH'] = config['server']['static']
    else:
        app.config['STATIC_PATH'] = "."
    if 'formTemplates' in config['server']:
        app.config['FORM_TEMPLATES'] = config['server']['formTemplates']
    else:
        app.config['FORM_TEMPLATES'] = app.config['STATIC_PATH']
    if 'debug' in config['server']:
        app.debug = True if config['server']['debug'] == 'True' else False
    else:
        app.debug = False


def _configure_logger(config_file):
    config = loadJSONFromFile(config_file)
    from logging.config import dictConfig
    dictConfig(config)


def _run_server():
    if not app.debug:
        logger = logging.getLogger("production")
    else:
        logger = logging.getLogger("develop")
    logger.info("Starting server on: " + app.config['address']+ ":" + str(app.config['port']))
    logger.info("Static Base Directory: " + app.config['STATIC_PATH'])
    logger.info("Forms Template Directory : " + app.config['FORM_TEMPLATES'])
    http_server = WSGIServer((app.config['address'], app.config['port']), app, handler_class=WebSocketHandler)  # @IgnorePep8
    http_server.serve_forever()


if __name__ == '__main__':
    #: Start the application
    main(sys.argv[1:])
