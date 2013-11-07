class Action:
    def __init__(self, name):
        self.name = name

class Read(Action):
    def __init__(self):
        Action.__init__(self, "read")

class Write(Action):
    def __init__(self):
        Action.__init__(self, "write")

class Assign(Action):
    def __init__(self):
        Action.__init__(self, "assign")

def get_available_actions():
    actions = [
                Read(),
                Write(),
                Assign(),
              ]
    return {t.name: t for t in actions}
