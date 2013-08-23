#!/bin/sh
BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')
export PYTHONPATH=${BASE}/caliope_server_el_cid/src


# if [ -z $(ps  ax|grep jsOptimizerProcess|grep -v grep|awk '{print $1}') ]; 
# then
# 	python src/cid/utils/jsOptimizerProcess.py  \
# 				-c conf/caliope_server.json  &
# fi

python src/cid/caliope_server.py \
			-c conf/caliope_server.json \
                        -l conf/logger.json
