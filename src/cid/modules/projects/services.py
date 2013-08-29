# -*- encoding: utf-8 -*-
"""
@authors: Nelson Daniel Ochoa ndaniel8a@gmail.com
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

#CaliopeStorage
from cid.core.entities import CaliopeNode, CaliopeUser, DoesNotExist
from cid.core.entities.services import CaliopeEntityController, CaliopeEntityService

#utils
from cid.utils.fileUtils import loadJSONFromFile
from cid.core.login.services import LoginManager
#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCInvalidRequestError, RPCError
from tinyrpc.dispatch import public

#Flask
from flask import current_app

from models import ProjectEntity, ProjectData


class ProjectServices(CaliopeEntityService):
    def __init__(self, *args, **kwargs):
        super(ProjectServices, self).__init__(*args, **kwargs)

    @staticmethod
    @public(name='getAll')
    def get_all():
        pass

    @staticmethod
    @public(name='getData')
    def get_data(uuid):
        data = {}
        data['uuid'] = uuid
        task_controller = ProjectController(**data)
        return task_controller.get_data()


    @staticmethod
    @public(name='getModel')
    def get_model():
        project_controller = ProjectController()
        rv = project_controller.get_model()
        rv['data'] = project_controller.get_data()
        return rv

    @staticmethod
    @public(name='getModelAndData')
    def get_model_and_data(uuid):
        data = {}
        data['uuid'] = uuid
        project_controller = ProjectController(**data)
        rv = project_controller.get_model()
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
        super(ProjectController, self).__init__(*args, **kwargs)
        if 'uuid' in kwargs:
            try:
                node = CaliopeNode.index.get(uuid=kwargs['uuid'])
                self.project = ProjectEntity().__class__.inflate(node.__node__)
            except DoesNotExist as e:
                self.project = None
            except Exception as e:
                raise e
        else:
            #: TODO check initialization
            self.project = None
            self.set_data(**{})

    def get_model(self):
        if self._check_template():
            rv = dict()
            rv['form'] = self._get_form()
            rv['actions'] = self._get_actions()
            rv['layout'] = self._get_layout()
            return rv
        else:
            raise RPCError('Template error')

    def set_data(self, **data):
        if self.project is None:
            self.project = ProjectEntity()
            self.project.save()
            self.project.init_entity_data(**data)
            ownerUserNode = CaliopeUser.index.get(username=LoginManager().get_user())
            self.project.set_owner(ownerUserNode)
        else:
            self.project.set_entity_data(**data)

    def get_data(self):
        if hasattr(self, 'project') and self.project is not None:
            return self.project.get_entity_data()
        else:
            return None

    def set_holders(self, holders, category):
        pass

    def _check_template(self):
        #: TODO: Check if form_name is valid and form_path is a file
        #: TODO: Cache this files
        try:
            self.template = loadJSONFromFile('modules/projects/templates/projectmtv.json', current_app.root_path)
            return True
        except IOError:
            return False

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

