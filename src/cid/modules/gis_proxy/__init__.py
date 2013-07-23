from flask import Blueprint
import gis_proxy

gis_proxy_blueprint = gis_proxy.gis_proxy

def getBlueprint():
    return gis_proxy_blueprint
