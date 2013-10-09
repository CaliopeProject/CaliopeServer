# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class FichaUrbanistica(CaliopeEntityData):
    #Definición de datos para la ficha urbanística
    #modelacion_urbanistica - MODELACIÓN URBANÍSTICA - Tipo Label
    nombre_proyecto = StringProperty() # nombre proyecto  
    #localizacion = tipo adjunto
    #division_predial = tipo adjunto
    #modelacion_prouesta = tipo adjunto
    #datos_modelacion - DATOS BÁSICOS MODELACIÓN URBANÍSTICA - Tipo Label
    total_viviendas = FloatProperty() # C21-Sumatoria de los siguientes campos =SUMA(C22:C25) - se utiliza en otras fórmulas
    vip_50smmlv = FloatProperty() # VIP 50 SMMLV (50m2)
    vip_70_smmlv = FloatProperty() # VIP 70 SMMLV (57 a 60 m2)
    vis = FloatProperty()
    viv = FloatProperty()
    viviendas_hectarea_bruta = FloatProperty() # VIVIENDAS POR HECTAREA BRUTA =C21/(D49/10000) 
    viviendas_hectarea_neta = FloatProperty() # VIVIENDAS POR HECTAREA NETA =C21/(D55/10000)
    viviendas_hectarea_util = FloatProperty() # VIVIENDAS POR HECTAREA UTIL =C21/(D70/10000)
    total_habitantes = FloatProperty() # =C21*3,51
    habitantes_hectarea_bruta = FloatProperty() #HABITANTES POR HECTAREA BRUTA =(C21*3,51)/(D49/10000)
    habitantes_hectarea_neta = FloatProperty() # HABITANTES POR HECTAREA NETA =(C21*3,51)/(D55/10000)
    habitantes_hectarea_util = FloatProperty() # HABITANTES POR HECTAREA UTIL =(C21*3,51)/(D69/10000)
    # areas_construccionm2 - RESUMEN ÁREAS DE CONSTRUCCIÓN m2 - Tipo Label
    vivienda = FloatProperty() # VIVIENDA =D84-E34
    comercio_primer_piso = FloatProperty()
#    servicios IDU  = FloatProperty() # =D85 AREA TOTAL CONSTRUIDA IDU
    # espacio_publico - ESTANDARES DE ESPACIO PÚBLICO - Tipo Label
    parques_viviendam2 = FloatProperty() # Parques por vivienda m2 . =D60/C21
    equipamentos_vivienda = FloatProperty() #Equipamientos por vivienda =D65/C21
    # estacionamientos - Estacionamientos Tipo Label
    estacionamientos_vip = FloatProperty() # N° de estacionamientos VIP =(C21/6)+(C21/15)
    estacionamientos_comercio = FloatProperty() # N° de estacionamientos comercio =(E34*0,7)/250+(E34*0,7)/40)
    estacionamientos_servicios = FloatProperty() # N° de estacionamientos Servicios =((((D85*0,9)*0,95)/25)+(((D85*0,9)*0,05)/150))
    area_estacionamientos_vip = FloatProperty() # Área Estacionamientos VIP =C41*25
    area_estacionamientos_comercio  = FloatProperty() # Área Estacionamientos comercio =C42*25
    area_estacionamientos_servicios = FloatProperty() # Área Estacionamientos Servicios - float =C43*25
    #observaciones Observaciones - Tipo Label
    observaciones_datos_basicos = StringProperty()
    # cuadro_areas - CUADRO DE ÁREAS - Tipo Label
    area_bruta_valor = FloatProperty() #  ÁREA BRUTA - Subtítulo
    area_bruta_desc = StringProperty() # observaciones
    afectaciones_valor = FloatProperty() #AFECTACIONES ó reservas como está en plaza de la hoja, sumatoria de otros campos adicionados  (Avenida del Ferrocarril V-1, Avenida NQS V-1, Intersección Av. N.Q.S y, Av.Ferrocarril, Intersección Av. N.Q.S y Av.19)
