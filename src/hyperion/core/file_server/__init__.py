from flask import Blueprint
import server

blueprint = server.file_server


def getBlueprint():
    return blueprint
