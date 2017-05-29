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
from PyQt4 import QtCore

import ConfigParser
import logging
import os
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
        self.logger.info("Call core-gui.")
        self.core_gui = subprocess.Popen(['core-gui'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # timer to check if the core-gui was finalized by its GUI
        self.logger.info("Start timer to check core-gui is running.")
        self.timer_id = self.startTimer(100)

        self.run_mode = self.EDIT_MODE


    # ---------------------------------------------------------------------------------------------
    def load_config_file(self, config="atn-sim-gui.cfg"):
        """
        Faz a leitura de um arquivo de configuração para carregar o diretório do arquivo do cenário
        da simulação criado pelo CORE e do diretório do gerador de informações de alvos ptracks.

        :param config: nome do arquivo de configuração.
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

        :return:
        """
        return self.scenario_dir


    # ---------------------------------------------------------------------------------------------
    def parse_xml_file(self, f_xml_file):
        """

        :param f_xml_file:
        :return:
        """

        # Encontra o número do nó onde está sendo executado Dump1090
        #self.node_number_Dump1090 = self.extract_host_id_dump1090(f_xml_file)

        # Encontra o enderço da rede de controle do CORE
        #self.control_net = self.extract_control_net(f_xml_file)

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