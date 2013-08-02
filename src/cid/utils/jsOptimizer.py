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
            with open(self.js_cache_store_path + prefix + ".ts",'r') as fts: 
                ts = fts.read()
                fts.close()       
                if len(ts) and mts == int(ts):
                    return False
        except IOError:
            pass
        
        with open(self.js_cache_store_path + prefix + ".ts",'w') as fts: 
            fts.write(repr(int(mts)))
            fts.close()

        return True


    def watch_file(self,path):
        if self.jstype.match(path) is not None:
            prefix = hashlib.sha1(path).hexdigest()
            if self.file_was_modified(prefix,path): 
                print path
                str = open(path,'r').read()
                js = unicode(str, errors='ignore')
                
                if len(js):
                    try:
                        ujs = uglipyjs.compile(js)
                    except:
                        pass
                    else:  
                        print path
                        fjs = open(self.js_cache_store_path + prefix + ".js",'w')
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

                   
rootdir = sys.argv[1]

jso = jsOptimizer('js-cache/')
jso.watch(rootdir)

def foo():
    while True:
        #print('watching')
        gevent.sleep(10)
        jso.watch(rootdir)
            
gevent.spawn(foo)
