#
# CORE
# Copyright (c)2010-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#
''' Sample user-defined service.
'''
import os

from core.service import CoreService, addservice
from core.misc.ipaddr import IPv4Prefix, IPv6Prefix

class AsterixServer(CoreService):
    ''' This is a sample user-defined service.
    '''
    # a unique name is required, without spaces
    _name = "AsterixServer"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('asterixserver.cfg', 'asterixserver.sh')
    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('sh asterixserver.sh',)
    # list of shutdown commands
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        if filename == "asterixserver.sh":
            cfg = "#!/bin/sh\n"
            cfg += "# auto-generated by AsterixServer (asterix_server.py)\n"
            cfg += "sleep 10\n"
            cfg += "python -m adsb.asterix_server.asterix_server -c asterixserver.cfg"

        elif filename == "asterixserver.cfg":
            port = 40000 + int(node.objid)
            txport = 50000 + int(node.objid)
            cfg = "[glb]\n"
            cfg += "sic = {}\n".format(int(node.objid))
            cfg += "port = {}\n".format(int(port))
            cfg += "txport = {}\n".format(int(txport))
            cfg += "net = 127.0.0.1\n\n"

        return cfg

    @staticmethod
    def subnetentry(x):
        ''' Generate a subnet declaration block given an IPv4 prefix string
            for inclusion in the config file.
        '''
        if x.find(":") >= 0:
            # this is an IPv6 address
            return ""
        else:
            net = IPv4Prefix(x)
            return 'echo "  network %s"' % (net)

# this line is required to add the above class to the list of available services
addservice(AdsbIn)
