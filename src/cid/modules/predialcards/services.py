# -*- encoding: utf-8 -*-
"""
@authors: Nelson Daniel Ochoa ndaniel8a@gmail.com

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
from neomodel.exception import DoesNotExist

#CaliopeStorage
from cid.core.models import CaliopeUser, CaliopeNode
from cid.core.entities.services import CaliopeEntityController, CaliopeEntityService

#utils
from cid.utils.fileUtils import loadJSONFromFile
from cid.core.login.services import LoginManager
#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, RPCError
from tinyrpc.dispatch import public

#Flask
from flask import current_app

from models import PredialCardEntity


class PredialCardsServices(CaliopeEntityService):
    def __init__(self, *args, **kwargs):
        super(PredialCardsServices, self).__init__(*args, **kwargs)

    @staticmethod
    @public(name='getModel')
    def get_model():
        rv = PredialCardsController().get_model()
        return rv


class PredialCardsController(CaliopeEntityController):
    def __init__(self, *args, **kwargs):
        super(PredialCardsController, self).__init__(*args, **kwargs)
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.predial_card = PredialCardEntity().__class__.inflate(node.__node__)
            except DoesNotExist as e:
                self.predial_card = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.predial_card = None
            self.set_data(**{})

    def set_data(self, **data):
        if self.predial_card is None:
            self.predial_card = PredialCardEntity()
            self.predial_card.save()
            self.predial_card.init_entity_data(**data)
            ownerUserNode = CaliopeUser.index.get(username=LoginManager().get_user())
            self.predial_card.set_owner(ownerUserNode)
        else:
            self.predial_card.set_entity_data(**data)

    def get_data(self):
        return self.predial_card.get_entity_data()

    def _check_template(self):
        #: TODO: Check if form_name is valid and form_path is a file
        #: TODO: Cache this files
        try:
            self.template = loadJSONFromFile('modules/predialcards/templates/predialCard.json', current_app.root_path)
            return True
        except IOError:
            return False

    def get_model(self):
        if self._check_template():
            rv = dict()
            rv['form'] = self._get_form()
            rv['actions'] = self._get_actions()
            rv['layout'] = self._get_layout()
            return rv
        else:
            raise RPCError('Template error')

    def _get_form(self):
        return self.template

    def _get_actions(self):
        #: TODO: Implement depending on user
        if 'actions' in self.template:
            self.actions = self.template['actions']
            self.template.pop('actions')
        return self.actions

    def _get_layout(self):
        #: TODO: Implement depending on user
        if 'layout' in self.template:
            self.layout = self.template['layout']
            self.template.pop('layout')
        else:
            self.layout = []
        return self.layout