# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class FichaPredial(VersionedNode):

    #Definición de datos para la ficha predial

    identificador_predial = StringProperty()
    chip = StringProperty()
    direccion_fuente = StringProperty()
    barrio = StringProperty()
    estrato = IntegerProperty() # opciones: Null, predios no residenciale y residenciales del 1 al 6#
#    tipo_propietario = ListProperty() #opciones: Propietario, Poseedor
#    tipo_persona = ListProperty() #opciones: Persona Natural, Persona Jurídica
    propietario_actual = StringProperty()
    doc_propietario = StringProperty()
#    tipo_doc_propietario = ListProperty() # CC, NIT, Extrangería
#    sector_predio = ListProperty() # Público, Privado
    direccion_notificacion = StringProperty()# definido en el formulario como textarea
    telefono = StringProperty()
    predio = StringProperty()
    acto_traslativo = StringProperty()
    matricula_inmobiliaria = StringProperty()
    cedula_catastral = IntegerProperty()
    titulo_adquisicion = StringProperty() # definido en el formulario como "textarea"
    cabida_superficiaria = IntegerProperty() # definido en el formulario como "textarea"
    linderos = StringProperty() # Opciones: NORTE: SUR: ORIENTE: OCCIDENTE: FUENTE:  "type": "ckedit"
#    tipo_linderos = StringListProperty() # Opciones: Claros - Confusos
#    incorporacion_topografica = StringListProperty() # opciones: SI, NO
    incoroporacion_topografica_desc = StringProperty() # definido en el formulario como "textarea",
#    registro_topografico = StringListProperty() # opciones: SI, NO
#    tradicion = StringListProperty()
    vigencia_informacion = DateTimeProperty() # definido en el formulario como "datepicker"
#    componente_espacial = StringListProperty() # Opciones: Registral:   Catastral:   Topográfica:
    componente_espacial_registral= StringProperty()
    componente_espacial_catastral= StringProperty()
    componente_espacial_topografica= StringProperty()
    area_registral = FloatProperty()
    area_catastral = FloatProperty()
    area_topografica = FloatProperty()
    observaciones_componente_espacial = StringProperty() # definido en el formulario como "textarea"
    elaboro = StringProperty()
    # informacion_unica_predial = tipo adjunto
    # mapa_tradicion_predial = tipo adjunto
    profesional = StringProperty()
    tarjeta_professional = StringProperty()
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
