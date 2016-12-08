#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016, ICEA
#
# This file is part of atn-sim
#
# atn-sim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# atn-sim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import ConfigParser
import os
import time
import socket
import sys

__author__ = "Marcio Monteiro"
__version__ = "0.1"
__date__ = "2016-dec-08"


class TrackCmd:

    TCP_IP = "172.17.255.254"
    TCP_PORT = 5006
    EXERCISE = None
    BUFFER_SIZE = 1024

    def __init__(self, config="track_server.cfg"):

        if os.path.exists(config):
            self.config = ConfigParser.ConfigParser()
            self.config.read(config)

            if self.config.has_option("Tracks", "server"):
                self.TCP_IP = self.config.get("Tracks", "server")

            if self.config.has_option("Tracks", "port"):
                self.TCP_PORT = int(self.config.get("Tracks", "port"))

            if self.config.has_option("Tracks", "exercise"):
                self.EXERCISE = self.config.get("Tracks", "exercise")

    def start(self):
        if self.EXERCISE is not None:
            self.send_cmd("START %s" % self.EXERCISE)
        else:
            print "Cannot start: exercise is undefined"

    def stop(self):
        self.send_cmd("STOP")

    def restart(self):
        self.stop()
        time.sleep(2)
        self.start()

    def send_cmd(self, cmd):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.TCP_IP, self.TCP_PORT))

        # Greetings
        s.recv(self.BUFFER_SIZE)

        # Sending command
        s.send(cmd)

        data = s.recv(self.BUFFER_SIZE)

        s.close()

        print data

if __name__ == "__main__":

    cmd = TrackCmd()

    if len(sys.argv) <= 1:
        print "Argument required: start or stop"
        sys.exit(0)

    if sys.argv[1] == "start":
        cmd.start()
    elif sys.argv[1] == "stop":
        cmd.stop()
    elif sys.argv[1] == "restart":
        cmd.restart()
    else:
        print "Invalid command: %s" % sys.argv[1]


