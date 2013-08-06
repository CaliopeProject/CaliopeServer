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
from simplekv.memory.redisstore import RedisStore
from os import path
from pyinotify import (WatchManager, Notifier, ProcessEvent, IN_CREATE, IN_MODIFY, IN_DELETE)
from jsOptimizer import *

class StaticsChangesProcessor(ProcessEvent):
    def process_IN_CREATE(self, event):
        pass
        #print "Create: %s" %  path.join(event.path, event.name)
        #jso.js_put_file_cache(path.join(event.path, event.name),store)

    def process_IN_MODIFY(self, event):
        #print "Modify: %s" %  path.join(event.path, event.name)
        jso.js_put_file_cache(path.join(event.path, event.name),store)

    def process_IN_DELETE(self, event):
        pass

def main(argv):
    store = RedisStore(redis.StrictRedis())
    jso = jsOptimizer()
    jso.watch(argv[1],store,force=True)
    try:
        wm = WatchManager()

        notifier = Notifier(wm, StaticsChangesProcessor())
        wm.add_watch(argv[1], IN_CREATE|IN_MODIFY|IN_DELETE, rec=True)
        notifier.loop()
    finally:
        pass

if __name__ == '__main__':
    #: Start the application
    main(sys.argv)
