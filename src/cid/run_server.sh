BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')

export PYTHONPATH=${BASE}/caliope_server_el_cid

./caliope_server.py -c conf/caliope_server.json