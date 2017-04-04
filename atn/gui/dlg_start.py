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

import dlg_start_ui as dstart_ui

# < class CDlgStart >------------------------------------------------------------------------------

class CDlgStart(QtGui.QDialog, dstart_ui.Ui_dlg_start):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None):
        # init super class
        QtGui.QDialog.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        # do signal/slot connections
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_upgrade.clicked.connect(self.on_upgrade)
        self.btn_run.clicked.connect(self.on_run)

    # ---------------------------------------------------------------------------------------------
    def set_title(self, f_title):
        """
        Define o título da janela de diálogo com o nome do cenário de simulação (f_title)
        :param f_title: o nome do cenário de simulação.
        :return:
        """
        self.setWindowTitle ( "Start Simulation: " + f_title )


    # ---------------------------------------------------------------------------------------------
    def on_cancel(self):
        """

        :return:
        """
        self.done(QtGui.QDialog.Rejected)


    # ---------------------------------------------------------------------------------------------
    def on_upgrade(self):
        """

        :return:
        """
        self.done(1)


    # ---------------------------------------------------------------------------------------------
    def on_run(self):
        """

        :return:
        """
        self.done(2)


# < the end>---------------------------------------------------------------------------------------