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

class Newton(CoreService):
    ''' This is a sample user-defined service. 
    '''
    # a unique name is required, without spaces
    _name = "Newton"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('tracks.cfg', 'data/exes/LG2016.exe.xml', 'data/traf/LG2016.trf.xml',
                'data/proc/tabTrj.xml', 'data/proc/tabEsp.xml', 'data/proc/tabSub.xml',
                'data/tabs/tabPrf.xml',  'data/tabs/tabFix.xml', 'data/tabs/tabAer.xml')

    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('sh tracks.sh',)
    # list of shutdown commands
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = "# Teste"

        if filename == "data/exes/LG2016.exe.xml":
            cfg = ""
            cfg += "<?xml version='1.0' encoding='UTF-8'?>\n"
            cfg += "<!DOCTYPE exercicios>\n"
            cfg += "<exercicios VERSION='0001' CODE='1961' FORMAT='NEWTON'>\n"
            cfg += "    <exercicio nExe='LG2016'>\n"
            cfg += "        <descricao>Meu Primeiro Exercicio - LG2016</descricao>\n"
            cfg += "        <horainicio>06:00</horainicio>\n"
            cfg += "    </exercicio>\n"
            cfg += "</exercicios>\n"

        if filename == "data/traf/LG2016.trf.xml":
            cfg = ""
            cfg += "<?xml version='1.0' encoding='UTF-8'?>\n"
            cfg += '<!DOCTYPE trafegos>\n'
            cfg += '<trafegos VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '    <trafego nTrf="1">\n'
            cfg += '    <designador>B737</designador>\n'
            cfg += '        <ssr>7003</ssr>\n'
            cfg += '        <indicativo>AZU1234</indicativo>\n'
            cfg += '        <origem>SBBR</origem>\n'
            cfg += '        <destino>SBRJ</destino>\n'
            cfg += '        <procedimento>TRJ4000</procedimento>\n'
            cfg += '        <temptrafego>0</temptrafego>\n'
            cfg += '        <coord>\n'
            cfg += '            <tipo>L</tipo>\n'
            cfg += '            <campoA>-23.220060</campoA>\n'
            cfg += '            <campoB>-45.898599</campoB>\n'
            cfg += '        </coord>\n'
            cfg += '        <velocidade>250</velocidade>\n'
            cfg += '        <altitude>3000</altitude>\n'
            cfg += '        <proa>46</proa>\n'
            cfg += '	</trafego>\n'
            cfg += '</trafegos>\n'

        if filename == "data/proc/tabTrj.xml":
            cfg = ""
            cfg += '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE trajetorias>\n'
            cfg += '<trajetorias VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '\n'
            cfg += '<trajetoria nTrj="4000">\n'
            cfg += '    <descricao> Trajetorias do Meu Primeiro Exercicio - LG2016</descricao>\n'
            cfg += '\n'
            cfg += '    <breakpoint nBrk="1">\n'
            cfg += '        <coord>\n'
            cfg += '            <tipo>L</tipo>\n'
            cfg += '            <campoA>-22.902570</campoA>\n'
            cfg += '            <campoB>-44.287992</campoB>\n'
            cfg += '        </coord>\n'
            cfg += '        <altitude>10000</altitude>\n'
            cfg += '        <velocidade>210</velocidade>\n'
            cfg += '    </breakpoint>\n'
            cfg += '\n'
            cfg += '    <breakpoint nBrk="2">\n'
            cfg += '       	<coord>\n'
            cfg += '           	<tipo>L</tipo>\n'
            cfg += '           	<campoA>-22.957090</campoA>\n'
            cfg += '           	<campoB>-44.239982</campoB>\n'
            cfg += '       	</coord>\n'
            cfg += '       	<altitude>10000</altitude>\n'
            cfg += '       	<velocidade>210</velocidade>\n'
            cfg += '    </breakpoint>\n'
            cfg += '\n'
            cfg += '    <breakpoint nBrk="3">\n'
            cfg += '       	<coord>\n'
            cfg += '           	<tipo>L</tipo>\n'
            cfg += '           	<campoA>-23.635927</campoA>\n'
            cfg += '           	<campoB>-45.832747</campoB>\n'
            cfg += '       	</coord>\n'
            cfg += '       	<altitude>10000</altitude>\n'
            cfg += '       	<velocidade>210</velocidade>\n'
            cfg += '    </breakpoint>\n'
            cfg += '\n'
            cfg += '    <breakpoint nBrk="4">\n'
            cfg += '       	<coord>\n'
            cfg += '           	<tipo>L</tipo>\n'
            cfg += '           	<campoA>-23.220060</campoA>\n'
            cfg += '           	<campoB>-45.898599</campoB>\n'
            cfg += '       	</coord>\n'
            cfg += '       	<altitude>10000</altitude>\n'
            cfg += '       	<velocidade>210</velocidade>\n'
            cfg += '    </breakpoint>\n'
            cfg += '\n'
            cfg += '</trajetoria>\n'
            cfg += '\n'
            cfg += '</trajetorias>\n'

        if filename == 'data/proc/tabEsp.xml':
            cfg = ""
            cfg += '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE esperas>\n'
            cfg += '<esperas VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '    <espera nEsp="1">\n'
            cfg += '        <fixo>83</fixo>\n'
            cfg += '        <sentido>D</sentido>\n'
            cfg += '        <rumo>274</rumo>\n'
            cfg += '    </espera>\n'
            cfg += '</esperas>\n'

        if filename == 'data/proc/tabSub.xml':
            cfg = ""
            cfg += "<?xml version='1.0' encoding='UTF-8'?>\n"
            cfg += "<!DOCTYPE subidas>\n"
            cfg += "<subidas VERSION='0001' CODE='1961' FORMAT='NEWTON'>\n"
            cfg += "\n"
            cfg += "    <subida nSub='57'>\n"
            cfg += "        <nome>KOTRU 1B</nome>\n"
            cfg += "        <aerodromo>SBSJ</aerodromo>\n"
            cfg += "        <pista>33</pista>\n"
            cfg += "\n"
            cfg += "        <breakpoint nBrk='1'>\n"
            cfg += "            <coord>\n"
            cfg += "                <tipo>D</tipo>\n"
            cfg += "                <campoA>82</campoA>\n"
            cfg += "                <campoB>8</campoB>\n"
            cfg += "                <campoC>333</campoC>\n"
            cfg += "            </coord>\n"
            cfg += "            <altitude>8000</altitude>\n"
            cfg += "            <velocidade>250</velocidade>\n"
            cfg += "        </breakpoint>\n"
            cfg += "\n"
            cfg += "        <breakpoint nBrk='2'>\n"
            cfg += "            <coord>\n"
            cfg += "                <tipo>D</tipo>\n"
            cfg += "                <campoA>82</campoA>\n"
            cfg += "                <campoB>18</campoB>\n"
            cfg += "                <campoC>333</campoC>\n"
            cfg += "            </coord>\n"
            cfg += "            <altitude>10000</altitude>\n"
            cfg += "            <velocidade>300</velocidade>\n"
            cfg += "        </breakpoint>\n"
            cfg += "\n"
            cfg += "        <breakpoint nBrk='3'>\n"
            cfg += "            <coord>\n"
            cfg += "                <tipo>F</tipo>\n"
            cfg += "                <campoA>377</campoA>\n"
            cfg += "            </coord>\n"
            cfg += "            <altitude>32000</altitude>\n"
            cfg += "            <velocidade>300</velocidade>\n"
            cfg += "        </breakpoint>\n"
            cfg += "    </subida>\n"
            cfg += "</subidas>\n"

        if filename == "data/tabs/tabPrf.xml":
            cfg = ""
            cfg += '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE performances>\n'
            cfg += '<performances VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '    <performance nPrf="B737">\n'
            cfg += '        <descricao>BOEING 737</descricao>\n'
            cfg += '        <numfami>8</numfami>\n'
            cfg += '        <esteira>M</esteira>\n'
            cfg += '        <tetosv>420</tetosv>\n'
            cfg += '        <faixa>420</faixa>\n'
            cfg += '        <veldec>125</veldec>\n'
            cfg += '        <velsbdec>190</velsbdec>\n'
            cfg += '        <velapx>160</velapx>\n'
            cfg += '        <velcruz>440</velcruz>\n'
            cfg += '        <velmxcrz>540</velmxcrz>\n'
            cfg += '        <rzsubdec>1300</rzsubdec>\n'
            cfg += '        <rzmxsbdec>3500</rzmxsbdec>\n'
            cfg += '        <rzsbcrz>1900</rzsbcrz>\n'
            cfg += '        <rzmxsbcrz>3500</rzmxsbcrz>\n'
            cfg += '        <rzdescapx>2500</rzdescapx>\n'
            cfg += '        <rzmxdesapx>4000</rzmxdesapx>\n'
            cfg += '        <rzdescrz>2000</rzdescrz>\n'
            cfg += '        <rzmxdescrz>3500</rzmxdescrz>\n'
            cfg += '        <razvarvel>45</razvarvel>\n'
            cfg += '        <rzmxvarvel>60</rzmxvarvel>\n'
            cfg += '    </performance>\n'
            cfg += '</performances>\n'

        if filename == "data/tabs/tabFix.xml":
            cfg = ""
            cfg += '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE fixos>\n'
            cfg += '<fixos VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '    <fixo nFix="1">\n'
            cfg += '        <nome>BSCWAZ</nome>\n'
            cfg += '        <indicativo>BSCWA</indicativo>\n'
            cfg += '        <coord>\n'
            cfg += '            <tipo>L</tipo>\n'
            cfg += '            <campoA>-16.335333</campoA>\n'
            cfg += '            <campoB>-58.387167</campoB>\n'
            cfg += '        </coord>\n'
            cfg += '    </fixo>\n'
            cfg += '</fixos>\n'

        if filename == "data/tabs/tabAer.xml":
            cfg = ""
            cfg += '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE aerodromos>\n'
            cfg += '<aerodromos VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
            cfg += '    <aerodromo nAer="SBSJ">\n'
            cfg += '        <nome>SAO JOSE DOS CAMPOS</nome>\n'
            cfg += '        <elevacao>2120</elevacao>\n'
            cfg += '\n'
            cfg += '        <pista nPis="15">\n'
            cfg += '            <rumo>152</rumo>\n'
            cfg += '            <coord>\n'
            cfg += '                <tipo>G</tipo>\n'
            cfg += '                <campoA>2313.09S</campoA>\n'
            cfg += '                <campoB>4552.18W</campoB>\n'
            cfg += '            </coord>\n'
            cfg += '        </pista>\n'
            cfg += '\n'
            cfg += '        <pista nPis="33">\n'
            cfg += '            <rumo>332</rumo>\n'
            cfg += '            <coord>\n'
            cfg += '                <tipo>G</tipo>\n'
            cfg += '                <campoA>2314.1S</campoA>\n'
            cfg += '                <campoB>4551.11W</campoB>\n'
            cfg += '            </coord>\n'
            cfg += '        </pista>\n'
            cfg += '    </aerodromo>\n'
            cfg += '</aerodromos>\n'

        if filename == "tracks.cfg":
            cfg = "# configuracoes\n"
            cfg += "\n"
            cfg += "# -----------------------------------------------------------------------------\n"
            cfg += "[glb]\n"
            cfg += "\n"
            cfg += "# exercicio\n"
            cfg += "exe = LG2016\n"
            cfg += "\n"
            cfg += "# canal de comunicacao\n"
            cfg += "canal = 4\n"
            cfg += "\n"
            cfg += "\n"
            cfg += "# diretorios\n"
            cfg += "# -----------------------------------------------------------------------------\n"
            cfg += "[dir]\n"
            cfg += "\n"
            cfg += "# aerodromos\n"
            cfg += "aer = aers\n"
            cfg += "\n"
            cfg += "# exercicios\n"
            cfg += "exe = exes\n"
            cfg += "\n"
            cfg += "# fontes\n"
            cfg += "fnt = font\n"
            cfg += "\n"
            cfg += "# images\n"
            cfg += "img = images\n"
            cfg += "\n"
            cfg += "# sons\n"
            cfg += "snd = sound\n"
            cfg += "\n"
            cfg += "# tabelas\n"
            cfg += "tab = tabs\n"
            cfg += "\n"
            #cfg += "# dados\n"
            #cfg += "dat = /tmp/%s/data\n" % node.name
            cfg += "\n"
            cfg += "\n"
            cfg += "# rede\n"
            cfg += "# -----------------------------------------------------------------------------\n"
            cfg += "[net]\n"
            cfg += "\n"
            cfg += "# endereco de configuracao\n"
            cfg += "cnfg = 227.12.2\n"
            cfg += "\n"
            cfg += "# endereco de dados\n"
            cfg += "data = 231.12.2\n"
            cfg += "\n"
            cfg += "# endereco de mensagens radar\n"
            cfg += "rdar = 235.12.2\n"
            cfg += "\n"
            cfg += "# porta de comunicacao\n"
            cfg += "port = 1970\n"
            cfg += "\n"
            cfg += "\n"
            cfg += "# temporizacao\n"
            cfg += "# -----------------------------------------------------------------------------\n"
            cfg += "[time]\n"
            cfg += "\n"
            cfg += "# fast-time simulation acceleration factor\n"
            cfg += "accel = 1.\n"
            cfg += "\n"
            cfg += "# reenvio de configuracao do sistema\n"
            cfg += "cnfg = 5\n"
            cfg += "\n"
            cfg += "# tempo de ativacao das aeronaves\n"
            cfg += "fgen = 30\n"
            cfg += "\n"
            cfg += "# colisao entre aeronaves\n"
            cfg += "prox = 1\n"
            cfg += "\n"
            cfg += "# tempo de envio das mensagens\n"
            cfg += "wait = .5\n"
            cfg += "\n"
            cfg += "# < the end >------------------------------------------------------------------\n"



    # 'data/tabs/tabPrf.xml',  'data/tabs/tabFix.xml', 'data/tabs/tabAer.xml'



        # if filename == "tracks.sh":
        #     cfg = "#!/bin/sh\n"
        #     cfg += "# auto-generated by Tracks (newton.py)\n"
        #     cfg += "\n"
        #     cfg += "rm -rf /tmp/%s/data\n" % node.name
        #     cfg += "mkdir -p /tmp/%s/data\n" % node.name
        #     cfg += "mkdir -p /tmp/%s/data/exes\n" % node.name
        #     cfg += "mkdir -p /tmp/%s/data/proc\n" % node.name
        #     cfg += "mkdir -p /tmp/%s/data/tabs\n" % node.name
        #     cfg += "mkdir -p /tmp/%s/data/traf\n" % node.name
        #     cfg += "\n"
        #     cfg += "cp CINE0001.exe.xml /tmp/%s/data/exes/\n" % node.name
        #     cfg += "cp CINE0001.trf.xml /tmp/%s/data/traf/CINE0001.trf.xml\n" % node.name
        #     cfg += "cp tabTrj.xml /tmp/%s/data/proc/tabTrj.xml\n" % node.name
        #     cfg += "cp -r /opt/adsb/ptracks/data/tabs/* /tmp/%s/data/tabs\n" % node.name
        #     cfg += "cp tracks.cfg /tmp/%s/" % node.name
        #     cfg += "\n"
        #     cfg += "cd /tmp/%s\n" % node.name
        #     cfg += "python /opt/adsb/ptracks/newton.py &\n"
        #     cfg += "sleep 2\n"
        #     cfg += "python /opt/adsb/ptracks_feed.py\n"
        #     cfg += "\n"
        # elif filename == "CINE0001.exe.xml":
        #     cfg = "<?xml version='1.0' encoding='UTF-8'?>\n"
        #     cfg += "<!DOCTYPE exercicios>\n"
        #     cfg += '<exercicios VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
        #     cfg += "\n"
        #     cfg += '    <exercicio nExe="CINE0001">\n'
        #     cfg += '        <descricao>Teste de Cinemetica</descricao>\n'
        #     cfg += '        <horainicio>06:00</horainicio>\n'
        #     cfg += '    </exercicio>\n'
        #     cfg += '\n'
        #     cfg += '</exercicios>\n'
        # elif filename == "CINE0001.trf.xml":
        #     cfg = "<?xml version='1.0' encoding='UTF-8'?>\n"
        #     cfg += "<!DOCTYPE trafegos>\n"
        #     cfg += '<trafegos VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
        #     cfg += '\n'
        #     cfg += '    <trafego nTrf="%s">\n' % node.objid
        #     cfg += '        <designador>B737</designador>\n'
        #     cfg += '        <ssr>7003</ssr>\n'
        #     cfg += '        <indicativo>TAM6543</indicativo>\n'
        #     cfg += '        <origem>SBBR</origem>\n'
        #     cfg += '        <destino>SBRJ</destino>\n'
        #     cfg += '        <procedimento>TRJ%04d</procedimento>\n' % node.objid
        #     cfg += '        <temptrafego>0</temptrafego>\n'
        #     cfg += '        <coord>\n'
        #     cfg += '            <tipo>F</tipo>\n'
        #     cfg += '            <campoA>1365</campoA>\n'
        #     cfg += '        </coord>\n'
        #     cfg += '        <velocidade>250</velocidade>\n'
        #     cfg += '        <altitude>3000</altitude>\n'
        #     cfg += '        <proa>46</proa>\n'
        #     cfg += '    </trafego>\n'
        #     cfg += '\n'
        #     cfg += '</trafegos>\n'
        # elif filename == "tabTrj.xml":
        #     cfg = "<?xml version='1.0' encoding='UTF-8'?>\n"
        #     cfg += '<!DOCTYPE trajetorias>\n'
        #     cfg += '<trajetorias VERSION="0001" CODE="1961" FORMAT="NEWTON">\n'
        #     cfg += '\n'
        #     cfg += '    <trajetoria nTrj="%s">\n' % node.objid
        #     cfg += '        <descricao>001 - LUZ / ALINA</descricao>\n'
        #     cfg += '\n'
        #     cfg += '        <breakpoint nBrk="1">\n'
        #     cfg += '            <coord>\n'
        #     cfg += '                <tipo>F</tipo>\n'
        #     cfg += '                <campoA>161</campoA>\n'
        #     cfg += '            </coord>\n'
        #     cfg += '            <altitude>10000</altitude>\n'
        #     cfg += '            <velocidade>210</velocidade>\n'
        #     cfg += '        </breakpoint>\n'
        #     cfg += '\n'
        #     cfg += '        <breakpoint nBrk="2">\n'
        #     cfg += '            <coord>\n'
        #     cfg += '                <tipo>F</tipo>\n'
        #     cfg += '                <campoA>654</campoA>\n'
        #     cfg += '            </coord>\n'
        #     cfg += '            <altitude>9000</altitude>\n'
        #     cfg += '            <velocidade>300</velocidade>\n'
        #     cfg += '        </breakpoint>\n'
        #     cfg += '    </trajetoria>\n'
        #     cfg += '\n'
        #     cfg += '</trajetorias>\n'
        #

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
addservice(Newton)

