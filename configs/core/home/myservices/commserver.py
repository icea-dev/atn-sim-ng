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

class CommServer(CoreService):
    ''' This is a sample user-defined service. 
    '''
    # a unique name is required, without spaces
    _name = "CommServer"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('srbc.ini', 'CommServerRede',)
    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('sh /opt/adsb/softwares/commserver/commserver-daemon start',)
    # list of shutdown commands
    _shutdown = ('sh /opt/adsb/softwares/commserver/commserver-daemon stop',)

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = ""

        if filename == "srbc.ini":
            cfg += "[readUDP]\n"
            cfg += "host=172.16.0.255\n"
            cfg += "msq.out=0x120\n"
            cfg += "porta=65000\n"
            cfg += "saida=queue\n"
            cfg += "\n"
            cfg += "[unpackSRBC]\n"
            cfg += "console=01\n"
            cfg += "entrada=queue\n"
            cfg += "msq.in=0x120\n"
            cfg += "msq.out=0x230\n"
            cfg += "protocolo=ICEA\n"
            cfg += "saida=queue\n"
            cfg += "radar.0=0x230,01,1\n"
            cfg += "\n"
            cfg += "[Icea2Tvt2]\n"
            cfg += "entrada=queue\n"
            cfg += "msq.in=0x230\n"
            cfg += "msq.out=0x210\n"
            cfg += "msq.irouter=localhost\n"
            cfg += "msq.orouter=localhost\n"
            cfg += "saida=queue\n"
            cfg += "radar=2230\n"
            cfg += "bypass=true\n"
            cfg += "\n"
            cfg += "[writeUDP]\n"
            cfg += "destino=172.16.0.255\n"
            cfg += "entrada=queue\n"
            cfg += "msq.in=0x210\n"
            cfg += "broadcast=on\n"
            cfg += "#mutlicast=off\n"
            cfg += "\n"
            cfg += "[RADAR]\n"
            cfg += "monograma=G\n"
            cfg += "sinal=simulado\n"

        if filename == "CommServerRede":
            cfg += "1 20000 1 A\n"
            cfg += "2 20001 2 B\n"
            cfg += "3 20002 3 C\n"
            cfg += "4 20003 4 D\n"
            cfg += "5 20004 5 E\n"
            cfg += "6 20005 6 F\n"
            cfg += "7 20006 7 G\n"
            cfg += "8 20007 8 H\n"

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
addservice(CommServer)

