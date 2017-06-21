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
remoção da mysql

revision 0.1  2016/dez  matiasims
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.2$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/04"

# < imports >--------------------------------------------------------------------------------------

# python library
import ConfigParser
import logging
import math
import os
import Queue
import socket
import sys
import threading
import time

# atn-sim
import atn.geo_utils as gutl

import atn.surveillance.adsb.decoder as dcdr  #!!
import atn.surveillance.adsb.forwarders.asterix_fwrd as fast
import atn.surveillance.adsb.forwarders.buster_fwrd as fbstr
import atn.surveillance.adsb.forwarders.dump1090_fwrd as f1090

import atn.surveillance.asterix.adsb_decoder as axdc
import atn.surveillance.asterix.asterix_encoder as axec

# < module defs >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)
M_LOG_FILE = "adsb_in.log"

# receiver
M_NET_PORT = 30001
M_MAX_REC_MSGS = 5000
M_RECV_BUFF_SIZE = 1024

# asterix server
M_ASTERIX_PORT = 15000
M_ASTERIX_HOST = "localhost"

# speed of light (m/s)
M_LIGHT_SPEED = 299792458.

# tempo para estatística (s)
M_TIM_STAT = 60

# tamanho máximo da lista de mensagens
M_MAX_REC_MSG = 5000

# < class AdsbIn >---------------------------------------------------------------------------------

