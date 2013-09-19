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

import sys
import StringIO
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

def extractContent(file):
    print "extractContent"

    fp = open(file, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)

    rsrcmgr = PDFResourceManager()
    codec = 'UTF-8'
    laparams = LAParams()
    outfp = StringIO.StringIO()

    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    #if not doc.is_extractable:
    #    return None

    for i, page in enumerate(doc.get_pages()):
        print "page=" + str(i)
        if page is not None:
            interpreter.process_page(page)
    print "EOF"
    device.close()
    fp.close()

    return outfp.getvalue()

