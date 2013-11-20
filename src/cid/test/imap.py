#!/usr/bin/python

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

  def Test(self):
    result = self.mail.uid('search', None, 'ALL') # search and return uids instead
    if not self.isOK(result):
      return False
    email_uids = result[1][0].split()
    if len(email_uids) == 0:
      return False
    latest_email_uid = email_uids[1]
    result = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
    if not self.isOK(result):
      return False
    print 'Data[0]: ', result[1][0][1]
    return True

ii = ImapImport(server='imap.gmail.com', account='metrovivienda2@gmail.com', password='otrosecreto')
if not ii.Login():
  print >> sys.stderr, 'Could not login'
  sys.exit(1)
if not ii.SelectFolder(folder='label1'):
  print >> sys.stderr, 'Could not select folder'
ii.Test()
