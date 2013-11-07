import json
import sys
import actions
import things

class AccessControl:

    def __init__(self, configuration):
        """ Initialize the access control instance. """
        self.config = json.loads(configuration)
        self.available_actions = actions.get_available_actions()
        self.available_things = things.get_available_things()
        # Load actions, groups and things.
        self._load_actions()
        self._load_groups_and_users()
        self._load_things()

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

    def _load_groups_and_users(self):
        """ Populate groups with their users. Groups can belong to other groups. """

        # Make sure we don't call this function twice.
        assert not hasattr(self, 'groups')

        self.groups = {}
        for group in self.config['groups']:
            # Now get the users for this group.
            self.groups[group] = self._resolve_right_side('groups', group, seen=set())

    def _get_class_name_from_internal(self, whole_name):
      """ Get a string like 'internal.name' and return what is after the point  """
      split = whole_name.split('.')
      if len(split) != 2:
        print >> sys.stderr, 'Wrong name. Expected internal.something, got:{}'.format(whole_name)
        sys.exit(1)
      assert split[0] == 'internal'
      return split[1]

    def _load_things(self):
        """ Load the list of things that we can use. """
        # Make sure we do not call this function twice.
        assert not hasattr(self, 'things')
        # This is the dict we are going to store.
        self.things = {}
        # Check that all the things can be resolved to something we know.
        for thing_left in self.config['things']:
            self.things[thing_left] = []
            for right_thing in self._resolve_right_side('things', thing_left, seen=set()):
                name = self._get_class_name_from_internal(right_thing)
                if name not in self.available_things:
                    print  >> sys.stderr, \
                        '{} not in the list of available things. List is: {}'. \
                                 format(name, self.available_things)
                    sys.exit(1)
                self.things[thing_left].append(name)

    def _load_actions(self):
        """ Load the list of actions we can use.
            This function is similar to _load_things. 
        """
        # Make sure we do not call this function twice.
        assert not hasattr(self, 'actions')
        # This is the dict we are going to store.
        self.actions = {}
        # Check that all the actions can be resolved to something we know.
        for thing_left in self.config['actions']:
            self.actions[thing_left] = []
            for right_thing in self._resolve_right_side('actions', thing_left, seen=set()):
                name = self._get_class_name_from_internal(right_thing)
                if name not in self.available_actions:
                    print  >> sys.stderr, \
                        '{} not in the list of available actions. List is: {}'. \
                                 format(name, self.available_actions)
                    sys.exit(1)
                self.actions[thing_left].append(name)

    def get_actions(self):
        return self.actions.keys()

    def get_things(self):
        return self.things.keys()

    def get_groups(self):
        return self.groups.keys()

    def get_users_in_grup(self, group):
        return self.groups[group]


def main():
    ac = AccessControl(open('permissions.json').read())
    print 'groups:', ac.get_groups()
    print 'actions:', ac.get_actions()
    print 'things:', ac.get_things()
    #for group in ac.get_groups():
    #    print 'group:', group
    #    print ac.get_users_in_grup(ac.get_groups()[0])


if __name__ == "__main__":
    main()
