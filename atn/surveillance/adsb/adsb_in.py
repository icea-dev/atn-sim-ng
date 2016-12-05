import ConfigParser
import logging
import os
import Queue
import socket
import threading
import time

from .forwarders.dump1090_fwrd import Dump1090Forwarder
from .forwarders.database_fwrd import DatabseForwarder
from .forwarders.asterix_fwrd import AsterixForwarder
from ..asterix.adsb_decoder import AdsBDecoder
from ..asterix.asterix_encoder import AdsBAsterixEncode


class AdsbIn:

    log_file = "adsbin.log"
    log_level = logging.DEBUG

    net_port = 30001

    rec_msgs = []
    max_rec_msgs = 5000

    # Asterix
    QUEUE_SIZE = 10
    asterix_server = False
    asterix_sic = None
    asterix_rx_port = None
    asterix_tx_port = None
    asterix_dst = None

    def __init__(self, config="adsbin.cfg", store_msgs=False):
        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')

        self.store_rec_msgs = store_msgs

        # List of destination to which received messages will be forwarded to.
        self.forwarders = []

        # Id
        self.id = None

        if os.path.exists(config):
            conf = ConfigParser.ConfigParser()
            conf.read(config)

            self.id = conf.get("General", "id")

            # Reading destinations to forward received messages
            for dst in conf.get("General", "destinations").split():
                items = conf.items(dst)
                d = {}

                for i in items:
                    d[i[0]] = i[1]

                if d["type"] == "dump1090":
                    f = Dump1090Forwarder(items=d)
                    f.set_timeout(0.5)
                    self.forwarders.append(f)
                elif d["type"] == "database":
                    f = DatabseForwarder(sensor_id=self.id, items=d)
                    self.forwarders.append(f)
                elif d["type"] == "asterix":
                    # Enable Asterix Server
                    self.asterix_server = True

                    # Asterix parameters
                    self.asterix_sic = int(d["sic"])
                    self.asterix_rx_port = 15000
                    self.asterix_tx_port = int(d["port"])
                    self.asterix_dst = d["server"]

                    # Forwards to local Asterix Server, which is listening on localhost:15000
                    d["server"] = "127.0.0.1"
                    d["port"] = self.asterix_rx_port

                    # Create forwarder
                    f = AsterixForwarder(items=d)
                    self.forwarders.append(f)

    def _start_asterix_server(self):

        print "Intializing Asterix Server..."

        sic = self.asterix_sic
        rx_port = self.asterix_rx_port
        tx_port = self.asterix_tx_port
        net = self.asterix_dst

        queue = Queue.Queue(self.QUEUE_SIZE)

        # Create an object to decode ADS-B Message
        decoder = AdsBDecoder(sic)
        decoder.create_socket(rx_port)
        decoder.set_queue(queue)
        decoder.start_thread()

        # Create an object to encode ASTERIX
        encoder = AdsBAsterixEncode(sic)
        encoder.create_socket(tx_port)
        encoder.set_net(net)
        encoder.set_queue(queue)
        encoder.start_thread()

    def start(self):
        t1 = threading.Thread(target=self._start, args=())
        t1.start()

        # If receiver contains an Asterix destination ...
        if self.asterix_server:
            t2 = threading.Thread(target=self._start_asterix_server, args=())
            t2.start()

    def _start(self):
        print "  ,---.  ,------.   ,---.        ,-----.          ,--.         "
        print " /  O  \ |  .-.  \ '   .-',-----.|  |) /_         |  |,--,--,  "
        print "|  .-.  ||  |  \  :`.  `-.'-----'|  .-.  \        |  ||      \ "
        print "|  | |  ||  '--'  /.-'    |      |  '--' /        |  ||  ||  | "
        print "`--' `--'`-------' `-----'       `------'         `--'`--''--' "

        # Create a socket for receiving ADS-B messages
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', self.net_port))

        logging.info("Waiting on port :" + str(self.net_port))

        t0 = time.time()
        num_msgs = 0

        while True:

            # Buffer size is 1024 bytes
            message_raw, addr = sock.recvfrom(1024)
            splits = message_raw.split()

            if len(splits) > 1:
                message = splits[0]
                tx_node = splits[1]
            else:
                message = splits[0]
                tx_node = None

            # Time of arrival
            toa = time.time()

            # Debugging info
            # self.logger.info("Received message from " + str(addr) + " : " + data + " at t=%.20f" % toa)

            if self.store_rec_msgs:
                if len(self.rec_msgs) <= self.max_rec_msgs:
                    self.store_msg(message)

            # Forward received ADS-B message to all configured forwarders
            for f in self.forwarders:
                f.forward(message, toa, tx_node, self.id)

            # Logging
            t1 = time.time()
            num_msgs += 1

            if t1 - t0 > 30:
                logging.info("Throughput = %f msgs/sec" % (num_msgs/(t1-t0)))
                t0 = time.time()
                num_msgs = 0

    def stop(self):
        pass

    def store_msg(self, message):
        self.rec_msgs.append(message)

    def retrieve_msg(self):
        if len(self.rec_msgs) > 0:
            return self.rec_msgs.pop()
        else:
            return None


if __name__ == '__main__':

    transponder = AdsbIn()
    transponder.start()
