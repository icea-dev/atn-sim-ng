#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
dlg_trf_run_time.py

dialogo para criar um tráfego em tempo de execução no cenário de simulação.

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

revision 0.1  2017/may  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/05"

# < import >---------------------------------------------------------------------------------------

# python library
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtXml
from string import Template

import os
import dlg_traf_run_time_ui as dlg_ui

# < class CDlgTrafRunTime >------------------------------------------------------------------------

class CDlgTrafRunTime(QtGui.QDialog, dlg_ui.Ui_dlg_traf_run_time):
    """
    DOCUMENT ME!
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None):
        # init super class
        QtGui.QDialog.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        self.qtw_traf.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # do signal/slot connections
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_create.clicked.connect(self.on_create)

        # create doubleSpinBox for latitude
        self.lat = QtGui.QDoubleSpinBox()
        self.lat.setDecimals(4)
        self.lat.setRange(-90., 90.)
        #self.lat.setValue(f_table[l_row]['latitude'])
        #self.lat.valueChanged.connect(self.valuechange)

        # latitude
        self.qtw_traf.setCellWidget(0, 0, self.lat)

        # create doubleSpinBox for longitude
        self.lng = QtGui.QDoubleSpinBox()
        self.lng.setDecimals(4)
        self.lng.setRange(-180., 180.)
        #self.lng.setValue(f_table[l_row]['longitude'])
        #self.lng.valueChanged.connect(self.valuechange)

        # longitude
        self.qtw_traf.setCellWidget(0, 1, self.lng)

        # create comboBox for type of aircraft  (designador)
        self.type_aircraft = QtGui.QComboBox()
        #self.cb.addItems(self.designador_list)
        #self.cb.setCurrentIndex(self.cb.findText(f_table[l_row]['designador']))
        #self.cb.currentIndexChanged.connect(self.selectionchange)

        # type of auircraft (designador)
        self.qtw_traf.setCellWidget(0, 2, self.type_aircraft)

        # ssr
        self.qtw_traf.setItem(0, 3, QtGui.QTableWidgetItem("7001"))

        # callsign (indicativo)
        self.qtw_traf.setItem(0, 4, QtGui.QTableWidgetItem("XXX7001"))

        # departure (origem)
        self.qtw_traf.setItem(0, 5, QtGui.QTableWidgetItem("ZZZZ"))

        # arrival (destino)
        self.qtw_traf.setItem(0, 6, QtGui.QTableWidgetItem("ZZZZ"))

        # create spinBox for Heading
        self.heading = QtGui.QSpinBox()
        self.heading.setRange(0, 360)
        self.heading.setValue(180)
        #self.heading.valueChanged.connect(self.valuechange)

        # heading
        self.qtw_traf.setCellWidget(0, 7, self.heading)

        # create spinBox for speed
        self.speed = QtGui.QSpinBox()
        self.speed.setRange(0, 600)
        self.speed.setValue(300)
        #self.speed.valueChanged.connect(self.valuechange)

        # speed
        self.qtw_traf.setCellWidget(0, 8, self.speed)

        # create spinBox for altitude
        self.altitude = QtGui.QSpinBox()
        self.altitude.setRange(0, 40000)
        self.altitude.setValue(0)
        #self.altitude.valueChanged.connect(self.valuechange)

        # altitude
        self.qtw_traf.setCellWidget(0, 9, self.altitude)

        # create comboBox for procedure
        self.procedure = QtGui.QComboBox()
        #self.procedure.addItems(self.proc_list)
        #self.procedure.setCurrentIndex(self.prc.findText(f_table[l_row]['procedimento']))
        #self.procedure.currentIndexChanged.connect(self.selectionchange)

        # procedure
        self.qtw_traf.setCellWidget(0, 10, self.procedure)

        # self.designador_list = self.load_performance()
        # self.proc_list = self.load_tables()

        # redefines the size of the QTableWidget
        self.qtw_traf.resizeRowsToContents()
        self.qtw_traf.resizeColumnsToContents()

        # Defines thew new size of the dialog window
        width = self.qtw_traf.horizontalHeader().length() + \
                ( self.qtw_traf.horizontalHeader().sizeHint().width() *  3 / 4 )
        self.setFixedWidth ( width + 10 )


    # ---------------------------------------------------------------------------------------------
    def set_title(self, f_title):
        """
        Define o título da janela de diálogo com o nome do cenário de simulação (f_title)

        :param f_title: o nome do cenário de simulação.
        :return:
        """
        self.setWindowTitle("Create aircraft at run time: " + f_title)


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


# < the end>---------------------------------------------------------------------------------------
