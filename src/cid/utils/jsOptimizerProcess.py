#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Calderón andres.calderon@correlibre.org

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Infometrika

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
import redis
import sys
import getopt
from simplekv.memory.redisstore import RedisStore
from os import path
from pyinotify import (WatchManager, Notifier, ProcessEvent, IN_ACCESS,IN_ATTRIB,IN_CREATE, IN_MODIFY, IN_DELETE)
from cid.utils.jsOptimizer import *
from cid.utils.fileUtils import loadJSONFromFile


class StaticsChangesProcessor(ProcessEvent):
    def __init__(self, jso,store):
        self.jso = jso
        self.store = store

    def process_IN_CREATE(self, event):
        #print "Create: %s" %  path.join(event.path, event.name)
        self.jso.js_put_file_cache(path.join(event.path, event.name),self.store)


    def process_IN_MODIFY(self, event):
        #print "Modify: %s" %  path.join(event.path, event.name)
        self.jso.js_put_file_cache(path.join(event.path, event.name),self.store)

    def process_IN_DELETE(self, event):
        pass

    def process_IN_ATTRIB(self, event):
        self.jso.js_put_file_cache(path.join(event.path, event.name),self.store)
        #print "in attrib: %s" %  path.join(event.path, event.name)


    def process_IN_ACCESS(self, event):
        pass
        #print "in access: %s" %  path.join(event.path, event.name)




def _parseCommandArguments(argv):
    print "_parseCommandArguments" + str(argv)
    server_config_file = "conf/caliope_server.json"
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config=",])
    except getopt.GetoptError:
        print 'jsOptimizerProcess.py -c <server_configfile>' 
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'jsOptimizerProcess.py -c <server_configfile>' 
            sys.exit()
        elif opt in ("-c", "--config"):
            server_config_file = arg
    return server_config_file

def configure_server_and_app(server_config_file):
    config = loadJSONFromFile(server_config_file, '')
    print config['server']
    if 'static' in config['server']:
        static_path = config['server']['static']
    else:
        static_path = "."
    return static_path
    
def main(argv):
    server_config_file = _parseCommandArguments(argv)
    static_path = configure_server_and_app(server_config_file)
    print "server_config_file = "+ server_config_file
    print "static_path = "+ static_path
    store = RedisStore(redis.StrictRedis())
    jso = jsOptimizer()
    jso.watch(static_path,store,force=True)
    try:
        wm = WatchManager()
        notifier = Notifier(wm, StaticsChangesProcessor(jso,store))
        wm.add_watch(static_path, IN_ATTRIB|IN_ACCESS|IN_CREATE|IN_MODIFY|IN_DELETE, rec=True)
        notifier.loop()
    finally:
        pass

if __name__ == '__main__':
    #: Start the application
    main(sys.argv[1:])

