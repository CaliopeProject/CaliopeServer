import json
import sys
import things

class AccessControl:

    def __init__(self, configuration):
        """ Initialize the access control instance. """
        self.config = json.loads(configuration)

    def _resolve_right_side(self, config_kind, key_name, seen):
        """ Resolve right side in configuration. Useful for rules that can use
            other rules. For instance, a group can specify other groups in the
            configuration. Circular references are detected.
            config_kind can be: groups, things, actions.
        """
        if key_name in seen:
          print >> sys.stderr, 'Circular reference found resolving {} : {}'.format(config_kind, key_name)
          sys.exit(1)
        seen.add(key_name)
        right_side = []
        for instance_or_kind in self.config[config_kind][key_name]:
            if instance_or_kind in self.config[config_kind]:
                # A group of things(kind). Let's recourse to resolve.
                right_side += self._resolve_right_side(config_kind, instance_or_kind, seen)
            else:
                # An instance. Let's add it.
                right_side.append(instance_or_kind)
        return right_side

    def load_groups_and_users(self):
        """ Populate groups with their users. Groups can belong to other groups. """

        # Make sure we don't call this function twice.
        assert not hasattr(self, 'groups')

        self.groups = {}
        for group in self.config['groups']:
            # Now get the users for this group.
            self.groups[group] = self._resolve_right_side('groups', group, seen=set())

    def load_things(self):
        """ Load the list of things that we can use. """
        # Make sure we do not call this function twice.
        assert not hasattr(self, 'things')

        self.things = {}
        for thing_left in self.config['things']:
            self.things[thing_left] = self._resolve_right_side('things', thing_left, seen=set())
        # Check that all the things can be resolved to a class we know.
        self.available_things = things.get_available_things()
        for thing_left in self.config['things']:
            for right_thing in self.things[thing_left]:
                print  right_thing


    def get_groups(self):
      return self.groups.keys()

    def get_users_in_grup(self, group):
      return self.groups[group]


def main():
    ac = AccessControl(open('permissions.json').read())
    ac.load_groups_and_users()
    ac.load_things()
    print ac.get_groups()
    for group in ac.get_groups():
        print 'group:', group
        print ac.get_users_in_grup(ac.get_groups()[0])


if __name__ == "__main__":
    main()
