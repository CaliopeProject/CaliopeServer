# -*- encoding: utf-8 -*-
"""
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

import email
from email.header import decode_header
import imaplib
import sys

allowed_mime_types = ['image/jpeg', 'application/pdf', 'application/zip',
                      'application/gzip', 'audio/mp4', 'audio/mpeg', 'audio/ogg',
                      'audio/vorbis', 'audio/webm', 'image/gif', 'image/jpeg',
                      'image/pjpeg', 'image/png', 'image/tiff', 'text/csv',
                      'text/plain', 'text/xml', 'video/mpeg', 'video/mp4',
                      'video/ogg', 'video/quicktime', 'video/webm',
                      'application/vnd.oasis.opendocument.text',
                      'application/vnd.oasis.opendocument.spreadsheet',
                      'application/vnd.oasis.opendocument.presentation',
                      'application/vnd.oasis.opendocument.graphics',
                      'application/vnd.ms-excel',
                      'application/octet-stream',
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      'application/vnd.ms-powerpoint',
                      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document']


class ImapImport:
    def __init__(self, server, account, password):
        self.server = server
        self.account = account
        self.password = password

    def isOK(self, ret):
        return ret[0] == 'OK'

    def Login(self):
        self.mail = imaplib.IMAP4_SSL(self.server)
        if not self.isOK(self.mail.login(self.account, self.password)):
            return False
        if not self.isOK(self.mail.list()):
            return False
        return True

    def Logout(self):
        print >> sys.stderr, 'Logging out.'
        self.mail.expunge()
        self.mail.close()
        self.mail.logout()

    def SelectFolder(self, folder):
        ret = self.mail.select(folder)
        if not self.isOK(ret):
            return False
        print >> sys.stderr, ret[1][0], 'emails in folder', folder
        return True

    def GetAvailableEmailUids(self):
        result = self.mail.uid('search', None, 'ALL')
        if not self.isOK(result):
            return False, None
        return True, result[1][0].split()

    def DeleteEmail(self, uid):
        if not self.isOK(self.mail.uid('store', uid, '+FLAGS', '\\Deleted')):
            print >> sys.stderr, 'Could no delete email with uid', uid

    def FetchEmail(self, email_uid):
        result = self.mail.uid('fetch', email_uid, '(RFC822)')
        if not self.isOK(result):
            print >> sys.stderr, 'Could not get fetch email with uid:', email_uid
            return False, None

        message = email.message_from_string(result[1][0][1])

        attachments = []

        available_body = {}
        for part in message.walk():
            c_type = part.get_content_type()
            c_disp = part.get('Content-Disposition')
            if c_type in ('text/plain', 'text/html') and c_disp == None:
                available_body[c_type] = part.get_payload().decode('quopri')
            elif c_type in allowed_mime_types:
                attachments.append((c_type, part.get_filename(), part.get_payload(decode=True)))
            else:
                print >> sys.stderr, 'Mime type "{}" not supported yet.'.format(c_type)
        body = ''
        for c_type in ('text/html', 'text/plain'):
            if c_type in available_body:
                body = available_body[c_type]
                break
        subject, s_encoding = decode_header(message['Subject'])[0]
        if s_encoding:
            subject = subject.decode(s_encoding).encode('utf-8')
        return True, {'subject' : subject,
                      'body' : body,
                      'attachments' : attachments}

def CheckEmail(delete=False):
    rv = list()
    ii = ImapImport(server='imap.gmail.com', account='metrovivienda2@gmail.com', password='otrosecreto')

    if not ii.Login():
        print >> sys.stderr, 'Could not login'
        ii.Logout()
        return

    if not ii.SelectFolder(folder='CaliopeMail'):
        print >> sys.stderr, 'Could not select folder'
        ii.Logout()
        return

    status, email_uids = ii.GetAvailableEmailUids()

    if not status:
        print >> sys.stderr, 'Could not get email uids'
        ii.Logout()
        return

    n_retrieved = 0
    for email_uid in email_uids:
        status, mail = ii.FetchEmail(email_uid)
        if status:
            n_retrieved += 1
            rv.append(mail)
            if delete:
                ii.DeleteEmail(email_uid)

    print >> sys.stderr, 'Retrieved', n_retrieved, 'emails'
    ii.Logout()
    return rv

#tinyrpc
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.client import RPCClient, RPCError
from tinyrpc.transports.http import HttpWebSocketClientTransport
import hashlib

def EncodeStr(s):
    return s.decode('utf-8').encode('ascii', 'ignore')

class CaliopeClient(object):
    def __init__(self, *args, **kwargs):
         self.login(u'user', u'123')

    def login(self, username, password):
        self.rpc_client = RPCClient(JSONRPCProtocol(),
                                    HttpWebSocketClientTransport('ws://localhost:9000/api/ws'))
        self.loginManager = self.rpc_client.get_proxy("login.")
        hashed_password = hashlib.sha256(password).hexdigest()
        return self.loginManager.authenticate(username=username,
                                              password=hashed_password)

    def get_model(self, msg):
        tasks_proxy = self.rpc_client.get_proxy(prefix="tasks.")
        model = tasks_proxy.getModel()
        uuid = model["data"]["uuid"]["value"]
        #:update
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="name",
                                         value=EncodeStr(msg['subject']))
        update = tasks_proxy.updateField(uuid=uuid,
                                         field_name="description",
                                         value=EncodeStr(msg['body']))
        #:commit
        commit = tasks_proxy.commit(uuid=uuid)

c = CaliopeClient()
import time
while True:
    rv = CheckEmail(delete=True)
    for msg in rv:
        c.get_model(msg)

    time.sleep(30)

