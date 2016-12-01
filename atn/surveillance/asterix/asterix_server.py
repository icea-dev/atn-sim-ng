"""@package asterix_server
Server to encode the surveillance information in ASTERIX format
"""

import ConfigParser
import getopt
import os
import Queue
import sys

from .adsb_decoder import AdsBDecoder
from .asterix_encoder import AdsBAsterixEncode

# QUEUE_SIZE [int]: The maximum number of elements in the queue.
QUEUE_SIZE = 10

__author__ = "Ivan Matias"
__date__ = "2016/03"


def usage():
    """Shows a help to use application.
    """
    print "Usage: python -m atn.surveillance.asterix.server [options]"
    print ""
    print "Options:"
    print " -h, --help          Display this help and exit."
    print " -c, --config=<FILE> Configuration file."


if '__main__' == __name__:

    print "Intializing Asterix Server..."

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:v", ["help", "config="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)

    # sic [int]: The System Code Identification default.
    sic = 225

    # port [int]: Data receiving port default.
    port = 60000

    # tx_port [int]: Data broadcasting port default.
    tx_port = 20000

    # net [string]: IPv4 broadcast address default.
    net = '127.0.0.1'

    # config [string]: Configuration file.
    config = "asterixserver.cfg"

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg

    # Reading configuration file
    if os.path.exists(config):
        conf = ConfigParser.ConfigParser()
        conf.read(config)

        sic = conf.getint("General", "sic")

        port = conf.getint("General", "port")

        tx_port = conf.getint("General", "txport")

        net = conf.get("General", "net")

    queue = Queue.Queue(QUEUE_SIZE)

    # Create an object to decode ADS-B Message
    decoder = AdsBDecoder(sic)
    decoder.create_socket(port)
    decoder.set_queue(queue)
    decoder.start_thread()

    # Create an object to encode ASTERIX
    encoder = AdsBAsterixEncode(sic)
    encoder.create_socket(tx_port)
    encoder.set_net(net)
    encoder.set_queue(queue)
    encoder.start_thread()