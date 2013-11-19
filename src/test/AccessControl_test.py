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
        users = set(['revisor_1', 'revisor_2', 'revisor_3', 'recepcionista_1',
                     'recepcionista_2', 'superuser', 'secretaria_1', 'reportero_1',
                     'reportero_2', 'gerente_1'])

        for user in self.acl.get_user_list():
            self.assertIn(user, users)
            users.remove(user)

        self.assertEqual(users, set())

    def test_GroupsShorthands(self):

        groups = set(['everybody', 'secretarias', 'revisores', 'reportes',
                      'superusers', 'gerentes', 'recepcionistas'])

        for group in self.acl.get_group_shorthands():
            self.assertIn(group, groups)
            groups.remove(group)

        self.assertEqual(groups, set())

    def test_UsersInGroup(self):

        user_and_groups = \
            {'everybody' : set(['recepcionista_1', 'recepcionista_2', 'revisor_1',
                            'revisor_2', 'revisor_3', 'gerente_1', 'reportero_1',
                            'reportero_2']),
             'secretarias' :  set(['secretaria_1']),
             'revisores' : set(['revisor_1', 'revisor_2', 'revisor_3']),
             'reportes' : set(['reportero_1', 'reportero_2']),
             'superusers': set(['superuser']),
             'gerentes' : set(['gerente_1']),
             'recepcionistas' : set(['recepcionista_1', 'recepcionista_2'])}

        for group in user_and_groups:
          for user in self.acl.get_users_in_grup(group):
            self.assertIn(user, user_and_groups[group])
            user_and_groups[group].remove(user)

        # For each group, check that all the users were removed.
        for key, value in user_and_groups.items():
            self.assertEqual(user_and_groups[group], set())

    def test_Actions(self):

        actions = set(['read', 'write', 'assign', 'all_actions'])

        for action_name in self.acl.get_action_names():
            self.assertIn(action_name, actions)
            actions.remove(action_name)

        self.assertEqual(actions, set())
             
        actions_resolved = {
            'read' : set(['read']),
            'write' : set(['write']),
            'assign' : set(['assign']),
            'all_actions' : set(['read', 'write', 'assign'])
          }

        for shorthand in actions_resolved:
            for action in self.acl.get_action_instance(shorthand):
                self.assertIn(action, actions_resolved[action]) 

    def test_Things(self):

        things = set(['report', 'everything', 'document', 'form', 'task'])

        for thing in self.acl.get_thing_names():
          self.assertIn(thing, things)
          things.remove(thing)

        self.assertEqual(things, set())

        things_resolved = {
            'report' : set(['report']),
            'everything' : set(['form', 'document', 'task', 'report']),
            'document' : set(['document']),
            'form' : set(['form']),
            'task' : set(['task'])
        }

        for shorthand in self.acl.get_thing_names():
            for thing in self.acl.get_thing_instance(shorthand):
                self.assertIn(thing, things_resolved[thing])

    def test_GetGroupsForUser(self):
        groups_of_user = set(['everybody', 'gerentes'])
        for group in self.acl.get_groups_for_user('gerente_1'):
            self.assertIn(group, groups_of_user)
            groups_of_user.remove(group)
        self.assertEqual(groups_of_user, set())

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
