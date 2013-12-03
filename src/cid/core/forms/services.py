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

from cid.core.pubsub import PubSub

from cid.core.entities import (VersionedNode, CaliopeUser,
                               CaliopeServices)

from cid.core.login import LoginManager


class FormManager(CaliopeServices):
    def __init__(self, *args, **kwargs):
        super(FormManager, self).__init__(*args, **kwargs)

    @classmethod
    @public("getForms")
    def get_forms(cls):
        rv = []
        for formId in current_app.caliope_forms:
            if current_app.caliope_forms[formId]['browsable']:
                f = {
                    'formId': {'value': formId},
                    'label': {'value': current_app.caliope_forms[formId]['label']}
                }
                rv.append(f)
        return rv

    @classmethod
    @public("getModel")
    def get_empty_model(cls, formId, data=False):
        if formId in current_app.caliope_forms:
            form = current_app.caliope_forms[formId]
            module = form['module']
            rv = super(FormManager, cls). \
                get_empty_model(entity_class=module,
                                template_html=form[
                                    'html'],
                                template_layout=form[
                                    'layout'],
                                actions=[
                                    {"name": "Guardar",
                                     "method": "form.commit",
                                     "params-to-send": "uuid",
                                     "encapsulate-in-data": "false"},
                                    {"name": "Descartar Borrador",
                                     "method": "form.discardDraft",
                                     "params-to-send": "uuid",
                                     "encapsulate-in-data": "false"}],
                                data=data)

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
    def commit(cls, uuid, loopback_notification=False):
        rv = dict()
        related = cls._get_related(uuid)

        if related > 0:
            for target_uuid in related.keys():
                #Avoid related locks if theres is a back-relationship:
                if cls._is_related(target_uuid, uuid):
                    continue
                    #: This is to save nodes when no data added but there are
                # in a relationships, we're saving "blank" connected nodes.
                if VersionedNode.pull(target_uuid) is None:
                    cls.update_field(target_uuid, "uuid", target_uuid)
                rv.update(cls.commit(target_uuid, loopback_notification))
        rv.update(super(FormManager, cls).commit(uuid, loopback_notification))

        PubSub().publish_command("", uuid, 'message',
                                 {'msg': 'Formulario actualizado.', 'type': 'success'}, loopback=True)
        return rv


    @classmethod
    @public("discardDraft")
    def discard_draft(cls, uuid):
        rv = dict()
        related = cls._get_related(uuid)

        if related > 0:
            for target_uuid in related.keys():
                #Avoid related locks if theres is a back-relationship:
                if cls._is_related(target_uuid, uuid):
                    continue
                rv.update(cls.discard_draft(target_uuid))
        rv.update(super(FormManager, cls).discard_draft(uuid))
        return rv


    @classmethod
    @public("getAll")
    def get_all(cls, context=None):
        user_node = CaliopeUser.index.get(username=LoginManager().get_user())

        if context:
            node_context = VersionedNode.pull(context).__node__.id
        else:
            node_context = '*'

        results, metadata = user_node.cypher("""
            START n=node(*)
            MATCH path=(n)-[:TARGET]-(task)-[:__CONTEXT__]-(context), p_none=(task)<-[?:PARENT*]-()
            WHERE has(n.uuid) and p_none=null
            RETURN n
             """.format(context=node_context))

        rv = list()
        instances = list()
        entities = list()
        models = list()
        for row in results:
            form = dict()
            uuid = row[0]['uuid']
            entity_name = VersionedNode.pull(uuid).__class__.__name__

            if entity_name not in entities:
                entities.append(entity_name)

            data = super(FormManager, cls).get_data(uuid=uuid)

            form['uuid'] = uuid
            form['classname'] = entity_name
            form['data'] = data
            form['browsable'] = current_app.caliope_forms[entity_name]['browsable']

            instances.append(form)
        rv.append({'instances': instances})

        for entity_name in entities:
            models.append(cls.get_empty_model(entity_name))

        rv.append({'models': models})

        return rv