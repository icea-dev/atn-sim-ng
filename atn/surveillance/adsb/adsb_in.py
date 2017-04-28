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

# Python library
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
from atn.surveillance.adsb.forwarders.asterix_fwrd import AsterixForwarder
from atn.surveillance.adsb.forwarders.dump1090_fwrd import Dump1090Forwarder

from atn.surveillance.asterix.adsb_decoder import AdsBDecoder
from atn.surveillance.asterix.asterix_encoder import AdsBAsterixEncode

#import atn.core_utils as core_utils
#import atn.emane_utils as emane_utils
import atn.geo_utils as geo_utils
import atn.location as location

# < module data >----------------------------------------------------------------------------------

# logger
M_LOG_FILE = "adsb_in.log"
M_LOG_LEVEL = logging.DEBUG

# receiver
M_NET_PORT = 30001
M_MAX_REC_MSGS = 5000
M_RECV_BUFF_SIZE = 1024

# asterix server
M_QUEUE_SIZE = 10
M_ASTERIX_PORT = 15000
M_ASTERIX_HOST = "localhost"

# speed of light (m/s)
M_LIGHT_SPEED = 299792458.

# latitude central (CORE)
M_LAT_REF = -13.869227

# longitude central (CORE)
M_LNG_REF = -49.918091

# < class AdsbIn >---------------------------------------------------------------------------------

