# -*- encoding: utf-8 -*-
"""
Created on 27/06/2013

@author: Andrés Felipe Calderón andres.calderon@correlibre.org
@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is part of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

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
__author__ = 'afc'

#flask
from flask.globals import current_app

import os
import gevent
from hotqueue import HotQueue
import magic
import PDFProcessor
from prometheia.core.OCR import OCR
from cid.core.documents import DocumentManager
from cid.core.entities import ContentDocument
from urlparse import urlparse

UPLOAD_FOLDER = "./storage"


def queue_processor():
        queue = HotQueue("postprocessing_queue")
        ocr = OCR.Engine()

        for uuid in queue.consume():
            print str(uuid)
            dm = DocumentManager()
            doc = dm.getDocument(uuid)
            print str(doc.url)
            url = urlparse(doc.url)
            filename = os.path.join(UPLOAD_FOLDER, url.path)
            m = magic.Magic()
            print filename + ' ' + str(m.id_filename(filename))

            if 'PDF' in  str(m.id_filename(filename)):
                pdf_text = PDFProcessor.extractContent(str(filename))
                cm = ContentDocument()
                cm.content = unicode(pdf_text, encoding='utf-8')
                cm.save()
                #ocr_text = ocr.interpret(str(filename))
                print pdf_text


def prometheia_processor():
    queue = HotQueue("postprocessing_queue")
    gevent.spawn(queue_processor)