#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
This file is part of atn-sim

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

revision 0.1  2017/Jul  Matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/07"

# < imports >--------------------------------------------------------------------------------------
import binascii
import ConfigParser
import logging
import math
import netifaces
import os
import threading
import time
import socket

from collections import deque

from ...network import mcast_socket
from ..asterix import asterix_utils
from ... import core_utils
from ... import emane_utils
from ... import geo_utils


M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)
M_LOG_FILE = "radar.log"


# < class Radar >----------------------------------------------------------------------------------
class Radar:

    """
    This class emulates the functionality of the radar
    """
    FT_TO_M = 0.3048
    M_TO_FT = 3.28084
    M_TO_NM = 0.000539957
    NM_TO_M = 1852
    MPS_TO_KT = 1.94384
    KT_TO_MPS = 0.51444444444
    DEG_SETOR = 11.25

    # PSR default values
    SWEEP_TIME = 4.0
    VERTICAL_COVERAGE = 60000.0
    PSR_HORIZONTAL_COVERAGE = 80.0 * NM_TO_M
    SSR_HORIZONTAL_COVERAGE = 200.0 * NM_TO_M

    # Default values
    NET_IFACE = "ctrl0"
    NET_PTRACKS_PORT = 1970
    NET_PTRACKS_GROUP = "235.12.2.4"
    NET_IP_DEFAULT = "172.16.0.255"
    NET_PORT_DEFAULT = 20000

    # ASTERIX Data Source Identifier
    SAC = 232  # E8: Brazil
    SIC = 0


    # -----------------------------------------------------------------------------------
    def __init__(self, fs_config="radar.cfg"):
        """
        Initialize attributes of class
        """
        # logger
        M_LOG.info("__init__:>>")

        #
        self.__f_latitude = 0.0
        self.__f_longitude = 0.0
        self.__f_altitude = 0.0

        # Radar parameters
        self.__f_sweep_time = self.SWEEP_TIME
        self.__f_vertical_coverage = self.VERTICAL_COVERAGE
        self.__f_psr_horizontal_coverage = self.PSR_HORIZONTAL_COVERAGE
        self.__f_ssr_horizontal_coverage = self.SSR_HORIZONTAL_COVERAGE

        # Network parameters
        self.__s_net_ip = self.NET_IP_DEFAULT
        self.__i_net_port = self.NET_PORT_DEFAULT

        # List of aircraft
        self.__tracks = {}

        # Message Queue
        self.__q_queue = deque([])

        # sock (socket):  The end point to send ASTERIX CAT 21.
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # ASTERIX Data Source Identifier
        self.__i_sac = self.SAC
        self.__i_sic = self.SIC

        # load configuration file
        self.__load_config(fs_config)

        # logger
        M_LOG.info("__init__:<<")


    # ---------------------------------------------------------------------------------------------
    def __broadcast_asterix(self, fi_sector, fb_north_flag=False):

        # sac = 232
        # sic = 10
        # logger
        #M_LOG.info("__boradcast_asterix:>>")

        ltt_time_of_day = time.time()

        ldct_sector_record = {
            444: {'MsgTyp': 2},
            10: {'SAC': self.__i_sac, 'SIC': self.__i_sic},
            20: {'Azi': (fi_sector * 11.25)},
            30: {'ToD': ltt_time_of_day}
        }

        ldct_north_record = {
            444: {'MsgTyp': 2},
            10: {'SAC': self.__i_sac, 'SIC': self.__i_sic},
            30: {'ToD': (ltt_time_of_day + 0.867)},
            41: {'RotS': 4},
            # 50: {'COM_presence': 1, 'PSR_presence': 1, 'MDS_presence': 1, 'fx': 0,
            #      # COM
            #      'NOGO': 0, 'RDPC': 0, 'RDPR': 0, 'OVL RDP COM': 0, 'OVL XMT': 0, 'MSC COM': 0, 'TSV': 0,
            #      # PSR
            #      'ANT PSR': 0, 'CHAB PSR': 3, 'OVL': 0, 'OVL RDP': 0, 'MSC PSR': 0,
            #      # MDS
            #      'ANT': 0, 'CHAB': 1, 'OVL_SUR': 0, 'MSC': 0, 'SCF': 0, 'DLF': 0, 'OVL SCF': 0, 'OVL DLF': 0,
            #      }

        }

        # 0: nodenum,
        # 1: x * self.M_TO_NM,
        # 2: y * self.M_TO_NM,
        # 3: z * self.M_TO_FT,
        # 4: azimuth,
        # 5: speed * self.MPS_TO_KT,
        # 6: ssr,
        # 7: callsign,
        # 8: sector
        # 9: theta (h_angle)

        llst_detected_tracks = []

        M_LOG.info("__broadcast_asterix:  tracks detected before [%d]" % len(llst_detected_tracks))
        for li_track_number, ldct_track in self.__tracks.items():

            if ldct_track['sector'] != fi_sector:
                continue

            if ldct_track['detect'] is False:
                continue

            M_LOG.debug ("__broadcast_asterix:  sector actual [%d] track sector [%d]" % (fi_sector, ldct_track['sector']))
            M_LOG.debug ("__broadcast_asterix:  track ssr [%s] rho [%f]" % (ldct_track['ssr'], ldct_track['rho']))
            li_spi = 0
            if ldct_track['spi'] is True:
                li_spi = 1

            ldct_track_record = {
                10: {'SAC': self.__i_sac, 'SIC': self.__i_sic},
                140: {'ToD': ltt_time_of_day},
                20: {'TYP': 2, 'SIM': 0, 'RDP': 0, 'SPI': li_spi, 'RAB': 0, 'FX': 1, 'TST': 0, 'ME': 0, 'MI': 0, 'FOEFRI': 0, 'FX2': 0},
                40: {'RHO': ldct_track['rho'] , 'THETA': ldct_track['theta']},
                70: {'V': 0, 'G': 0, 'L': 0, 'Mode3A': int(ldct_track['ssr'], 8)},
                90: {'V': 0, 'G': 0, 'FL': (ldct_track['fl']/100)},
                161: {'Tn': li_track_number},
                200: {'CGS': ldct_track['ground_speed'], 'CHdg': ldct_track['heading']},
                170: {'CNF': 0, 'RAD': 2, 'DOU': 0, 'MAH': 0, 'CDM': 0, 'FX': 1, 'TRE': 0, 'GHO': 0, 'SUP': 0, 'TCC': 0, 'FX2': 0}
            }

            llst_detected_tracks.append(ldct_track_record)

        M_LOG.info("__broadcast_asterix:  tracks detected after [%d]" % len(llst_detected_tracks))
        if len(llst_detected_tracks) > 0:
            ldct_asterix_record = {48: llst_detected_tracks, 34: [ldct_sector_record]}
        else:
            ldct_asterix_record = {34: [ldct_sector_record]}

        self.__transmit(ldct_asterix_record)

        if fb_north_flag:
            ldct_asterix_north_record = {34: [ldct_north_record]}

            self.__transmit(ldct_asterix_north_record)

        # logger
        #M_LOG.info("__broadcast_asterix:<<")


    # ---------------------------------------------------------------------------------------------
    def __calc_distance_from(self, ff_lat, ff_lon, ff_alt):
        """method calc_distance_from

        This method calculates the distance of the aircraft on radar
        """
        lf_x, lf_y, lf_z = geo_utils.geog2enu(ff_lat, ff_lon, ff_alt,
                                              self.__f_latitude, self.__f_longitude,
                                              self.__f_altitude)

        return lf_x, lf_y


    # ---------------------------------------------------------------------------------------------
    def __listen_ptracks(self):
        """

        :return:
        """
        # logger
        M_LOG.info("__listen_ptracks:>>")

        # IP address of incoming messages
        ls_ip = netifaces.ifaddresses(self.NET_IFACE)[2][0]['addr']
        l_sock = mcast_socket.McastSocket(local_port=self.NET_PTRACKS_PORT, reuse=True)
        l_sock.mcast_add(self.NET_PTRACKS_GROUP, ls_ip)

        M_LOG.info("__listen_ptracks:  Waiting for track messages on %s:%d" % (self.NET_PTRACKS_GROUP, self.NET_PTRACKS_PORT))

        while True:
            l_data, l_sender = l_sock.recvfrom(1024)
            M_LOG.debug("__listen_ptracks:  receive data [%s]" % l_data)

            # Inserting received messages in the queue
            self.__q_queue.append(l_data)

        M_LOG.info("__listen_ptracks:<<")


    # ---------------------------------------------------------------------------------------------
    def __load_config(self, fs_config):
        """
        load configuration from file.

        :param fs_config: configuration file.
        :return:
        """
        # logger
        M_LOG.info("__load_config:>>")


        # Reading configuration file
        if os.path.exists(fs_config):
            M_LOG.info("Configuration file %s found." % fs_config)

            l_cparser = ConfigParser.ConfigParser()
            l_cparser.read(fs_config)

            self.__f_latitude  = l_cparser.getfloat("Location", "latitude")
            self.__f_longitude = l_cparser.getfloat("Location", "longitude")
            self.__f_altitude  = l_cparser.getfloat("Location", "altitude")

            # Radar parameters
            self.__f_sweep_time = l_cparser.getfloat("PSR", "sweep_time")
            self.__f_vertical_coverage = l_cparser.getfloat("PSR", "vertical_coverage")
            self.__f_psr_horizontal_coverage = l_cparser.getfloat("PSR", "psr_horizontal_coverage") * self.NM_TO_M
            self.__f_ssr_horizontal_coverage = l_cparser.getfloat("PSR", "ssr_horizontal_coverage") * self.NM_TO_M

            # Network parameters
            self.__s_net_ip = l_cparser.get("Network", "destination")
            self.__i_net_port = l_cparser.getint("Network", "port")

            # System Area Code (SAC)
            if l_cparser.has_option("Network", "sac"):
                self.__i_sac = int(l_cparser.get("Network", "sac"))  # in hex

            # System Identification Code (SIC)
            if l_cparser.has_option("Network", "sic"):
                self.__i_sic = int(l_cparser.get("Network", "sic"))  # in hex

        # Node name of radar in simulation
        ls_node_name = core_utils.get_node_name()

        # Simulation ID
        li_session_id = core_utils.get_session_id()

        # NEM ID
        li_nem_id = core_utils.get_nem_id(node_name=ls_node_name, session_id=li_session_id)

        # Placing radar on the proper location
        emane_utils.set_location(nemid=li_nem_id, lat=self.__f_latitude, lon=self.__f_longitude, alt=self.__f_altitude,
                                 heading=0.0, speed=0.0, climb=0.0)

        M_LOG.debug("Location of Radar:")
        M_LOG.debug("  Latitude:  %f" % self.__f_latitude)
        M_LOG.debug("  Longitude: %f" % self.__f_longitude)
        M_LOG.debug("  Altitude:  %f m" % self.__f_altitude)
        M_LOG.debug("Network settings:")
        M_LOG.debug("  Destination:  %s" % self.__s_net_ip)
        M_LOG.debug("  Port:         %d" % self.__i_net_port)
        M_LOG.debug("ASTERIX settings:")
        M_LOG.debug("  SAC:          %d" % self.__i_sac)
        M_LOG.debug("  SIC:          %d" % self.__i_sic)

        # logger
        M_LOG.info("__load_config:<<")


    # ---------------------------------------------------------------------------------------------
    def __process_msg(self, data):
        """

        :param data:
        :return:
        """
        # logger
        M_LOG.info("__process_msg:>>")

        # ex: 1#7003#-1#4656.1#-16.48614#-47.947058#210.8#9.7#353.9#TAM6543#B737#21653.3006492#icao24
        # logger
        llst_message = data.split('#')

        # Node number
        li_msg_num = int(llst_message[0])

        # SSR
        ls_ssr = llst_message[1]

        # SPI
        li_msg_spi = int(llst_message[2])

        # if spi > 0, SPI=ON, otherwise SPI=OFF
        if li_msg_spi > 1:
            lb_spi = True
        else:
            lb_spi = False

        # Altitude (meters)
        lf_altitude = float(llst_message[3])

        # Latitude (degrees)
        lf_latitude = float(llst_message[4])

        # Longitude (degrees)
        lf_longitude = float(llst_message[5])

        # Ground speed (knots)
        lf_ground_speed = float(llst_message[6])
        lf_ground_speed = lf_ground_speed * self.KT_TO_MPS

        # Vertical rate (m/s)
        lf_vertical_rate = float(llst_message[7])

        # Heading (degrees)
        lf_heading = float(llst_message[8])

        # Callsign
        ls_callsign = llst_message[9]

        # Aircraft performance type
        ls_aircraft_type = llst_message[10]

        # Timestamp
        # self.old_timestamp = self.timestamp
        lf_timestamp = float(llst_message[11])

        # ICAO 24 bit code
        ls_icao24 = llst_message[12]

        # Radar detect
        lf_x, lf_y = self.__calc_distance_from(lf_latitude, lf_longitude, lf_altitude)

        lf_z = lf_altitude

        # Sector
        lf_h_angle = RadarUtils.calc_horizontal_angle(lf_x, lf_y, lf_z)

        li_sector = int(lf_h_angle / self.DEG_SETOR)

        # Radar distance detection
        lf_hdist_2d = math.sqrt(lf_x * lf_x + lf_y * lf_y)

        lb_detect = True
        if lf_hdist_2d > self.__f_ssr_horizontal_coverage:
            lb_detect = False

        # Convert to NM
        lf_hdist_2d = lf_hdist_2d * self.M_TO_NM
        # Distance from radar (3D)
        lf_slant_range = math.sqrt(lf_x * lf_x + lf_y * lf_y + lf_z * lf_z) * self.M_TO_NM

        # Altitude in feet
        lf_altitude = lf_altitude * self.FT_TO_M

        M_LOG.debug ("__process_msg:  msg decode")

        l_track = {
            'detect': lb_detect,
            'sector': li_sector,
            'ssr': ls_ssr,
            'spi': lb_spi,
            'slant_range' : lf_slant_range,
            'rho' : lf_hdist_2d,
            'theta': lf_h_angle,
            'fl': lf_altitude,
            # m/s
            'ground_speed': lf_ground_speed,
            # degrees
            'heading': lf_heading,
        }

        self.__tracks[li_msg_num] = l_track

        # logger
        M_LOG.info("__process_msg:<<")


    # ---------------------------------------------------------------------------------------------
    def __process_queue(self):
        """

        :return:
        """
        # logger
        M_LOG.info("__process_queue:>>")

        M_LOG.info("__process_queue:  enter loop ...")

        while True:

            M_LOG.debug("__process_queue: queue len [%d]" % len(self.__q_queue))
            if len(self.__q_queue) == 0:
                time.sleep(0.5)
                continue
            else:
                while len(self.__q_queue) != 0:
                    ls_data = self.__q_queue.popleft()
                    self.__process_msg(ls_data)

        # logger
        M_LOG.info("__process_queue:<<")


    # ---------------------------------------------------------------------------------------------
    def __send_asterix_data(self):
        """
        This method has the cyclic function 4/2 for aircraft that are within
        the radar coverage and send in broadcast mode (UDP) network
        """
        # logger
        M_LOG.info("__send_asterix_data:>>")

        while True:

            ltt_time0 = time.time()
            ltt_timep = time.time()

            for li_sector in range(0, 32):

                lb_send_north = False
                if li_sector == 25:
                    lb_send_north = True

                self.__broadcast_asterix(li_sector, lb_send_north)

            ltt_deltap = time.time() - ltt_timep

            time.sleep(self.__f_sweep_time - ltt_deltap)

            #M_LOG.debug("Objects detected: %d" % len(tracks))
            #for t in tracks:
            #    print "  > %s: %f %f %f %f %f %s" % (t[7], t[1], t[2], t[3], t[4], t[5], t[8])
            #
            ltt_deltat = time.time() - ltt_time0
            M_LOG.debug("Complete rotation in %f sec" % ltt_deltat)

        # logger
        M_LOG.info("__send_asterix_data:<<")


    # -----------------------------------------------------------------------------------
    def __transmit(self, fdct_asterix_record):
        """

        :param fdct_asterix_record:
        :return:
        """
        # logger
        #M_LOG.info("__transmit:>>")

        #M_LOG.debug("__transmit:  Sending track messages to %s:%d" % (self.__s_net_ip, self.__i_net_port))
        # Encoding data to ASTERIX format
        lbuf_data_bin = asterix_utils.encode(fdct_asterix_record)
        lbuf_msg = hex(lbuf_data_bin).rstrip("L").lstrip("0x")
        self.__sock.sendto(binascii.unhexlify(lbuf_msg), (self.__s_net_ip, self.__i_net_port))
        #M_LOG.debug("__transmit: data [%s]" % lbuf_msg)

        # logger
        #M_LOG.info("__transmit:<<")


    # ---------------------------------------------------------------------------------------------
    def start(self):
        """

        :return:
        """
        # logger
        M_LOG.info("start:>>")

        l_thread1 = threading.Thread(target=self.__send_asterix_data, args=())
        l_thread2 = threading.Thread(target=self.__listen_ptracks, args=())
        l_thread3 = threading.Thread(target=self.__process_queue, args=())

        l_thread1.start();
        l_thread2.start();
        l_thread3.start();

        # logger
        M_LOG.info("start:<<")


