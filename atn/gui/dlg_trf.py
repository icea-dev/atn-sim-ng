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
    def __init__(self, f_parent=None):
        # init super class
        QtGui.QDialog.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        self.qtw_trf.setColumnCount(12)
        self.qtw_trf.setHorizontalHeaderLabels(
            ["Node", "Latitude", "Longitude", "Designador", "SSR", "Indicativo", "Origem", "Destino", "Proa", "Velocidade",
             "Altitude", "Procedimento"])

        # do signal/slot connections
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_create.clicked.connect(self.on_create)

        self.scenario_filename = ""

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
        self.done(QtGui.QDialog.Rejected)


    # ---------------------------------------------------------------------------------------------
    def on_create(self):
        """

        :return:
        """
        self.done(QtGui.QDialog.Accepted)


    # ---------------------------------------------------------------------------------------------
    def populate_table(self, f_table):
        """
        Alimenta a tabela da janela de diálogo
        :param f_table: uma lista com os dados necessários para criar um tráfego para o ptracks
        :return:
        """

        # para todas as linhas da tabela...
        self.qtw_trf.setRowCount(0);

        # para todas as linhas da tabela...
        for l_row in xrange(0, len(f_table)):

            # cria nova linha na tabela
            self.qtw_trf.insertRow(l_row)

            # node
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
            self.cb.addItems(["B737", "A380", "AVRO"])
            self.cb.setCurrentIndex(self.cb.findData(f_table[l_row]['designador']))
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
            self.prc.addItems([u"trajetória", "espera", "subida"])
            self.prc.setCurrentIndex(self.prc.findData(f_table[l_row]['procedimento']))
            self.prc.currentIndexChanged.connect(self.selectionchange)

            # procedimento
            self.qtw_trf.setCellWidget(l_row, 11, self.prc)


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

        return l_result


# < the end>---------------------------------------------------------------------------------------