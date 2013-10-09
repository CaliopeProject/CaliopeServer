# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.entities import (CaliopeEntityData, CaliopeEntity, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)

from cid.core.entities.base_models.versioned_node import VersionedNode


class ActaReciboPredios(VersionedNode):
    #Definición de datos para el ACTA DE RECIBO DE PREDIOS
    fecha_acta = DateTimeProperty() # FECHA definido en el formulario como "datepicker"
    hora_acta = StringProperty() # HORA:
    #comentario1 - Presentes con el objeto de hacer  entrega real y efectiva  del inmueble,  las siguientes personas : - Tipo Label
    nombre_entrega1 = StringProperty() # NOMBRE - Tiene 4 columnas pero pueden ser más o menos columnas. Se definen en las siguientes líneas
    nombre_entrega2 = StringProperty()
    nombre_entrega3 = StringProperty()
    nombre_entrega4 = StringProperty()
    identificacion_entrega1 = StringProperty() # IDENTIFICACIÓN - Tiene 4 columnas pero pueden ser más o menos columnas. Se definen en las siguientes líneas
    identificacion_entrega2 = StringProperty()
    identificacion_entrega3 = StringProperty()
    identificacion_entrega4 = StringProperty()
    cargo_calidad_entrega1 = StringProperty() # CARGO / CALIDAD - Tiene 4 columnas pero pueden ser más o menos columnas. Se definen en las siguientes líneas
    cargo_calidad_entrega2 = StringProperty() 
    cargo_calidad_entrega3 = StringProperty() 
    cargo_calidad_entrega4 = StringProperty() 
    # id_predio - 1. IDENTIFICACIÓN DEL PREDIO - Tipo Label
    nombre_predio = StringProperty() # NOMBRE
    nomenclatura_predio = StringProperty() # NOMENCLATURA
    area_predio = StringProperty() # ÁREA
    cedula_catastral = IntegerProperty() # CEDULA CATASTRAL
    folio_matricula = StringProperty() # FOLIO DE MATRICULA
    localidad_predio = StringProperty() # LOCALIDAD
    # coordenadas_alinderacion - COORDENADAS DE ALINDERA CION: - Adjunto
    # construcciones 2. CONSTRUCCIONES: - Tipo Label
    # servicios_instalados 3. SERVICIOS INSTALADOS - Tipo Label
    # servicio - Servicio - Tipo Label con Opciones: Acueducto y Alcantarillado, Energía, Teléfono
    # Contador para: contador_acueducto, contador_energia, contador_telefono
    contador_acueducto = StringProperty()
    contador_energia = StringProperty()
    contador_telefono = StringProperty()
    # Lectura actual - Tipo Label con opciones: lectura_acueducto, lectura_energia, lectura_telefono
    lectura_acueducto = StringProperty()
    lectura_energia = StringProperty()
    lectura_telefono = StringProperty()
    # comentario2: Determinado el inmueble y constatados  los correspondientes linderos, EL (LOS) VENDEDOR (ES)  hace entrega real, material y efectiva del inmueble en mención, libre y limpio de ocupaciones de toda índole (personas, semovientes, maquinarias, materiales, etc.), a buen recibo y satisfacción por parte del COMPRADOR.   Clausurada la anterior diligencia, se da por terminada  y se recibe oficialmente el inmueble a favor de METROVIVIENDA
    observaciones_acta = StringProperty() # Observaciones
    vendedor = StringProperty()# Vendedor (es una firma)
    cc_vendedor = StringProperty() # cc_vendedor - CC
    comprador = StringProperty() # Por el Comprador (es una firma)
    cc_comprador = StringProperty() # cc_comprador - CC
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