class AdsbIn(object):
    """
    DOCUMENT ME!
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, fi_id, ff_lat, ff_lng, ff_alt, fs_config="adsb_in.cfg", fv_store_msgs=False):
        """
        constructor
        
        @param fi_id: sensor id
        @param ff_(lat, lng, alt): station position
        @param fs_config: arquivo de configuração
        @param fv_store_msgs: store messages flag
        """
        # destinations to which messages will be forwarded to
        self.__lst_forwarders = []

        # station location
        self.__f_lat = ff_lat
        self.__f_lng = ff_lng
        self.__f_alt = ff_alt

        # id
        self.__i_id = fi_id

        # lista de mensagens
        self.__q_rec_msgs = Queue.Queue(M_MAX_REC_MSG)
        self.__v_store_rec_msgs = fv_store_msgs
        
        # asterix forwarder/server
        self.__v_asterix_server = False
        self.__i_asterix_rx_port = None
        self.__i_asterix_tx_port = None
        self.__i_asterix_sic = None
        self.__s_asterix_dest = None

        #M_LOG.debug(">>>>>>>>>>>>>>>>>>>> Sensor: {} <<<<<<<<<<<<<<<<<<<<<<<<".format(fi_id))
        #M_LOG.debug("position lat: {}, lng: {}, alt: {}".format(self.__f_lat, self.__f_lng, self.__f_alt))

        # station location (ECEF)
        self.__f_x, self.__f_y, self.__f_z = gutl.geog2ecef(ff_lat, ff_lng, ff_alt)
        #M_LOG.debug("self.__f_x: {}, self.__f_y: {}, self.__f_z: {}".format(self.__f_x, self.__f_y, self.__f_z))
      
        # load configuration file
        self.__load_config(fs_config)

    # ---------------------------------------------------------------------------------------------
    def __estimate_toa(self, fs_message):
        """
        make a estimate of time of arrival
        """
        # clear to go
        assert fs_message

        # split message
        llst_msg = fs_message.split()
        #M_LOG.debug("llst_msg: {}".format(llst_msg))

        # ads-b message
        ls_msg_adsb = llst_msg[0]
        
        # received position
        lf_rcv_lat = float(llst_msg[1])
        lf_rcv_lon = float(llst_msg[2])
        lf_rcv_alt = float(llst_msg[3])

        # get aircraft (ICAO24 address)
        ls_icao24 = str(dcdr.get_icao_addr(ls_msg_adsb)).upper()
        #M_LOG.debug(">>>>>>>>>>>>>>>>>>>> Aeronave: {} <<<<<<<<<<<<<<<<<<<<<<<<".format(ls_icao24))
        #M_LOG.debug("position lat: {}, lng: {}, alt: {}".format(lf_rcv_lat, lf_rcv_lon, lf_rcv_alt))

        # aircraft position (ECEF)
        lf_anv_x, lf_anv_y, lf_anv_z = gutl.geog2ecef(lf_rcv_lat, lf_rcv_lon, lf_rcv_alt)
        #M_LOG.debug("lf_anv_x: {}, lf_anv_y: {}, lf_anv_z: {}".format(lf_anv_x, lf_anv_y, lf_anv_z))

        # convert lat/lng to enu 
        #lf_flt_x, lf_flt_y, lf_flt_z = gutl.geog2enu(lf_rcv_lat, lf_rcv_lon, lf_rcv_alt, 
        #                                             self.__f_lat, self.__f_lng, self.__f_alt)
        #M_LOG.debug("lf_flt_x: {}, lf_flt_y: {}, lf_flt_z: {}".format(lf_flt_x, lf_flt_y, lf_flt_z))

        # euclidean distance
        #lf_dist = math.sqrt(lf_flt_x * lf_flt_x + lf_flt_y * lf_flt_y + lf_flt_z * lf_flt_z)
        #M_LOG.debug("lf_dist: {}".format(lf_dist))

        # 2D distance between aircraft and sensor positions
        #lf_dist_2d = math.sqrt(pow(lf_anv_x - self.__f_x, 2) + pow(lf_anv_y - self.__f_y, 2))
        #M_LOG.debug("lf_dist_2d: {}".format(lf_dist_2d))

        # 3D distance between aircraft and sensor positions
        lf_dist_3d = math.sqrt(pow(lf_anv_x - self.__f_x, 2) + pow(lf_anv_y - self.__f_y, 2) + pow(lf_anv_z - self.__f_z, 2))
        #M_LOG.debug("lf_dist_3d: {}".format(lf_dist_3d))

        # return ads-b message, estimated time (distance / speed of light)
        return ls_msg_adsb, lf_dist_3d / M_LIGHT_SPEED

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
        load configuration from file
        
        @param fs_config: configuration file
        """    
        # configuration file exists ?
        if os.path.exists(fs_config):
            # create parser
            l_cparser = ConfigParser.ConfigParser()
            assert l_cparser
          
            # load file through parser
            l_cparser.read(fs_config)

            # reading destinations to forward received messages...
            for l_dest in l_cparser.get("glb", "destinations").split():
                # get section items as tuples list
                llst_items = l_cparser.items(l_dest)

                # init key=value dictionary
                ldct_dest = {}

                # for all items...
                for lt_item in llst_items:
                    # put item (key, value) on dictionary
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

                # destiny is buster server ?
                elif "buster" == ldct_dest["type"].lower():
                    # create buster server forwarder
                    l_fwdr = fbstr.BusterForwarder(fi_id=self.__i_id, flst_pos=[self.__f_x, self.__f_y, self.__f_z], f_options=ldct_dest)
                    assert l_fwdr
                    
                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

                # destiny is dump1090 ? 
                elif "dump1090" == ldct_dest["type"].lower():
                    # create dump 1090 forwarder
                    l_fwdr = f1090.Dump1090Forwarder(items=ldct_dest)
                    assert l_fwdr
                    
                    # set timeout
                    l_fwdr.set_timeout(0.5)
                    
                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)
                
    # ---------------------------------------------------------------------------------------------
    def __receive(self):
        """
        loop de recebimento das mensagens ADS-B
        """
        # create a socket for receiving ADS-B messages
        l_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        assert l_sock

        # setup socket
        l_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        l_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # bind socket
        l_sock.bind(("", M_NET_PORT))

        # show
        print "waiting on port: {}".format(M_NET_PORT)

        # initial time
        lf_now = time.time()

        # init message counter
        li_num_msgs = 0

        # loop forever...
        while True:
            # block 'til receive message (buffer size is 1024 bytes)
            ls_message, l_addr = l_sock.recvfrom(M_RECV_BUFF_SIZE)
            
            if ls_message:
                # estimate TOA (time-of-arrival)
                ls_msg_adsb, lf_toa_est = self.__estimate_toa(ls_message)

            # senão,...
            else:
                # next message 
                continue

            # store message ?
            if self.__v_store_rec_msgs and (not self.__q_rec_msgs.full()):
                # put on queue
                self.__q_rec_msgs.put(ls_msg_adsb)

            # for all configured forwarders...
            for l_fwdr in self.__lst_forwarders:
                # forward received ADS-B message
                l_fwdr.forward(ls_msg_adsb, lf_toa_est)

            # elapsed time (seg)
            lf_dif = time.time() - lf_now

            # increment message counter
            li_num_msgs += 1

            # tempo da estatística ?
            if lf_dif >= M_TIM_STAT:
                # logger
                M_LOG.info("throughput: {} msgs/sec".format(li_num_msgs / lf_dif))

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
        l_thr_1 = threading.Thread(target=self.__receive)
        assert l_thr_1

        # start thread
        l_thr_1.start()

        # if receiver contains an asterix destination...
        if self.__v_asterix_server:
            # create asterix server threads
            self.__init_asterix_server()

    # ---------------------------------------------------------------------------------------------
    def retrieve_msg(self):
        """
        retrieve messages
        """
        # queue empty ?
        if self.__q_rec_msgs.empty():
            # return 
            return None

        # return
        return self.__q_rec_msgs.get()

# -------------------------------------------------------------------------------------------------
def main():
    """
    jump start
    """
    # show logo
    print "  ,---.  ,------.   ,---.        ,-----.          ,--.         "
    print " /  O  \ |  .-.  \ '   .-',-----.|  |) /_         |  |,--,--,  "
    print "|  .-.  ||  |  \  :`.  `-.'-----'|  .-.  \        |  ||      \ "
    print "|  | |  ||  '--'  /.-'    |      |  '--' /        |  ||  ||  | "
    print "`--' `--'`-------' `-----'       `------'         `--'`--''--' "

    # create ADS-B in 
    l_transponder = AdsbIn(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    assert l_transponder

    # execute ADS-B in
    l_transponder.run()

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:

    # logger
    logging.basicConfig(filename=M_LOG_FILE, filemode="w", format="%(asctime)s %(levelname)s: %(message)s")

    # jump start
    main()

# < the end >--------------------------------------------------------------------------------------
