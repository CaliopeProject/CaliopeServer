#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Nelson Castillo <nelsoneci@gmail.com>
          Sebastián Ortiz V. neoecos@gmail.com


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
import hashlib

from cid.core.entities import (DoesNotExist,
                               UniqueProperty,
                               CaliopeUser,
                               CaliopeGroup)


class DefaultDatabase(object):
    """
    :py:class: DefaultDatabase creates the default database for the system.

    """

    def test_defaultUserGroupOne(self):
        """
        Creates user and g-000 and membership from user to group
        :return:
        """
        try:
            u1 = CaliopeUser()
            u1.username = 'user'
            u1.password = hashlib.sha256(u'123').hexdigest()
            u1.domainname = 'correlibre.org'
            u1.first_name = "User"
            u1.last_name = "Test"
            u1.avatar = "common-img/avatar.png"
            u1.save()
            g1 = CaliopeGroup()
            g1.name = 'Group'
            g1.code = 'g-000'
            g1.save()
            u1.member_of.connect(g1)
            g1.members.connect(u1)
            assert u1.member_of.is_connected(g1)
            assert g1.members.is_connected(u1)
        except UniqueProperty:
            try:
                u1 = CaliopeUser.index.get(username='user')
                g1 = CaliopeGroup.index.get(code='g-000')
                assert u1 is not None and g1 is not None
                assert u1.member_of.is_connected(g1)
                assert g1.members.is_connected(u1)
            except DoesNotExist:
                assert False

    def test_defaultUserGroupMany(self):
        """
        Creates user[1-5] and g-00[1-5] and the correspondent memberships.
        :return:
        """
        try:
            for i in xrange(1, 6):
                u1 = CaliopeUser()
                u1.username = 'user' + str(i)
                u1.password = hashlib.sha256(u'123').hexdigest()
                u1.domainname = 'correlibre.org'
                u1.first_name = "User" + str(i)
                u1.last_name = "Test"
                u1.avatar = "common-img/avatar" + str(i) + ".png"
                u1.save()
                g1 = CaliopeGroup()
                g1.name = 'Group' + str(i)
                g1.code = 'g-00' + str(i)
                g1.save()
                u1.member_of.connect(g1)
                g1.members.connect(u1)
                assert u1.member_of.is_connected(g1)
                assert g1.members.is_connected(u1)
        except UniqueProperty:
            try:
                for i in xrange(1, 6):
                    u1 = CaliopeUser.index.get(username='user' + str(i))
                    g1 = CaliopeGroup.index.get(code='g-00' + str(i))
                    assert u1 is not None and g1 is not None
                    assert u1.member_of.is_connected(g1)
                    assert g1.members.is_connected(u1)
            except DoesNotExist:
                assert False

if __name__ == "__main__":
    print "Creating default database"
    db = DefaultDatabase()
    db.test_defaultUserGroupOne()
    print "Created default user and g-000"
    db.test_defaultUserGroupMany()
    print "Created user[1-5]  and g-00[1-5]"
