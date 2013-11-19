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

class Kanban(Thing):
    def __init__(self):
        Thing.__init__(self, "kanban")

class Gis(Thing):
    def __init__(self):
        Thing.__init__(self, "gis")

class SIIM_Form(Thing):
    def __init__(self):
        Thing.__init__(self, "siim_form")

def get_available_things():
    things = [
               Form(),
               Document(),
               Task(),
               Report(),
               Kanban(),
               Gis(),
               SIIM_Form(),
             ]
    return {t.name: t for t in things}

def get_thing_by_class(cls): 
    if cls.__name__ == 'SIIMForm':
       return SIIM_Form()
    return None
