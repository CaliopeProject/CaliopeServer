# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Cid Server is the web server of SIIM2 Framework
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
import importlib

from flask import current_app
#tinyrpc
from tinyrpc.dispatch import public
from tinyrpc.dispatch import RPCDispatcher

CORE_MODULES = ['cid.core.dispatcher']


def register_modules(app, package_base='cid'):
    """
    Register modules listed in the configuration of the app.

    """
    _load_core_modules(app)

    for module in app.config['modules']:
        module_config = module.values()[0]
        module_name = module.keys()[0]
        package = module_config['package'] if 'package' in module_config else ''

        #: default route is /package
        route = module_config['route'] if 'route' in module_config else '/' \
                                                                        + module_name
        service = module_config['service'] if 'service' in module_config else \
            module_name
        service += "."

        base = module_config['base'] if 'base' in module_config else package_base

        #:TODO  Is possible to only module to have more than 1 blueprint
        blueprint_name = module_config['module_imp'] if 'module_imp' in module_config else \
            module_config['package'].split('.')[-1]
        try:
            module_imp = importlib.import_module(base + '.' + package)

            try:
                app.register_blueprint(module_imp.getBlueprint(), url_prefix=route)
            except AttributeError as e:
                #This modules does not contain a blueprint
                #app.logger.warning(str(e))
                pass
            try:
                dispatcher = getattr(app, 'dispatcher', None)
                if dispatcher is not None:
                    dispatcher.register_instance(module_imp.get_service(), service)
                else:
                    raise Exception("No dispatcher found")
            except AttributeError as e:
                #app.logger.warning(str(e))
                pass
            #This modules does not contain a blueprint
        except ImportError as e:
            app.logger.exception(str(e))
        except Exception as e:
            app.logger.critical(e)



    _load_get_methods(app)


def _load_core_modules(app):
    dispatcher = RPCDispatcher()
    setattr(app, 'dispatcher', dispatcher)
    for module in CORE_MODULES:
        try:
            module_imp = importlib.import_module(module)
            app.register_blueprint(module_imp.bp)
        except AttributeError as e:
            app.logger.warning(str(e))
        except ImportError as e:
            app.logger.exception(str(e))


def _load_get_methods(app):
    getattr(app, 'dispatcher', None).add_method(_getMethods, name="general.getMethods")


@public
def _getMethods():
    methods = __get_methods(getattr(current_app, 'dispatcher', None), "")
    return {'methods': methods}


def __get_methods(dp, context):
    methods = []
    for name in dp.method_map.keys():
        methods.append(context + name)

    for prefix, subdispatchers in dp.subdispatchers.iteritems():
        for sd in subdispatchers:
            methods = methods + __get_methods(sd, prefix)
    return methods


