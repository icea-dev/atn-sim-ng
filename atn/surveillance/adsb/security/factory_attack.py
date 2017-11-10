#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
Copyright 2016, ICEA

This file is part of atn-sim

atn-sim is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

atn-sim is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/oct  matiasims
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import logging
from .flasher import Flasher
from .evil_twin import EvilTwin
from .evil_twin_kinematics import EvilTwinKinematics
from .evil_twin_callsign import EvilTwinCallsign
from .flooding import Flooding

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/10"


M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

class FactoryAttack():
    """
    Classe responsável por implementar a operação de criação de ataques cibernéticos reais.

    """

    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def createCyberAttack(fs_type=None):
        """
        Cria um cyber ataque definido em fs_type.
        
        :param fs_type: o tipo de ataqtue cibernético
        :return lo_abstract_attack: um objeto do tipo AbstractAttack
        """
        M_LOG.info(">> FactoryAttack.createCyberAttack : %s" % fs_type)

        if fs_type == 'Flasher':
            return Flasher()
        elif fs_type == 'EvilTwin':
            return EvilTwin()
        elif fs_type == 'EvilTwinKinematics':
            return EvilTwinKinematics()
        elif fs_type == 'EvilTwinCallsign':
            return EvilTwinCallsign()
        elif fs_type == 'Flooding':
            return Flooding()

        M_LOG.info("<< FactoryAttack.createCyberAttack : None")

        return None


# < the end >--------------------------------------------------------------------------------------
