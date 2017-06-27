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

revision 0.2  2017/abr  mlabru
remoção MySQL, pep-8

revision 0.1  2016/dec  conte
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.2$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/05"

# < imports >--------------------------------------------------------------------------------------

# python library
import ConfigParser
import logging
import math
import numpy
import os
import Queue
import socket
import threading
import time

# numpy & scipy
from scipy import linalg

# atn-sim
import atn.geo_utils as gutl

import atn.surveillance.adsb.decoder as dcdr
import atn.surveillance.adsb.forwarders.dump1090_fwrd as f1090
import atn.surveillance.adsb.security.bcolors as bcolors
import atn.surveillance.adsb.security.mlat as mlat
import atn.surveillance.adsb.security.sensors as sensors

import atn.surveillance.asterix.adsb_decoder as axdc
import atn.surveillance.asterix.asterix_encoder as axec

# < module defs >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)
M_LOG_FILE = "buster_server.log"

# convertions
M_FT_TO_M = 0.3048
M_KT_TO_MPS = 0.514444
M_FTPM_TO_MPS = 0.00508

# receiver
M_NET_PORT = 12270
M_RECV_BUFF_SIZE = 1024

# distance threshold (m)
M_THRESHOLD = 6000

# tempo para estatística (s)
M_TIM_STAT = 60

M_EVEN_MSG = 0
M_ODD_MSG = 1

# speed of light (in meters per second)
M_LIGHT_SPEED = 299792458.

# < class CBusterServer >--------------------------------------------------------------------------

