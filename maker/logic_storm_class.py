#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2011 Jonathan Ferreyra <jalejandroferreyra@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os, os.path
from maker import pathtools

class LogicStormClass():

    def __init__(self):
        self.pathPlantilla = pathtools.convertPath(
                pathtools.getPathProgramFolder() + '/plantillas/plantilla_clase_storm.py')
        self.__imports = ''
        self.__atributos_clase = ''
        self.__atributos_init = ''
        self.__parametos = ''
        self.__sql_table = ''

        self.tiene_referencia = False

        # segun el tipo correspondiente de Storm, se obtiene el tipo de la bd
        self.database_types = {
        'SQLite':{
            'Int':'INTEGER',
            'Unicode':'VARCHAR',
            'Bool':'INT',
            'Float':'FLOAT',
            'Decimal':'VARCHAR',
            'DateTime':'VARCHAR',
            'RawStr':'BLOB',
            'Pickle':'BLOB',
            'Date':'VARCHAR',
            'Time':'VARCHAR',
            'TimeDelta':'VARCHAR',
            'List':'VARCHAR'
        },
        'MySQL':{
            'Int':'INT',
            'Unicode':'VARCHAR',
            'Bool':'TINYINT(1)',
            'Float':'FLOAT',
            'Decimal':'DECIMAL',
            'DateTime':'DATETIME',
            'RawStr':'BLOB,BYNARY',
            'Pickle':'BLOB,BYNARY',
            'Date':'DATE',
            'Time':'TIME',
            'TimeDelta':'TEXT'
        },
        'PostgreSQL':{
            'Int':'INT',
            'Unicode':'VARCHAR',
            'Bool':'BOOL',
            'Float':'FLOAT',
            'Decimal':'DECIMAL',
            'DateTime':'TIMESTAMP',
            'RawStr':'BYTEA',
            'Pickle':'BYTEA',
            'Date':'DATE',
            'Time':'TIME',
            'TimeDelta':'INTERVAL',
            'List':'ARRAY[]'
        }
        }

    def generarClase(self, destino, nombre_clase, atributos, database = 'SQLite', package = False):
        """
        Genera una clase Storm con las condiciones especificadas.

        destino = ubicacion fisica donde se generara el archivo de la clase
        nombre_clase = nombre que tendra la clase generada
        atributos = diccionario que contendra las condiciones que deben cumplir cada atributo

        formato del diccionario (ejemplo) :
        atributos = {
        {'cruzada': '', 'widget': u'QLineEdit', 'atributo': u'dni', 'default': u'', 'primario': 'True', 'referencia': '', 'not_null': 'True', 'storm_type': u'Unicode'}
        {'cruzada': '', 'widget': u'QLineEdit', 'atributo': u'nombre', 'default': u'', 'primario': 'False', 'referencia': '', 'not_null': 'True', 'storm_type': u'Unicode'}
        {'cruzada': 'False', 'widget': u'QLineEdit', 'atributo': u'cuenta', 'default': u'', 'primario': 'False', 'referencia': u'Cuenta', 'not_null': 'True', 'storm_type': u'Unicode'}
        }
        """

        self.__generarImports(atributos)
        self.__generarAtributosSimples(atributos)
        self.__generarReferencias(atributos)
        self.__generarAtributosInit(atributos)
        self.__generarParametrosInit(atributos)
        #self.__generarSQLTable(database, atributos)


        clase = self.obtenerContenidoPlantilla()
        # reemplaza el nombre de la clase
        nombre_clase = self.__normalizarCampo( nombre_clase.capitalize() )
        clase = clase.replace('$nombre_clase$', nombre_clase)
        clase = clase.replace('$nombre_objeto$', nombre_clase)

        if self.__imports != '':
            clase = clase.replace('$imports$', self.__imports)
        else:
            clase = clase.replace('$imports$', '')

        if self.__atributos_clase != '' :
            clase = clase.replace('$atributos_clase$', self.__atributos_clase)
        else:
            clase = clase.replace('$atributos_clase$', '')

        if self.__parametos != '' :
            clase = clase.replace('$parametros$', self.__parametos)
        else:
            clase = clase.replace('$parametros$', '')

        if self.__atributos_init != '' :
            clase = clase.replace('$atributos_init$', self.__atributos_init)
        else:
            clase = clase.replace('$atributos_init$', '')

        if self.__sql_table != '' :
            clase = clase.replace('$sql_table$', self.__sql_table)
        else:
            clase = clase.replace('$sql_table$', "''''''")

        if self.tiene_referencia :
            clase = clase.replace('$herencia$', "Storm")
        else:
            clase = clase.replace('$herencia$', "object")

        if package == True :
            self.generarPaquete(nombre_clase, destino, clase)
        else:
            self.guardarClase(destino, clase)

        return True

    def __generarAtributosInit(self, atributos):
        """
        A partir de los datos de los atributos verifica si es necesario
        generar la cadena de atributos para el metodo __init__().
        """
        for index in range(len(atributos)):
            atributo = atributos[index]

            atributo_init = (' ' * 8) + 'self.%s = %s\n' % (atributo['atributo'].lower(),atributo['atributo'].lower())
            self.__atributos_init += atributo_init

    def __generarParametrosInit(self, atributos):
        """
        A partir de los datos de los atributos verifica si es necesario
        generar la cadena de parametros para el metodo __init__().
        """
        for index in range(len(atributos)):
            atributo = atributos[index]

            un_parametro = ' %s,' % atributo['atributo'].lower()
            self.__parametos += un_parametro
        if len(atributos) > 0 :
            self.__parametos = ', ' + self.__parametos[:-1]

    def __generarImports(self, atributos):
        """
        A partir de los datos de los atributos verifica si es necesario
        generar la cadena de imports de clases a las que se referencia.
        """
        for index in range(len(atributos)):
            atributo = atributos[index]
            if atributo['referencia'] != '':
                if atributo['cruzada'] == 'False':
                    un_import = 'from %s import %s\n' % (atributo['referencia'].lower(),atributo['referencia'].capitalize())
                    self.__imports += un_import

    def __generarReferencias(self, atributos):
        """
        A partir de los datos de los atributos verifica si es necesario
        generar la cadena de atributos de clase que contienen referencias.
        """
        un_atributo_clase = ''

        for index in range(len(atributos)):
            atributo = atributos[index]
            if atributo['referencia'] != '':
                un_atributo_clase = '    %s_id = Int()\n    %s = Reference(%s_id, %s.ide)\n' % \
                        (atributo['atributo'],
                         atributo['atributo'],
                         atributo['atributo'],
                         atributo['referencia'].capitalize())
                # en caso de ser una referencia cruzada
                if atributo['cruzada'] == 'True':
                    un_atributo_clase = un_atributo_clase.replace(
                        atributo['referencia'].capitalize() + '.ide',
                        '"' + atributo['referencia'].capitalize() + '.ide' + '"'
                    )
                # en caso de ser primario
                if atributo['primario'] == 'True':
                        un_atributo_clase = un_atributo_clase.replace('()','(primary = True)')

                self.tiene_referencia = True
            self.__atributos_clase += un_atributo_clase

    def __generarAtributosSimples(self, atributos):
        """
        A partir de los datos de los atributos verifica si es necesario
        generar la cadena de atributos de clase que NO contienen referencias.
        """
        self.__atributos_clase += '    ide = Int(primary = True)\n'
        un_atributo_clase = ''
        valor, texto = None, ''
        for index in range(len(atributos)):
            atributo = atributos[index]
            if atributo['referencia'] == '':
                un_atributo_clase = '    %s = %s()\n' % (atributo['atributo'],atributo['storm_type'])

                # si es primario
                if (atributo['primario'] == 'True'):
                    un_atributo_clase = un_atributo_clase.replace('()','(primary = True)')
                # no es primario y es not_null y tiene valor_por_defecto
                if (atributo['primario'] == 'False') and (atributo['not_null'] == 'True') and (atributo['default'] != ''):
                    if atributo['storm_type'] == 'Int' :
                        valor = int(atributo['default'])
                        texto = '(allow_none = False, value_factory = %d)' % valor
                    elif atributo['storm_type'] == 'Unicode' :
                        valor = int(atributo['default'])
                        texto = '(allow_none = False, value_factory = %s)' % valor

                    un_atributo_clase = un_atributo_clase.replace('()',texto)

                # no es primario y es not_null y no tiene valor_por_defecto
                if (atributo['primario'] == 'False') and (atributo['not_null'] == 'True') and (atributo['default'] == ''):
                    un_atributo_clase = un_atributo_clase.replace('()','(allow_none = True)')

                # no es primario y no es not_null y tiene valor_por_defecto
                if (atributo['primario'] == 'False') and (atributo['not_null'] == 'False') and (atributo['default'] != ''):
                    if atributo['storm_type'] == 'Int' :
                        valor = int(atributo['default'])
                        texto = '(value_factory = %d)' % valor
                    elif atributo['storm_type'] == 'Unicode' :
                        valor = int(atributo['default'])
                        texto = '(value_factory = %s)' % valor

                    un_atributo_clase = un_atributo_clase.replace('()',texto)

                self.__atributos_clase += un_atributo_clase

    def __generarSQLTable(self, database, atributos):
        """
        A partir de los datos de los atributos generar la cadena de atributos
        para la tabla de la base de datos
        """

        campos  = ''

        for index in range(len(atributos)):
            atributo = atributos[index]

            un_campo = (' ' * 8) + atributo['atributo'].lower() + ' ' + self.database_types[database][atributo['storm_type']]

            if atributo['primario'] == 'True' :
                un_campo += " PRIMARY KEY"
            else:
                if atributo['not_null'] == 'True' :
                    un_campo += " NOT NULL"

            campos += un_campo + ",\n"
        campos = campos[:-2]

        self.__sql_table = """'''
        (
%s
        )'''""" % campos

    def generarPaquete(self, nombre_clase, destino, clase):

        # obtiene el directorio de esta ruta
        directory = self.convertPath( os.path.dirname(destino[:-3]) + '/' )
        # print directory
        generate_in = self.convertPath(directory + nombre_clase.lower() + '/' )
        # print generate_in
        # crea la carpeta para esta clase
        if not os.path.exists(generate_in):
            os.mkdir( generate_in )
        self.guardarClase(generate_in + '__init__.py', clase)

    def obtenerContenidoPlantilla(self):
        import os
        plantilla = open(self.pathPlantilla,'r')
        contenido = unicode(plantilla.read(),'utf-8')
        plantilla.close()
        return contenido

    def guardarClase(self, destino, contenido):
        plantilla = open(destino,'w')
        plantilla.write(contenido.encode('utf-8'))
        plantilla.close()

    def __normalizarCampo(self, campo):
        """
        Verifica que el campo no contenga espacios.
        """
        while campo.find('  ') != -1 :
            campo.replace('  ',' ')
        campo = campo.replace(' ','_')
        return campo

    def convertPath(self,path):
        """Convierte el path a el específico de la plataforma (separador)"""
        import os
        if os.name == 'posix':
            return "/"+apply( os.path.join, tuple(path.split('/')))
        elif os.name == 'nt':
            return apply( os.path.join, tuple(path.split('/')))

if __name__ == "__main__":
    p = LogicStormClass()
    pass

