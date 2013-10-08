
#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, CaliopeJSONProperty)

from cid.modules.projects.models import ProjectEntity


class FichaCatastral(CaliopeEntity):
    pass


class FichaCatastralData(CaliopeEntityData):
    __entity_data__ = FichaCatastral
    #Definición de datos para la ficha predial

    #imagenes_generales - IMÁGENES GENERALES DEL PROYECTO - Titulo1 - Se define como label en el formulario: imagenes_generales
    #localización_general = tipo adjunto
    #topografia = tipo adjunto
    #imagen_satelite = tipo adjunto
    #consideraciones_ambientales = tipo adjunto
    #info_gestion -  INFORMACIÓN PARA GESTIÓN Y FINANCIACIÓN Subtitulo de IMÁGENES GENERALES DEL PROYECTO - Se define como label
    fuente_proyecto = StringProperty()
    tipo_predio = StringProperty()
    tiempo_gestion = StringProperty() # se escribe el año
    tipo_gestion = StringProperty()
    fuente_recursos = StringProperty()
    desarrollo_prioritario = StringProperty()
    fecha_vencimiento_dp = DateProperty() 
    #localizacion - LOCALIZACIÓN Subtitulo de IMÁGENES GENERALES DEL PROYECTO - Se define como label en el formulario
    teritorio_habitat = StringProperty()
    linea_intevencion = StringProperty()
    localidad = StringProperty() # colocar las 20 localidades
    upz = StringProperty()
    barrio = StringProperty()
    observaciones_localizacion = StringProperty()
    #info_catastral - INFORMACIÓN CATASTRAL Titulo2 - Se define como label en el formulario
    vigencia_info_catastral = StringProperty() # se escribe el año
    barmanpre = StringProperty()
    chip = StringProperty()
    direccion = StringProperty()
    propietario = StringProperty()
    matricula_inmobiliaria = StringProperty()
    area_terreno_catastral = FloatProperty()
    area_construida = FloatProperty()
    altura_pisos_actuales = FloatProperty()
    destino_economico = StringProperty()  
    #VALORACIÓN SUELO Y CONSTRUCCIONES Titulo3 - Se define como label en el formulario
    vigencia_info_avreferencia = StringProperty() # se escribe el año
    total_terreno_valor = FloatProperty()
    m2_terreno_valor = FloatProperty()
    area_construida_valor = FloatProperty()
    m2_construido_valor  = FloatProperty()
    avaluo_catastral_total  = FloatProperty()
    avaluo_catastral_m2_valor = FloatProperty()
    m2_avaluoreferencia_valor = FloatProperty()
    avaluo_comercial_total = FloatProperty()
    m2_terreno_comercial_valor = FloatProperty()
    #areas - AREAS Subtitulo de INFORMACIÓN CATASTRAL - Se define como label en el formulario
    area_SIG = FloatProperty()
    area_bruta = FloatProperty()
    area_neta = FloatProperty()
    area_util = FloatProperty()
    observaciones_areas = StringProperty()
    #condiciones_fis_amb - CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO Titulo4 - Se define como label en el formulario
    #estructura_eco_ppal ESTRUCTURA ECOLOGICA PRINCIPAL Subtitulo de CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO - Se define como label
    estructura_ecologica_desc = StringProperty()        
    estructura_ecologica_valor = FloatProperty()
    areas_protegidas_desc = StringProperty()          
    areas_protegidas_valor = FloatProperty()
    parques_urbanos_desc = StringProperty()      
    parques_urbanos_valor = FloatProperty()
    corredores_ecologicos_desc = StringProperty()     
    corredores_ecologicos_valor = FloatProperty()
    rio_bogota_desc = StringProperty()       
    rio_bogota_valor = FloatProperty()
    otras_condiciones_fisicas_desc = StringProperty()
    otras_condiciones_fisicas_valor = FloatProperty() 
    #afectacion_riesgo - AFECTACION POR RIESGO Subtitulo de CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO - Se define como label 
    aglomeraciones_desc = StringProperty()     
    aglomeraciones_valor = FloatProperty()
    deslizamientos_desc = StringProperty()      
    deslizamientos_valor = FloatProperty()
    incendios_desc = StringProperty()    
    incendios_valor = FloatProperty()
    inundaciones_desc = StringProperty()                      
    inundaciones_valor = FloatProperty()
    riesgos_tecnologicos_desc = StringProperty()          
    riesgos_tecnologicos_valor = FloatProperty()
    sismos_desc = StringProperty()      
    sismos_valor = FloatProperty()
    #afectacion_vias - AFECTACION POR VIAS O REDES Subtitulo de CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO - Se define como label 
    malla_vial_desc = StringProperty()        
    malla_vial_valor = FloatProperty()
    red_acueducto_desc = StringProperty()     
    red_acueducto_valor = FloatProperty()
    red_alcantarillado_desc = StringProperty()      
    red_alcantarillado_valor = FloatProperty()
    red_gas_desc = StringProperty()     
    red_gas_valor = FloatProperty()
    red_energia_desc = StringProperty()        
    red_energia_valor = FloatProperty()
    otra_afectacion_desc = StringProperty()
    otra_afectacion_valor = FloatProperty()
    #condiciones_industriales CONDICIONES INDUSTRIALES DE LA ZONA Subtitulo de CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO 
    zopra_desc = StringProperty()
    zopra_valor = FloatProperty()
    residuos_solidos_desc = StringProperty()    
    residuos_solidos_valor = FloatProperty()
    pasivos_ambientales_desc = StringProperty()    
    pasivos_ambientales_valor = FloatProperty()
    otras_condiciones_indust_desc = StringProperty()
    otras_condiciones_indust_valor = FloatProperty() 
    #calidad CALIDAD DE AIRE Y RUIDO Subtitulo de CONDICIONES FÍSICAS Y AMBIENTALES DEL PREDIO - Se define como label en el formulario
    calidad_aire_desc = StringProperty()   
    calidad_aire_valor = FloatProperty()
    ruido_desc = StringProperty()    
    ruido_valor = FloatProperty()
    #Final del formulario
    elaboro = StringProperty()
    reviso = StringProperty()
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
