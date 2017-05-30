#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
track_generator_mngr

Track generator Manager

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
from string import Template

import ConfigParser
import logging
import os
import socket
import subprocess

module_logger = logging.getLogger('main_app.track_generator_mngr')

# < class CTrackGeneratorMngr >--------------------------------------------------------------------


class CTrackGeneratorMngr(QtCore.QObject):
    """

    """

    D_NET_CNFG = None
    D_NET_PORT = None

    D_MSG_VRS = None
    D_MSG_FRZ = None
    D_MSG_UFZ = None


    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        """
        Constructor

        :param f_parent:
        :param f_mediator:
        """
        super(CTrackGeneratorMngr, self).__init__(f_parent)

        self.logger = logging.getLogger('main_app.track_generator_mngr.CTrackGeneratorMngr')
        self.logger.info("Creating instance of CTrackGeneratorMngr")

        # the mediator
        self.mediator = f_mediator

        # Track Generator processes
        self.ptracks = None
        self.adapter = None
        self.visil = None
        self.pilot = None
        self.db_edit = None

        # The scenario filename
        self.scenario = None

        # The traffic filename
        self.traf_ptracks = None

        # Channel Track generator
        self.channel = 4

        # Track generator directories
        self.dir = None
        self.data_dir = None

        # Read configuration files
        self.load_config_file()

        # Read configuration files of the Track Generator
        self.load_track_generator_config_file(os.path.join(self.dir, "tracks.cfg"))

        self.net_tracks_cnfg = self.D_NET_CNFG + "." + str(self.channel)
        self.logger.debug("Multicast address of ptracks cnfg %s" % self.net_tracks_cnfg)

        # Create the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Make the socket multicast-aware, and set TTL.
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)


    # ---------------------------------------------------------------------------------------------
    def load_config_file(self, config="atn-sim-gui.cfg"):
        """
        Reads a configuration file to load the root directory of the Track generator.

        :param config: configuration file name.
        :return:
        """

        if os.path.exists(config):
            conf = ConfigParser.ConfigParser()
            conf.read(config)
            self.dir = conf.get("Dir", "ptracks")
        else:
            self.dir = os.path.join(os.environ['HOME'], 'ptracks')

        self.data_dir = os.path.join(self.dir, 'data')

        self.logger.debug("Root directory of the Track Generator: [%s]" % self.dir)
        self.logger.debug("Data directory of the Track generator: [%s]" % self.data_dir)


    # ---------------------------------------------------------------------------------------------
    def load_track_generator_config_file(self,config_file):
        """
        Loads the information to send configuration mesages to the Track Generator (ptracks)

        :param config_file: configuration file name.
        :return: none
        """

        if os.path.exists(config_file):
            conf = ConfigParser.ConfigParser()
            conf.read(config_file)
            self.D_NET_CNFG = conf.get("net", "cnfg")
            self.D_NET_PORT = conf.get("net", "port")
        else:
            self.D_NET_CNFG = self.get_ptracks_data('D_NET_CNFG')
            self.D_NET_PORT = self.get_ptracks_data('D_NET_PORT')

        self.logger.debug("NET_CNFG [%s]" % self.D_NET_CNFG)
        self.logger.debug("NET_PORT [%s]" % self.D_NET_PORT)

        self.D_MSG_VRS = self.get_ptracks_data('D_MSG_VRS')
        self.D_MSG_FRZ = self.get_ptracks_data('D_MSG_FRZ')
        self.D_MSG_UFZ = self.get_ptracks_data('D_MSG_UFZ')

        self.D_MSG_VRS.strip('\n')

        self.logger.debug("MSG_VRS [%s]" % self.D_MSG_VRS)
        self.logger.debug("MSG_FRZ [%s]" % self.D_MSG_FRZ)
        self.logger.debug("MSG_UFZ [%s]" % self.D_MSG_UFZ)


    # ---------------------------------------------------------------------------------------------
    def get_traf_filename(self):
        """
        Return traffic file from Track Generator
        :return:
        """
        return self.traf_ptracks


    # ---------------------------------------------------------------------------------------------
    def get_root_dir(self):
        """

        :return:
        """
        return self.dir


    # ---------------------------------------------------------------------------------------------
    def check_files(self, f_scenario_filename):
        """
        Check that exercise and traffic files exist in the ptracks data structure.

        :param f_scenario_filename: The filename of the simulation scenario without its extension
        :return: True, if the file traffics exists otherwise False.
        """
        self.scenario = f_scenario_filename
        self.logger.debug("The scenario filename [%s]" % self.scenario)

        # the name of the ptracks exercise file
        l_exe_ptracks = self.data_dir + "/exes/" + self.scenario  + ".exe.xml"
        self.logger.debug("The ptracks exercise file [%s]" % l_exe_ptracks)

        if not os.path.isfile(l_exe_ptracks):
            # Creates the exercise file
            self.create_ptracks_exe(l_exe_ptracks)

        # The name of the ptracks traffics file
        self.traf_ptracks = self.data_dir + "/traf/" + self.scenario + ".trf.xml"
        self.logger.debug("The ptracks traffic file [%s]" % self.traf_ptracks)

        if not os.path.isfile(self.traf_ptracks):
            return False

        return True


    # ---------------------------------------------------------------------------------------------
    def create_file(self, f_data_list):
        """
        Create a traffic file for the ptracks.

        :param f_data_list: List of dictionaries with the information needed to create the traffic file.
        :return:
        """

        # open template file (trafegos)
        l_file_in = open("templates/trf.xml.in")

        # read it
        l_src = Template(l_file_in.read())

        # document data
        l_data = {"trafegos": '\n'.join(f_data_list)}

        # do the substitution
        l_result = l_src.substitute(l_data)

        with open(self.traf_ptracks, 'w') as l_file:
            l_file.write(l_result)


    # ---------------------------------------------------------------------------------------------
    def create_ptracks_exe(self, f_scenario_filename):
        """
        Create the ptracks exe file for the chosen scenario.

        :param f_scenario_filename: the name of the simulation scneario.
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

        # grava o arquivo de exercícios
        with open(f_scenario_filename, 'w') as f:
            f.write(result)


    # ---------------------------------------------------------------------------------------------
    def is_database_manager_running(self):
        """

        :return:
        """
        return self.db_edit


    # ---------------------------------------------------------------------------------------------
    def get_database_manager_process(self):
        """

        :return:
        """
        return self.db_edit.poll()


    # ---------------------------------------------------------------------------------------------
    def get_ptracks_data(self, data):
        """
        Obtém a informação do arquivo do ptracks que contém as definições globais que o
        gerador de pistas (ptracks) utiliza.
        :param data: o tipo da informação a ser recuperada
        :return: string
        """
        # Monta o comando a ser executado
        cmd = "cat " + self.dir + "/control/common/glb_defs.py" + " | grep " + data
        output = subprocess.check_output(cmd, shell=True)
        values = output.split('=')

        if len(values[1]) > 2:
            values = values[1].split(' ')

        return values[1]


    # ---------------------------------------------------------------------------------------------
    def send_pause_message(self):
        """
        Sends the pause message to the multicast address used to control the ptracks system.

        :return:
        """

        self.logger.info("Sending pause message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_FRZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def send_play_message(self):
        """
        Sends the play message to the multicast address used to control the ptracks system.

        :return:
        """

        self.logger.info("Sending play message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_UFZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def send_multicast_data(self,data,port,addr):
        """
        Sends data to the multicast address (addr) in specified port to the ptrack system.

        :param data: a data to be sent.
        :param port: a port to be used.
        :param addr: a address to be used.

        :return:
        """

        self.logger.debug("sending data: [%s] to [%s:%s]" % (data, addr, port))

        # Send the data
        self.sock.sendto(data, (addr, port))


    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        Runs ptracks ...

        :return:
        """
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        self.adapter = subprocess.Popen(['python', 'adapter.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        self.ptracks = subprocess.Popen(['python', 'newton.py', '-e', self.scenario, '-c', str(self.channel)],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def stop_processes(self):
        """
        Stop the processes of the Track Generator
        :return: None.
        """

        # Stop adapter
        if self.adapter:
            kill = "kill -9 $(pgrep -P " + str(self.adapter.pid) + ")"
            os.system(kill)
            self.adapter.terminate()

        # Stop ptracks
        if self.ptracks:
            kill = "kill -9 $(pgrep -P " + str(self.ptracks.pid) + ")"
            os.system(kill)
            self.ptracks.terminate()

        # Stop ptracks view
        if self.visil:
            kill = "kill -9 $(pgrep -P " + str(self.visil.pid) + ")"
            os.system(kill)
            self.visil.terminate()

        # Stop ptracks pilot
        if self.pilot:
            kill = "kill -9 $(pgrep -P " + str(self.pilot.pid) + ")"
            os.system(kill)
            self.pilot.terminate()


    # ---------------------------------------------------------------------------------------------
    def run_pilot(self):
        """

        :return:
        """
        # Muda para o diretório onde o sistema do ptracks se encontra
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Executa o piloto
        self.pilot = subprocess.Popen(['python', 'piloto.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        # Retorna para o diretório do simulador ATN
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def run_visil(self):
        """

        :return:
        """
        # Muda para o diretório onde o sistema do ptracks se encontra
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Executa o piloto
        self.visil = subprocess.Popen(['python', 'visil.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        # Retorna para o diretório do simulador ATN
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def run_database_manager(self):
        """

        :return:
        """
        # Muda para o diretório onde o sistema do ptracks se encontra
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Inicia o core-gui no modo de edição
        self.db_edit = subprocess.Popen(['python', 'dbEdit.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        # Retorna para o diretório do simulador ATN
        os.chdir(l_cur_dir)


# < the end >--------------------------------------------------------------------------------------
