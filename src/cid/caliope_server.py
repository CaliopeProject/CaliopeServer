#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Cid Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

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
from logging import getLogger

import redis


#gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey

#flask
from flask import (Flask )
from flask.helpers import safe_join

#simplekv
from simplekv.memory.redisstore import RedisStore

#Apps import
from cid.core import module_manager
from cid.utils.fileUtils import loadJSONFromFile, send_from_memory, Gzip


#: Gevent to patch all TCP/IP connections
monkey.patch_all()
app = Flask(__name__)


@app.route('/')
def index():
    return send_from_memory(safe_join(app.config['STATIC_PATH'], 'index.html'))


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_memory(safe_join(app.config['STATIC_PATH'], filename))


def main(argv):
    init_flask_app()
    server_config_file, logger_config_file = _parseCommandArguments(argv)
    configure_server_and_app(server_config_file)
    configure_logger(logger_config_file)
    register_modules()
    run_server()


def init_flask_app():
    app.secret_key = os.urandom(24)
    #: Disable internal debugger
    app.use_debbuger = False
    app.use_reloader = False
    #: load gzip compressor
    gzip = Gzip(app)


def _parseCommandArguments(argv):
    server_config_file = "conf/caliope_server.json"
    logger_config_file = "conf/logger.json"
    try:
        opts, args = getopt.getopt(argv, "hc:l:", ["help", "config=", "log="])
    except getopt.GetoptError:
        print 'caliope_server.py -c <server_configfile> - l <logger_configfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'caliope_server.py -c <server_configfile> - l <logger_configfile>'
            sys.exit()
        elif opt in ("-c", "--config"):
            server_config_file = arg
        elif opt in ("-l", "--log"):
            logger_config_file = arg
    return server_config_file, logger_config_file


def configure_server_and_app(server_config_file):
    config = loadJSONFromFile(server_config_file, app.root_path)
    #TODO: Validate 'server' in config and load default if not present
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
        #: Load app config
    if 'app' in config:
        if 'modules' in config['app']:
            app.config['modules'] = config['app']['modules']
        else:
            app.config['modules'] = {'dispatcher': {'module_name': 'cid.core.dispatcher',
                                                    'module_route': '/api'}}
    if 'storage' in config:
        app.config['storage'] = config['storage']
    else:
        #: TODO: load default storage if not found in config
        pass
    if 'debug' in config['server']:
        app.debug = True if config['server']['debug'] == 'True' else False
    else:
        app.debug = False
        #: TODO: Add a new configuration for session_storage, default volatile dict
    if 'session_storage' in config:
        pass
    else:
        app.config['session_storage'] = {}


def configure_logger(server_config_file):
    config = loadJSONFromFile(server_config_file, app.root_path)
    from logging.config import dictConfig

    dictConfig(config)


def register_modules():
    """
    Register modules listed in the configuration of the app.

    """
    module_manager.register_modules(app)


def run_server():
    if not app.debug:
        Flask.logger = getLogger("production")
    else:
        Flask.logger = getLogger("develop")
    app.logger.info("Starting server on: " + app.config['address'] + ":" + str(app.config['port']))
    app.logger.info("Static Base Directory: " + app.config['STATIC_PATH'])
    app.logger.info("Forms Template Directory : " + app.config['FORM_TEMPLATES'])
    app.storekv = RedisStore(redis.StrictRedis())
    http_server = WSGIServer((app.config['address'], app.config['port']), app,
                             handler_class=WebSocketHandler)  # @IgnorePep8
    http_server.serve_forever()


if __name__ == '__main__':
    #: Start the application
    main(sys.argv[1:])
