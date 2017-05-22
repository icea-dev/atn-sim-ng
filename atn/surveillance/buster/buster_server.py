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
import atn.geo_utils as geoutils

import atn.surveillance.adsb.decoder as dcdr
import atn.surveillance.adsb.forwarders.dump1090_fwrd as f1090

import atn.surveillance.asterix.adsb_decoder as axdc
import atn.surveillance.asterix.asterix_encoder as axec

import atn.surveillance.buster.bcolors as bcolors
import atn.surveillance.buster.sensors as sensors

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
M_THRESHOLD = 1000

# tempo para estatística (s)
M_TIM_STAT = 30

M_EVEN_MSG = 0
M_ODD_MSG = 1

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

        # reference point for (lat, lng) to (x, y)
        self.__t_ref_pos = None

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
    def __calc_estimated_xy(self, flst_pos_x, flst_pos_y, flst_pos_z, flst_toa):
        """
        get estimated x,y
        """
        # number of measurements
        li_num_meds = len(flst_toa)

        # sorting by time of arrival, where the last sensor to receive is always the reference
        # this keeps the MLAT error low.
        _t = numpy.array(flst_toa)
        _i = numpy.argsort(_t)[::-1]

        _xpos = [0] * li_num_meds
        _ypos = [0] * li_num_meds
        _zpos = [0] * li_num_meds
        _toa  = [0] * li_num_meds

        for i in xrange(0, li_num_meds):
            _xpos[i] = flst_pos_x[_i[i]]
            _ypos[i] = flst_pos_y[_i[i]]
            _zpos[i] = flst_pos_z[_i[i]]
            _toa[i]  = flst_toa[_i[i]]

        # speed of light (in meters per second)
        vel = 299792458

        # time difference of arrival
        dt = [0] * li_num_meds

        for i in xrange(0, li_num_meds):
            dt[i] = _toa[i] - _toa[0]
            if i > 0 and dt[i] == 0:
                return None, None

        A = [0] * li_num_meds
        B = [0] * li_num_meds
        C = [0] * li_num_meds
        D = [0] * li_num_meds

        #
        for m in xrange(2, li_num_meds):
            A[m] = 2 * _xpos[m] / (vel * dt[m]) - 2 * _xpos[1] / (vel * dt[1])
            B[m] = 2 * _ypos[m] / (vel * dt[m]) - 2 * _ypos[1] / (vel * dt[1])
            C[m] = 2 * _zpos[m] / (vel * dt[m]) - 2 * _zpos[1] / (vel * dt[1])
            D[m] = (vel * dt[m]) - \
                   (vel * dt[1]) - (_xpos[m] ** 2 + _ypos[m] ** 2 + _zpos[m] ** 2) / \
                   (vel * dt[m]) + (_xpos[1] ** 2 + _ypos[1] ** 2 + _zpos[1] ** 2) / \
                   (vel * dt[1])

        X = numpy.matrix([[A[2], B[2], C[2]], [A[3], B[3], C[3]], [A[4], B[4], C[4]]])
        b = numpy.array([-D[2], -D[3], -D[4]])
        b.shape = (3, 1)

        try:
            location = linalg.inv(X).dot(b)

            x_est = location[0][0]
            y_est = location[1][0]
            z_est = location[2][0]

            return x_est, y_est

        # em caso de erro....
        except numpy.linalg.linalg.LinAlgError:
            x_est = None
            y_est = None

        return x_est, y_est
        
    # ---------------------------------------------------------------------------------------------
    def __count_messages(self, fs_adsb_msg, fv_del=False):
        """
        count equal messages
        """ 
        # init answer
        llst_ans = []

        # for all messages in dictionary...
        for l_key, llst_data in self.__dct_rcv_msg.iteritems():
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
            if lf_lat and lf_lng:
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
        li_icao24 = dcdr.get_icao_addr(ls_adsb_msg)

        # airborne position msg type ok ?
        if dcdr.get_tc(ls_adsb_msg) in xrange(9, 19):
            # get airborne position
            lf_lat, lf_lon, lf_alt = self.__decode_position(li_icao24, ls_adsb_msg)

            # valid position ?
            if (lf_lat is not None) and (lf_lon is not None):
                # convert lat/lng to x, y
                return geoutils.geog2enu(lf_lat, lf_lon, lf_alt, 
                                         self.__t_ref_pos[0], self.__t_ref_pos[1], self.__t_ref_pos[2])

        # senão,...
        else:
            # already have a position ?
            if li_icao24 in self.__dct_lst_pos:
                # use last reported position as reference
                lf_lat, lf_lon, lf_alt = self.__dct_lst_pos[li_icao24]

                # convert lat/lng to x, y
                return geoutils.geog2enu(lf_lat, lf_lon, lf_alt,
                                         self.__t_ref_pos[0], self.__t_ref_pos[1], self.__t_ref_pos[2])

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
                elif "dump1090" == ldct_dest["type"]:
                    # create forwarder
                    l_fwd = f1090.Dump1090Forwarder(items=ldct_dest)
                    assert l_fwd

                    # set timeout
                    l_fwd.set_timeout(0.5)

                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwd)
                '''  
                # destination database ?
                elif "database" == ldct_dest["type"]:
                    # create forwarder
                    l_fwd = database_fwrd.DatabseForwarder(items=ldct_dest)
                    assert l_fwd

                    # put on forwarders list
                    self.__lst_forwarders.append(l_fwd)
                '''
        # load sensors setup file
        self.__load_sensors("sensors.txt")

    # ---------------------------------------------------------------------------------------------
    def __load_sensors(self, fs_filename):
        """
        load sensors
        """
        # ckeck input
        assert fs_filename
        
        # open file
        with open(fs_filename) as l_fin:
            # for all lines in file...
            for ls_line in l_fin:
                # strip eol
                ls_line = ls_line.rstrip('\n')

                # split line
                llst_line = ls_line.split(',')

                # create sensor
                l_sensor = sensors.BSensor(int(llst_line[0]), float(llst_line[1]), float(llst_line[2]), float(llst_line[3]))
                assert l_sensor
                
                # add sensor to dictionary
                self.__dct_sensors[int(llst_line[0])] = l_sensor

                # sensor is reference point
                self.__t_ref_pos = (l_sensor.lat, l_sensor.lng, l_sensor.alt)

        # for all sensors...
        for l_id, l_sensor in self.__dct_sensors.iteritems():
            # converts lat, lon to x, y
            l_sensor.update(self.__t_ref_pos[0], self.__t_ref_pos[1], self.__t_ref_pos[2])

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
        llst_pos_x = []
        llst_pos_y = []
        llst_pos_z = []

        # for all messages...
        for l_msg in llst_msg:
            # sensor id
            li_sns = l_msg[1]
            
            # time of arrival
            llst_toa.append(l_msg[2])

            # location of sensor
            llst_pos_x[li_sns] = self.__dct_sensors[li_sns].x
            llst_pos_y[li_sns] = self.__dct_sensors[li_sns].y
            llst_pos_z[li_sns] = self.__dct_sensors[li_sns].alt

        # verify declared position (in x, y)
        l_x, l_y = self.__get_declared_xy(fs_adsb_msg)

        # determine source of transmission using multilateration
        lf_flt_x, lf_flt_y = self.__calc_estimated_xy(llst_pos_x, llst_pos_y, llst_pos_z, llst_toa)

        # determine reliability of message
        if (l_x is not None) and (l_y is not None) and (lf_flt_x is not None) and (lf_flt_y is not None):

            # 2D distance between reported and estimated positions
            lf_dist_2d = math.sqrt((l_x - lf_flt_x) ** 2 + (l_y - lf_flt_y) ** 2)

            # distance inside acceptable range ?
            if lf_dist_2d <= M_THRESHOLD:
                # accept message
                M_LOG.info("process_msg:'%s'\t%d\t%s[OK]%s" % (fs_adsb_msg, lf_dist_2d, bcolors.OKBLUE, bcolors.ENDC))

                # for all forwarders...
                for l_frwd in self.__lst_forwarders:
                    # send received ADS-B message
                    l_frwd.forward(fs_adsb_msg, None)

            # senão,...
            else:
                # drop message
                M_LOG.warning("process_msg:'%s'\t%d\t%s[FAIL]%s" % (fs_adsb_msg, lf_dist_2d, bcolors.FAIL, bcolors.ENDC))

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
                llst_msg = ls_message.split()

                # get message fields: sensor_id [0], message [1], toa [2], created [3]
                fdct_rcv_msg[llst_msg[3]] = [llst_msg[0], llst_msg[1], llst_msg[2]]

            # logger
            M_LOG.info("receive::received message {} from {} at {}".format(ls_message, l_addr_from, time.time()))

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
        
                # get oldest message
                llst_data = self.__dct_rcv_msg[llst_keys[0]]

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
