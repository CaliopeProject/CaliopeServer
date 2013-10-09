# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode

class ViabilidadNormativa(VersionedNode):
    #Definición de datos para la ficha de viabilidad normativa 
    #nombre_proyecto NOMBRE DEL PROYECTO - Se define como label en el formulario
    #localización = tipo adjunto
    #afectaciones = tipo adjunto
    #norma_zonificacion_pot -  NORMA GENERAL-ZONIFICACION POT - Se define como label
    upz = StringProperty()
    sector = StringProperty()
    tratamiento_zonificacion_pot = StringProperty()
    area_actividad_zonificacion_pot  = StringProperty()
    zona_zonificacion_pot = StringProperty()
    #norma_zonificacion_acuerdo6 -  NORMA GENERAL-ZONIFICACION ACUERDO 6 - Se define como label
    tratamiento_zonificacion_acuerdo6 = StringProperty()
    area_actividad_zonificacion_acuerdo6 = StringProperty()
    zona_zonificacion_acuerdo6 = StringProperty()
    usos_zonificacion_acuerdo6 = StringProperty()
    #norma_especifica -  NORMA ESPECÍFICA - ESTUDIO NORMA - Se define como label
    plano_urbanistico_topografico_desc = StringProperty() #caja de texto
    regimen_normativo = StringProperty()# caja de texto
    normas = StringProperty()# caja de texto
    #usos - USOS Opciones de la lista de chequeo: SUBSECTOR, ACTO ADMINISTRATIVO, DECRETO, OTROS	
        #subsector
        #acto_administrativo
        #decreto
        #otros_usos_desc
    #uso1 USO - título de la columna 
    #uso1_categoria -  CATEGORIA - Subtítulo de USO (uso1)
    #uso1_vivienda_familiar -  VIVIENDA UNIFAMILIAR Y BIFAMILIAR - Subtítulo de USO (uso1)
#    familiar_categoria = StringListProperty() # opciones escritas por el usuario: Se permite, No se permite
    #uso1_vivienda_multifamiliar -  VIVIENDA MULTIFAMILIAR - Subtítulo de USO (uso1)
#    multifamiliar_categoria = StringListProperty() # opciones escritas por el usuario: Se permite, No se permite
    #uso1_estacionamientos - ESTACIONAMIENTOS Sector de Demanda - Título
    estacionamiento_privado_familiar =  StringProperty() #Estacionamientos - Privados - Vivienda Unifamiliar y Bifamiliar
    estacionamiento_visitante_familiar =  StringProperty() #Estacionamientos - Visitantes - Vivienda Unifamiliar y Bifamiliar
    estacionamiento_privado_multifamiliar =  StringProperty() #Estacionamientos - Privados - Vivienda Multifamiliar
    estacionamiento_visitante_multifamiliar =  StringProperty() #Estacionamientos - Visitantes - Vivienda Multifamiliar
    #uso2 USO - título de la columna
    #uso2_categoria -  CATEGORIA - Subtítulo de USO (uso2)   
    #uso2_dotacional -  DOTACIONAL - Subtítulo de USO (uso2)
#    dotacional_categoria = StringListProperty() # opciones escritas por el usuario: Se permite, No se permite
    #uso2_comercio_servicios -  COMERCIO Y SERVICIOS - Subtítulo de USO (uso2)
#    comercio_categoria = StringListProperty() # opciones escritas por el usuario: Se permite, No se permite
    #uso2_industria -  INDUSTRIA - Subtítulo de USO (uso2)
#    industria_categoria = StringListProperty() # opciones: Se permite, No se permite
    #uso2_condiciones_observaciones - CONDICIONES Y OBSERVACIONES
    uso2_condiciones_observaciones =  StringProperty()
    #edificabilidad - EDIFICABILIDAD Opciones lista de chequeo: SUBSECTOR, ACTO ADMINISTRATIVO, DECRETO, OTROS
        #subsector
        #acto_administrativo
        #decreto
        #otros_usos_desc
    #tipo_predio - TIPO DE PREDIO - Título
    tipo_predio_desc = StringProperty()
    indice_ocupacion = StringProperty() #INDICE DE OCUPACION VIVIENDA MULTIFAMILIAR - Subtítulo de TIPO DE PREDIO
    indice_construccion = StringProperty() #INDICE DE CONSTRUCCION - Rango numérico escrito por el usuario - Subtítulo de TIPO DE PREDIO
    altura = StringProperty() #altura - ALTURA - Subtítulo de TIPO DE PREDIO
    tipologia = StringProperty() #tipologia - TIPOLOGÍA - Subtítulo de TIPO DE PREDIO
    aislamiento_posterior = StringProperty() #aislamiento_posterior - AISLAMIENTO POSTERIOR - Subtítulo de TIPO DE PREDIO
    antejardines = StringProperty() #antejardines - ANTEJARDINES - Subtítulo de TIPO DE PREDIO
    semisotano = StringProperty() #semisotano - SEMISOTANO - Subtítulo de TIPO DE PREDIO    
    voladizos = StringProperty() #voladizos - VOLADIZOS - Subtítulo de TIPO DE PREDIO    
    subdivision_predial = StringProperty() #subdivision_predial - SUBDIVISION PREDIAL MINIMA - Subtítulo de TIPO DE PREDIO    
    observaciones_edificabilidad = StringProperty() #observaciones_edificabilidad - OBSERVACIONES  - Subtítulo de TIPO DE PREDIO    
    #verificacion_norma - VERIFICACION DE NORMA Y DETERMINANTES - Título
    verificacion_norma_desc = StringProperty() 
    #notas_recomendaciones - NOTAS-RECOMENDACIONES - Título
    notas_recomendaciones = StringProperty()
    #observaciones_urbanisticas - OBSERVACIONES URBANISTICAS - Título
    observaciones_urbanisticas = StringProperty() 
    #resumen_diagnostico - RESUMEN DIAGNÓSTICO FINAL - Título
    resumen_diagnostico = StringProperty() 
    #Final del formulario
    elaboro = StringProperty()
    reviso = StringProperty()
    #fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
 #   estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado

