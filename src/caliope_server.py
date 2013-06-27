#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
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
'''
#system, and standard library
import os
import getopt
import sys
import json

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


#: Gevent to patch all TCP/IP connections
monkey.patch_all()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(server_notifications, url_prefix='/event_from_server')
app.register_blueprint(file_uploader, url_prefix='/upload')


@app.route('/')
def index():
        return render_template('index.html')


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['STATIC_PATH'], filename)


def main(argv):
    configfile = "conf/caliope_server.json"
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
            configfile = arg
    try:
        config = json.loads(open(configfile).read())
    except IOError:
        print "Error: can\'t find config file or read data"
    else:
        if 'port' in config:
            port = int(config['port'])
        else:
            port = 8000

        if 'static' in config:
            app.config['STATIC_PATH'] = config['static']
        else:
            app.config['STATIC_PATH'] = "."
        print "=============================="
        print "listening at port : " + str(port)
        print "static base directory : " + app.config['STATIC_PATH']
        print "=============================="

        app.jinja_loader = FileSystemLoader(os.path.join(".",
                                            app.config['STATIC_PATH']))
        http_server = WSGIServer(('', port), app, handler_class=WebSocketHandler)
        http_server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
