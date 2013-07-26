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
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidParamsError, JSONRPCInvalidRequestError, JSONRPCInternalError

from neomodel.exception import DoesNotExist

from flask import current_app, g

from cid.core.login import LoginManager
from cid.utils import fileUtils
from cid.model import SIIMForm


class FormManager(object):
    """

    This class is the base for all future forms elements.
    """
    @staticmethod
    @public("getTemplate")
    def get_form_template(formId, domain=None, version=None):
        if formId is not None:
            form = Form(formId=formId)
            return form.get_form_template()
        else:
            raise JSONRPCInvalidParamsError()

    @staticmethod
    @public("getData")
    def get_form_data(formId=None, uuid=None):
        if formId is None or uuid is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = Form(formId=formId)
            return form.get_form_with_data(uuid)

    @staticmethod
    @public("getDataList")
    def get_form_data_list(formId=None, filters=None):
        if formId is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = Form(formId=formId)
            return form.get_from_with_data_list(filters)

    @staticmethod
    @public("editFromForm")
    #: TODO: test
    def edit_form(formId=None, uuid=None, data=None):
        if formId is None or uuid is None or data is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = Form(formId=formId)
            return form.update_form_data(uuid, data)

    @staticmethod
    @public("createFromForm")
    def edit_form(formId=None, data=None, formUUID=None):
        if formId is None or data is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = Form(formId=formId)
            return form.create_form(data)


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

    def _check_access(self):
        #: TODO: Implement
        lm = g.get('lm', None)
        if self.form_name == 'login':
            return True
        elif lm is not None:
            return True
        else:
            return False

    def _check_valid_form(self):
        #: TODO: Check if form_name is valid and form_path is a file
        #: TODO: Cache this files
        try:
            self.form_json = fileUtils.loadJSONFromFile(self.form_path + "/" + self.form_name + ".json",
                                                    current_app.root_path)
            return True
        except IOError:
            return False

    def _get_form(self):
        return self.form_json

    def _get_actions(self):
        #: TODO: Implement depending on user
        self.actions = [
                        {"name": "create", "method":"form.createFromForm"}, 
                        {"name": "delete", "method":"form.delete"}, 
                        {"name": "edit", "method":"form.editFromForm"}
                    ]
        return self.actions

    def get_form_template(self):
        if self._check_access():
            if self._check_valid_form():
                rv = dict()
                rv['form'] = self._get_form()
                rv['actions'] = self._get_actions()
                return rv
            else:
                return JSONRPCInternalError('Invalid Form')
        else:
            raise JSONRPCInvalidRequestError('Forbidden')

    def _get_node_data(self, uuid):
        #: TODO: User dynamic class types             
        self.form_cls = SIIMForm
        try:
            self.node = self.form_cls.index.get(uuid=uuid)
            self.form_data = self.node.get_form_data()
            return self.form_data
        except DoesNotExist as e:
            self.node = None
            self.form_data = None
            raise JSONRPCInvalidRequestError(e)

    def _get_node_data_list(self, filters):
        #: TODO: User dynamic class types
        self.form_cls = SIIMForm
        try:
            self.nodes = self.form_cls.index.search('uuid:*')
            self.form_data_list = [node.get_form_data() for node in self.nodes]
            return self.form_data_list
        except DoesNotExist as e:
            self.node = None
            self.form_data = None
            raise JSONRPCInvalidRequestError(e)


    def get_form_with_data(self, uuid):
        #: TODO: this looks like a decorator is needed
        if self._check_access():            
            rv = self.get_form_template()            
            rv['data'] = self._get_node_data(uuid)
            return rv
        else:
            raise JSONRPCInvalidRequestError('Forbidden')

    def get_from_with_data_list(self, filters=None):
        #: TODO: this looks like a decorator is needed
        if self._check_access():
            rv = self.get_form_template()
            rv['data'] = self._get_node_data_list(filters)
            return rv
        else:
            raise JSONRPCInvalidRequestError('Forbidden')

    def update_form_data(self, uuid, data):
        if self._check_access():
            rv = dict()
            rv['uuid'] = self._update_or_create_node_data(uuid, data)
            return rv
        else:
            raise JSONRPCInvalidRequestError('Forbidden')

    def _update_or_create_node_data(self, data, uuid=None):
        if uuid is not None:
            self._get_node_data(uuid)
            self.node = self.node.set_form_data(data)
        else:
            #: Create new node
            self.node = SIIMForm(**data)
        print "self.form_name = " + self.form_name
        self.node.formid = self.form_name
        self.node.save()
        return self.node.uuid

    def create_form(self, data):
        if self._check_access():
            rv = dict()
            rv['uuid'] = self._update_or_create_node_data(data)
            return rv
        else:
            raise JSONRPCInvalidRequestError('Forbidden')



