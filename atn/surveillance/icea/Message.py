import binascii
import ctypes
import os

class Message(object):

    def __init__(self):
    
        # endereco icao
        self._icao24     = None
                                                                                                                                                                                                                                        
        # callsign
        self._szCSign    = None

        # message
        self._szMessage  = None

    def __str__(self):
        output = ""
        output += "_icao24...: %s\n" % self._icao24
        output += "_szCSign..: %s\n" % self._szCSign
        output += "_szMessage: %s\n" % self._szMessage
        return output
#
# end class Message
#

if __name__ == "__main__":
	
	# instance object Message
    l_Message = Message()
  
    # initialize attributs of object
    l_Message._icao24    = binascii.b2a_hex(os.urandom(3))
    l_Message._szCSign   = 'TAM7777'
    l_Message._szMessage = None

    # output
    print ""
    print l_Message
    print ""
