BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')

cd src/cid
./caliope_server.py -c conf/caliope_server.json
