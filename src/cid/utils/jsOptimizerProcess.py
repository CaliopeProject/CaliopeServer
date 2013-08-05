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
from jsOptimizer import *
#import gevent
import threading

from flask import current_app, g

def js_watcher(jso,base_path):
    ct = threading.currentThread()
    while True:
        print('watching')
        #gevent.sleep(1)
        jso.watch(base_path)
        
def jsOptimizerProcess(cache_path, base_path):
    print "javascript_cache_path = "+cache_path
    print "javascript_base_path = "+base_path
    jso = jsOptimizer(cache_path)
    #g.js_optimizer = jso
    tr = threading.Thread(target=js_watcher, args=(jso,base_path ))  
    tr.start() 
    print "jsOptimizerProcess running"

    #gevent.spawn(js_watcher(jso,base_path))


            
