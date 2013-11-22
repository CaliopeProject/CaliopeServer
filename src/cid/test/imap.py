#!/usr/bin/python

import email
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
        if not self.IsOK(self.mail.uid('store', uid, '+FLAGS', '\\Deleted')):
          print >> sys.stderr, 'Could no delete email with uid', uid

    def FetchEmail(self, email_uid):
        result = self.mail.uid('fetch', email_uid, '(RFC822)')
        if not self.isOK(result):
          print >> sys.stderr, 'Could not get fetch email with uid:', email_uidh
          return False, None

        message = email.message_from_string(result[1][0][1])

        attachments = []

        for part in message.walk():
            c_type = part.get_content_type()
            c_disp = part.get('Content-Disposition')
            body = ''
            if (c_type == 'text/plain' or c_type == 'text/html') and c_disp == None:
                body += part.get_payload().decode('quopri')
            elif c_type in allowed_mime_types:
                attachments.append((c_type, part.get_filename(), part.get_payload(decode=True)))
            else:
                print >> sys.stderr, 'Mime type "{}" not supported yet.'.format(c_type)
        return True, [message['Subject'], body, attachments]


def CheckEmail():
    ii = ImapImport(server='imap.gmail.com', account='metrovivienda2@gmail.com', password='otrosecreto')

    if not ii.Login():
        print >> sys.stderr, 'Could not login'
        ii.Logout()
        return

    if not ii.SelectFolder(folder='label1'):
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
        status, email = ii.FetchEmail(email_uid)
        if status:
          n_retrieved += 1
          subject, body, attachments = email
          print 'Subject:', subject
          print 'Body:', body
          for a in attachments:
            print 'mime', a[0]
            print 'filename', a[1]
            #print 'contents', a[2]

          # Delete the email.
          ii.DeleteEmail(email_uid)

    print >> sys.stderr, 'Retrieved', n_retrieved, 'emails'
    ii.Logout()

CheckEmail()
