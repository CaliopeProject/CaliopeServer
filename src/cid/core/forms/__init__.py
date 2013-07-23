# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM2 Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

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

from tinyrpc.dispatch import public
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidParamsError

from flask import current_app

from ..login import LoginManager
from ...utils import fileUtils
from ...model import SIIMForm


class FormManager(object):
    """

    This class is the base for all future forms elements.
    """
    @staticmethod
    @public("getFormTemplate")
    def get_form_template(formId, domain=None, version=None):
        if formId is not None:
            form = Form(formId=formId)
            return form.get_form_template()
        else:
            raise JSONRPCInvalidParamsError()


class Form(object):

    def __init__(self, **kwargs):
        self.form_name = kwargs['formId'] if 'formId' in kwargs else None
        self.form_path = kwargs['form_path'] if 'form path' in kwargs else current_app.config['FORM_TEMPLATES']
        self.form_cls = kwargs['form_cls'] if 'form_cls' in kwargs else SIIMForm
        self.app = kwargs['current_app'] if 'current_app' in kwargs else None
        self.form_json = None

    def _get_form_acl(self):
        #: TODO: Check form node and check acl for node
        pass

    def _check_valid_form(self):
        #: TODO: Check if form_name is valid and form_path is a file
        #: TODO: Cache this files
        self.form_json = fileUtils.loadJSONFromFile(self.form_path + "/" + self.form_name + ".json",
                                                    current_app.root_path)
        return True

    def _get_form(self):
        return self.form_json

    def _get_actions(self):
        #: TODO: Implement depending on user
        self.actions = ["authenticate"]
        return self.actions

    @LoginManager.login_required
    def get_form_template(self):
        if self._check_access():
            if self._check_valid_form():
                rv = dict()
                rv['form'] = self._get_form()
                rv['actions'] = self._get_actions()
                return rv





