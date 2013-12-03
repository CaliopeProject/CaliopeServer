from .services import DocumentServices
from cid.core.entities import CaliopeDocument


def get_service():
    CaliopeDocument()
    return DocumentServices(service_class=CaliopeDocument)