# < class RadarUtils >-----------------------------------------------------------------------------
class RadarUtils:

    DEG_PI_3 = 60.0           # PI / 3
    DEG_PI_2 = 90.0           # PI / 2
    DEG_PI = 180.0            # PI
    DEG_3PI_2 = 270.0         # 3 PI / 2
    DEG_2PI = 360.0           # 2 PI
    RAD_DEG = 57.29577951     # Converte RAD para DEG
    DEG_RAD = 0.017453292     # Converte DEG para RAD
    DEG_SETOR = 11.25


    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def calc_horizontal_angle(ff_x_pos, ff_y_pos, ff_z_pos = None):
        """

        :param ff_x_pos:
        :param ff_y_pos:
        :param ff_z_pos:
        :return:
        """

        # calcula a nova radial (proa de demanda)
        if ff_x_pos > 0:
            return 90.0 - math.degrees(math.atan(ff_y_pos / ff_x_pos))

        if ff_x_pos < 0:
            lf_angle_tmp = 270.0 - math.degrees(math.atan(ff_y_pos / ff_x_pos))

            if lf_angle_tmp >= 360.0:
                return lf_angle_tmp - 360.0
            else:
                return lf_angle_tmp

        if ff_y_pos >= 0:
            return 0.0
        else:
            return RadarUtils.DEG_PI


    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def calc_vertical_angle(ff_x_pos, ff_y_pos, ff_z_pos):
        """

        :param ff_x_pos:
        :param ff_y_pos:
        :param ff_z_pos:
        :return:
        """

        if ff_z_pos == 0.0:
            return 0.0

        if ff_x_pos == 0.0:
            return 90.0

        lf_v_angle = math.atan(ff_z_pos / abs(ff_x_pos))

        if ff_z_pos < 0:
            return -lf_v_angle

        return lf_v_angle


# < main >-----------------------------------------------------------------------------------------
def main():

    l_oRadar = Radar()
    l_oRadar.start()

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:

    # logger
    logging.basicConfig(filename=M_LOG_FILE, filemode="w", format="%(asctime)s %(levelname)s: %(message)s")

    # jump start
    main()

# < the end >--------------------------------------------------------------------------------------

