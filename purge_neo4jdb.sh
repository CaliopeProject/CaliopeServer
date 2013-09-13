ENV=caliope

sudo /etc/init.d/neo4j-service stop
sudo rm -fr /var/lib/neo4j/data/*
sudo /etc/init.d/neo4j-service start

${HOME}/.virtualenvs/${ENV}/bin/nosetests


