# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.forms import FormNode

from cid.core.entities import (RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

class EvaluacionProducto(FormNode):
    #Definición de datos para el formato EVALUACIÓN DEL PRODUCTO

    # evaluacion_producto - EVALUACIÓN DEL PRODUCTO - Tipo Label
    #identificacion_producto - IDENTIFICACIÓN DEL PRODUCTO Y/O SERVICIO NO CONFORME - Tipo Label
    # fecha - FECHA - Tipo Label
    fecha_evaluacion = DateTimeProperty() # definido en el formulario como "datepicker"
    producto = StringProperty() # PRODUCTO O SERVICIO    
    incumplimiento = StringProperty() # DESCRIPCIÓN DEL REQUISITO INCUMPLIDO
#    cumple = StringListProperty() # CUMPLE con Opciones: SI - NO
    # tratamiento - TRATAMIENTO - Tipo Label
#    opcion_tratamiento = StringListProperty() # Opciones: Lista de chequeo: Reproceso, Concesión, Identificación para su no uso, Eliminación
    reproceso = StringProperty()
    concesion = StringProperty()
    identificacion_no_uso = StringProperty()
    eliminacion = StringProperty()
    acciones = StringProperty() # ACCIONES REALIZADAS    
    registros = StringProperty() # REGISTRO(S) ASOCIADOS
    # verificacion_acciones - VERIFICACIÓN DE LAS ACCIONES - Tipo Label
    nombre_responsable = StringProperty() # NOMBRES Y APELLIDOS RESPONSABLE
    cargo_responsable = StringProperty() # CARGO Y  AREA
    observaciones = StringProperty() # OBSERVACIONES
#    iniciar_acciones = StringListProperty() # Opciones: SI - NO
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
