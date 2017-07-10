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

        self.qtwTabFiles.setColumnCount(2)
        self.qtwTabFiles.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # do signal/slot connections
        self.btnCancel.clicked.connect(self.on_cancel)
        self.btnUpdate.clicked.connect(self.on_update)
        self.btnNew.clicked.connect(self.on_new)

        self.__mediator = f_mediator

        self.llst_core, self.llst_ptracks = self.__mediator.get_list_core_ptracks()

        self.populate_table()

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
    def on_cancel(self):
        """
        Método chamado quando o usuário decide cancelar a atividade. Fecha a janela de diálogo.
        Estabelece o código de retorno como rejected.

        :return:
        """
        self.done(QtGui.QDialog.Rejected)


    # ---------------------------------------------------------------------------------------------
    def on_new(self):
        """
        Método chamado quando o usuário decide criar o arquivo de tráfegos. Fecha a janela de diálogo.
        Estabelece o código de retorno como accepted.

        :return:
        """
        self.done(QtGui.QDialog.Accepted)


    # ---------------------------------------------------------------------------------------------
    def on_update(self):
        """
        Método chamado quando o usuário decide criar o arquivo de tráfegos. Fecha a janela de diálogo.
        Estabelece o código de retorno como accepted.

        :return:
        """
        self.done(QtGui.QDialog.Accepted)


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

            if file in self.llst_ptracks:
                # ptracks name
                self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem(file))
                li_find = li_find + 1
            else:
                self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem("New"))

            li_row = li_row + 1

        if li_find != len(self.llst_ptracks):
            for file in self.llst_ptracks:
                if file in self.llst_core:
                    continue

                # cria nova linha na tabela
                self.qtwTabFiles.insertRow(li_row)

                # core name
                self.qtwTabFiles.setItem(li_row, 0, QtGui.QTableWidgetItem( "New" ) )

                # ptracks name
                self.qtwTabFiles.setItem(li_row, 1, QtGui.QTableWidgetItem(file))

        # redefine o tamanho da QTableWidget
        self.qtwTabFiles.resizeRowsToContents()
        self.qtwTabFiles.resizeColumnsToContents()


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

        # latitude
        #l_latitude = self.qtw_trf.cellWidget(l_row, 1).value()
        # longitude
        #l_longitude = self.qtw_trf.cellWidget(l_row, 2).value()


# < the end>---------------------------------------------------------------------------------------
