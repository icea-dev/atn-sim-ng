#!/usr/bin/python

import math


# Conversao de coordenadas Geografica para ENU
# Parametros do WGS84 - Defense Mapping Agency Technical Report

a = 6378137.0  # semi-eixo maior em metros
b = 6356752.3142 # semi-eixo menor em metros
e2 = 0.00669437999013 # primeira excentricidade ao quadrado


def geog2ecef(lat, lon, alt):
    """Geografica para ECEF.

    Entrada: lat e lon (graus), alt (m)
    Saida: x, y, z   (m)
    """
    N = a / math.sqrt(1.0 - (e2 * math.sin(math.radians(lat)) * math.sin(math.radians(lat))))
    x = (N + alt) * math.cos(math.radians(lat)) * math.cos(math.radians(lon))
    y = (N + alt) * math.cos(math.radians(lat)) * math.sin(math.radians(lon))
    z = (N * (1.0 - e2) + alt) * math.sin(math.radians(lat))
    return x, y, z


def ecef2enu(X, Y, Z, latrad, lonrad, altrad):
    """ECEF para ENU.

    Entrada: X, Y, Z (m) - coordenadas ECEF do alvo
            latrad e lonrad (graus), altrad (m) - coordenadas do radar
    Saida:   x, y, z (m) - coordenadas ENU do alvo em relacao ao radar
    """
    xrad, yrad, zrad = geog2ecef(latrad, lonrad, altrad)

    xdif = X - xrad
    ydif = Y - yrad
    zdif = Z - zrad

    x = - math.sin(math.radians(lonrad))*xdif + math.cos(math.radians(lonrad))*ydif
    y = - math.sin(math.radians(latrad))*math.cos(math.radians(lonrad))*xdif - math.sin(math.radians(latrad))*math.sin(math.radians(lonrad))*ydif + math.cos(math.radians(latrad))*zdif
    z =   math.cos(math.radians(latrad))*math.cos(math.radians(lonrad))*xdif + math.cos(math.radians(latrad))*math.sin(math.radians(lonrad))*ydif + math.sin(math.radians(latrad))*zdif
    return x, y, z


def geog2enu(latalvo, lonalvo, altalvo, latrad, lonrad, altrad):
    """Geografica para ENU.

    Entrada: latalvo e lonalvo (graus), altalvo (m)  - coord geograficas do alvo
             latrad e lonrad (graus), altrad (m)     - coord geograficas do radar
    Saida: x, y, z   (m)  -  coordenadas cartesianas do alvo em relacao ao radar
    """
    X, Y, Z = geog2ecef(latalvo, lonalvo, altalvo)
    x, y, z = ecef2enu(X, Y, Z, latrad, lonrad, altrad)
    return x, y, z

if __name__ == "__main__":
    print ""
    latrad = float(raw_input("Entre com latitude  do radar (em graus):  "))
    lonrad = float(raw_input("Entre com longitude do radar (em graus):  "))
    altrad = float(raw_input("Entre com altitude  do radar (em metros):  "))
    print ""

    while True:
        latalvo = float(raw_input("Entre com latitude  do alvo (em graus):  "))
        lonalvo = float(raw_input("Entre com longitude do alvo (em graus):  "))
        altalvo = float(raw_input("Entre com altitude  do alvo (em metros):  "))

        x, y, z = geog2enu(latalvo, lonalvo, altalvo, latrad, lonrad, altrad)
        print "Coord X do alvo:  %15.10f m" % x, "  | %15.10f mn" % float(x/1852)
        print "Coord Y do alvo:  %15.10f m" % y, "  | %15.10f mn" % float(y/1852)
        print "Coord Z do alvo:  %15.10f m" % z, "  | %15.10f mn" % float(z/1852)
        print ""
