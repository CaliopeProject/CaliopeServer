class Thing:
    def __init__(self, name):
        self.name = name

class Form(Thing):
    def __init__(self):
        Thing.__init__(self, "form")

class Document(Thing):
    def __init__(self):
        Thing.__init__(self, "document")

class Task(Thing):
    def __init__(self):
        Thing.__init__(self, "task")

class Report(Thing):
    def __init__(self):
        Thing.__init__(self, "report")

def get_things():
    things = [
               Form(),
               Document(),
               Task(),
               Report(),
             ]

    return {t.name: t for t in things}

print get_things()
