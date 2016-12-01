"""@package adsb_decoder
"""
import threading
import socket
import time

from .aircraft_data import AircraftData
from ..adsb import decoder

__author__ = "Ivan Matias"
__date__ = "2016/03"


class AdsBDecoder(object):
    """This class is responsible for receiving and decoding ADS-B messages.

    This class handle the reception and decoding of 1090 Mhz Extended Squitter
    messages. It supported by one 1090 Mhz antenna. The decoding is capable of receiving
    and processing Extended Squitter messages including at least the following types:
    Airborne Position, Aircraft Identification and Airborne Velocity.

    """

    ## BUFFER_SIZE [int]: Maximum size of the data buffer
    BUFFER_SIZE = 1024

    ## ADSB_MESSAGE_MODES [int]: Downlink Format code
    ADSB_MESSAGE_MODES = 17

    ## ODD [int]: ADS-B odd message code
    ODD = 1

    ## EVEN [int]: ADS-B even message code
    EVEN = 0


    def __init__(self, sic, time_out=0.5):
        """The constructor

        Args:
            sic (int): System Identification Code for surveillance sensor.
            time_out (float): Time between sucessive target reports.

        """

        ## sic [int]: The system identification code for surveillance sensor.
        self.sic = sic

        ## time_out [float]: The time between sucessive target reports.
        self.time_out = time_out

        ## delete_time [int]: The time to check whether the aircraft were updated.
        self.delete_time = 60

        ## aircraft_table [dict]:  The aircraft data table.
        self.aircraft_table = {}


    def create_socket(self, port):
        """Creates the socket for receiving the ADS-B messages.

        Args:
            port (int): Data receiving port.

        """

        ## sock [socket]: The end point for receiving the ADS-B message.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', int(port)))


    def set_queue(self, queue):
        """Sets the queue for exchanging data between threads.

        Args:
            queue (Queue): The queue object pointer.

        """

        ## queue [Queue]:  The queue to exchange data.
        self.queue = queue


    def decode_position(self, icao24, adsb_data):
        """Decodes the airborne position data.

        Args:
            icao24 (string): The ICAO 24-bit aircraft address.
            adsb_data (string): The ADS-B message.

        Returns:
            bool: True if it is possible decode position of the aircraft; otherwise False.
        """
        # Verifica se e uma frame par (even) ou impar (odd)
        frame_type = int(decoder.get_oe_flag(adsb_data))

        return_type = False

        if 1 == frame_type:
            self.aircraft_table[icao24].set_odd_msg(adsb_data)
            t0 = 0
            t1 = 1
        else:
            self.aircraft_table[icao24].set_even_msg(adsb_data)
            t0 = 1
            t1 = 0

        # Eh possivel decodificar as mensagens para posicao ?
        if self.aircraft_table[icao24].decode_position():
            latitude, longitude = decoder.get_position(
                self.aircraft_table[icao24].get_even_msg(),
                self.aircraft_table[icao24].get_odd_msg(), t0, t1)

            if latitude and longitude:
                self.aircraft_table[icao24].set_position(latitude, longitude)
                return_type = True

            self.aircraft_table[icao24].set_altitude(decoder.get_alt(adsb_data))

        return return_type


    def decode(self, adsb_data, time_of_day):
        """Decodes the ADS-B messages.

        Args:
            adsb_data (string): The ADS-B message.
            time_of_day (int): Time of applicability in seconds, in the form of elapsed time since last midnight.

        Returns:
            None if the ADS-B Message is empty or downlink format is different from 17.

        """

        # Mensagem vazia ?
        if adsb_data is None:
            return None

        # Formato da mensagem (Downlink Format) diferente de 17
        if decoder.get_df(adsb_data) != self.ADSB_MESSAGE_MODES:
            return None

        icao24 = decoder.get_icao_addr(adsb_data)

        # verifica se existe uma aeronave para este endereco ICAO
        if icao24 not in self.aircraft_table:
            # Cria um novo objeto
            self.aircraft_table[icao24] = AircraftData(self.sic)

        type_code = decoder.get_tc(adsb_data)

        # Mensagem de Airbone Position?
        if (type_code in range(9, 19)) and (self.decode_position(icao24, adsb_data) is True):
            self.aircraft_table[icao24].set_time_of_day(time_of_day)

        # Decodifica a mensagem Airbone Velocity
        if type_code == 19:
            (spd, hdg, vertical_rate, tag) = decoder.get_velocity(adsb_data)
            self.aircraft_table[icao24].set_velocity(spd, hdg, vertical_rate)

        # Decodifica a mensagem de callsign
        if type_code in range(1, 5):
            callsign = decoder.get_callsign(adsb_data).replace("_", "")
            self.aircraft_table[icao24].set_callsign(callsign)


    def delete_data(self):
        """Thread to delete an aircraft if there is no update of your data.

        """
        while True:
            aircraft_icao24_keys = self.aircraft_table.keys()

            for icao24 in aircraft_icao24_keys:
                if self.aircraft_table[icao24].was_updated() is False:
                    del self.aircraft_table[icao24]

            time.sleep(self.delete_time)


    def queue_data(self):
        """Thread to put the information of decode aircraft in queue.

        """
        while True:
            if len(self.aircraft_table) > 0 and not self.queue.full():
                self.queue.put(self.aircraft_table)

            time.sleep(self.time_out)


    def decode_data(self):
        """Thread to receive and decode the ADS-B message.

        """
        while True:
            # Buffer size is 1024 bytes
            data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            adsb_data = data[0:28]
            time_of_day = int(data[28:], 16)

            self.decode(adsb_data, time_of_day)


    def start_thread(self):
        """Starts threads

        """
        decode_thread = threading.Thread(target=self.decode_data, args=())
        data_thread = threading.Thread(target=self.queue_data, args=())
        delete_thread = threading.Thread(target=self.delete_data, args=())

        decode_thread.start()
        data_thread.start()
        delete_thread.start()
