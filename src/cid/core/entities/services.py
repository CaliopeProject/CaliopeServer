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

from flask import current_app

from cid.core.login import LoginManager
from cid.utils import fileUtils
from cid.core.models import CaliopeUser

from cid.core.entities import *


class CaliopeEntityService(object):
    """

    This class is the base for all future forms elements.
    """
    @staticmethod
    @public("getTemplate")
    def get_form_template(formId, domain=None, version=None):
        if formId is not None:
            form = CaliopeEntityController(formId=formId)
            return form.get_form_template()
        else:
            raise JSONRPCInvalidParamsError()

    @staticmethod
    @public("getData")
    def get_form_data(formId=None, uuid=None):
        if formId is None or uuid is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = CaliopeEntityController(formId=formId)
            return form.get_form_with_data(uuid)

    @staticmethod
    @public("getDataList")
    def get_form_data_list(formId=None, filters=None):
        if formId is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = CaliopeEntityController(formId=formId)
            return form.get_from_with_data_list(filters)

    @staticmethod
    @public("editFromForm")
    #: TODO: test
    def edit_form(formId=None, formUUID=None, data=None):
        if formId is None or formUUID is None or data is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = CaliopeEntityController(formId=formId)
            return form.update_form_data(data['uuid'], data)

    @staticmethod
    @public("createFromForm")
    def create_form(formId, data, formUUID):
        if formId is None or data is None or formUUID is None:
            raise JSONRPCInvalidRequestError()
        else:
            form = CaliopeEntityController(formId=formId)
            return form.create_form(data,formUUID)


class CaliopeEntityController(object):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_model():
        raise NotImplementedError

    def set_data(self,**data):
        raise NotImplementedError

    def get_data(self,**data):
        raise NotImplementedError