class CBusterServer(object):
    """
    BusterServer class
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, fs_config="buster_server.cfg"):
        """
        constructor
        """ 
        # init super class
        super(CBusterServer, self).__init__()

        # used for decoding ADS-B position messages
        # the key is the icao24 address
        self.__dct_lst_pos = {}
        self.__dct_lst_odd = {}
        self.__dct_lst_even = {}

        # tabela de sensores
        self.__dct_sensors = {}

        # lista de forwarders
        self.__lst_forwarders = []

        # asterix forwarder/server
        self.__v_asterix_server = False
        self.__i_asterix_rx_port = None
        self.__i_asterix_tx_port = None
        self.__i_asterix_sic = None
        self.__s_asterix_dest = None

        # create message dict
        self.__dct_rcv_msg = {}

        # load config file
        self.__load_config(fs_config)

    # ---------------------------------------------------------------------------------------------
    def __count_messages(self, fs_adsb_msg, fv_del=False):
        """
        count equal messages
        """ 
        # init answer
        llst_ans = []

        # local copy of dictionary
        ldct_rcv_msg = dict(self.__dct_rcv_msg)

        # for all messages in dictionary...
        for l_key, llst_data in ldct_rcv_msg.iteritems():
            # found message ?
            if llst_data[1] == fs_adsb_msg:
                # delete item ?
                if fv_del:
                    # delete item
                    del self.__dct_rcv_msg[l_key]

                # senão, keep item ?
                else:
                    # save item (created, sensor_id, toa)
                    llst_ans.append([l_key, llst_data[0], llst_data[2]])
                    
        # return
        return llst_ans
        
    # ---------------------------------------------------------------------------------------------
    def __decode_position(self, fi_icao24, ls_adsb_msg):
        """
        decode position
        """ 
        # message is odd ?
        if M_ODD_MSG == int(dcdr.get_oe_flag(ls_adsb_msg)):
            # save odd message
            self.__dct_lst_odd[fi_icao24] = ls_adsb_msg
            l_t0 = 0
            l_t1 = 1

        # senão, is even...
        else:
            # save even message
            self.__dct_lst_even[fi_icao24] = ls_adsb_msg
            l_t0 = 1
            l_t1 = 0

        # received both parts of message ?
        if (fi_icao24 in self.__dct_lst_odd) and (fi_icao24 in self.__dct_lst_even):
            # if CPR cannot be decoded, the method returns (None, None)
            lf_lat, lf_lng = dcdr.get_position(self.__dct_lst_even[fi_icao24], self.__dct_lst_odd[fi_icao24], l_t0, l_t1)

            # decoded ?
            if (lf_lat is not None) and (lf_lng is not None):
                # get altitude
                lf_alt = dcdr.get_alt(ls_adsb_msg) * M_FT_TO_M

                # save last position
                self.__dct_lst_pos[fi_icao24] = (lf_lat, lf_lng, lf_alt)

                # return ok
                return lf_lat, lf_lng, lf_alt

            # senão,...
            else:
                # logger
                M_LOG.warning("{}decode_position: cannot decode position message{}".format(bcolors.WARNING, bcolors.ENDC))

        # return
        return None, None, None

    # ---------------------------------------------------------------------------------------------
    def __get_declared_xy(self, ls_adsb_msg):
        """
        get declared xy
        """
        # get aircraft (ICAO24 address)
        ls_icao24 = str(dcdr.get_icao_addr(ls_adsb_msg)).upper()

        # airborne position msg type (9-18) ok ?
        if 8 < dcdr.get_tc(ls_adsb_msg) < 19:
            # get airborne position
            lf_lat, lf_lon, lf_alt = self.__decode_position(ls_icao24, ls_adsb_msg)
            #M_LOG.debug("declared_ll: {} / {} / {}".format(lf_lat, lf_lon, lf_alt))

            # valid position ?
            if (lf_lat is not None) and (lf_lon is not None) and (lf_alt is not None):
                # convert lat/lng/alt to x, y, z
                return gutl.geog2ecef(lf_lat, lf_lon, lf_alt)

        # senão, already have a position ?
        elif ls_icao24 in self.__dct_lst_pos:
            # use last reported position as reference
            lf_lat, lf_lon, lf_alt = self.__dct_lst_pos[ls_icao24]
            #M_LOG.debug("declared_ll: {} / {} / {}".format(lf_lat, lf_lon, lf_alt))

            # convert lat/lng/alt to x, y, z
            return gutl.geog2ecef(lf_lat, lf_lon, lf_alt)

        # return
        return None, None, None

    # ---------------------------------------------------------------------------------------------
    def __init_asterix_server(self):
        """
        intialize asterix server
        """
        # show
        print "intializing asterix server..."

        # create message queue
        l_queue = Queue.Queue()
        assert l_queue 

        # create a decoder for ADS-B messages
        l_decoder = axdc.AdsBDecoder(self.__i_asterix_sic)
        assert l_decoder

        l_decoder.create_socket(self.__i_asterix_rx_port)
        l_decoder.set_queue(l_queue)
        l_decoder.start_thread()

        # create a encoder to ASTERIX
        l_encoder = axec.AdsBAsterixEncode(self.__i_asterix_sic)
        assert l_encoder

        l_encoder.create_socket(self.__i_asterix_tx_port)
        l_encoder.set_net(self.__s_asterix_dest)
        l_encoder.set_queue(l_queue)
        l_encoder.start_thread()

    # ---------------------------------------------------------------------------------------------
    def __load_config(self, fs_config):
        """
        carrega o arquivo de configuração
        """
        # configuration file exists ?
        if os.path.exists(fs_config):
            # create config parser
            l_cparser = ConfigParser.ConfigParser()
            assert l_cparser

            # load file through parser
            l_cparser.read(fs_config)

            # reading destinations to forward reliable messages
            for l_dst in l_cparser.get("glb", "destinations").split():
                # get section items as tuples list
                llst_items = l_cparser.items(l_dst)

                # init key=value dictionary
                ldct_dest = {}

                # for all tuples in list...
                for lt_item in llst_items:
                    # put tuple on a dictionary
                    ldct_dest[lt_item[0]] = lt_item[1]

                # destiny is asterix ?
                if "asterix" == ldct_dest["type"].lower():
                    # enable asterix server
                    self.__v_asterix_server = True

                    # asterix parameters
                    self.__i_asterix_sic = int(ldct_dest["sic"])
                    self.__i_asterix_rx_port = M_ASTERIX_PORT
                    self.__i_asterix_tx_port = int(ldct_dest["port"])
                    self.__s_asterix_dest = ldct_dest["server"]

                    # forwards to local asterix server, which is listening on localhost:15000
                    ldct_dest["server"] = M_ASTERIX_HOST
                    ldct_dest["port"] = M_ASTERIX_PORT

                    # create asterix forwarder
                    l_fwdr = fast.AsterixForwarder(items=ldct_dest)
                    assert l_fwdr 

                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

                # destination dump1090 ?
                elif "dump1090" == ldct_dest["type"].lower():
                    # create forwarder
                    l_fwdr = f1090.Dump1090Forwarder(items=ldct_dest)
                    assert l_fwdr

                    # set timeout
                    l_fwdr.set_timeout(0.5)

                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

    # ---------------------------------------------------------------------------------------------
    def __process_msg(self, fs_adsb_msg, fv_del=False):
        """
        process message
        """ 
        # checking which sensors have received the same message
        llst_msg = self.__count_messages(fs_adsb_msg, False)
        li_msgs = len(llst_msg)

        # no data ?
        if 0 == li_msgs:
            # do not process it with insufficient data 
            return False

        # insufficient data ?
        elif li_msgs < len(self.__dct_sensors):
            # delete messages ?
            if fv_del:
                # delete messages 
                self.__count_messages(fs_adsb_msg, True)

            # do not process it with insufficient data
            return False

        # init arrays
        llst_toa = []
        llst_pos = []

        # for all messages...
        for l_msg in llst_msg:
            # sensor id
            li_sns = int(l_msg[1])

            # sensor position doesn't exists ? 
            if self.__dct_sensors.get(li_sns, None) is None:
                return False
                        
            # location of sensor (x, y, z ECEF)
            llst_pos.append([self.__dct_sensors[li_sns][0], self.__dct_sensors[li_sns][1], self.__dct_sensors[li_sns][2]])

            # time of arrival to distance
            llst_toa.append(float(l_msg[2]) * M_LIGHT_SPEED)

        # declared position (x, y, z ECEF)
        lf_anv_x, lf_anv_y, lf_anv_z = self.__get_declared_xy(fs_adsb_msg)
        #M_LOG.debug("declared_xy: {} / {} / {}".format(lf_anv_x, lf_anv_y, lf_anv_z))

        # determine reliability of message
        if (lf_anv_x is not None) and (lf_anv_y is not None) and (lf_anv_z is not None):
            # determine source of transmission using multilateration
            lf_est_x, lf_est_y, lf_est_z = mlat.mlat_1(llst_pos, llst_toa)
            #M_LOG.debug("estimated_xy: {} / {} / {}".format(lf_est_x, lf_est_y, lf_est_z)) 

            # determine reliability of message
            if (lf_est_x is not None) and (lf_est_y is not None) and (lf_est_z is not None):
                # 3D distance between reported and estimated positions
                lf_dist_3d = math.sqrt(pow(lf_anv_x - lf_est_x, 2) + pow(lf_anv_y - lf_est_y, 2) + pow(lf_anv_z - lf_est_z, 2))
                #M_LOG.debug("lf_dist_3d: {}".format(lf_dist_3d))

                # distance inside acceptable range ?
                if lf_dist_3d <= M_THRESHOLD:
                    # accept message
                    print "process_msg:'%s'\t%d\t%s[OK]%s" % (fs_adsb_msg, lf_dist_3d, bcolors.OKBLUE, bcolors.ENDC)
                    M_LOG.info("process_msg:'%s'\t%d [OK]" % (fs_adsb_msg, lf_dist_3d))

                    # for all forwarders...
                    for l_frwd in self.__lst_forwarders:
                        # send received ADS-B message
                        l_frwd.forward(fs_adsb_msg, None)

                # senão,...
                else:
                    # drop message
                    print "process_msg:'%s'\t%d\t%s[FAIL]%s" % (fs_adsb_msg, lf_dist_3d, bcolors.FAIL, bcolors.ENDC)
                    M_LOG.info("process_msg:'%s'\t%d [FAIL]" % (fs_adsb_msg, lf_dist_3d))

        # delete processed messages 
        self.__count_messages(fs_adsb_msg, True)

        # return
        return True

    # ---------------------------------------------------------------------------------------------
    def __receive(self, fdct_rcv_msg):
        """
        loop de recebimento das mensagens
        """
        # check input
        assert fdct_rcv_msg is not None
        
        # create a socket for receiving messages
        l_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        assert l_sock

        # setup socket
        l_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        l_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # bind socket
        l_sock.bind(('', M_NET_PORT))

        # show
        print "waiting on port: {}".format(M_NET_PORT)

        # initial time
        lf_now = time.time()

        # init message counter
        li_num_msgs = 0

        # forever...
        while True:
            # block 'til receive message (buffer size is 1024 bytes)
            ls_message, l_addr_from = l_sock.recvfrom(M_RECV_BUFF_SIZE)
            
            if ls_message:
                # split message
                llst_msg = ls_message.split('#')

                # sensor id
                li_sns = int(llst_msg[0])
                 
                # get message fields: sensor_id [0], message [1], toa [2], created [3], lst_pos [4]
                fdct_rcv_msg[float(llst_msg[3])] = [li_sns, str(llst_msg[1]), float(llst_msg[2])]
                #M_LOG.debug("dct_rcv_msg: {}".format(fdct_rcv_msg))

                # sensor position doesn't exists ?
                if self.__dct_sensors.get(li_sns, None) is None:
                    # save sensor position
                    self.__dct_sensors[li_sns] = eval(llst_msg[4])
                    #M_LOG.debug("sensor:{} position: {}".format(li_sns, eval(llst_msg[4])))

            # elapsed time (seg)
            lf_dif = time.time() - lf_now

            # increment message counter
            li_num_msgs += 1

            # tempo da estatística ?
            if lf_dif >= M_TIM_STAT:
                # logger
                M_LOG.info("receive::throughput: {} msgs/sec".format(li_num_msgs / lf_dif))

                # reset initial time
                lf_now = time.time()

                # reset message counter
                li_num_msgs = 0

    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        run adsb-in
        """
        # create receive messages thread
        lthr_rcv = threading.Thread(target=self.__receive, args=(self.__dct_rcv_msg,))
        assert lthr_rcv

        # start thread
        lthr_rcv.start()

        # if receiver contains an asterix destination...
        if self.__v_asterix_server:
            # create asterix server threads
            self.__init_asterix_server()

        # forever...
        while True:
            # dicionário tem dados ?
            if self.__dct_rcv_msg:
                # get key (created) list
                llst_keys = sorted(self.__dct_rcv_msg.keys())
                #M_LOG.debug("llst_keys: {}".format(llst_keys))
        
                # get oldest message
                llst_data = self.__dct_rcv_msg[llst_keys[0]]
                #M_LOG.debug("llst_data: {}".format(llst_data))

                # get data
                l_message = llst_data[1]

                # try 4 times...
                for li_try in xrange(4):
                    # process ok ?
                    if self.__process_msg(l_message):
                        # quit
                        break

                    # senão,...
                    else:
                        # wait...and try again
                        time.sleep(0.1)

                # more than one try ? 
                if li_try > 0:
                    # process and delete
                    self.__process_msg(l_message, True)

            # em caso de não haver mensagens...
            else:
                # permite o scheduler
                time.sleep(0.1)

