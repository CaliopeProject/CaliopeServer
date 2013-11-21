#!/usr/bin/python

import email
import imaplib
import sys

class ImapImport:

  def isOK(self, ret):
    return ret[0] == 'OK'

  def __init__(self, server, account, password):
    self.server = server
    self.account = account
    self.password = password

  def SelectFolder(self, folder):
    ret = self.mail.select(folder) # connect to inbox.
    if not self.isOK(ret):
      return False
    print >> sys.stderr, ret[1][0], 'emails in folder', folder
    return True

  def Login(self):
    self.mail = imaplib.IMAP4_SSL(self.server)
    if not self.isOK(self.mail.login(self.account, self.password)): 
      return False
    if not self.isOK(self.mail.list()):
      return False
    return True

  def GetEmailUIDs(self):
    result = self.mail.uid('search', None, 'ALL') # search and return uids instead
    if not self.isOK(result):
      return False, None
    return True, result[1][0].split()

  def FetchEmail(self, uid):
    result = self.mail.uid('fetch', uid, '(RFC822)')
    if not self.isOK(result):
      return False, None
    mail = email.message_from_string(result[1][0][1])
    return True, mail

ii = ImapImport(server='imap.gmail.com', account='metrovivienda2@gmail.com', password='otrosecreto')
if not ii.Login():
  print >> sys.stderr, 'Could not login'
  sys.exit(1)
if not ii.SelectFolder(folder='label1'):
  print >> sys.stderr, 'Could not select folder'
status, uids = ii.GetEmailUIDs()
email_uid_to_fetch = uids[-1]
if not status:
  print >> sys.stderr, 'Could not get email uids'
status, message = ii.FetchEmail(email_uid_to_fetch)
if not status:
  print >> sys.stderr, 'Could not get fetch emai with uid'


allowed_mime_types = ['image/jpeg', 'application/pdf', 'application/zip', 'application/gzip', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/vorbis', 'audio/webm', 'image/gif', 'image/jpeg', 'image/pjpeg', 'image/png', 'image/tiff', 'text/csv', 'text/plain', 'text/xml', 'video/mpeg', 'video/mp4', 'video/ogg', 'video/quicktime', 'video/webm', 'application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.presentation', 'application/vnd.oasis.opendocument.graphics', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']


attachment_id = 0
for part in message.walk():
    c_type = part.get_content_type()
    c_disp = part.get('Content-Disposition')
    print 'c_type:{}\nc_disp:{}\n'.format(c_type, c_disp)
    body = ''
    if c_type == 'text/plain' and c_disp == None:
        print 'Body part <start>'
        print part.get_payload().decode('quopri')#.decode('utf-8')
        print 'Body part <stop>'
        body += '\n' + part.get_payload()
    elif c_type in allowed_mime_types:
        print 'ELSE Body part <start>'
        file_name = 'attachment_{}.png'.format(attachment_id)
        # TODO(nel): use with.
        f = open(file_name, 'w')
        f.write(part.get_payload(decode=True))
        f.close()
        print 'ELSE Body part <stop>'

print 'BODY:', body
