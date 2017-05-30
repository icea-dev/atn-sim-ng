#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
wnd_main_atn_sim

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
from core.api import coreapi

import os
import logging
import socket
import subprocess
import wnd_main_atn_sim_ui as wmain_ui
import dlg_trf as dtraf_ui
import dlg_start as dstart_ui
import dlg_trf_run_time as dtraf_run_time_ui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


module_logger = logging.getLogger('main_app.wnd_main_atn_sim')


# < class CWndMainATNSim >-------------------------------------------------------------------------


class CWndMainATNSim(QtGui.QMainWindow, wmain_ui.Ui_CWndMainATNSim):
    """
    DOCUMENT ME!
    """

    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        # init super class
        super(CWndMainATNSim, self).__init__(f_parent)

        self.logger = logging.getLogger("main_app.wnd_main_atn_sim.CWndMainATNSim")
        self.logger.info("Creating instance of CWndMainATNSim")

        # create main menu ui
        self.setupUi(self)

        # Mediator
        self.mediator = f_mediator

        # Desabilita as ações para a sessão em tempo de execução
        self.enabled_actions(False)

        self.act_scenario_to_xml.setEnabled(False)
        self.act_scenario_to_exe.setEnabled(False)

        # create signal and slots connections
        self.act_edit_scenario.triggered.connect(self.cbk_start_edit_mode)
        self.act_start_session.triggered.connect(self.cbk_start_session)
        self.act_stop_session.triggered.connect(self.cbk_stop_session)
        self.act_start_dump1090.triggered.connect(self.cbk_start_dump1090)
        self.act_start_pilot.triggered.connect(self.cbk_start_pilot)
        self.act_start_visil.triggered.connect(self.cbk_start_visil)

        self.act_db_edit.triggered.connect(self.cbk_start_db_edit)

        self.act_add_aircraft.triggered.connect(self.cbk_add_acft_run_time)

        self.act_quit.triggered.connect(QtGui.QApplication.quit)

        self.dlg_traf = dtraf_ui.CDlgTraf(f_ptracks_dir=self.mediator.get_track_generator_dir())

        self.dlg_start = dstart_ui.CDlgStart()

        self.dlg_traf_run_time = dtraf_run_time_ui.CDlgTrafRunTime()

        # Icons
        self.iconPause = QtGui.QIcon()
        self.iconPause.addPixmap(QtGui.QPixmap(_fromUtf8(":/gui/pause-session-2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconPlay = QtGui.QIcon()
        self.iconPlay.addPixmap(QtGui.QPixmap(_fromUtf8(":/gui/start-session-2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)


    # ---------------------------------------------------------------------------------------------
    def show_message_status_bar(self, message):
        """
        Displays a message in the application status bar.

        :param message: the message.

        :return: None.
        """
        self.statusbar.showMessage(message)


    # ---------------------------------------------------------------------------------------------
    def clear_status_bar(self):
        """
        Clears messages from the apllication status bar.

        :return: None.
        """
        self.statusbar.clearMessage()


    # ---------------------------------------------------------------------------------------------
    def reset_menu_options(self):
        """
        Resets the application menu options.

        :return: None.
        """

        if self.act_start_session.isEnabled() is False:
            self.act_start_session.setEnabled(True)

        if self.act_edit_scenario.isEnabled() is False:
            self.act_edit_scenario.setEnabled(True)

        # Disables the menu options for the run mode of the simulation scenario.
        self.enabled_actions(False)

        self.change_text_button_start_session(f_play=True)


    # ---------------------------------------------------------------------------------------------
    def enable_button_edit_mode(self, f_status):
        """
        Enables or disables the menu option that starts the core-gui in edit mode.
        :param f_status: True enable, False disable
        :return: None.
        """
        self.act_edit_scenario.setEnabled(f_status)


    # ---------------------------------------------------------------------------------------------
    def get_text_button_start_session(self):
        """
        Get the text of the menu note from starting the simulation.

        :return: string, the text.
        """
        return self.act_start_session.text()


    # ---------------------------------------------------------------------------------------------
    def change_text_button_start_session(self, f_play=False):
        """
        Change icon and menu note text freeze(pause) and unfreeze(play) exercise.

        :return: None.
        """

        if f_play is True:
            self.act_start_session.setIcon(self.iconPlay)
            self.act_start_session.setText("Start ATN simulation")
        else:
            self.act_start_session.setIcon(self.iconPause)
            self.act_start_session.setText("Pause ATN simulation")


    # ---------------------------------------------------------------------------------------------
    def get_scenario_filename(self, f_scenario_dir):
        """
        Gets the simulation scenario file in XML.

        :param: f_scenario_dir: directory where you find the simulation scenario files.

        :return: the scenario filename.
        """

        # Selects the simulation scenario file in XML
        l_scenario_filename = QtGui.QFileDialog.getOpenFileName(self, 'Open simulation scenario - XML',
                                                                f_scenario_dir, 'XML files (*.xml)')
        return l_scenario_filename


    # ---------------------------------------------------------------------------------------------
    def get_aircrafts_data(self, f_title, f_data_table, f_filename):
        """
        Gets the data entered by the user of the aircraft created in the core-gui at edit mode.

        :param f_title: the title of the dialog window.
        :param f_data_table: the aircraft's default data.
        :param: f_filename: the filename to be created

        :return: True , if the user decided to create the traffic file otherwise False.
        """

        # Displays the default aircraft data (f_data_table) in the dialog window
        self.dlg_traf.populate_table(f_data_table)

        # Sets the title of the dialog window
        self.dlg_traf.set_title(f_title)

        # Open the dialog window
        l_ret_val = self.dlg_traf.exec_()

        if QtGui.QDialog.Rejected == l_ret_val:
            l_msg = QtGui.QMessageBox()
            l_msg.setIcon(QtGui.QMessageBox.Critical)
            l_msg_text = "Error creating file: %s" % f_filename
            l_msg.setText(l_msg_text)
            l_msg.setWindowTitle("Start Session")
            l_msg.setStandardButtons(QtGui.QMessageBox.Ok)
            l_msg.exec_()
            return False

        return True


    # ---------------------------------------------------------------------------------------------
    def get_dialog_data(self):
        """
        Gets the user-supllied data of aircraft created through the core-gui in edit mode.

        :return: List of dictionaries with the information needed to create the traffic file.
        """
        return self.dlg_traf.get_data()


    # ---------------------------------------------------------------------------------------------
    def enabled_actions(self, status):
        """
        Habilita ous desabilita as ações do menu para o core-gui em tempo de execução da simulação do
        cenário.

        :param status: True habilita a ação e False desbilita.
        :return:
        """

        # Desabilita as ações para uma simulação ATN ativa
        self.act_stop_session.setEnabled(status)
        self.act_start_dump1090.setEnabled(status)
        self.act_start_visil.setEnabled(status)
        self.act_start_pilot.setEnabled(status)
        self.act_add_aircraft.setEnabled(status)


    # ---------------------------------------------------------------------------------------------
    def show_message(self, f_title, f_text):
        """

        :param f_title:
        :param f_text:
        :return:
        """
        l_msg = QtGui.QMessageBox()
        l_msg.setIcon(QtGui.QMessageBox.Information)
        l_msg.setText(f_text)
        l_msg.setWindowTitle(f_title)
        l_msg.setStandardButtons(QtGui.QMessageBox.Ok)
        l_msg.exec_()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_edit_mode(self):
        """
        Callback to run core-gui in edit mode.

        :return:
        """
        # Is there a mediator ?
        if self.mediator:
            self.mediator.run_core_gui_edit_mode()

            # Displays the message in the status bar of the GUI
            self.statusbar.showMessage("Starting core-gui in edit mode!")

            # desable the action of strating the simulation scenario
            self.act_start_session.setEnabled(False)
            self.act_edit_scenario.setEnabled(False)


    # ---------------------------------------------------------------------------------------------
    def cbk_start_session(self):
        """
        Start the simulation of a particular simulation scenario.

        :return: None.
        """

        # Is there a mediator ?
        if self.mediator:
            self.mediator.run_core_gui_exec_mode()


    # ---------------------------------------------------------------------------------------------
    def cbk_stop_session(self):
        """
        Stop running session

        :return:
        """
        # Is there a mediator ?
        if self.mediator:
            self.mediator.stop_atn_simulation()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_dump1090(self):
        """
        Inicia o firefox para apresentar os dados ADS-B enviados ao aplicativo Dump1090
        :return:
        """
        # Is there a mediator ?
        if self.mediator:
            self.mediator.run_browser_dump1090()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_pilot(self):
        """
        Starts the Track Generator pilot

        :return: None.
        """

        # Is there a mediator ?
        if self.mediator:
            self.mediator.run_track_generator_pilot()


    # ---------------------------------------------------------------------------------------------
    def cbk_start_visil(self):
        """
        Starts the Track Generator view

        :return: None;
        """

        # Is there a mediator ?
        if self.mediator:
            self.mediator.run_track_generator_view()


    # ---------------------------------------------------------------------------------------------
    def cbk_add_acft_run_time(self):
        """

        :return:
        """

        # Coloca o nome do arquivo do cenário de simulação na barra de título da janela de diálogo.
        self.dlg_traf_run_time.set_title(self.filename)

        # Abre a janela de diálogo
        l_ret_val = self.dlg_traf_run_time.exec_()

        # Verifica o código de retorno da janela de diálogo, caso desista da operação
        # Avisa o usuário do erro de criação do tráfego em tempo de execução.
        #if QtGui.QDialog.Accepted == l_ret_val:
            # Cria o arquivo de tráfegos para o ptracks.
            #self.create_ptracks_traf(self.dlg_traf.get_data(), f_traf_filename)
            #return True


    # ---------------------------------------------------------------------------------------------
    def cbk_start_db_edit(self):
        """
        Starts the Track Generator database manager
        :return: None.
        """
        if self.mediator:
            self.mediator.run_track_generator_database_manager()


# < the end>---------------------------------------------------------------------------------------
