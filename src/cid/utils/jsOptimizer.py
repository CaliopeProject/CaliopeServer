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
import os
import time
import sys
import hashlib
import re
import uglipyjs
import gevent

class jsOptimizer(object):
    def __init__(self,js_cache_store_path):
        self.js_cache_store_path = js_cache_store_path
        self.jstype = re.compile(".*js$")


    def file_was_modified(self,prefix,path):
        mts = int(os.path.getmtime(path))

        try:
            with open(self.js_cache_store_path + '/' + prefix + ".ts",'r') as fts: 
                ts = fts.read()
                fts.close()       
                if len(ts) and mts == int(ts):
                    return False
        except IOError:
            pass
        
        with open(self.js_cache_store_path + '/' + prefix + ".ts",'w') as fts: 
            fts.write(repr(int(mts)))
            fts.close()

        return True


    def watch_file(self,path):
        if self.jstype.match(path) is not None:
            prefix = hashlib.sha1(path).hexdigest()
            if self.file_was_modified(prefix,path): 
                str = open(path,'r').read()
                js = unicode(str, errors='ignore')
                
                if len(js):
                    try:
                        ujs = uglipyjs.compile(js)
                    except:
                        pass
                    else:  
                        #print path
                        fjs = open(self.js_cache_store_path + '/' + prefix + ".js",'w')
                        fjs.write(ujs)
                        fjs.close()  


    def watch(self,rootdir):
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                path = root+'/'+file
                self.watch_file(path)
            
            for folder in subFolders:
                for file in files:
                    path = root+'/'+file
                    self.watch_file(path)

                   
