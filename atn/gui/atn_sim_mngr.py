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
import logging

import wnd_main_atn_sim as wmain
import core_mngr as coremngr
import track_generator_mngr as trackmngr

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


    # ---------------------------------------------------------------------------------------------
    def show_gui(self):
        """

        :return:
        """
        self.logger.info("Show GUI")
        self.wmain.show()


    # ---------------------------------------------------------------------------------------------
    def run_core_gui_edit_mode(self):
        """
        Calls the core-gui in edit mode for the construction of the simulation scneario.

        :return:
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

        :return:
        """
        l_button_text = self.wmain.get_text_button_start_session()

        if l_button_text == "Pause ATN simulation":
            self.wmain.change_text_button_start_session(f_play=True)

            self.set_state_simulation(f_state=True)

            l_status_msg = "The scenario: " + self.filename + " has been paused!"
            self.wmain.show_message_status_bar(l_status_msg)

            # Send the pause message to the Track Generator (ptracks)
            self.track_mngr.send_pause_message()
            return

        self.wmain.change_text_button_start_session()

        if self.state_simulation():
            self.set_state_simulation(f_state=False)

            l_status_msg = "Running the scenario: " + self.filename
            self.wmain.show_message_status_bar(l_status_msg)

            # Send the play message to the Track Generator (ptracks)
            self.track_mngr.send_play_message()

            return

        # Get the simulation scenario filename
        l_scenario_filename_path = self.wmain.get_scenario_filename(self.core_mngr.get_scenario_dir())

        # No file selected, finishes processing
        if not l_scenario_filename_path:
            self.wmain.change_text_button_start_session(f_play=True)

        # Parse the XML file to find the nodes that are Dump1090 servers and the address of
        # the CORE control network
        self.core_mngr.parse_xml_file(l_scenario_filename_path)

        # Agora chamar o track_mngr eecute ptracks
        # Chamar do core o execute core gui in run mode

        # Obtém o nome do arquivo do cenário de simulação sem a extensão.
        self.filename = os.path.splitext(os.path.basename(str(l_file_path)))[0]

        # Monta o diretório de arquivos do ptracks
        l_exe_filename = self.ptracks_data_dir + "/exes/" + self.filename  + ".exe.xml"

        # Cria o arquivo de exercicio para o cenário escolhido caso ele não exista.
        if not os.path.isfile(l_exe_filename):
            self.create_ptracks_exe(l_exe_filename)

        # Monta o nome do arquivo de tráfego do ptracks para o cenário de simulação escolhido
        l_traf_filename = self.ptracks_data_dir + "/traf/" + self.filename + ".trf.xml"

        # Não existe um arquivo de tráfego para o cenário de simulação escolhido, cria ...
        if not os.path.isfile(l_traf_filename):
            l_ret_val = self.create_new_ptracks_traf( l_file_path, l_traf_filename )

            # Arquivo de tráfego para o ptracks não foi criado, abandona a execução do
            # cenário de simulação, avisa do erro !
            if not l_ret_val:
                self.act_start_session.setIcon(self.iconPlay)
                self.act_start_session.setText("Start ATN simulation")
                return

        # Monta o nome da sessão que será executada no core-gui
        l_split = l_file_path.split('/')
        self.session_name = l_split [ len(l_split) - 1 ]

        # Executa o core-gui
        self.p = subprocess.Popen(['core-gui', '--start', l_file_path ],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Executar o ptracks .....
        l_cur_dir = os.getcwd()
        os.chdir(self.ptracks_dir)
        self.adapter = subprocess.Popen(['python', 'adapter.py'], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        self.ptracks = subprocess.Popen(['python', 'newton.py', '-e', self.filename, '-c', str(self.canal)],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        os.chdir(l_cur_dir)

        # Apresenta as mensagens na barra de status
        l_status_msg = "Running the scenario: " + self.filename
        self.statusbar.showMessage(l_status_msg)

        # Timer para verificar se o processo foi finalizado pelo core-gui.
        self.check_process()

        # Desabilita as ações de criar cenario e iniciar a simulação ATN
        self.act_edit_scenario.setEnabled(False)

        # Habilita as ações para uma simulação ATN ativa
        self.enabled_actions(True)


    # ---------------------------------------------------------------------------------------------
    def pause_atn_simulator(self):
        """
        Pause the ATN simulator.

        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def stop_atn_simulation(self):
        """
        Stop the ATN simulator.

        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def run_browser_dump1090(self):
        """
        Runs a web browser to view the ADS-B data generated by the simulation of the ATN scenario.

        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def run_display_track_generator(self):
        """
        Runs an application(visil) to display the data generated by the Track Generator (ptracks).

        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def run_pilot_track_generator(self):
        """
        Runs an application to pilot the aircraft of the Track Generator (ptracks)
        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def run_database_manager_track_generator(self):
        """
        Runs an application to manage the database (dbedit) of the Track Generator (ptracks)
        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def add_aircraft_exec_mode(self):
        """
        Creates an aircraft in the runtime simulation scenario.
        :return:
        """
        pass


    # ---------------------------------------------------------------------------------------------
    def terminate_processes(self, f_edit_mode=False):
        """

        :return:
        """
        self.logger.info("Clear the status bar")
        self.wmain.clear_status_bar()

        self.logger.info("Reset menu options")
        self.wmain.reset_menu_options()

        #if f_edit_mode is False:
            # Finaliza os processos iniciados.
            #self.kill_processes()
            #self.track_mngr.kil_processes()


    # ---------------------------------------------------------------------------------------------
    def set_state_simulation(self, f_state=False):
        """

        :param f_state:
        :return:
        """
        self.is_simulation_pause = f_state


    # ---------------------------------------------------------------------------------------------
    def state_simulation(self):
        """

        :return:
        """
        return self.is_simulation_pause


# < the end >--------------------------------------------------------------------------------------