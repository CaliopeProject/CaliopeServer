# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class ControlAjustes(VersionedNode):
    #Definición de datos para el CONTROL DE AJUSTES DE DISEÑO

    actividad_diseno = StringProperty() # ACTIVIDAD DE DISEÑO:
    responsable = StringProperty() # RESPONSABLE: 
    #descripcion_ajuste - DESCRIPCIÓN DEL AJUSTE  - Tipo Label
    #razones_ajuste - RAZONES DEL AJUSTE  - Tipo Label
    justificacion = StringProperty() # JUSTIFICACION:
    #evaluacion_impacto - EVALUACION DEL IMPACTO  - Tipo Label
    impactos_evaluados = StringProperty() # IMPACTOS EVALUADOS
    resultados_evaluacion = StringProperty() # RESULTADOS DE LA EVALUACIÓN 
    responsable_evaluacion = StringProperty() # RESPONSABLE
    # datos_nuevos - DATOS NUEVOS Y AJUSTES - Tipo Label
    numero_evaluacion = IntegerProperty() # Nº 
    documento_origen = IntegerProperty() # DOCUMENTO ORIGEN DEL DATO
    version = StringProperty() # VERSIÓN
    dato = StringProperty() # DATO
    magnitud = StringProperty() # MAGNITUD
    #ajuste - DESCRIPCIÓN DEL AJUSTE A REALIZAR  - Tipo Label
    ajuste_desc = StringProperty()
    aprobado_por = StringProperty() # APROBADO POR: 
    cargo = StringProperty() # CARGO:
    fecha_aprobado = DateTimeProperty() # FECHA:
    #productos_ajuste - PRODUCTOS A ENTREGAR ACORDE CON EL AJUSTE - Tipo Label
    numero_producto = IntegerProperty() # Nº
    producto_desc = StringProperty() # PRODUCTO
    codigo_producto = StringProperty() # CÓDIGO
    version_producto = StringProperty() # VERSIÓN
    fecha = DateTimeProperty() # FECHA
    cambio_realizado = StringProperty() # CAMBIO REALIZADO
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