#    afectaciones_desc StringProperty() # observaciones
    area_urbanizable_valor = FloatProperty()#AREA NETA URBANIZABLE
    area_urbanizable_desc = StringProperty() # observaciones
    area_edificabilidad_valor = FloatProperty()#AREA NETA BASE PARA CALCULO DE EDIFICABILIDAD
    area_edificabilidad_desc = StringProperty() # observaciones
    area_cesiones_valor = FloatProperty()#ÁREA NETA BASE CÁLCULO CESIONES 
    area_cesiones_desc = StringProperty() # observaciones    
    cesiones_publicas_valor = FloatProperty()#CESIONES PÚBLICAS
    cesiones_publicas_desc = StringProperty() # observaciones
    control_ambiental_valor = FloatProperty()#CONTROL AMBIENTAL
    control_ambiental_desc = StringProperty() # observaciones
    cesiones_parques1_valor = FloatProperty()#CESIONES PÚBLICAS PARQUES 
    cesiones_parques1_desc = StringProperty() # observaciones
    cesiones_parques2_valor = FloatProperty()#Cesiones Públicas para parques 
    cesiones_parques2_desc = StringProperty() # observaciones
    zmpa_valor = FloatProperty()#Z.M.P.A Valida como parque
    zmpa_desc = StringProperty() # observaciones
    area_parque_adicional_valor = FloatProperty()#Área de parque adicional por IC superior al básico
    area_parque_adicional_desc = StringProperty() # observaciones
    parque_adicional_valor = FloatProperty()#Parque adicional 
    parque_adicional_desc = StringProperty() # observaciones
    cesiones_publicas_eq_valor = FloatProperty()#CESIONES PÚBLICAS EQUIPAMIENTOS 8% 
    cesiones_publicas_eq_desc = StringProperty() # observaciones
    zona_verde_adicional_valor = FloatProperty()#ZONA VERDE ADICIONAL
    zona_verde_adicional_desc = StringProperty() # observaciones
    pago_sesionesm2_valor = FloatProperty()#PAGO COMPENSATORIO DE CESIONES m2
    pago_sesionesm2_desc = StringProperty() # observaciones
    vias_locales_valor = FloatProperty() #VIAS LOCALES
    vias_locales_desc = StringProperty() # observaciones
    area_util_valor = FloatProperty() #AREA UTIL
    area_util_desc = StringProperty() # observaciones
    vip_con_comercio_valor = FloatProperty() #RESIDENCIAL VIP CON COMERCIO EN LOS PRIMEROS PISOS
    vip_con_comercio_desc = StringProperty() # observaciones
    area_institucional_valor = FloatProperty()#INSTITUCIONAL
    area_institucional_desc = StringProperty()#observaciones
    #indice_ocupacion - INDICE DE OCUPACIÓN - Tipo Label
    area_vivienda_comercial_valor = FloatProperty() #AREA OCUPADA VIVIENDA CON COMERCIO PRIMER PISO
    area_vivienda_comercial_desc = StringProperty() # observaciones
    area_ocupada_comercio_valor = FloatProperty() #AREA OCUPADA COMERCIO (Comercio aislado) -   
    area_ocupada_comercio_desc = StringProperty() # observaciones
    area_ocupada_idu_valor = FloatProperty() #AREA OCUPADA SEDE IDU		
    area_ocupada_idu_desc = StringProperty() # observaciones
    area_total_ocupada_valor = FloatProperty() #AREA TOTAL OCUPADA	   
    area_total_ocupada_desc = StringProperty() # observaciones
    io_valor = FloatProperty() #IO 		
    io_desc = StringProperty() # observaciones
    #indice_construccion - INDICE DE CONSTRUCCIÓN - Tipo Label
    construida_comercial_valor = FloatProperty() #AREA CONSTRUIDA COMERCIAL (Comercio aislado)
    construida_comercial_desc = StringProperty()
    pisos_valor = FloatProperty() #NUMERO DE PISOS VIVIENDA
    pisos_desc= StringProperty() # observaciones
    total_construida_residencial_valor = FloatProperty() #AREA TOTAL CONSTRUIDA USO RESIDENCIAL (AO x N° DE PISOS + AC Comercio aislado)
    total_construida_residencial_desc = StringProperty() # observaciones
    total_construida_idu_valor = FloatProperty() #AREA TOTAL CONSTRUIDA IDU (AO x 20 PISOS)
    total_construida_idu_desc = StringProperty() # observaciones
    area_construida_ic_valor = FloatProperty() #AREA CONSTRUIDA PARA IC
    area_construida_ic_desc = StringProperty() # observaciones
    ic_valor = FloatProperty() #IC
    ic_desc = StringProperty() # observaciones
    #vivienda_areas_comerciales VIVIENDA Y ÁREAS COMERCIALES - Tipo Label
    # num_total_viviendas NUMERO TOTAL DE VIVIENDAS Tiene dos opciones cada una con campos de valor y descripción : por piso y total
    viviendas_piso_valor = FloatProperty() #POR PISO
    viviendas_piso_desc = StringProperty() # observaciones
    total_viviendas_valor = FloatProperty() #TOTAL
    total_viviendas_desc = StringProperty() # observaciones
    area_comercio_valor = FloatProperty() # AREA COMERCIO
    area_comercio_desc = StringProperty() # observaciones
    area_ventas_valor = FloatProperty() # AREA DE VENTAS (APROX.)
    area_ventas_desc = StringProperty() # observaciones
    #equipamento_comunal_privado EQUIPAMIENTO COMUNAL PRIVADO - Tipo Label
    #uso_residencial USO RESIDENCIAL - Tipo Label
    zonas_recreativas = FloatProperty() #zonas verdes recreativas 
    servicios_comunales = FloatProperty() #servicios comunales. 
    otros_equipamentos = FloatProperty() #OTROS
    observaciones_equipamentos = StringProperty() # observaciones
    #uso_institucional - USO INSTITUCIONAL - Tipo Label
    zonas_recreativas = FloatProperty() #zonas verdes recreativas 
    servicios_comunales = FloatProperty() #servicios comunales. 
    otros_usos_institucionales = FloatProperty() #OTROS
    observaciones_uso_institucional = StringProperty() # observaciones
    #grafico_areas GRÁFICO DE ÁREAS = tipo adjunto
    elaboro = StringProperty()
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
