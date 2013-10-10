# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class ConceptoViabilidad(VersionedNode):

    #Definición de datos para el CONCEPTO DE VIABILIDAD TECNICA DE PROYECTOS VIP

    id_proyecto = StringProperty() #ID proyecto:
    nombre_proyecto = StringProperty() # Nombre del Proyecto:
    responsable_proyecto = StringProperty() # Responsable del Proyecto:
    fecha_concepto = DateTimeProperty() # Fecha del concepto: definido en el formulario como "datepicker"
    #imagen_proyecto - Imagen proyecto - Tipo Adjunto
    #justificacion 1. JUSTIFICACIÓN - Tipo Label
    justificacion_desc = StringProperty()
    #id_inmuebles - 2. IDENTIFICACIÓN DE INMUEBLES - Tipo Label
    id_inmuebles_desc = StringProperty()
    informacion_predial = StringProperty() # 2.1. Información predial 
    #anexo1 - Anexo 1.: Ficha Predial - Tipo Adjunto
    informacion_juridica = StringProperty() # 2.2. Información jurídica
    #anexo2 - Anexo 2.: Ficha prejurídica - Tipo Adjunto
    #propuesta - 3. PROPUESTA - Tipo Label
    localizacion = StringProperty() # 3.1. Localización
    norma_aplicable = StringProperty() # 3.2. Norma aplicable
    #anexo3 - Anexo 3.: Ficha normativa - Tipo Adjunto
    descripcion_proyecto = StringProperty() #3.3. Descripción del proyecto
    estructura_urbana = StringProperty() # 3.4. Estructura urbana
    estructura_ecologica = StringProperty() # 3.4.1. Estructura Ecológica Principal
    estructura_funcional1 = StringProperty() # 3.4.2. Estructura Funcional y de servicios 
    sistema_espacio_publico = StringProperty() # 3.4.2.1. Sistema de Espacio Público
    sistema_equipamentos = StringProperty() # 3.4.2.2. Sistema de Equipamientos
    sistema_movilidad = StringProperty() # 3.4.2.3. Sistema de Movilidad y Accesibilidad
    malla_vial = StringProperty() # 3.4.2.3.1. Malla vial
    subsistema_transporte = StringProperty() # 3.4.2.3.2. Subsistema de Transporte
    servicios_publicos = StringProperty() # 3.4.2.4. Sistema de Servicios Públicos
    estructura_funcional2 = StringProperty() # 3.4.3. Estructura Funcional y de servicios
    modelacion_urbanistica = StringProperty() # 3.5. Modelación urbanística
    #anexo4 - Anexo 4.: Ficha de modelación urbanística - Tipo Adjunto
    modelacion_financiera = StringProperty() # 3.6. Modelación financiera
    costos_urbanismo = StringProperty() # 3.6.1. Costos de Urbanismo 
    balance_proyecto = StringProperty() # 3.6.2. Balance del proyecto
    # anexo5 Anexo 5.: Ficha de modelación Financiera, responsable DGI - Tipo Adjunto
    cronograma_proyecto = StringProperty() # 3.7. Cronograma de ejecución del proyecto
    #anexo6 - Anexo 6: Cronograma de ejecución del proyecto
    conclusion_proyecto = StringProperty() # 3.8. Conclusión del concepto
    #anexos 3.9. Anexos - Tipo Label
    #anexo_391 1. Ficha Predial
    #anexo_392 2. Ficha Normativa (y sus respectivos anexos que deben ser listados)
    #anexo_393 3. Ficha Prejuridica (y sus respectivos anexos que deben ser listados)
    #anexo_394 4. Ficha Urbanística
    #anexo_395 5. Ficha Financiera
    #anexo_396 6. Cronograma de ejecución del proyecto
    elaboro = StringProperty() # Concepto elaborado por: 
    firma = StringProperty() # Directora de Operaciones Estratégicas y Proyectos - No definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
