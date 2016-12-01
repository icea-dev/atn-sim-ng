import logging
import socket

from .adsb_fwrd import AdsbForwarder


class Dump1090Forwarder(AdsbForwarder):

    def __init__(self, verbose=False, items=None, server="localhost", port="30001"):
        self.logger = logging.getLogger('adsb_in_app.Dump1090')
        self.s = None
        self.timeout = 1.0
        self.verbose = verbose

        if self.verbose:
            self.logger.disabled = False
        else:
            self.logger.disabled = True

        self.logger.info('Creating an instance of Dump1090')

        if items is not None:
            self.ip_destination = items["server"]
            self.tcp_port_d = int(items["port"])
        else:
            self.ip_destination = server
            self.tcp_port_d = port

    def set_timeout(self, timeout=0.5):
        self.timeout = timeout

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.settimeout(self.timeout)
            self.s.connect((self.ip_destination, self.tcp_port_d))
            return True
        except socket.error:
            self.s = None
            return False

    def send_msg(self, message, verbose=False):
        if self.s:
            sent = self.s.send("*" + str(message).upper() + ";\n")

            if sent == 0:
                return False

            if verbose:
                self.logger.info("DUMP1090 : " + "*" + str(message).upper() + ";\n")

            return True
        else:
            return False

    def disconnect(self):
        if self.s:
            self.s.close()

    def forward(self, message, time_of_arrival=None, tx_id=None, rx_id=None):
        self.connect()
        self.send_msg(message=message)
        self.disconnect()

    def __str__(self):
        return "DUMP1090 IP...: " + self.ip_destination + ":" + str(self.tcp_port_d)
