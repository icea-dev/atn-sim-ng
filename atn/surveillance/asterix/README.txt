Para executar o serviço AsterixServer:

python -m adsb.asterix_server.asterix_server -c asterixserver.cfg

Configuração do asterixserver.cfg

[General]
sic = ${soma(node.name)}
port = 40000 + ${soma(node.name)}
txport = 50000 + ${soma(node.name)}
net = ${IP}

Onde :

${soma(node.name)} É a soma dos dígitos da string node.name.
${IP}        	   Endereço IP do destino das mensagens ASTERIX.

O arquivo de configuração do serviço AdsBIn tem que ser modificado para 
incluir a transmissão das mensagens ADS-B para o AsterixServer.

Configuração do adsbin.cfg

[General]
id = ${node.name}
destinations = Dump1090 asterix

[Dump1090]
type = Dump1090
server = localhost
port = 30001

[asterix]
type = asterix
server = 127.0.0.1
port = ${soma(node.name)}

Onde:
${node.name} 	   O nome do nó no core.
${soma(node.name)} É a soma dos dígitos da string node.name.

