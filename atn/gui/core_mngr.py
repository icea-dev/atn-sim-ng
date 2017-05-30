#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
core_mngr

CORE manager

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
from core.api import coreapi
from PyQt4 import QtCore
from PyQt4 import QtXml

import ConfigParser
import logging
import os
import socket
import subprocess


module_logger = logging.getLogger('main_app.core_mngr')


# < class CCoreMngr >----------------------------------------------------------------------------
class CCoreMngr(QtCore.QObject):
    """
    Class responsible for controlling the core-gui module. Starts it in both run and edit mode.
    """

    NONE_MODE = 0
    EDIT_MODE = 1
    RUN_MODE = 2

    # Interface da rede de controle do CORE
    ctrl_net_iface = "ctrl0net"


    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        """
        Constructor
        """
        super(CCoreMngr, self).__init__(f_parent)

        self.logger = logging.getLogger('main_app.core_mngr.CCoreMngr')
        self.logger.info("Creating instance of CCoreMngr")

        # the mediator
        self.mediator = f_mediator

        # the core-gui process
        self.core_gui = None

        # timer id
        self.timer_id = 0

        # the session name
        self.session_name = None

        # Node number of Dump1090
        self.node_number_Dump1090 = []

        # Endereço da rede de controle do CORE
        self.control_net = None

        # run mode of core-gui
        self.run_mode = self.NONE_MODE

        # Read configuration file
        self.scenario_dir = None
        self.load_config_file()


    # ---------------------------------------------------------------------------------------------
    def run_gui_edit_mode(self):
        """
        Runs core-gui in edit mode.

        :return:
        """

        # If there is a process started and not finalized, it finishes its processing.
        if self.core_gui:
            l_ret_code = self.core_gui.poll()
            if l_ret_code is None:
                self.core_gui.terminate()

        # starts core-gui in edit mode
        self.logger.info("Call core-gui in edit mode.")
        self.core_gui = subprocess.Popen(['core-gui'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # timer to check if the core-gui was finalized by its GUI
        self.logger.info("Start timer to check core-gui is running.")
        self.timer_id = self.startTimer(100)

        self.run_mode = self.EDIT_MODE


    # ---------------------------------------------------------------------------------------------
    def run_gui_exec_mode(self, f_scenario_filename_path):
        """
        Runs core-gui in run mode.

        :return:
        """
        # Gets the name of the session that will be executed
        l_split = f_scenario_filename_path.split('/')
        self.session_name = l_split [ len(l_split) - 1 ]
        self.logger.debug("Session name [%s]" % self.session_name)

        self.logger.info("Call core-gui in rum mode.")
        # starts core-gui in run mode
        self.core_gui = subprocess.Popen(['core-gui', '--start', f_scenario_filename_path ],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.timer_id = self.startTimer(100)

        self.run_mode = self.RUN_MODE


    # ---------------------------------------------------------------------------------------------
    def stop_session(self):
        """

        :return:
        """
        # Monta a mensagem para solicitar as sessões que estão sendo executadas no CORE
        l_num = '0'
        l_flags = coreapi.CORE_API_STR_FLAG
        l_tlv_data = coreapi.CoreSessionTlv.pack(coreapi.CORE_TLV_SESS_NUMBER, l_num)
        l_msg = coreapi.CoreSessionMessage.pack(l_flags, l_tlv_data)

        # Socket para comunicação com o CORE, conecta-se ao CORE e envia a mensagem
        l_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        l_sock.connect(('localhost', coreapi.CORE_API_PORT))
        l_sock.send(l_msg)

        # Espera a resposta do CORE
        l_hdr = l_sock.recv(coreapi.CoreMessage.hdrsiz)
        l_msg_type, l_msg_flags, l_msg_len = coreapi.CoreMessage.unpackhdr(l_hdr)
        l_data = ""

        if l_msg_len:
            l_data = l_sock.recv(l_msg_len)

        # Desempacota a mensagem do CORE
        l_msg = coreapi.CoreMessage(l_msg_flags, l_hdr, l_data)
        l_sessions = l_msg.gettlv(coreapi.CORE_TLV_SESS_NUMBER)
        l_names = l_msg.gettlv(coreapi.CORE_TLV_SESS_NAME)

        # Cria uma lista de strings com os identificadores das sessões que estão sendo executadas.
        l_lst_session = l_sessions.split('|')

        # Existem nomes para as sessões ?
        if l_names != None:
            # Cria uma lista com os nomes das sessões que estão sendo executadas.
            l_lst_names = l_names.split('|')
            l_index = 0
            while True:
                # Tenta encontrar o nome da sessão que está sendo executada
                if l_lst_names [ l_index ] == self.session_name:
                    break
                l_index += 1

            # Monta a mensagem para finalizar a sessão no CORE
            l_num = l_lst_session [ l_index ]
            l_flags = coreapi.CORE_API_DEL_FLAG
            l_tlv_data = coreapi.CoreSessionTlv.pack(coreapi.CORE_TLV_SESS_NUMBER, l_num)
            l_msg = coreapi.CoreSessionMessage.pack(l_flags, l_tlv_data)
            l_sock.send(l_msg)

        l_sock.close()

        # Finaliza a core-gui
        if self.core_gui:
            self.killTimer(self.timer_id)
            self.core_gui.terminate()

        # Não existe sessão do CORE sendo executada.
        self.node_number_Dump1090 = []
        self.control_net = None

        self.run_mode = self.NONE_MODE


    # ---------------------------------------------------------------------------------------------
    def load_config_file(self, config="atn-sim-gui.cfg"):
        """
        Reads a configuration file to load the directory of the simulation scenario created in CORE.

        :param config: configuration filename
        :return:
        """
        if os.path.exists(config):
            conf = ConfigParser.ConfigParser()
            conf.read(config)

            self.scenario_dir = conf.get("Dir", "scenario")
        else:
            self.scenario_dir = os.path.join(os.environ['HOME'], 'atn-sim/configs/scenarios')

        self.logger.debug("Directory of the scenarios: [%s]" % self.scenario_dir)


    # ---------------------------------------------------------------------------------------------
    def get_scenario_dir(self):
        """
        Returns the directory of the simulation scenario files.

        :return: string
        """
        return self.scenario_dir


    # ---------------------------------------------------------------------------------------------
    def parse_xml_file(self, f_xml_file):
        """
        Parser of the XML file of the simulation scenario to obtain the nodes running the Dump1090
        service and the address of the CORE control network.

        :param f_xml_file: XML file
        :return:
        """

        # Find nodes running the Dump1090 service
        self.node_number_Dump1090 = self.extract_host_id_dump1090(f_xml_file)

        # Find the address of the CORE control network
        self.control_net = self.extract_control_net(f_xml_file)


    # ---------------------------------------------------------------------------------------------
    def extract_host_id_dump1090(self, f_xml_filename):
        """ Extrai o número do nó do CORE que está sendo executado o Dump1090

        :param f_xml_filename: arquivo XML do cenário do CORE.
        :return: uma lista com os nós do CORE com o serviço Dump1090
        """
        # cria o QFile para o arquivo XML
        l_data_file = QtCore.QFile(f_xml_filename)
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

        # cria uma lista com os elementos
        l_node_list = l_elem_root.elementsByTagName("host")

        ll_node_nbrs = []

        # para todos os nós na lista...
        for li_ndx in xrange(l_node_list.length()):

            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            if "host" != l_element.tagName():
                continue

            # obtém o primeiro nó da sub-árvore
            l_node = l_element.firstChild()
            assert l_node is not None

            lv_host_ok = False
            li_ntrf = None

            # percorre a sub-árvore
            while not l_node.isNull():
                # tenta converter o nó em um elemento
                l_element = l_node.toElement()
                assert l_element is not None

                # o nó é um elemento ?
                if not l_element.isNull():

                    if "alias" == l_element.tagName():
                        if l_element.hasAttribute("domain"):
                            if "COREID" == l_element.attribute("domain"):
                                li_ntrf = int(l_element.text())

                    if "CORE:services" == l_element.tagName():
                        l_node_svc = l_element.firstChild()

                        while not l_node_svc.isNull():
                            l_elm_svc = l_node_svc.toElement()
                            assert l_elm_svc is not None

                            if not l_elm_svc.isNull():
                                if "service" == l_elm_svc.tagName():
                                    if l_elm_svc.hasAttribute("name"):
                                        if "Dump1090" == l_elm_svc.attribute("name"):
                                            lv_host_ok = True

                            l_node_svc = l_node_svc.nextSibling()
                            assert l_node_svc is not None

                # próximo nó
                l_node = l_node.nextSibling()
                assert l_node is not None

            # achou aircraft ?
            if lv_host_ok:
                ll_node_nbrs.append(li_ntrf)

        return ll_node_nbrs


    # ---------------------------------------------------------------------------------------------
    def extract_control_net(self, f_xml_filename):
        """
        Extrai o endereço da rede de controle do CORE
        :param f_xml_filename: o arquivo xml do cenário do CORE
        :return: endereço da rede de controle do CORE
        """
        # cria o QFile para o arquivo XML
        l_data_file = QtCore.QFile(f_xml_filename)
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

        # cria uma lista com os elementos
        l_node_list = l_elem_root.elementsByTagName("CORE:sessionconfig")

        # para todos os nós na lista...
        for li_ndx in xrange(l_node_list.length()):

            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            if "CORE:sessionconfig" != l_element.tagName():
                continue

            # obtém o primeiro nó da sub-árvore
            l_node = l_element.firstChild()
            assert l_node is not None

            lv_net_session_ok = False

            # percorre a sub-árvore
            while not l_node.isNull():
                # tenta converter o nó em um elemento
                l_element = l_node.toElement()
                assert l_element is not None

                # o nó é um elemento ?
                if not l_element.isNull():

                    if "options" == l_element.tagName():
                        l_node_opt = l_element.firstChild()

                        while not l_node_opt.isNull():
                            l_elm_opt = l_node_opt.toElement()
                            assert l_elm_opt is not None

                            if not l_elm_opt.isNull():
                                if "parameter" == l_elm_opt.tagName():
                                    if l_elm_opt.hasAttribute("name"):
                                        if "controlnet" == l_elm_opt.attribute("name"):
                                            ls_controle_net = l_elm_opt.text()
                                            lv_net_session_ok = True

                            l_node_opt = l_node_opt.nextSibling()
                            assert l_node_opt is not None

                # próximo nó
                l_node = l_node.nextSibling()
                assert l_node is not None

            # achou aircraft ?
            if lv_net_session_ok:
                return ls_controle_net

        return None


    # ---------------------------------------------------------------------------------------------
    def get_mode(self):
        """

        :return:
        """
        return self.run_mode


    # ---------------------------------------------------------------------------------------------
    def get_control_net(self):
        """

        :return:
        """
        return self.control_net


    # ---------------------------------------------------------------------------------------------
    def get_nodes_dump1090(self):
        """

        :return:
        """
        return self.node_number_Dump1090


    # ---------------------------------------------------------------------------------------------
    def timerEvent(self, event):
        """
        The event handler to receive timer events for the object.

        :param event: the timer event.
        :return:
        """
        l_ret_code = self.core_gui.poll()

        if l_ret_code is not None:
            logging.info("The core-gui has finished.")

            edit_mode = False
            if self.EDIT_MODE == self.run_mode:
                edit_mode = True

            self.mediator.terminate_processes(f_edit_mode=edit_mode)
            self.killTimer(self.timer_id)


# < the end >--------------------------------------------------------------------------------------