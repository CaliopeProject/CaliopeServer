import json
import sys

class AccessControl:

  def __init__(self, configuration):
      self.config = json.loads(configuration)

  def ResolveGroups(self, group_name, seen=set()):
      if group_name in seen:
        print >> sys.stderr, 'circular reference found for group {}'.format(group_name)
      seen.add(group_name)
      members = []
      for member_or_group in self.config['groups'][group_name]:
          if member_or_group in self.groups:
              members += self.ResolveGroups(member_or_group, seen)
          else:
              members.append(member_or_group)
      return members

  def _LoadGroupsAndUsers(self):
      """ Populate the list of groups. Groups can belong to other groups. """

      # Make sure we don't call this function twice.
      assert not hasattr(self, 'groups')

      # First load the groups. Groups names have priority over user names.
      self.groups = {}
      for group in self.config['groups']:
          print 'resolving group {}'.format(group)
          self.groups[group] = self.ResolveGroups(group)

      for group in self.config['groups']:
        print 'group({}) => {}'.format(group, self.groups[group])
      #    for user in self.config['groups'][group]:
      #        #if user in self.config['groups']:
      #        #    print >> sys.stderr, 'Username {} has been used already as group name'.format(user)
      #        #    sys.exit(1)
      #        pass

def main():
    ac = AccessControl(open('permissions.json').read())
    ac._LoadGroupsAndUsers()
    #ac._ParseGroups()


if __name__ == "__main__":
    main()
