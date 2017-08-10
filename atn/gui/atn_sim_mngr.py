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
import time

import core_mngr as coremngr
import parser_utils as parser
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
    def create_core_scenario(self, f_ptracks_filename):
        """

        :param f_core_filename:
        :return:
        """
        # Create a simulation scenario demo file for CORE
        self.core_mngr.create_scenario(f_ptracks_filename)

        # Get a list of aircraft data from the Track Generator exercise
        llst_aircraft = self.track_mngr.get_traf_data(f_ptracks_filename)

        # Run the core-gui with simulation scenario demo file
        self.core_mngr.run_gui_edit_mode(f_ptracks_filename)

        # Wait ...
        time.sleep(5)

        # Default values for the CORE reference point
        ls_alt = "2.0"
        ls_lat = "-13.869227"
        ls_lon = "-49.918091"
        ls_scale = "50000.0"
        ls_ref_pt = "0|0|{}|{}|{}|{}".format(ls_lat, ls_lon, ls_alt, ls_scale)

        # Adds aircraft to CORE
        for ldct_aircrfat_data in llst_aircraft:
            li_node_number = int(ldct_aircrfat_data['node']) + 2

            ldct_wlan_data = {}
            ldct_wlan_data['wlan_number'] = 1
            ldct_wlan_data['address_ip4'] = "10.0.0.{}/24".format(li_node_number)
            ldct_wlan_data['address_ip6'] = "2001::1/128".format(li_node_number)

            self.core_mngr.add_node_run_time(f_aircraft_data=ldct_aircrfat_data,
                                             f_wlan_data=ldct_wlan_data,
                                             fs_ref_pt=ls_ref_pt)

            time.sleep(1)

        ls_msg = "OK"

        return ls_msg


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
                                "altitude": 2000, "procedimento": "TRJ200", "temptrafego": 0, "id": str(li_ntrf)}

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
    def parser_trf_xml(self, fs_trf_pn):
        """
        carrega o arquivo de tráfego

        @param fs_trf_pn: pathname do arquivo em disco
        """
        # check input
        assert fs_trf_pn

        # cria o QFile para o arquivo XML do tráfego
        l_data_file = QtCore.QFile(fs_trf_pn)
        assert l_data_file is not None

        # abre o arquivo XML do tráfego
        l_data_file.open(QtCore.QIODevice.ReadOnly)

        # erro na abertura do arquivo ?
        if not l_data_file.isOpen():
            return None

        # cria o documento XML do tráfego
        l_xdoc_trf = QtXml.QDomDocument("trafegos")
        assert l_xdoc_trf is not None

        # erro na carga do documento ?
        if not l_xdoc_trf.setContent(l_data_file):
            # fecha o arquivo
            l_data_file.close()

            return None

        # fecha o arquivo
        l_data_file.close()

        # obtém o elemento raíz do documento
        l_elem_root = l_xdoc_trf.documentElement()
        assert l_elem_root is not None

        # faz o parse dos atributos do elemento raíz
        ldct_root = parser.parse_root_element(l_elem_root)

        # cria uma lista com os elementos de tráfego
        l_node_list = l_elem_root.elementsByTagName("trafego")

        llst_aircraft_ptracks = []

        # para todos os nós na lista...
        for li_ndx in xrange(l_node_list.length()):
            # inicia o dicionário de dados
            ldct_data = {}

            # obtém um nó da lista
            l_element = l_node_list.at(li_ndx).toElement()
            assert l_element is not None

            # read identification if available
            if l_element.hasAttribute("nTrf"):
                ldct_data["nTrf"] = int(l_element.attribute("nTrf"))

            # obtém o primeiro nó da sub-árvore
            l_node = l_element.firstChild()
            assert l_node is not None

            # percorre a sub-árvore
            while not l_node.isNull():
                # tenta converter o nó em um elemento
                l_element = l_node.toElement()
                assert l_element is not None

                # o nó é um elemento ?
                if not l_element.isNull():
                    # atualiza o dicionário de dados
                    ldct_data.update(parser.parse_trafego(l_element))

                # próximo nó
                l_node = l_node.nextSibling()
                assert l_node is not None

            # carrega os dados de tráfego a partir de um dicionário
            llst_aircraft_ptracks.append(ldct_data)

        return llst_aircraft_ptracks


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
        l_scenario_core = l_scenario_filename_path.replace('xml', 'imn')
        self.core_mngr.run_gui_exec_mode(l_scenario_core)

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
    def sync_atn_simulator(self, f_core_filename):
        """
        The method synchronize the CORE database and the Track generator (ptracks).

        :param f_core_filename: CORE simulation scenario.
        :return: None if the synchronization of the database was successfully performed otherwise
        an error message.
        """
        # Creates the full file name path of the CORE simulation scenario.
        ls_scenario_pn = self.core_mngr.get_scenario_dir() + "/" + f_core_filename + ".xml"

        # Gets the aircraft data from the CORE simulation scenario
        llst_aircraft_core = self.extract_anvs(ls_scenario_pn)

        # File of ptracks aircraft of the chosen CORE simulation scenario exists in the database ?
        if self.track_mngr.check_files(f_core_filename):
            # File exists, get dadta from ptracks aircraft
            llst_aircraft_ptracks = self.parser_trf_xml(self.track_mngr.get_traf_filename())

            llst_aircraft_core_new = []

            for dct_aircraft_core in llst_aircraft_core:
                li_trf = int(dct_aircraft_core['id'])
                for d_ptracks in llst_aircraft_ptracks:
                    if li_trf == int(str(d_ptracks['nTrf'])):
                        dct_aircraft_core['designador'] = str(d_ptracks['designador'])
                        dct_aircraft_core['ssr'] = str(d_ptracks['ssr'])
                        dct_aircraft_core['indicativo'] = str(d_ptracks['indicativo'])
                        dct_aircraft_core['origem'] = str(d_ptracks['origem'])
                        dct_aircraft_core['destino'] = str(d_ptracks['destino'])
                        dct_aircraft_core['procedimento'] = str(d_ptracks['procedimento'])
                        dct_aircraft_core['proa'] = float(str(d_ptracks['proa']))
                        dct_aircraft_core['velocidade'] = float(str(d_ptracks['velocidade']))
                        dct_aircraft_core['altitude'] = float(str(d_ptracks['altitude']))
                        dct_aircraft_core['latitude'] = float(str(d_ptracks['coord']['cpoA']))
                        dct_aircraft_core['longitude'] = float(str(d_ptracks['coord']['cpoB']))
                        dct_aircraft_core['temptrafego'] = int(str(d_ptracks['temptrafego']))

                        break;

                llst_aircraft_core_new.append(dct_aircraft_core.copy())

            llst_aircraft_core = []
            llst_aircraft_core = list(llst_aircraft_core_new)

        # Displays the GUI to create the file in ptracks database.
        if self.wmain.get_aircrafts_data(f_core_filename,
                                         llst_aircraft_core,
                                         self.track_mngr.get_traf_filename()):
            # Creates the file for Track Generator
            self.track_mngr.create_file(self.wmain.get_dialog_data())
            return True

        return False


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


    # ---------------------------------------------------------------------------------------------
    def update_core_scenario(self, f_core_filename):
        """

        :param f_core_filename:
        :return:
        """
        ls_msg = "OK"

        return ls_msg

# < the end >--------------------------------------------------------------------------------------
