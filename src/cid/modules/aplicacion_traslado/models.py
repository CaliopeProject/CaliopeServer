
#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, CaliopeJSONProperty)

from cid.modules.projects.models import ProjectEntity


class AplicacionTraslado(CaliopeEntity):
    pass


class AplicacionTrasladoData(CaliopeEntityData):
    __entity_data__ = AplicacionTraslado

    #Definición de datos para el FORMULARIO APLICACIÓN DE TRASLADO
  
    #decreto_327 - TRASLADO DEC 327 / 04 - Tipo Label
    radicado = StringProperty() #Radicado  
    solicitante = StringProperty() #Solicitante  
    valor_predio = FloatProperty() #Valor Predio - Fórmula: =+F12
    m2 = FloatProperty() #Metros Cuadrados - Fórmula: =+F14
    valor_catastral_m2 = FloatProperty() #Valor Catastral M2 - Fórmula: =+F15  
    area_util_proyecto = FloatProperty() #Area Util Proyecto  
    area_vis = FloatProperty() #Area VIS  
    #vis - VIS - Tipo Label
    #a1_label A1 - área equivalente 
    a1_valor = FloatProperty() # A1 - Fórmula: =+C16*(D21/D22)
    #a2_label A2 
    a2_valor = FloatProperty() # A2 - Fórmula: =+C16
    # v1_label V1 
    v1_valor = FloatProperty() # V1 - Fórmula: =+C13
    #v2_label V2 
    v2_valor = FloatProperty() # V2 - Fórmula: =+F23
    area_etapa_desc = StringProperty() # Ej: Area Etapa III Neuvo Usme- La Esperanza 
    area_etapa_valor = FloatProperty() # Valor - Fórmula: =+F22
    avaluo_comercial = FloatProperty() # Avaluo comercial Predio - trae valor de otro archivo.
    valor_a_pagar = FloatProperty() # Valor a Pagar - Fórmula: =+D24*D19
    # valores_catastrales - VALORES CATASTRALES - Tipo Label
    # valor_catastral_predio VALOR CASTASTRAL PREDIO - Tipo Label
    year1_desc = StringProperty() # año (Comentario: Digitar avalúo Catastral)
    year1_valor = FloatProperty()
    year2_desc = StringProperty() # año (Comentario: Digitar avalúo Catastral)
    year2_valor = FloatProperty()
    total_avaluos = FloatProperty() # sin título: suma de los valores catastrales anteriores dividido entre 2
    area1_m2 = FloatProperty() # AREA M2 - (comentario: Digitar área del boletin catastral)
    valor_catastral1_m2 = FloatProperty() # VALOR CATASTRAL M2
    year3_desc = StringProperty() # año
    year3_valor = FloatProperty()
    year4_desc = StringProperty() # año
    year4_valor = FloatProperty()
    promedio = FloatProperty() # PROMEDIO
    area2_m2 = FloatProperty()
    valor_catastral2_m2 = FloatProperty() # VALOR CATASTRAL M2
    elaboro = StringProperty() # Elaborado Por: 
    reviso = StringProperty() # Revisados por: 
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
