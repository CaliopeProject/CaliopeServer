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
# Ready, we've got an email.message.Message object.
print message.__class__.__name__
