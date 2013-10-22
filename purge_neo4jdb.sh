ENV=caliope
BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')
PYTHON=${HOME}/.virtualenvs/${ENV}/bin/python

export PYTHONPATH=${BASE}/caliope_server_el_cid/src

#sudo /etc/init.d/neo4j-service stop
#sudo rm -fr /var/lib/neo4j/data/*
#sudo /etc/init.d/neo4j-service start
${PYTHON} ${PYTHONPATH}/cid/utils/cleanDb.py
${HOME}/.virtualenvs/${ENV}/bin/nosetests
${PYTHON} ${PYTHONPATH}/cid/utils/DefaultDatabase.py
