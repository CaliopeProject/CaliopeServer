# -*- encoding: utf-8 -*-

#Caliope Entities
from cid.core.forms import FormNode

from cid.core.entities import (VersionedNode, RelationshipFrom,
                               CaliopeUser, One, NotConnected, DateTimeProperty,
                               StringProperty, IntegerProperty, FloatProperty, CaliopeJSONProperty)



class DerechoPreferencia(FormNode):
    #Definición de datos para el Derecho de Preferencia-Datos Básicos

    #anexar_informacion RELACIÓN DE LA INFORMACIÓN QUE DEBE ANEXARSE - Tipo Label
    # oferta - Formato de Oferta de predio a Metrovivienda por concepto de derecho de preferencia (diligenciado) - Tipo Adjunto
    # poder_apoderado - En caso de actuar mediante apoderado, se requiere el poder respectivo debidamente autenticado.  - Tipo Adjunto 
    # adquisicion_predio - Copia del documento que certifique la adquisición del predio (escritura, sentencia judicial, otros)  - Tipo Adjunto
    # cc_propietario - Copia de la cédula de ciudadanía del propietario  - Tipo Adjunto
    # representacion_legal - En caso de persona jurídica, acreditar existencia y representación legal mediante documento idóneo, con vigencia de expedición no mayor a un mes.  - Tipo Adjunto
    # intencion_compra - Información  que acredite o certifique la intención de compra del interesado (valor de la oferta, condiciones de pago, datos de contacto del posible comprador y cualquier otra que considere necesaria.  - Tipo Adjunto
    #informacion_propietario INFORMACIÓN DEL PROPIETARIO - Tipo Label
#    relacion_predio = ListProperty() #Relación con el predio - opciones: Propietario, Apoderado
#    tipo_propietario = ListProperty() #Tipo de propietario de suelo - opciones: Persona Natural, Persona Jurídica
    propietario_actual = StringProperty() # Nombre entidad o persona propietaria del predio
    doc_propietario = StringProperty() # NIT o CC
    direccion_notifiacion = StringProperty() # Dirección para la notificación
    telefono = StringProperty() # Teléfono y celular
    representante_legal = StringProperty() # En caso de persona jurídica, nombre representante legal
    cc_representante = StringProperty() # CC representante legal
    #datos_apoderado - Si es apoderado, adicionalmente solicitamos: - Tipo Label
    nombre_apoderado = StringProperty() # Nombre del apoderado:
    cc_apoderado = StringProperty() # C.C.:
    direccion_apoderado = StringProperty() # Dirección de notificación:
    telefono_apoderado = StringProperty() # Teléfono:
    celular_apoderado = StringProperty() # No. De celular:
    # informacion_predio INFORMACIÓN GENERAL DEL PREDIO OFERTADO - Tipo Label
    nombre_predio = StringProperty() # Nombre del predio (si existe)
    direccion_predio = StringProperty() # Dirección
    ubicacion_predio = StringProperty() # Ubicación del predio (vereda)
    telefono_predio = StringProperty() # Teléfono
    matricula_inmobiliaria = StringProperty() # Número matricula inmobiliaria
    area_predio = FloatProperty()# Área (extensión) del predio
#    tramite_en_curso = StringListProperty() # ¿Se encuentra en curso algún trámite o proceso de carácter jurídico sobre su predio? Opciones SI, NO
    # informacion_comprador - Información del (los) posible (s) comprador (es) - Tipo Label
    nombre_comprador = StringProperty() # Nombre:
    cc_comprador = StringProperty() # C.C.:
    direccion_comprador = StringProperty() # Dirección: 
    telefono_comprador = StringProperty() # Teléfono: 
    # firmas - Firma(s) del(los) ofertante(s) o su(s) representante(s) - no definidas en el formulario.
    # fecha_creacion = DateProperty() # Generacion Automatica pero no se ha definido en el formulario
#    estado_ficha = StringListProperty() # Opciones: Rechazado, Aprobado, Revisado, Anulado, Completado
