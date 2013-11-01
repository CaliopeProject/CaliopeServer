import json
import sys

class AccessControl:

  def __init__(self, configuration):
      self.config = json.loads(configuration)

  def _ResolveGroups(self, group_name, seen):
      if group_name in seen:
        print >> sys.stderr, 'Circular reference found. Group:{}'.format(group_name)
        sys.exit(1)
      seen.add(group_name)
      members = []
      for member_or_group in self.config['groups'][group_name]:
          if member_or_group in self.config['groups']:
              # A group. Let's recourse.
              members += self._ResolveGroups(member_or_group, seen)
          else:
              # A member. Let's add it.
              members.append(member_or_group)
      return members

  def _LoadGroupsAndUsers(self):
      """ Populate the list of groups. Groups can belong to other groups. """

      # Make sure we don't call this function twice.
      assert not hasattr(self, 'groups')

      # First load the groups. Groups names have priority over user names.
      self.groups = {}
      for group in self.config['groups']:
          # Now get the users for this group.
          self.groups[group] = self._ResolveGroups(group, seen=set())

def main():
    ac = AccessControl(open('permissions.json').read())
    ac._LoadGroupsAndUsers()
    #ac._ParseGroups()


if __name__ == "__main__":
    main()
