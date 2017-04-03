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

import wnd_traf_ui as wtrf_ui

# < class CWndMainATNSim >-------------------------------------------------------------------------

class CWndTraf(QtGui.QWidget, wtrf_ui.Ui_frm_trf):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None):
        # init super class
        QtGui.QWidget.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        self.qtw_trf.setColumnCount(12)
        self.qtw_trf.setHorizontalHeaderLabels(
            ["Node", "Latitude", "Longitude", "Designador", "SSR", "Indicativo", "Origem", "Destino", "Proa", "Velocidade",
             "Altitude", "Procedimento"])

        # do signal/slot connections
        self.btn_cancel.clicked.connect(self.hide)
        self.btn_create.clicked.connect(self.cbk_create_aircrafts)

        self.traf_filename = ""

    # ---------------------------------------------------------------------------------------------
    def selectionchange(self,i):
        print "Items in the list are :"

        for count in xrange(self.cb.count()):
           print self.cb.itemText(count)

        print "Current index", i, "selection changed ", self.cb.currentText()


    # ---------------------------------------------------------------------------------------------
    def valuechange(self,i):
        print "Items in the list are :"

        for count in xrange(self.cb.count()):
           print self.cb.itemText(count)

        print "Current index", i, "selection changed ", self.cb.currentText()


    # ---------------------------------------------------------------------------------------------
    def create_ptracks_traf(self, f_traf_filename):
        """
        Cria o arquivo de tráfego para o exercício do ptracks.
        :param f_traf_filename:  o nome do arquivo de tráfegos do ptracks
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
            l_node = self.qtw_trf.item(l_row, 0).text().toUtf8()
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
            l_procedimento = "TRJ200"

            l_data = {"ntrf": l_row + 1, "latitude": l_latitude, "longitude": l_longitude,
                    "designador": l_designador, "ssr": l_ssr, "indicativo": l_indicativo,
                    "origem": l_origem, "destino": l_destino, "proa": l_proa,
                    "velocidade": l_velocidade, "altitude": l_altitude,
                    "procedimento": l_procedimento}

            # do the substitution
            l_result.append(l_src.substitute(l_data))

        # open template file (trafegos)
        l_file_in = open("templates/trf.xml.in")

        # read it
        l_src = Template(l_file_in.read())

        # document data
        l_data = {"trafegos": '\n'.join(l_result)}

        # do the substitution
        l_result = l_src.substitute(l_data)

        # grava o arquivo de tráfegos
        with open(f_traf_filename, 'w') as l_file:
            l_file.write(l_result)


    # ---------------------------------------------------------------------------------------------
    def extract_anvs(self, fname, f_traf_filename):
        """
        Extrai as aeronaves que foram criadas pelo core-gui.
        :param fname:
        :return:
        """
        # cria o QFile para o arquivo XML
        l_data_file = QtCore.QFile(fname)
        assert l_data_file is not None

        # abre o arquivo XML
        l_data_file.open(QtCore.QIODevice.ReadOnly)

        # cria o documento XML
        l_xdoc_aer = QtXml.QDomDocument("scenario")
        assert l_xdoc_aer is not None

        l_xdoc_aer.setContent(l_data_file)

        # fecha o arquivo
        l_data_file.close()

        # obtém o elemento raíz do documento
        l_elem_root = l_xdoc_aer.documentElement()
        assert l_elem_root is not None

        l_index = 0

        # cria uma lista com os elementos
        l_node_list = l_elem_root.elementsByTagName("host")

        # para todos os nós na lista...
        for li_ndx in xrange(l_node_list.length()):

            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            if "host" != l_element.tagName():
                continue

            # read identification if available
            if l_element.hasAttribute("id"):
                ls_host_id = l_element.attribute("id")

            # obtém o primeiro nó da sub-árvore
            l_node = l_element.firstChild()
            assert l_node is not None

            lv_host_ok = False

            # percorre a sub-árvore
            while not l_node.isNull():
                # tenta converter o nó em um elemento
                l_element = l_node.toElement()
                assert l_element is not None

                # o nó é um elemento ?
                if not l_element.isNull():
                    if "type" == l_element.tagName():
                        if "aircraft" == l_element.text():
                            # faz o parse do elemento
                            lv_host_ok = True

                        else:
                            break

                    if "point" == l_element.tagName():
                        # faz o parse do elemento
                        lf_host_lat = float(l_element.attribute("lat"))
                        lf_host_lng = float(l_element.attribute("lon"))

                # próximo nó
                l_node = l_node.nextSibling()
                assert l_node is not None

            # achou aircraft ?
            if lv_host_ok:
                # cria nova linha na tabela
                self.qtw_trf.insertRow(l_index)

                # node
                self.qtw_trf.setItem(l_index, 0, QtGui.QTableWidgetItem(str(ls_host_id)))

                # cria doubleSpinBox para latitude
                self.lat = QtGui.QDoubleSpinBox()
                self.lat.setDecimals(4)
                self.lat.setRange(-90., 90.)
                self.lat.setValue(lf_host_lat)
                self.lat.valueChanged.connect(self.valuechange)

                # latitude
                self.qtw_trf.setCellWidget(l_index, 1, self.lat)

                # cria doubleSpinBox para longitude
                self.lng = QtGui.QDoubleSpinBox()
                self.lng.setDecimals(4)
                self.lng.setRange(-180., 180.)
                self.lng.setValue(lf_host_lng)
                self.lng.valueChanged.connect(self.valuechange)

                # longitude
                self.qtw_trf.setCellWidget(l_index, 2, self.lng)

                # cria combo para designador
                self.cb = QtGui.QComboBox()
                self.cb.addItems(["B737", "A380", "AVRO"])
                self.cb.currentIndexChanged.connect(self.selectionchange)

                # designador
                self.qtw_trf.setCellWidget(l_index, 3, self.cb)

                # ssr
                self.qtw_trf.setItem(l_index, 4, QtGui.QTableWidgetItem(str(7001 + l_index)))
                # indicativo
                self.qtw_trf.setItem(l_index, 5, QtGui.QTableWidgetItem("{}X{:03d}".format(str(ls_host_id[:3]).upper(), l_index + 1)))
                # origem
                self.qtw_trf.setItem(l_index, 6, QtGui.QTableWidgetItem("SBGR"))
                # destino
                self.qtw_trf.setItem(l_index, 7, QtGui.QTableWidgetItem("SBBR"))

                # cria spinBox para proa
                self.proa = QtGui.QSpinBox()
                self.proa.setRange(0, 360)
                self.proa.setValue(60)
                self.proa.valueChanged.connect(self.valuechange)

                # proa
                self.qtw_trf.setCellWidget(l_index, 8, self.proa)

                # cria spinBox para velocidade
                self.velocidade = QtGui.QSpinBox()
                self.velocidade.setRange(0, 600)
                self.velocidade.setValue(500)
                self.velocidade.valueChanged.connect(self.valuechange)

                # velocidade
                self.qtw_trf.setCellWidget(l_index, 9, self.velocidade)

                # cria spinBox para altitude
                self.altitude = QtGui.QSpinBox()
                self.altitude.setRange(0, 40000)
                self.altitude.setValue(2000)
                self.altitude.valueChanged.connect(self.valuechange)

                # altitude
                self.qtw_trf.setCellWidget(l_index, 10, self.altitude)

                # cria combo para procedimento
                self.prc = QtGui.QComboBox()
                self.prc.addItems([u"trajetória", "espera", "subida"])
                self.prc.currentIndexChanged.connect(self.selectionchange)

                # procedimento
                self.qtw_trf.setCellWidget(l_index, 11, self.prc)

                # incrementa contador de linhas
                l_index += 1

        self.traf_filename = f_traf_filename

    # ---------------------------------------------------------------------------------------------
    def cbk_create_aircrafts(self):
        """

        :return:
        """
        self.create_ptracks_traf(self.traf_filename)