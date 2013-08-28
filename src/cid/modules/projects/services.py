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
from models import Project


class ProjectServices(object):

    @staticmethod
    @public
    def getAll():
        return None


    @staticmethod
    @public(name='getData')
    def get_data(uuid):
        data = {}
        data['uuid'] = uuid
        project_controller = ProjectController(**data)
        return project_controller.get_data()


    @staticmethod
    @public(name='getModel')
    def get_model():
        print 'getModel'
        rv = FormManager.get_form_template('projectmtv')
        rv['data'] = ProjectController().get_data()
        return rv

    @staticmethod
    @public(name='getModelAndData')
    def get_model_and_data(uuid):
        data = {}
        data['uuid'] = uuid
        rv = FormManager.get_form_template('projectmtv')
        project_controller = ProjectController(**data)
        rv['data'] = project_controller.get_data()
        return rv


    @staticmethod
    @public
    def create(formId=None, data=None, formUUID=None):
        if 'uuid' in data:
            task = ProjectController(uuid=data['uuid'])
        else:
            task = ProjectController()
        task.set_data(**data)
        rv = task.get_data()
        return rv

    @staticmethod
    @public
    def edit(data=None):
        project_controller = ProjectController(**data)
        project_controller.set_data(**data)
        rv = project_controller.get_data()
        return rv


class ProjectController(CaliopeEntityController):

    def __init__(self, *args, **kwargs):
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.project = Project().__class__.inflate(node.__node__)
            except DoesNotExist as e:
                self.project = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.project = None
            self.set_data(**{})

    @staticmethod
    def get_model():
        pass

    def set_data(self, **data):

        if self.project is None:
            self.project = Project()
            self.project.save()
            self.project.init_entity_data(**data)
            ownerUserNode = CaliopeUser.index.get(username=LoginManager().get_user())            
        else:
            self.project.set_entity_data(**data)
                    

    def get_data(self):
        return self.project.get_entity_data()

