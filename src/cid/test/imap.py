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

ii = ImapImport(server='imap.gmail.com', account='metrovivienda2@gmail.com', password='otrosecreto')
if not ii.Login():
  print >> sys.stderr, 'Could not login'
  sys.exit(1)
if not ii.SelectFolder(folder='label1'):
  print >> sys.stderr, 'Could not select folder'
