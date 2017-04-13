#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
wnd_main_atnsim

janela principal do simulador

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/apr  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/04"

# < import >---------------------------------------------------------------------------------------

# python library
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtXml
from string import Template

import os
import dlg_traf_ui as dtrf_ui

# < class CDlgTraf >-------------------------------------------------------------------------------

class CDlgTraf(QtGui.QDialog, dtrf_ui.Ui_dlg_trf):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_ptracks_dir=os.path.join(os.environ["HOME"], 'ptracks')):
        # init super class
        QtGui.QDialog.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        self.qtw_trf.setColumnCount(13)
        self.qtw_trf.setHorizontalHeaderLabels(
            ["Node", "Latitude", "Longitude", "Type of Acft", "SSR", "Callsign", "Departure", "Arrival", "Heading", "Speed",
             "Altitude", "Procedure", "ID"])
        self.qtw_trf.setColumnHidden(12, True)

        self.qtw_trf.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # do signal/slot connections
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_create.clicked.connect(self.on_create)
        self.ptracks_dir = f_ptracks_dir

        self.scenario_filename = ""

        self.designador_list = self.load_performance()
        self.proc_list = self.load_tables()


    # ---------------------------------------------------------------------------------------------
    def load_xml_file(self, f_xml_filename, f_element, f_attribute):
        """
        Le um arquivo XML (f_xml_filename) e retorna a lista dos valores dos atributos (f_attribute)
        de cada no na árvore XML (f_element)

        :param f_xml_filename: o arquivo XML a ser lido
        :param f_element: o nome do elemento no nó da árvore XML
        :param f_attribute: o atributo do elemento
        :return: uma lista com os valores do atributo do elemento.
        """

        # cria o QFile para o arquivo XML
        l_data_file = QtCore.QFile(f_xml_filename)
        assert l_data_file is not None

        # abre o arquivo XML
        l_data_file.open(QtCore.QIODevice.ReadOnly)

        # cria o documento XML
        l_xdoc_aer = QtXml.QDomDocument("tabelas")
        assert l_xdoc_aer is not None

        l_xdoc_aer.setContent(l_data_file)

        # fecha o arquivo
        l_data_file.close()

        # obtém o elemento raíz do documento
        l_elem_root = l_xdoc_aer.documentElement()
        assert l_elem_root is not None

        # cria uma lista com os elementos
        l_node_list = l_elem_root.elementsByTagName(f_element)
        l_result_list = []

        for li_ndx in xrange(l_node_list.length()):
            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            # read identification if available
            if l_element.hasAttribute(f_attribute):
                l_value = l_element.attribute(f_attribute)
                if f_element == 'performance':
                    l_result_list.append(l_value)
                else:
                    l_proc = f_attribute [ 1: ].upper() + l_value
                    l_result_list.append(l_proc)

        return l_result_list


    # ---------------------------------------------------------------------------------------------
    def load_performance(self):
        """
        Le o arquivo tabPrf.xml para carregar os designadores das aeronaves cadastradas.

        :return: uma lista com os designadores das performances de aeronaves cadastradas no
        sistema ptracks.
        """

        # Monta o nome do arquivo de performance de aeronaves do ptracks
        l_xml_filename = os.path.join(self.ptracks_dir, 'data/tabs/tabPrf.xml')

        return self.load_xml_file(l_xml_filename, 'performance', 'nPrf')


    # ---------------------------------------------------------------------------------------------
    def filter_XML_files(self, f_filenames):
        """
        Faz a leitura de uma lista de arquivos e seleciona somente os arquivos XML.
        do diretório

        :param f_filenames: uma lista de arquivos
        :return: lista com os nomes dos arquivos XML
        """

        l_file_extensions = ['XML']
        l_result = []

        l_dir = os.path.join(self.ptracks_dir, 'data/proc/')

        # loop through all the file and folders
        for l_filename in f_filenames:
            # Check whether the current object is a file or not
            if os.path.isfile(os.path.join(l_dir, l_filename)):
                l_filename_text, l_filename_ext= os.path.splitext(l_filename)
                l_filename_ext= l_filename_ext[1:].upper()
                # Check whether the current object is a XML file
                if l_filename_ext in l_file_extensions:
                    l_result.append(l_filename)

        l_result.sort()

        return l_result


    # ---------------------------------------------------------------------------------------------
    def load_tables(self):
        """


        :return:
        """

        l_element_nodes = {'Ape': 'apxPerdida', 'Apx': 'aproximacao', 'Esp': 'espera', 'ILS': 'ils', 'Sub': 'subida',
                         'Trj': 'trajetoria'}

        # List all the files and folders in the current directory
        l_dir = os.path.join(self.ptracks_dir, 'data/proc/')
        l_xml_files = self.filter_XML_files(os.listdir(l_dir))

        l_result = []

        for l_xml_file in l_xml_files:
            l_element = l_element_nodes [ l_xml_file [ 3:6 ] ]
            l_attribute = 'n' + l_xml_file [ 3:6 ]
            l_xml_filename = os.path.join(l_dir, l_xml_file)
            l_list = self.load_xml_file(l_xml_filename, l_element, l_attribute)

            if len(l_list) > 0:
                l_result.extend ( l_list )

        l_result.sort()

        return l_result


    # ---------------------------------------------------------------------------------------------
    def set_title(self, f_title):
        """
        Define o título da janela de diálogo com o nome do cenário de simulação (f_title)

        :param f_title: o nome do cenário de simulação.
        :return:
        """
        self.scenario_filename = f_title
        self.setWindowTitle("Scenario Aircrafts: " + f_title)


    # ---------------------------------------------------------------------------------------------
    def on_cancel(self):
        """
        Método chamado quando o usuário decide cancelar a atividade. Fecha a janela de diálogo.
        Estabelece o código de retorno como rejected.

        :return:
        """
        self.done(QtGui.QDialog.Rejected)


    # ---------------------------------------------------------------------------------------------
    def on_create(self):
        """
        Método chamado quando o usuário decide criar o arquivo de tráfegos. Fecha a janela de diálogo.
        Estabelece o código de retorno como accepted.

        :return:
        """
        self.done(QtGui.QDialog.Accepted)


    # ---------------------------------------------------------------------------------------------
    def populate_table(self, f_table):
        """
        Alimenta a tabela da janela de diálogo com as informações do tráfego (f_table) retiradas do
        arquivo do cenáio de simulação

        :param f_table: uma lista com os dados necessários para criar um tráfego para o ptracks
        :return:
        """

        # para todas as linhas da tabela...
        self.qtw_trf.setRowCount(0);

        # para todas as linhas da tabela...
        for l_row in xrange(0, len(f_table)):

            # cria nova linha na tabela
            self.qtw_trf.insertRow(l_row)

            # node name
            self.qtw_trf.setItem(l_row, 0, QtGui.QTableWidgetItem( f_table[l_row]['node'] ))

            # cria doubleSpinBox para latitude
            self.lat = QtGui.QDoubleSpinBox()
            self.lat.setDecimals(4)
            self.lat.setRange(-90., 90.)
            self.lat.setValue(f_table[l_row]['latitude'])
            self.lat.valueChanged.connect(self.valuechange)

            # latitude
            self.qtw_trf.setCellWidget(l_row, 1, self.lat)

            # cria doubleSpinBox para longitude
            self.lng = QtGui.QDoubleSpinBox()
            self.lng.setDecimals(4)
            self.lng.setRange(-180., 180.)
            self.lng.setValue(f_table[l_row]['longitude'])
            self.lng.valueChanged.connect(self.valuechange)

            # longitude
            self.qtw_trf.setCellWidget(l_row, 2, self.lng)

            # cria combo para designador
            self.cb = QtGui.QComboBox()
            self.cb.addItems(self.designador_list)
            self.cb.setCurrentIndex(self.cb.findText(f_table[l_row]['designador']))
            self.cb.currentIndexChanged.connect(self.selectionchange)

            # designador
            self.qtw_trf.setCellWidget(l_row, 3, self.cb)

            # ssr
            self.qtw_trf.setItem(l_row, 4, QtGui.QTableWidgetItem(f_table[l_row]['ssr']))

            # indicativo
            self.qtw_trf.setItem(l_row, 5, QtGui.QTableWidgetItem(f_table[l_row]['indicativo']))
            # origem
            self.qtw_trf.setItem(l_row, 6, QtGui.QTableWidgetItem(f_table[l_row]['origem']))
            # destino
            self.qtw_trf.setItem(l_row, 7, QtGui.QTableWidgetItem(f_table[l_row]['destino']))

            # cria spinBox para proa
            self.proa = QtGui.QSpinBox()
            self.proa.setRange(0, 360)
            self.proa.setValue(f_table[l_row]['proa'])
            self.proa.valueChanged.connect(self.valuechange)

            # proa
            self.qtw_trf.setCellWidget(l_row, 8, self.proa)

            # cria spinBox para velocidade
            self.velocidade = QtGui.QSpinBox()
            self.velocidade.setRange(0, 600)
            self.velocidade.setValue(f_table[l_row]['velocidade'])
            self.velocidade.valueChanged.connect(self.valuechange)

            # velocidade
            self.qtw_trf.setCellWidget(l_row, 9, self.velocidade)

            # cria spinBox para altitude
            self.altitude = QtGui.QSpinBox()
            self.altitude.setRange(0, 40000)
            self.altitude.setValue(f_table[l_row]['altitude'])
            self.altitude.valueChanged.connect(self.valuechange)

            # altitude
            self.qtw_trf.setCellWidget(l_row, 10, self.altitude)

            # cria combo para procedimento
            self.prc = QtGui.QComboBox()
            self.prc.addItems(self.proc_list)
            self.prc.setCurrentIndex(self.prc.findText(f_table[l_row]['procedimento']))
            self.prc.currentIndexChanged.connect(self.selectionchange)

            # procedimento
            self.qtw_trf.setCellWidget(l_row, 11, self.prc)

            # traffic number
            self.qtw_trf.setItem(l_row, 12, QtGui.QTableWidgetItem(f_table[l_row]['id']))

        # redefine o tamanho da QTableWidget
        self.qtw_trf.resizeRowsToContents()
        self.qtw_trf.resizeColumnsToContents()

        # Define o novo tamanho da janela de diálogo de tráfegos
        width = self.qtw_trf.horizontalHeader().length() + \
                ( self.qtw_trf.horizontalHeader().sizeHint().width() *  3 / 4 )
        self.setFixedWidth ( width + 10 )


    # ---------------------------------------------------------------------------------------------
    def selectionchange(self,i):
        """
        Método chamado quando um item é selecionado.

        :param i: o indice do item selecionado.
        :return:
        """
        sender = self.sender()

        print "Items in the list are :"

        for count in xrange(sender.count()):
           print "[%s]" % sender.itemText(count)

        print "Current index", i, "selection changed ", sender.currentText()


    # ---------------------------------------------------------------------------------------------
    def valuechange(self,i):
        """
        Método chamado quando o valor de um item é alterado.

        :param i: o índice do item alterado.
        :return:
        """

        sender = self.sender()

        print "Minimum in the list is :", sender.minimum()
        print "Maximum in the list is :", sender.maximum()
        print "Value changed ", sender.value()


    # ---------------------------------------------------------------------------------------------
    def get_data(self):
        """
        Cria uma lista com os dados das aeronaves

        :return:
        """

        # open template file (aeronaves)
        l_file_in = open("templates/anv.xml.in")

        # read it
        l_src = Template(l_file_in.read())

        l_result = []

        # para todas as linhas da tabela...
        for l_row in xrange(0, self.qtw_trf.rowCount()):
            # node
            l_node = self.qtw_trf.item(l_row, 12).text().toUtf8()

            # latitude
            l_latitude = self.qtw_trf.cellWidget(l_row, 1).value()
            # longitude
            l_longitude = self.qtw_trf.cellWidget(l_row, 2).value()
            # designador
            l_designador = self.qtw_trf.cellWidget(l_row, 3).currentText().toUtf8()
            # ssr
            l_ssr = self.qtw_trf.item(l_row, 4).text().toUtf8()
            # indicativo
            l_indicativo = self.qtw_trf.item(l_row, 5).text().toUtf8()
            # origem
            l_origem = self.qtw_trf.item(l_row, 6).text().toUtf8()
            # destino
            l_destino = self.qtw_trf.item(l_row, 7).text().toUtf8()
            # proa
            l_proa = self.qtw_trf.cellWidget(l_row, 8).value()
            # velocidade
            l_velocidade = self.qtw_trf.cellWidget(l_row, 9).value()
            # altitude
            l_altitude = self.qtw_trf.cellWidget(l_row, 10).value()
            # procedimento
            l_procedimento = self.qtw_trf.cellWidget(l_row, 11).currentText().toUtf8()

            l_data = {"ntrf": l_node, "latitude": l_latitude, "longitude": l_longitude,
                    "designador": l_designador, "ssr": l_ssr, "indicativo": l_indicativo,
                    "origem": l_origem, "destino": l_destino, "proa": l_proa,
                    "velocidade": l_velocidade, "altitude": l_altitude,
                    "procedimento": l_procedimento}

            # do the substitution
            l_result.append(l_src.substitute(l_data))

        return l_result


# < the end>---------------------------------------------------------------------------------------
