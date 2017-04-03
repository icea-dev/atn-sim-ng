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
from string import Template
from core.api import coreapi

import os
import socket
import subprocess
import wnd_main_atn_sim_ui as wmain_ui
import wnd_trf as wtraf_ui

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

        self.wnd_traf = wtraf_ui.CWndTraf()

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
        Inicia a simulação de um determinado cenário de simulação. Verifica se existem os arquivos
        necessários para execução do ptracks. Caso eles não exsitem é dado a possibilidade de
        criá-los.
        :return:
        """
        l_scenario_dir = os.path.join(os.environ['HOME'], 'atn-sim/configs/scenarios')
        l_file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open simulation scenario - XML',
                                                        l_scenario_dir, 'XML files (*.xml)')

        if (not l_file_path):
            return

        self.filename = os.path.splitext(os.path.basename(str(l_file_path)))[0]
        print self.filename

        l_ptracks_dir = os.path.join(os.environ["HOME"], 'atn-sim/ptracks/data')
        l_exe_filename = l_ptracks_dir + "/exes/" + self.filename  + ".exe.xml"

        # Verifica se já existe um exercicio para o cenário escolhido
        if not os.path.isfile(l_exe_filename):
            self.create_ptracks_exe(l_exe_filename)

        l_traf_filename = l_ptracks_dir + "/traf/" + self.filename + ".trf.xml"

        # Verifica se já existe um arquivo de tráfegos para o cenário escolhido
        if not os.path.isfile(l_traf_filename):
            self.wnd_traf.extract_anvs(l_file_path, l_traf_filename)
            self.wnd_traf.show()

        '''
            l_msg = QtGui.QMessageBox()
            l_msg.setIcon(QtGui.QMessageBox.Question)
            l_msg_text = "File %s does not exist.\n Do you want to create it?" % l_exe_filename
            l_msg.setText(l_msg_text)
            l_msg.setWindowTitle("Start Session")
            l_msg.setStandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            l_ret_val = l_msg.exec_()
            print "value of pressed message box button: %d" % l_ret_val
        '''

        #l_split = l_file_path.split('/')
        #self.session_name = l_split [ len(l_split) - 1 ]

        #self.p = subprocess.Popen(['core-gui', '--start', l_file_path ],
        #                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        #l_status_msg = "Running the scenario: " + self.filename
        #self.statusbar.showMessage(l_status_msg)

        #self.check_process()


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
    def cbk_scenario_to_xml(self):
        """

        :return:
        """
        pass

    # ---------------------------------------------------------------------------------------------
    def create_ptracks_exe(self, f_scenario_filename):
        """
        Cria o arquivo exe do ptracks para o cenário solicitado
        :param f_scenario_filename: o nome do cenário de simulação
        :return:
        """
        # open template file (exercicio)
        l_file_in = open("templates/exe.xml.in")

        # read it
        l_src = Template(l_file_in.read())

        # document data
        l_title = "ATN Simulator"
        l_hora = "06:00"
        l_data = {"title": l_title, "exe": self.filename, "hora": l_hora}

        # do the substitution
        result = l_src.substitute(l_data)

        l_ptracks_dir = os.path.join(os.environ["HOME"], 'ptracks/data')
        l_exe_filename = l_ptracks_dir + "/exes/" + self.filename  + ".exe.xml"

        # grava o arquivo de exercícios
        with open(f_scenario_filename, 'w') as f:
            f.write(result)


# < the end>---------------------------------------------------------------------------------------