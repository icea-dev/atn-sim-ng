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


        #self.designador_list = self.load_performance()
        #self.proc_list = self.load_tables()

        # cria doubleSpinBox para latitude
        self.lat = QtGui.QDoubleSpinBox()
        self.lat.setDecimals(4)
        self.lat.setRange(-90., 90.)
        #self.lat.setValue(f_table[l_row]['latitude'])
        #self.lat.valueChanged.connect(self.valuechange)

        # latitude
        self.qtw_traf.setCellWidget(0, 0, self.lat)

        # cria doubleSpinBox para longitude
        self.lng = QtGui.QDoubleSpinBox()
        self.lng.setDecimals(4)
        self.lng.setRange(-180., 180.)
        #self.lng.setValue(f_table[l_row]['longitude'])
        #self.lng.valueChanged.connect(self.valuechange)

        # longitude
        self.qtw_traf.setCellWidget(0, 1, self.lng)

        '''
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
        '''
        

    # ---------------------------------------------------------------------------------------------
    def set_title(self, f_title):
        """
        Define o título da janela de diálogo com o nome do cenário de simulação (f_title)

        :param f_title: o nome do cenário de simulação.
        :return:
        """
        self.scenario_filename = f_title
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
