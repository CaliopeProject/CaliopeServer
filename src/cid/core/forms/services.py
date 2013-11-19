# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM2 Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
from tinyrpc.dispatch import public


from flask import current_app

from cid.core.entities import ( CaliopeServices)
from cid.core.entities.base_models.versioned_node import VersionedNode


class FormManager(CaliopeServices):
    def __init__(self, *args, **kwargs):
        super(FormManager, self).__init__(*args, **kwargs)

    @classmethod
    @public("getForms")
    def get_forms(cls):
        rv = []
        for formId in current_app.caliope_forms:
            f = {
                'formId': {'value': formId},
                'label': {'value': current_app.caliope_forms[formId]['label']}
            }
            rv.append(f)
        return rv

    @classmethod
    @public("getModel")
    def get_empty_model(cls, formId):
        if formId in current_app.caliope_forms:
            form = current_app.caliope_forms[formId]
            module = form['module']
            rv = super(FormManager, cls).get_empty_model(entity_class=module,
                                                         template_html=form[
                                                             'html'],
                                                         template_layout=form[
                                                             'layout'],
                                                         actions=[
                                                             {"name": "Guardar",
                                                              "method": "form.commit",
                                                              "params-to-send": "uuid",
                                                              "encapsulate-in-data": "false"}])

            rv['form']['name'] = form['name']
            return rv
        else:
            return ""

    @classmethod
    @public("getData")
    def get_data(cls, formId, uuid):
        if formId in current_app.caliope_forms:
            form = current_app.caliope_forms[formId]
            module = form['module']
            rv = super(FormManager, cls).get_data(uuid, entity_class=module)
            return rv


    @classmethod
    def create_form_from_id(cls, formId, data):
        if formId in current_app.caliope_forms:
            module = current_app.caliope_forms[formId]['module']
            node = module()
            try:
                map(lambda k, v: setattr(node, k, v), data.keys(),
                    data.values())
            except:
                pass
            node.save()

            rv = {'uuid': node.uuid}
            return rv
        else:
            return None

    @classmethod
    @public(name='commit')
    def commit(cls, uuid):
        rv = dict()
        related = cls._get_related(uuid)

        if related > 0:
            for target_uuid in related.keys():
                #: This is to save nodes when no data added but there are
                # in a relationships, we're saving "blank" connected nodes.
                if VersionedNode.pull(target_uuid) is None:
                    cls.update_field(target_uuid, "uuid", target_uuid)
                rv.update(cls.commit(target_uuid))
        rv.update(super(FormManager, cls).commit(uuid))
        return rv





