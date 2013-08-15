Caliope Server
===============

This is the server for Caliope Framework

Requeriments
==========
  * neo4j database
  * libevent-dev
  * python-dev
  * fortunes

How to?
==========
install and run neo4j
  * sudo -i
  * wget -O - http://debian.neo4j.org/neotechnology.gpg.key| apt-key add -
  * echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list 
  * apt-get update -y
  * apt-get install neo4j-enterprise

run `sudo apt-get install python-dev python-pip libevent-dev redis-server libjpeg-dev zlib1g-dev libpng-dev`
run `pip install -r requirements.txt` to install requirements and start the server with `sh run_server.sh` then browse `http://localhost:9000/` to try out.

