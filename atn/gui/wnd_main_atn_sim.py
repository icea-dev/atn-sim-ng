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

revision 0.1  2017/mar  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/03"

# < import >---------------------------------------------------------------------------------------

# python library
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtXml

from core.api import coreapi

import os
import socket
import subprocess
import wnd_main_atn_sim_ui as wmain_ui

# < class CWndMainATNSim >-------------------------------------------------------------------------

class CWndMainATNSim(QtGui.QMainWindow, wmain_ui.Ui_CWndMainATNSim):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None):
        # init super class
        super(CWndMainATNSim, self).__init__(f_parent)

        # create main menu ui
        self.setupUi(self)

        self.p = None

        self.timer = QtCore.QTimer()

        # create signal and slots connections
        self.act_edit_scenario.triggered.connect(self.cbk_start_edit_mode)
        self.act_start_session.triggered.connect(self.cbk_start_session)
        self.act_stop_session.triggered.connect(self.cbk_stop_session)
        self.act_quit.triggered.connect(QtGui.QApplication.quit)

        self.act_scenario_to_xml.triggered.connect(self.cbk_scenario_to_xml)


    # ---------------------------------------------------------------------------------------------
    def check_process(self):
        """

        :return:
        """
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.cbk_check_process)
        self.timer.start(100)

    # ---------------------------------------------------------------------------------------------
    def cbk_check_process(self):
        """

        :return:
        """
        l_ret_code = self.p.poll()
        if l_ret_code is not None:
            self.statusbar.clearMessage()
            self.timer.stop()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_edit_mode(self):
        """

        :return:
        """
        if self.p:
            self.p.terminate()

        self.p = subprocess.Popen(['core-gui'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.statusbar.showMessage("Starting core-gui in edit mode!")

        self.check_process()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_session(self):
        """

        :return:
        """
        l_scenario_dir = os.path.join(os.environ['HOME'], 'atn-sim/configs/scenarios')
        l_file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open simulation scenario - XML',
                                                        l_scenario_dir, 'XML files (*.xml)')

        if (not l_file_path):
            return

        # Verificar se já existe um exercicio para o cenário escolhido

        self.filename = os.path.splitext(os.path.basename(str(l_file_path)))[0]
        print self.filename

        l_split = l_file_path.split('/')
        self.session_name = l_split [ len(l_split) - 1 ]

        self.p = subprocess.Popen(['core-gui', '--start', l_file_path ],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        l_status_msg = "Running the scenario: " + self.filename
        self.statusbar.showMessage(l_status_msg)

        self.check_process()


    # ---------------------------------------------------------------------------------------------
    def cbk_stop_session(self):
        """
        Stop running session
        :return:
        """
        l_num = '0'
        l_flags = coreapi.CORE_API_STR_FLAG
        l_tlv_data = coreapi.CoreSessionTlv.pack(coreapi.CORE_TLV_SESS_NUMBER, l_num)
        l_msg = coreapi.CoreSessionMessage.pack(l_flags, l_tlv_data)

        l_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        l_sock.connect(('localhost', coreapi.CORE_API_PORT))
        l_sock.send(l_msg)

        l_hdr = l_sock.recv(coreapi.CoreMessage.hdrsiz)
        l_msg_type, l_msg_flags, l_msg_len = coreapi.CoreMessage.unpackhdr(l_hdr)
        l_data = ""
        if l_msg_len:
            l_data = l_sock.recv(l_msg_len)
        l_msg = coreapi.CoreMessage(l_msg_flags, l_hdr, l_data)
        l_sessions = l_msg.gettlv(coreapi.CORE_TLV_SESS_NUMBER)
        l_names = l_msg.gettlv(coreapi.CORE_TLV_SESS_NAME)

        l_lst_session = l_sessions.split('|')

        if l_names != None:
            l_lst_names = l_names.split('|')
            l_index = 0
            while True:
                if l_lst_names [ l_index ] == self.session_name:
                    break
                l_index += 1

            l_num = l_lst_session [ l_index ]
            l_flags = coreapi.CORE_API_DEL_FLAG
            l_tlv_data = coreapi.CoreSessionTlv.pack(coreapi.CORE_TLV_SESS_NUMBER, l_num)
            l_msg = coreapi.CoreSessionMessage.pack(l_flags, l_tlv_data)
            l_sock.send(l_msg)

        l_sock.close()

        if self.p:
            self.p.terminate()

        self.statusbar.clearMessage()

    # ---------------------------------------------------------------------------------------------
    def extract_anvs(self, fname):

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
            '''
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

        # habilita botão de gerar tráfegos
        self.btn_trf.setEnabled(l_index > 0)
        '''


    # ---------------------------------------------------------------------------------------------
    def cbk_scenario_to_xml(self):
        """

        :return:
        """
        pass


# < the end>---------------------------------------------------------------------------------------