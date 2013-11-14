#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
SIIM Server is the web server of SIIM's Framework
Copyright (C) 2013 Infometrika Ltda

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

from cid.utils.fileUtils import loadJSONFromFile

import cid.core.access_control.access_control
import unittest

class TestAccessControl(unittest.TestCase):

    def setUp(self):
        acl_conf = loadJSONFromFile('../../conf/permissions_for_test.json')
        self.acl = cid.core.access_control.access_control.AccessControl(acl_conf)

    def test_Users(self):
        users = ['revisor_1', 'revisor_2', 'revisor_3', 'recepcionista_1',
                 'recepcionista_2', 'superuser', 'secretaria_1', 'reportero_1',
                 'reportero_2', 'gerente_1']

        for user in self.acl.get_user_list():
            self.assertIn(user, users)

    def test_Groups(self):

        groups = ['everybody', 'secretarias', 'revisores', 'reportes',
                  'superusers', 'gerentes', 'recepcionistas']

        for group in self.acl.get_group_shorthands():
            self.assertIn(group, groups)

        user_and_groups = \
            {'everybody' : ['recepcionista_1', 'recepcionista_2', 'revisor_1',
                            'revisor_2', 'revisor_3', 'gerente_1', 'reportero_1',
                            'reportero_2'],
             'secretarias' :  ['secretaria_1'],
             'revisores' : ['revisor_1', 'revisor_2', 'revisor_3'],
             'reportes' : ['reportero_1', 'reportero_2'],
             'superusers': ['superuser'],
             'gerentes' : ['gerente_1'],
             'recepcionistas' : [u'recepcionista_1', u'recepcionista_2']}

        for group in user_and_groups:
          for user in self.acl.get_users_in_grup(group):
            self.assertIn(user, user_and_groups[group])

    def test_Actions(self):

        actions = ['read', 'write', 'assign', 'all_actions']

        for action_name in self.acl.get_action_names():
            self.assertIn(action_name, actions)
             
        actions_resolved = {
            'read' : ['read'],
            'write' : ['write'],
            'assign' : ['assign'],
            'all_actions' : ['read', 'write', 'assign']
          }

        for shorthand in actions_resolved:
            for action in self.acl.get_action_instance(shorthand):
                self.assertIn(action, actions_resolved[action]) 

    def test_Things(self):

        things = ['report', 'everything', 'document', 'form', 'task']

        for thing in self.acl.get_thing_names():
          self.assertIn(thing, things)

        things_resolved = {
            'report' : ['report'],
            'everything' : ['form', 'document', 'task', 'report'],
            'document' : ['document'],
            'form' : ['form'],
            'task' : [u'task']
        }

        for shorthand in self.acl.get_thing_names():
            for thing in self.acl.get_thing_instance(shorthand):
                self.assertIn(thing, things_resolved[thing])

    def test_GetUserPermissions(self):
        permissions_of_user = \
             set([('read', 'form', 'everybody'), ('read', 'form', 'gerentes'),
              ('read', 'document', 'everybody'), ('read', 'document', 'gerentes'),
              ('read', 'task', 'everybody'), ('read', 'task', 'gerentes'),
              ('read', 'report', 'everybody'), ('read', 'report', 'gerentes'),
              ('write', 'form', 'everybody'), ('write', 'form', 'gerentes'),
              ('write', 'document', 'everybody'), ('write', 'document', 'gerentes'),
              ('write', 'task', 'everybody'), ('write', 'task', 'gerentes'),
              ('write', 'report', 'everybody'), ('write', 'report', 'gerentes'),
              ('assign', 'form', 'everybody'), ('assign', 'form', 'gerentes'),
              ('assign', 'document', 'everybody'), ('assign', 'document', 'gerentes'),
              ('assign', 'task', 'everybody'), ('assign', 'task', 'gerentes'),
              ('assign', 'report', 'everybody'), ('assign', 'report', 'gerentes'),
              ('assign', 'form', 'reportes'), ('assign', 'document', 'reportes'),
              ('assign', 'task', 'reportes'), ('assign', 'report', 'reportes')])

        for perm in self.acl.get_user_permissions('gerente_1'):
            self.assertIn(perm, permissions_of_user)
            permissions_of_user.remove(perm)

        self.assertEqual(permissions_of_user, set())

if __name__ == '__main__':
    unittest.main()
