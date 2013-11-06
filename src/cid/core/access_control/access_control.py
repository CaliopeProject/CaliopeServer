import json
import sys

class AccessControl:

    def __init__(self, configuration):
        """ Initialize the access control instance. """
        self.config = json.loads(configuration)

    def _resolve_groups(self, group_name, seen):
        """ Get the users that belong to a group. """
        if group_name in seen:
          print >> sys.stderr, 'Circular reference found. Group:{}'.format(group_name)
          sys.exit(1)
        seen.add(group_name)
        members = []
        for member_or_group in self.config['groups'][group_name]:
            if member_or_group in self.config['groups']:
                # A group. Let's recourse.
                members += self._resolve_groups(member_or_group, seen)
            else:
                # A member. Let's add it.
                members.append(member_or_group)
        return members

    def load_groups_and_users(self):
        """ Populate groups with their users. Groups can belong to other groups. """

        # Make sure we don't call this function twice.
        assert not hasattr(self, 'groups')

        self.groups = {}
        for group in self.config['groups']:
            # Now get the users for this group.
            self.groups[group] = self._resolve_groups(group, seen=set())

    def get_groups(self):
      return self.groups.keys()

    def get_users_in_grup(self, group):
      return self.groups[group]

def main():
    ac = AccessControl(open('permissions.json').read())
    ac.load_groups_and_users()
    print ac.get_groups()
    for group in ac.get_groups():
        print 'group:', group
        print ac.get_users_in_grup(ac.get_groups()[0])

if __name__ == "__main__":
    main()
