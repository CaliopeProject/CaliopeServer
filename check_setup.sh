#!/bin/bash

ENV=caliope
PYTHON=${HOME}/.virtualenvs/${ENV}/bin/python


BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')
export PYTHONPATH=${BASE}/caliope_server_el_cid/src


sudo apt-get install install python-dev python-pip libevent-dev redis-server imagemagick libjpeg-dev zlib1g-dev libpng-dev tesseract-ocr libtesseract3 tesseract-ocr-eng tesseract-ocr-spa

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

${HOME}/.virtualenvs/${ENV}/bin/pip install --upgrade -r requirements.txt
