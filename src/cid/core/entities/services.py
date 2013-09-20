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


class CaliopeEntityService(object):
    """

    This class is the base for all future forms elements.
    """

    service_requested_uuid = set()

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    @public("getAll")
    def get_all(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("getModel")
    def get_model(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("getData")
    def get_data(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("getModelAndData")
    def get_model_and_data(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("edit")
    def edit(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @public("create")
    def create(*args, **kwargs):
        raise NotImplementedError


class CaliopeEntityController(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get_model():
        raise NotImplementedError

    def set_data(self, **data):
        raise NotImplementedError

    def get_data(self, **data):
        raise NotImplementedError

    def _check_template(self):
        raise NotImplementedError

    def _get_form(self):
        raise NotImplementedError

    def _get_actions(self):
        raise NotImplementedError

    def _get_layout(self):
        raise NotImplementedError




