import json
#from services import CaliopeEntityService
#from cid.core.tasks.models import TaskData

#neomodel primitives
from neomodel.relationship_manager import RelationshipDefinition, RelationshipFrom, RelationshipTo
from neomodel.properties import (Property,
                                 DateTimeProperty,
                                 IntegerProperty)

      
class CaliopeEntityUtil(object):

    def makeFormTemplate(self, entity_class, html=None):
        """
        Utility method to create a json template from a `class` definition.
        :param entity_class: Class to build the template
        :param html: Already defined html
        :return: `dict` with the json form template.
        """
        json_template = dict()
        json_template['name'] = entity_class.__name__
        json_template['html'] = html if html else self.show_dictionary(
            entity_class.__dict__)
        return json_template

    def makeLayoutTemplate(self, entity_class):
        elements = list()
        for field in entity_class.__dict__:
            if isinstance(entity_class.__dict__[field], Property):
                elements.append(field)
        columns = list()
        columns.append({"elements": elements})
        return {"columns": columns}

    def show_dictionary(self,  dictionary):
        fields = []
        for field in dictionary:
            if isinstance(dictionary[field],Property):
                json_entry = {"name": field, "caption":field }
                if isinstance(dictionary[field],DateTimeProperty):
                    json_entry['type'] = 'datepicker'
                    json_entry['format'] = 'dd/MM/yyyy'
                elif isinstance(dictionary[field],IntegerProperty):
                    json_entry['type'] = 'number'
                else:
                    json_entry['type'] = 'textarea'
                fields.append(json_entry)
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
    
#util = CaliopeEntityUtil()
#util.makeTemplate(TaskData())

#f=file('test.json','w')
#f.write(json.dumps(util.json_template, sort_keys=True, indent=2))
#f.close()
#f=file('test.json','r')
#data=json.loads(f.read())
#f.close()

#print str(util.validateTemplate(TaskData(),data))
