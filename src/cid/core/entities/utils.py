import json
from services import CaliopeEntityService
from cid.core.tasks.models import TaskData

#neomodel primitives
from neomodel.relationship_manager import RelationshipDefinition, RelationshipFrom, RelationshipTo
from neomodel.properties import ( Property,
                                  DateTimeProperty,
                                  StringProperty, IntegerProperty, JSONProperty)

      
class CaliopeEntityUtil(object):
    def __init__(self, *args, **kwargs):
        self.json_template = {}
    
    def makeTemplate(self,entitydata):
        self.json_template['name'] = entitydata.__class__.__name__
        self.json_template['html'] = self.show_dictionary(entitydata.__class__.__dict__)
        
        
    def show_dictionary(self,dictionary):
        fields = []
        for field in dictionary:
            if (isinstance(dictionary[field],Property)):
                json_entry = { "name": field, "caption":field }
                if (isinstance(dictionary[field],DateTimeProperty)):
                    json_entry['fieldtype'] = 'datepicker'
                    json_entry['format']    = 'dd/MM/yyyy'
                elif (isinstance(dictionary[field],IntegerProperty)):
                    json_entry['fieldtype'] = 'number'
                else:
                    json_entry['fieldtype'] = 'textarea'
                fields.append( json_entry )
        return fields
          
    def validateTemplate(self, entity, template):
        dictionary = entity.__class__.__dict__
        if 'html' not in template:
            return False
        html = template['html']
        for entry in html:
            if entry['name'] in dictionary and 'fieldtype' in entry:
                pass
            else:
                return False
        return True
    
util = CaliopeEntityUtil()

util.makeTemplate(TaskData())

f=file('test.json','w')
f.write(json.dumps(util.json_template, sort_keys=True, indent=2))
f.close()


f=file('test.json','r')
data=json.loads(f.read())
f.close()

print str(util.validateTemplate(TaskData(),data))