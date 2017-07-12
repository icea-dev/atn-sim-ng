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
import glob
import json
import logging
import os
import socket
import subprocess

module_logger = logging.getLogger('main_app.track_generator_mngr')

# < class CTrackGeneratorMngr >--------------------------------------------------------------------


class CTrackGeneratorMngr(QtCore.QObject):
    """

    """

    # Network address for configuration of the Track Generator
    D_NET_CNFG = None
    # Network address port for configuration of the Track Generator
    D_NET_PORT = None

    # Message structure version of the Track Generator
    D_MSG_VRS = None
    # Message type freexze simulation.
    D_MSG_FRZ = None
    # Message type unfreeze simulation.
    D_MSG_UFZ = None


    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        """
        Constructor

        :param f_parent: parent object for this object.
        :param f_mediator: application mediator object.
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
        :return: None.
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
        :return: None.
        """

        # open template file (exercicio)
        l_file_in = open("templates/exe.xml.in")

        # read it
        l_src = Template(l_file_in.read())

        # document data
        l_title = "ATN Simulator"
        l_hora = "06:00"
        l_data = {"title": l_title, "exe": self.scenario, "hora": l_hora}

        # do the substitution
        result = l_src.substitute(l_data)

        # grava o arquivo de exercícios
        with open(f_scenario_filename, 'w') as f:
            f.write(result)


    # ---------------------------------------------------------------------------------------------
    def get_database_manager_process(self):
        """
        Returns the object that contains the process.

        :return: The object.
        """

        return self.db_edit


    # ---------------------------------------------------------------------------------------------
    def get_file_list(self):
        """

        :return:
        """

        ls_widlcards = self.data_dir + "/exes/*.xml"
        llst_data = glob.glob(ls_widlcards)

        llst_file = []
        for file in llst_data:
            ls_file = file.split('/')
            llst_file.append(ls_file[-1][:len(ls_file[-1])-8])

        return llst_file


    # ---------------------------------------------------------------------------------------------
    def get_ptracks_data(self, data):
        """
        Gets the ptracks file information that contains the global settings that the ptracks
        uses.

        :param data: the type of information to be retrieved.
        :return: string : the information.
        """

        # Crate the command to be executed
        cmd = "cat " + self.dir + "/control/common/glb_defs.py" + " | grep " + data
        output = subprocess.check_output(cmd, shell=True)
        values = output.split('=')

        if len(values[1]) > 2:
            values = values[1].split(' ')

        return values[1]


    # ---------------------------------------------------------------------------------------------
    def get_root_dir(self):
        """
        Returns the root directory of the system.

        :return: string, the root directory.
        """

        return self.dir


    # ---------------------------------------------------------------------------------------------
    def get_traf_data(self, f_traf_filename):
        """
        Extract the aircraft that were created by the Track Generator.

        :param f_traf_filename:
        :return:
        """
        # Assembles the json file name with the aircraft data
        ls_json_pn = self.dir + "/" + f_traf_filename + ".json"

        # Run dbRead to writw aircraft data to a json file.
        # Changes to the directory where the ptracks system is located.
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Run database manager
        self.db_edit = subprocess.Popen(['python', 'dbRead.py', f_traf_filename ],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        self.db_edit.communicate()[0]

        # Returns to the ATN simulator directory
        os.chdir(l_cur_dir)

        ldct_data = []

        with open (ls_json_pn) as l_json_data:
            ldct_data = json.load(l_json_data)

        # Delete file
        if os.path.isfile(ls_json_pn):
            os.remove(ls_json_pn)

        return ldct_data


   # ---------------------------------------------------------------------------------------------
    def get_traf_filename(self):
        """
        Return traffic file from Track Generator.

        :return: string, the traffic filename
        """

        return self.traf_ptracks


    # ---------------------------------------------------------------------------------------------
    def is_database_manager_running(self):
        """
        Checks whether the runtime dadtabase editor is running.

        :return: A None value indicates that process hasn't terminated yet.
        """

        return self.db_edit.poll()


    # ---------------------------------------------------------------------------------------------
    def load_config_file(self, f_config="atn-sim-gui.cfg"):
        """
        Reads a configuration file to load the root directory of the Track generator.

        :param f_config: configuration file name.
        :return: None.
        """

        if os.path.exists(f_config):
            conf = ConfigParser.ConfigParser()
            conf.read(f_config)
            self.dir = conf.get("Dir", "ptracks")
        else:
            self.dir = os.path.join(os.environ['HOME'], 'ptracks')

        self.data_dir = os.path.join(self.dir, 'data')

        self.logger.debug("Root directory of the Track Generator: [%s]" % self.dir)
        self.logger.debug("Data directory of the Track generator: [%s]" % self.data_dir)


    # ---------------------------------------------------------------------------------------------
    def load_track_generator_config_file(self,f_config_file):
        """
        Loads the information to send configuration mesages to the Track Generator (ptracks)

        :param f_config_file: configuration file name.
        :return: None.
        """

        if os.path.exists(f_config_file):
            conf = ConfigParser.ConfigParser()
            conf.read(f_config_file)
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

        #self.D_MSG_VRS.strip('\n')

        self.logger.debug("MSG_VRS [%s]" % self.D_MSG_VRS)
        self.logger.debug("MSG_FRZ [%s]" % self.D_MSG_FRZ)
        self.logger.debug("MSG_UFZ [%s]" % self.D_MSG_UFZ)


    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        Runs ptracks ...

        :return: None.
        """

        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        self.adapter = subprocess.Popen(['python', 'adapter.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        self.ptracks = subprocess.Popen(['python', 'newton.py', '-e', self.scenario, '-c', str(self.channel)],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def run_database_manager(self):
        """
        Run the ptracks database manager.

        :return: None.
        """

        # Changes to the directory where the ptracks system is located.
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Run database manager
        self.db_edit = subprocess.Popen(['python', 'dbEdit.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        #self.db_edit.communicate()[0]

        # Returns to the ATN simulator directory
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def run_pilot(self):
        """
        Run the ptracks pilot ...

        :return: None.
        """

        # Changes to the directory where the ptracks system is located.
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Run pilot
        self.pilot = subprocess.Popen(['python', 'piloto.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        # Returns to the ATN simulator directory
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def run_visil(self):
        """
        Run the ptracks view ...

        :return: None.
        """

        # Changes to the directory where the ptracks system is located.
        l_cur_dir = os.getcwd()
        os.chdir(self.dir)

        # Run view
        self.visil = subprocess.Popen(['python', 'visil.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        # Returns to the ATN simulator directory
        os.chdir(l_cur_dir)


    # ---------------------------------------------------------------------------------------------
    def send_multicast_data(self,data,port,addr):
        """
        Sends data to the multicast address (addr) in specified port to the ptrack system.

        :param data: a data to be sent.
        :param port: a port to be used.
        :param addr: a address to be used.
        :return: None.
        """

        self.logger.debug("sending data: [%s] to [%s:%s]" % (data, addr, port))

        # Send the data
        self.sock.sendto(data, (addr, port))


    # ---------------------------------------------------------------------------------------------
    def send_pause_message(self):
        """
        Sends the pause message to the multicast address used to control the ptracks system.

        :return: None.
        """

        self.logger.info("Sending pause message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_FRZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def send_play_message(self):
        """
        Sends the play message to the multicast address used to control the ptracks system.

        :return: None.
        """

        self.logger.info("Sending play message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_UFZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def stop_processes(self):
        """
        Stop the processes of the Track Generator.

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


# < the end >--------------------------------------------------------------------------------------
