from flask import Blueprint
import hyperion_proxy

hyperion_proxy_blueprint = hyperion_proxy.hyperion_proxy


def getBlueprint():
    return hyperion_proxy_blueprint
