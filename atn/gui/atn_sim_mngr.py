#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
atn_sim_mngr

ATN simulator manager

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
from PyQt4 import QtXml

import ipcalc
import logging
import os

import core_mngr as coremngr
import track_generator_mngr as trackmngr
import webbrowser as web
import wnd_main_atn_sim as wmain

module_logger = logging.getLogger('main_app.atn_sim_mngr')

# < class CATNSimMngr >----------------------------------------------------------------------------

class CATNSimMngr:
    """
    The ATN simulator manager class is reponsible for controlling the ATN simulation.

    """

    # ---------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor
        """

        self.logger = logging.getLogger('main_app.atn_sim_mngr.CATNSimMngr')
        self.logger.info("Creating instance of CATNSimMngr")

        # create the CORE Manager
        self.core_mngr = coremngr.CCoreMngr(f_mediator=self)

        # create the Track Generator Manager
        self.track_mngr = trackmngr.CTrackGeneratorMngr(f_mediator=self)

        # create the main window
        self.wmain = wmain.CWndMainATNSim(f_mediator=self)

        # Define the state of the simulation
        self.is_simulation_pause = False

        # The filename of the simulation scenario without its extension
        self.scenario_filename = None


    # ---------------------------------------------------------------------------------------------
    def add_aircraft_exec_mode(self, f_aircraft_data):
        """
        Creates an aircraft in the runtime simulation scenario.

        :param: f_aircraft_data:
        :return: None.
        """

        self.logger.debug("Aircraft data %s" % f_aircraft_data)

        self.core_mngr.add_node_run_time(f_aircraft_data)

        #self.track_mngr.add_aircraft_run_time(f_aircraft_data)


    # ---------------------------------------------------------------------------------------------
    def extract_anvs(self, f_xml_filename):
        """
        Extract the aircraft that were created by the core-gui.

        :param f_xml_filename: XML file name.
        :return: None.
        """

        # Creates QFile for XML file.
        l_data_file = QtCore.QFile(f_xml_filename)
        assert l_data_file is not None

        # Opens the XML file.
        l_data_file.open(QtCore.QIODevice.ReadOnly)

        # Creates the XML document.
        l_xdoc_aer = QtXml.QDomDocument("scenario")
        assert l_xdoc_aer is not None

        l_xdoc_aer.setContent(l_data_file)

        # Closes the file.
        l_data_file.close()

        # Gets the document's root element.
        l_elem_root = l_xdoc_aer.documentElement()
        assert l_elem_root is not None

        l_index = 0

        # Creates a list of elements.
        l_node_list = l_elem_root.elementsByTagName("host")

        l_table_list = []

        # For all nodes in the list...
        for li_ndx in xrange(l_node_list.length()):

            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            if "host" != l_element.tagName():
                continue

            # Read identification if available
            if l_element.hasAttribute("id"):
                ls_host_id = l_element.attribute("id")

            # Get the first node of the subtree
            l_node = l_element.firstChild()
            assert l_node is not None

            lv_host_ok = False

            # Traverses the subtree
            while not l_node.isNull():
                # Attempts to convert the node to an element.
                l_element = l_node.toElement()
                assert l_element is not None

                # Is the node an element ?
                if not l_element.isNull():
                    if "type" == l_element.tagName():
                        if "aircraft" == l_element.text():
                            # Parse the element.
                            lv_host_ok = True

                        else:
                            break

                    if "point" == l_element.tagName():
                        # Parse the element.
                        lf_host_lat = float(l_element.attribute("lat"))
                        lf_host_lng = float(l_element.attribute("lon"))

                    if "alias" == l_element.tagName():
                        if l_element.hasAttribute("domain"):
                            if "COREID" == l_element.attribute("domain"):
                                li_ntrf = int(l_element.text())

                # Next node
                l_node = l_node.nextSibling()
                assert l_node is not None

            # Did you find the aircraft ?
            if lv_host_ok:
                l_table_item = {"node": str(ls_host_id), "latitude": lf_host_lat, "longitude": lf_host_lng,
                                "designador": "B737", "ssr": str(7001 + l_index),
                                "indicativo": "{}X{:03d}".format(str(ls_host_id[:3]).upper(), l_index + 1),
                                "origem": "SBGR", "destino": "SBBR", "proa": 60, "velocidade": 500,
                                "altitude": 2000, "procedimento": "TRJ200", "id": str(li_ntrf)}

                l_table_list.append(l_table_item)

                # Increment the line counter
                l_index += 1

        return l_table_list


    # ---------------------------------------------------------------------------------------------
    def get_list_core_ptracks(self):
        """

        :return:
        """
        llst_core = self.core_mngr.get_file_list()
        llst_ptracks = self.track_mngr.get_file_list()

        return llst_core, llst_ptracks

    # ---------------------------------------------------------------------------------------------
    def get_scenario_filename(self):
        """
        Returns the file name of the simulation scenario.

        :return: string, the file name.
        """

        return self.scenario_filename


    # ---------------------------------------------------------------------------------------------
    def get_track_generator_dir(self):
        """
        Returns the rooot directory of the sytem

        :return: string, the root directory.
        """

        return self.track_mngr.get_root_dir()


    # ---------------------------------------------------------------------------------------------
    def run_browser_dump1090(self):
        """
        Runs a web browser to view the ADS-B data generated by the simulation of the ATN scenario.

        :return: None.
        """

        l_browser_ok = False

        # Gets a list of the numbers of nodes running the Dump1090 service
        l_node_number = self.core_mngr.get_nodes_dump1090()

        if len(l_node_number) > 0:
            l_control_net = self.core_mngr.get_control_net()
            # Calculates the available addresses for each node in the CORE control network
            net = ipcalc.Network(str(l_control_net))

            lst_ip = []
            for ip in net:
                lst_ip.append(str(ip))

            i = 0
            browser = web.get('firefox')
            while i < len(l_node_number):
                # gets the IP address of the Dump1090 node.
                ip_dump1090 = lst_ip[l_node_number[i]]
                url = "http://" + str(ip_dump1090) + ":8080"
                # Open a tab in the browser with the Dump1090 service url.
                browser.open_new_tab(url)
                i = i + 1

            l_browser_ok = True

        if not l_browser_ok:
            self.wmain.show_message("Start browser Dump1090",
                                    "There is no Dump1090 service running on CORE!")


    # ---------------------------------------------------------------------------------------------
    def run_core_gui_edit_mode(self):
        """
        Calls the core-gui in edit mode for the construction of the simulation scneario.

        :return: None.
        """

        self.logger.info("Run core-gui in edit mode")
        self.core_mngr.run_gui_edit_mode()


    # ---------------------------------------------------------------------------------------------
    def run_core_gui_exec_mode(self):
        """
        Calls the core-gui in run mode to run the chosen simulation scenario. It also runs
        the Track Generator (ptracks) for the chosen simulation scenario. If there is no simulation
        scenario for the Track Generator, it creates the necessary files, following a standard
        template, to run the program.

        :return: None.
        """

        l_button_text = self.wmain.get_text_button_start_session()

        if l_button_text == "Pause ATN simulation":
            self.wmain.change_text_button_start_session(f_play=True)

            self.set_state_simulation(f_state=True)

            l_status_msg = "The scenario: " + self.scenario_filename + " has been paused!"
            self.wmain.show_message_status_bar(l_status_msg)

            # Send the pause message to the Track Generator (ptracks)
            self.track_mngr.send_pause_message()
            return

        self.wmain.change_text_button_start_session()

        if self.state_simulation():
            self.set_state_simulation(f_state=False)

            l_status_msg = "Running the scenario: " + self.scenario_filename
            self.wmain.show_message_status_bar(l_status_msg)

            # Send the play message to the Track Generator (ptracks)
            self.track_mngr.send_play_message()

            return

        # Get the simulation scenario filename
        l_scenario_filename_path = self.wmain.get_scenario_filename(self.core_mngr.get_scenario_dir())

        self.logger.debug("Scenario filename path %s" % l_scenario_filename_path)

        # No file selected, finishes processing
        if not l_scenario_filename_path:
            self.wmain.change_text_button_start_session(f_play=True)
            return

        # Parse the XML file to find the nodes that are Dump1090 servers, the address of
        # the CORE control network and CORE reference point
        self.core_mngr.parse_xml_file(l_scenario_filename_path)

        # Get the name of the simulation file without its extension
        self.scenario_filename = os.path.splitext(os.path.basename(str(l_scenario_filename_path)))[0]

        # Verifiy that the files needed to run the Track Generator exist
        if not self.track_mngr.check_files(self.scenario_filename):
            if self.wmain.get_aircrafts_data(self.scenario_filename,
                                             self.extract_anvs(l_scenario_filename_path),
                                             self.track_mngr.get_traf_filename()):
                # Creates the file for Track Generator
               self.track_mngr.create_file(self.wmain.get_dialog_data())

            else:
                # File was not created,it restores the initial conditions and leaves the execution
                # of the simulation scenario.
                self.wmain.change_text_button_start_session(f_play=True)
                return

        # Runs core-gui in run mode
        self.core_mngr.run_gui_exec_mode(l_scenario_filename_path)

        # Runs the Track Generator
        self.track_mngr.run()

        # Displays the message in the status bar
        l_status_msg = "Running the scenario: " + self.scenario_filename
        self.wmain.show_message_status_bar(l_status_msg)

        # Disable the menu option for create
        self.wmain.enable_button_edit_mode(False)

        # Enables the menu options for an active ATN simulation
        self.wmain.enabled_actions(True)


    # ---------------------------------------------------------------------------------------------
    def run_track_generator_database_manager(self):
        """
        Runs an application to manage the database (dbedit) of the Track Generator (ptracks)

        :return: None.
        """
        # If there is a process started and not finalized, its processing ends.
        if self.track_mngr.get_database_manager_process():
            l_ret_code = self.track_mngr.is_database_manager_running()
            if l_ret_code is None:
                self.wmain.show_message("Manage Exercises", "The exercise manager is already running!")
                return

        self.track_mngr.run_database_manager()

        # Show message in the GUI status bar
        self.wmain.show_message_status_bar("Starting editing the ptracks database!")


    # ---------------------------------------------------------------------------------------------
    def run_track_generator_pilot(self):
        """
        Runs an application to pilot the aircraft of the Track Generator (ptracks)

        :return: None.
        """

        self.track_mngr.run_pilot()


    # ---------------------------------------------------------------------------------------------
    def run_track_generator_view(self):
        """
        Runs an application(visil) to display the data generated by the Track Generator (ptracks).

        :return: None.
        """

        self.track_mngr.run_visil()


    # ---------------------------------------------------------------------------------------------
    def set_state_simulation(self, f_state=False):
        """
        Sets the state of the simulation.

        :param f_state: True simualtion is running otherwise is paused.
        :return: None.
        """

        self.is_simulation_pause = f_state


    # ---------------------------------------------------------------------------------------------
    def show_gui(self):
        """
        Displays the main window of the app.

        :return: None.
        """

        self.logger.info("Show GUI")
        self.wmain.show()


    # ---------------------------------------------------------------------------------------------
    def state_simulation(self):
        """
        Returns the state of simulation.

        :return: bool, True the simulation is running otherwise paused.
        """

        return self.is_simulation_pause


    # ---------------------------------------------------------------------------------------------
    def stop_atn_simulation(self):
        """
        Stop the ATN simulator.

        :return: None.
        """

        # Gets the execution mode of the core-gui.
        l_core_gui_mode = self.core_mngr.get_mode()

        # Stop core-gui.
        self.core_mngr.stop_session()

        # Enables the actions to create scenario and start ATN simulation.
        self.wmain.enable_button_edit_mode(True)

        # Disables actions for an active ATN simulation
        self.wmain.enabled_actions(False)

        self.set_state_simulation(False)

        if self.core_mngr.RUN_MODE == l_core_gui_mode:
            # End the initiated processes
            self.track_mngr.stop_processes()

        # Clears the GUI status bar
        self.wmain.clear_status_bar()

        # Restore icons and action text.
        self.wmain.change_text_button_start_session(f_play=True)


    # ---------------------------------------------------------------------------------------------
    def terminate_processes(self, f_edit_mode=False):
        """
        Ends the processes.

        :return: None.
        """

        self.logger.info("Clear the status bar")
        self.wmain.clear_status_bar()

        self.logger.info("Reset menu options")
        self.wmain.reset_menu_options()

        self.set_state_simulation(False)

        if f_edit_mode is False:
            # Stop processes.
            self.track_mngr.stop_processes()


# < the end >--------------------------------------------------------------------------------------
