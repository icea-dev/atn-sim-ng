#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
dlg_sync

dialogo para sincronizar os cenários de simulação do CORE com a base de dados do gerador de pistas.

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

revision 0.1  2017/jul  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/07"

# < import >---------------------------------------------------------------------------------------

# python library
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtXml
from string import Template

import os
import dlg_sync_ui as dsync_ui

# < class CDlgSync >-------------------------------------------------------------------------------

class CDlgSync(QtGui.QDialog, dsync_ui.Ui_dlg_sync):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        # init super class
        QtGui.QDialog.__init__(self, f_parent)

        # create window
        self.setupUi(self)

        self.qtwTabFiles.setColumnCount(1)
        self.qtwTabFiles.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # do signal/slot connections
        self.btnClose.clicked.connect(self.on_close)
        self.btnSync.clicked.connect(self.on_sync)
        self.qtwTabFiles.itemSelectionChanged.connect(self.on_select)

        self.__mediator = f_mediator

        self.llst_core, self.llst_ptracks = self.__mediator.get_list_core_ptracks()

        self.__s_core_filename = None
        self.__s_ptracks_filename = None

        self.populate_table()


    # ---------------------------------------------------------------------------------------------
    def on_close(self):
        """
        Método chamado quando o usuário decide fechar a janela de diálogo.

        :return:
        """
        self.done(QtGui.QDialog.Accepted)


    # ---------------------------------------------------------------------------------------------
    def on_select(self):
        """
        Método chamado quando um item é selecionado.

        :return:
        """
        # obtém o número da linha selecionada
        l_iRow = self.qtwTabFiles.currentRow()

        # existe uma linha selecionada
        if l_iRow > -1:
            l_oCoreItem = self.qtwTabFiles.item(l_iRow, 0)
            if l_oCoreItem is not None:
                self.__s_core_filename = str(l_oCoreItem.text())

            #l_oPTracksItem = self.qtwTabFiles.item(l_iRow, 1)
            #if l_oPTracksItem is not None:
                #self.__s_ptracks_filename = str(l_oPTracksItem.text())


    # ---------------------------------------------------------------------------------------------
    def on_sync(self):
        """
        Método chamado quando o usuário decide sincronizar o CORE com a base de dados do Gerador
        de Pistas.

        :return:
        """
        # Is there a mediator
        ls_msg = None
        if self.__mediator is not None:
            ls_msg = self.__mediator.sync_atn_simulator(self.__s_core_filename, self.__s_ptracks_filename)

        if ls_msg is not None:
            if ls_msg != "OK":
                QtGui.QMessageBox.warning(self, self.tr("Sync Database"), ls_msg, QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(self, self.tr("Sync Database"),
                                              self.tr("Synchornized database!"),
                                              QtGui.QMessageBox.Ok)


    # ---------------------------------------------------------------------------------------------
    def populate_table(self):
        """

        :return:
        """

        # para todas as linhas da tabela...
        self.qtwTabFiles.setRowCount(0)

        self.llst_core.sort()
        self.llst_ptracks.sort()

        li_row = 0
        li_find = 0

        # para todas as linhas da tabela...
        for file in self.llst_core:

            # cria nova linha na tabela
            self.qtwTabFiles.insertRow(li_row)

            # core name
            self.qtwTabFiles.setItem(li_row, 0, QtGui.QTableWidgetItem( file ) )

            #if file in self.llst_ptracks:
                # ptracks name
                #self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem(file))
                #li_find = li_find + 1
            #else:
                #self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem("New"))

            li_row = li_row + 1

        #if li_find != len(self.llst_ptracks):
            #for file in self.llst_ptracks:
                #if file in self.llst_core:
                    #continue

                # cria nova linha na tabela
                #self.qtwTabFiles.insertRow(li_row)

                # core name
                #self.qtwTabFiles.setItem(li_row, 0, QtGui.QTableWidgetItem( "New" ) )

                # ptracks name
                #self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem(file))

        # redefine o tamanho da QTableWidget
        #self.qtwTabFiles.resizeRowsToContents()
        #self.qtwTabFiles.resizeColumnsToContents()


# < the end>---------------------------------------------------------------------------------------
