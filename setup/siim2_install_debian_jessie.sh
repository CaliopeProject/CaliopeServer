#!/bin/bash

BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')

set -e
sudo apt-get install -y git aptitude
sudo aptitude -y update
sudo apt-get install -y git aptitude redis-server software-properties-common python-software-properties make python-dev python-pip libevent-dev virtualenvwrapper python-virtualenv redis-server libjpeg-dev zlib1g-dev libpng-dev tesseract-ocr libtesseract3 tesseract-ocr-eng tesseract-ocr-spa  python-software-properties python g++ nodejs npm


sudo bash <<EOF
 wget -O - http://debian.neo4j.org/neotechnology.gpg.key| apt-key add -
 echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
 aptitude -y update
 aptitude -y install neo4j-enterprise
EOF

sudo ln -s /usr/bin/nodejs /usr/bin/node

cd ${BASE}

git clone git@proyectos.correlibre.org:caliope/caliope_webui_beowulf.git

cd caliope_webui_beowulf
make

source /etc/bash_completion.d/virtualenvwrapper

if [ -z $(workon|grep caliope) ]
then
  mkvirtualenv caliope
else
  workon caliope
fi

git clone git@proyectos.correlibre.org:caliope/caliope_server_el_cid.git

cd ${BASE}/caliope_server_el_cid

PIL_LIBS="libjpeg.so libz.so libpng.so"

for l in $PIL_LIBS;
do
  if [ -a /usr/lib/${l} ];
  then
    echo $l checked
  else 
    f=$(find  /usr/lib/*gnu/ -name $l)
    echo $f linked
    sudo ln -s $f /usr/lib/${l}
  fi
done

pip install -r requirements.txt

nosetests

./start_server.sh
