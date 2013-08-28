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


#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError
from tinyrpc.dispatch import public

#Flask
from cid.core.login import LoginManager
#temporal
from cid.core.forms import FormManager
from models import PredialCard


class PredialCardsServices(object):

    @staticmethod
    @public(name='getModel')
    def get_model():
        rv = FormManager.get_form_template('predialCard')
        return rv



class PredialCardsController(CaliopeEntityController):

    def __init__(self, *args, **kwargs):
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.predialCard = PredialCard().__class__.inflate(node.__node__)
            except DoesNotExist as e:
                self.predialCard = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.predialCard = None
            self.set_data(**{})

    def get_data(self):
        return self.predialCard.get_entity_data()