class AdsbIn(object):
    """
    DOCUMENT ME!
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, ff_x, ff_y, ff_z, fs_config="adsb_in.cfg", fv_store_msgs=False):
        """
        constructor
        
        @param ff_(x, y, z): station position
        @param fs_config: arquivo de configuração
        @param fv_store_msgs: flag store messages (False)
        """
        # flag store messages
        self.__v_store_rec_msgs = fv_store_msgs

        # destinations to which messages will be forwarded to
        self.__lst_forwarders = []

        # received messages
        self.__lst_rec_msgs = []

        # id
        self.id = None

        # asterix forwarder/server
        self.__v_asterix_server = False
        self.__i_asterix_rx_port = None
        self.__i_asterix_tx_port = None
        self.__i_asterix_sic = None
        self.__s_asterix_dest = None

        # load configuration file
        self.__load_config(fs_config)

        # create CORE location
        self.__core_location = location.CLocation()
        assert self.__core_location

        # configure reference point
        self.__core_location.configure_values("0|0|{}|{}|2|50000".format(M_LAT_REF, M_LNG_REF))

        # discover station location
        self.__f_lat, self.__f_lng, self.__f_alt = self.__core_location.getgeo(ff_x, ff_y, ff_z)
      
    # ---------------------------------------------------------------------------------------------
    def __estimate_toa(self, fs_message):
        """
        make a estimate of time of arrival
        """
        # clear to go
        assert fs_message

        # split message
        llst_msg = fs_message.split()
        logging.debug("llst_msg: {}".format(llst_msg))

        # ads-b message
        ls_msg_adsb = llst_msg[0]
        
        # received position
        lf_rcv_lat = float(llst_msg[1])
        lf_rcv_lon = float(llst_msg[2])
        lf_rcv_alt = float(llst_msg[3])

        # convert lat/lng to enu 
        lf_x, lf_y, lf_z = geo_utils.geog2enu(lf_rcv_lat, lf_rcv_lon, lf_rcv_alt, 
                                              self.__f_lat, self.__f_lng, self.__f_alt)

        # euclidean distance
        lf_dist = math.sqrt(lf_x * lf_x + lf_y * lf_y + lf_z * lf_z)
        logging.debug("lf_dist: {}".format(lf_dist))

        # return ads-b message, estimated time (distance / speed of light)
        return ls_msg_adsb, lf_dist / M_LIGHT_SPEED

    # ---------------------------------------------------------------------------------------------
    def __load_config(self, fs_config):
        """
        load configuration from file
        
        @param fs_config: configuration file
        """    
        # configuration file exists ?
        if os.path.exists(fs_config):
            # create parser
            l_parser = ConfigParser.ConfigParser()

            # load file through parser
            l_parser.read(fs_config)

            # set id
            self.id = l_parser.get("General", "id")

            # reading destinations to forward received messages...
            for l_dest in l_parser.get("General", "destinations").split():
                # items from destination
                llst_items = l_parser.items(l_dest)

                # init key=value dictionary
                ldct_options = {}

                # for all items...
                for lt_item in llst_items:
                    # put item (key, value) on dictionary
                    ldct_options[lt_item[0]] = lt_item[1]

                # destiny is dump1090 ? 
                if ldct_options["type"].lower() == "dump1090":
                    # create dump 1090 forwarder
                    l_fwdr = Dump1090Forwarder(items=ldct_options)
                    assert l_fwdr
                    
                    l_fwdr.set_timeout(0.5)
                    
                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

                # destiny is database ?
                elif ldct_options["type"].lower() == "database":
                    # create database forwarder
                    l_fwdr = DatabseForwarder(sensor_id=self.id, items=ldct_options)
                    assert l_fwdr
                    
                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

                # destiny is asterix ?
                elif ldct_options["type"].lower() == "asterix":
                    # enable asterix server
                    self.__v_asterix_server = True

                    # asterix parameters
                    self.__i_asterix_sic = int(ldct_options["sic"])
                    self.__i_asterix_rx_port = M_ASTERIX_PORT
                    self.__i_asterix_tx_port = int(ldct_options["port"])
                    self.__s_asterix_dest = ldct_options["server"]

                    # forwards to local asterix server, which is listening on localhost:15000
                    ldct_options["server"] = M_ASTERIX_HOST
                    ldct_options["port"] = M_ASTERIX_PORT

                    # create asterix forwarder
                    l_fwdr = AsterixForwarder(items=ldct_options)
                    assert l_fwdr 

                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwdr)

        # senão,...
        else:
            self.id = core_utils.get_node_name()

    # ---------------------------------------------------------------------------------------------
    def retrieve_msg(self):
        """
        DOCUMENT ME!
        """
        if len(self.__lst_rec_msgs) > 0:
            return self.__lst_rec_msgs.pop()

        # return
        return None

    # ---------------------------------------------------------------------------------------------
    def __init_asterix_server(self):
        """
        intialize asterix server
        """
        # warning
        print "intializing asterix server..."

        # create message queue
        l_queue = Queue.Queue(M_QUEUE_SIZE)
        assert l_queue 

        # create a decoder for ADS-B messages
        l_decoder = AdsBDecoder(self.__i_asterix_sic)
        assert l_decoder

        l_decoder.create_socket(self.__i_asterix_rx_port)
        l_decoder.set_queue(l_queue)
        l_decoder.start_thread()

        # create a encoder to ASTERIX
        l_encoder = AdsBAsterixEncode(self.__i_asterix_sic)
        assert l_encoder

        l_encoder.create_socket(self.__i_asterix_tx_port)
        l_encoder.set_net(self.__s_asterix_dest)
        l_encoder.set_queue(l_queue)
        l_encoder.start_thread()

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
        l_sock.bind(('', M_NET_PORT))

        # logger
        logging.info("waiting on port: {}".format(M_NET_PORT))

        # initial time
        lf_now = time.time()

        # initmessage counter
        li_num_msgs = 0

        # loop forever...
        while True:
            # block 'til receive message (buffer size is 1024 bytes)
            ls_message, l_addr_from = l_sock.recvfrom(M_RECV_BUFF_SIZE)
            
            if ls_message:
                # estimate TOA (time-of-arrival)
                ls_msg_adsb, lf_toa_est = self.__estimate_toa(ls_message)
                logging.debug("ls_msg_adsb: {}".format(ls_msg_adsb))
                logging.debug("lf_toa_est: {}".format(lf_toa_est))

            # senão,...
            else:
                # next message 
                continue

            # logger
            logging.info("received message {} from {} at {.20f}".format(ls_msg_adsb, l_addr_from, time.time()))

            # store messages ?
            if self.__v_store_rec_msgs:
                if len(self.__lst_rec_msgs) <= M_MAX_REC_MSGS:
                    self.__lst_rec_msgs.append(ls_msg_adsb)

            # for all configured forwarders...
            for l_fwdr in self.__lst_forwarders:
                # forward received ADS-B message
                l_fwdr.forward(ls_msg_adsb, lf_toa_est)

            # elapsed time (seg)
            lf_dif = time.time() - lf_now

            # increment message counter
            li_num_msgs += 1

            # 30 seconds ?
            if lf_dif > 30:
                # logger
                logging.info("throughput: {} msgs/sec".format(li_num_msgs / lf_dif))

                # reset initial time
                lf_now = time.time()

                # reset message counter
                li_num_msgs = 0

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
    l_transponder = AdsbIn(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
    assert l_transponder

    # execute ADS-B in
    l_transponder.run()

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:

    # logger
    logging.basicConfig(filename=M_LOG_FILE, level=M_LOG_LEVEL)

    # jump start
    main()

# < the end >--------------------------------------------------------------------------------------
