# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.forms import FormNode

from cid.core.entities import (VersionedNode, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)


class ChequeoTrasladoProvision(FormNode):
    #Definición de datos para la LISTA DE CHEQUEO PARA LA REALIZACIÓN DEL TRASLADO DE PROVISIÓN VIS/VIP EN PROYECTOS DE METROVIVIENDA

    #documentacion - DOCUMENTACIÓN - Tipo Label
    #entrega - ENTREGA - Tipo Label
    #observacion - OBSERVACION - Tipo Label
#    solicitud_traslado = StringListProperty() # Solicitud de traslado, opciones:  SI, NO
#    observaciones_solicitud_traslado = StringProperty() # definido en el formulario como "textarea"
#    certificado_tradicion = StringListProperty() #Copia del certificado de Libertad de tradición y libertad predio original. opciones:  SI, NO
    observaciones_certificado_tradicion = StringProperty() # definido en el formulario como "textarea"    
#    cuadro_areas = StringListProperty() #Copia del cuadro de áreas del proyecto. opciones:  SI, NO
    observaciones_cuadro_areas = StringProperty() # definido en el formulario como "textarea"
#    representacion_legal = StringListProperty() #Certificado de Existencia y Representación Legal opciones:  SI, NO
    observaciones_representacion_legal = StringProperty() # definido en el formulario como "textarea"
#    curaduria_urbana = StringListProperty() #Certificación de la Curaduría Urbana donde se indiquen las áreas del proyecto, el tipo de proyecto y se estime la provisión de VIS o VIP.  opciones:  SI, NO
    observaciones_curaduria_urbana = StringProperty() # definido en el formulario como "textarea"
#    poder_si_aplica = StringListProperty() #En caso de de que aplique: poder o copia del mismo.  opciones:  SI, NO
    observaciones_poder_si_aplica = StringProperty() # definido en el formulario como "textarea"
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#   estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