# -------------------------------------------------------------------------------------------------
def main():
    """
    jump start
    ,-----.                  ,--.                 ,---.                                       
    |  |) /_ ,--.,--. ,---.,-'  '-. ,---. ,--.--.'   .-'  ,---. ,--.--.,--.  ,--.,---. ,--.--.
    |  .-.  \|  ||  |(  .-''-.  .-'| .-. :|  .--'`.  `-. | .-. :|  .--' \  `'  /| .-. :|  .--'
    |  '--' /'  ''  '.-'  `) |  |  \   --.|  |   .-'    |\   --.|  |     \    / \   --.|  |   
    `------'  `----' `----'  `--'   `----'`--'   `-----'  `----'`--'      `--'   `----'`--'   
    """
    # show logo
    print " __        __  ___  ___  __    __   ___  __        ___  __  "
    print "|__) |  | /__`  |  |__  |__)  /__` |__  |__) \  / |__  |__) "
    print "|__) \__/ .__/  |  |___ |  \  .__/ |___ |  \  \/  |___ |  \ "
    print

    # create server
    l_bserver = CBusterServer()
    assert l_bserver

    # run server
    l_bserver.run()
        
# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    
    # logger
    logging.basicConfig(filename=M_LOG_FILE, filemode='w', format='%(asctime)s %(levelname)s: (%(threadName)-9s) %(message)s')

    # jump start
    main()
    
# < the end >--------------------------------------------------------------------------------------
