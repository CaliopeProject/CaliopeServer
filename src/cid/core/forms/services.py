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
import re

import os

from tinyrpc.dispatch import public

from flask import current_app

from cid.core.pubsub import PubSub

from cid.core.entities import (VersionedNode, CaliopeUser, CaliopeDocument,
                               CaliopeServices)

from cid.core.login import LoginManager
from cid.utils.thumbnails import get_thumbnail
from cid.utils.fileUtils import human_readable_size


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
    def get_empty_model(cls, formId, data=False, thumbnails=False):
        if formId in current_app.caliope_forms:
            form = current_app.caliope_forms[formId]
            module = form['module']
            template_layout = form['thumbnail'] if thumbnails else form['layout']
            rv = super(FormManager, cls). \
                get_empty_model(entity_class=module,
                                template_html=form[
                                    'html'],
                                template_layout=template_layout,
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
    @public("find")
    def find(cls, formId, filter=None):
        rv = []
        if formId in current_app.caliope_forms:
            form = current_app.caliope_forms[formId]
            module = form['module']
            if filter and len(filter) == 1:
                k,v = filter.popitem()
                query = k + ':' + v
                rv = [vnode.serialize() for vnode in module.index.search(query)]
        return rv

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
        #TODO IMPORTANT!!! Use EntityServices. update field, and commit.
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
    def get_all(cls, context=None, recursive=False):
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

            #TODO: fix workaround
            if entity_name not in current_app.caliope_forms:
                continue

            if entity_name not in entities:
                entities.append(entity_name)

            data = super(FormManager, cls).get_data(uuid=uuid)

            form['uuid'] = uuid
            form['classname'] = entity_name
            form['data'] = data
            form['browsable'] = current_app.caliope_forms[entity_name]['browsable']

            if (recursive):
                cls.get_related_data(instances, data)

            instances.append(form)

        rv.append({'instances': instances})

        for entity_name in entities:
            models.append(cls.get_empty_model(entity_name, thumbnails=True))

        rv.append({'models': models})

        return rv

    @classmethod
    def get_related_data(cls, instances, data):

        uuid4hex = re.compile('[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}')

        for field_name in data:
            field = data[field_name]
            type(field) == dict
            for key in field:
                related_uuid = uuid4hex.match(key)
                if related_uuid:
                    entity_name = VersionedNode.pull(related_uuid.string).__class__.__name__
                    #TODO: fix workaround
                    if entity_name not in current_app.caliope_forms:
                        continue

                    form = dict()
                    node = super(FormManager, cls).get_data(uuid=related_uuid.string)
                    form['uuid'] = related_uuid.string
                    form['classname'] = entity_name
                    form['data'] = node
                    form['browsable'] = False

                    instances.append(form)

                    cls.get_related_data(instances, node)

    @classmethod
    @public("getAllWithThumbnails")
    def get_all_with_thumbnails(cls, context=None, thumbnails=False):
        rv = cls.get_all(context=context, recursive=False)

        #TODO: move to DocumentServices
        user_node = CaliopeUser.index.get(username=LoginManager().get_user())

        storage_setup = current_app.config['storage']
        if 'local' in storage_setup and 'absolut_path' in storage_setup['local']:
            STORAGE = storage_setup['local']['absolut_path']

        for form in rv[0]['instances']:
            #TODO: optimize
            results, metadata = user_node.cypher("""
                START form=node:CaliopeStorage(uuid='{uuid}')
                MATCH  pa=(form)-[*1..2]-(file)<-[CALIOPE_DOCUMENT]-(),p_none=(file)<-[?:PARENT*]-()
                WHERE p_none = null and has(file.url)
                return distinct file
                 """.format(uuid=form['uuid']))

            #TODO: use cache to thumbnails
            attachments = list()
            for row in results:
                attachment = row[0]
                file_uuid = attachment['uuid']
                node = CaliopeDocument.pull(file_uuid)
                if thumbnails:
                    filename = os.path.join(STORAGE, file_uuid)
                    size = os.stat(filename).st_size
                    data = {
                        'uuid': file_uuid,
                        'name': node.filename,
                        'size': human_readable_size(size),
                        'thumbnail': get_thumbnail(filename, field_name='data', mimetype=node.mimetype)
                    }
                else:
                    data = {
                        'uuid': file_uuid,
                        'name': node.filename
                    }
                attachments.append(data)
            form['attachments'] = attachments

        return rv
