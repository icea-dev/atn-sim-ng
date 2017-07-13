#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
parse_utils

DOCUMENT ME!

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/jul  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/07"

# < imports >--------------------------------------------------------------------------------------

# PyQt library
from PyQt4 import QtCore

# -------------------------------------------------------------------------------------------------
def parse_coord(f_element):
    """
    helper function to parse xml entries

    <coord>
      <tipo>F</tipo>
      <cpoA>IND</cpoA>
      <cpoB>5</cpoB>
      <cpoC>338</cpoC>
      <cpoD>1.5</cpoD>
    </coord>

    @param f_element: element to parse
    """
    # inicia o dicionário de dados
    ldct_tmp = {}

    # handle case tipo de coordenada
    if "tipo" == f_element.tagName():
        ldct_tmp["tipo"] = f_element.text()

    # handle latitude/X/cpoA
    elif "cpoA" == f_element.tagName():
        ldct_tmp["cpoA"] = f_element.text()

    # handle longitude/Y/cpoB
    elif "cpoB" == f_element.tagName():
        ldct_tmp["cpoB"] = f_element.text()

    # handle cpoC
    elif "cpoC" == f_element.tagName():
        ldct_tmp["cpoC"] = f_element.text()

    # handle cpoD
    elif "cpoD" == f_element.tagName():
        ldct_tmp["cpoD"] = f_element.text()

    # retorna o dicionário de dados
    return ldct_tmp

# -------------------------------------------------------------------------------------------------
def __parse_crd(f_element):
    """
    helper function to parse xml entries

    @param f_element: element to parse
    """
    # inicia o dicionário de dados
    ldct_crd = {}

    # obtém o primeiro nó da sub-árvore
    l_node = f_element.firstChild()
    assert l_node is not None

    # percorre a sub-árvore
    while not l_node.isNull():
        # tenta converter o nó em um elemento
        l_element = l_node.toElement()
        assert l_element is not None

        # o nó é um elemento ?
        if not l_element.isNull():
            # atualiza o dicionário de dados
            ldct_crd.update(parse_coord(l_element))

        # próximo nó
        l_node = l_node.nextSibling()
        assert l_node is not None

    # retorna o dicionário de dados
    return ldct_crd

# -------------------------------------------------------------------------------------------------
def parse_root_element(f_element):
    """
    helper function to parse xml entries

    @param f_element: root element to parse
    """
    # inicia o dicionário de dados
    ldct_root = {}

    # salva o tagName
    # ldct_root["tagName"] = f_element.tagName()
    ldct_root["tagName"] = f_element.tagName()

    # para todos os atributos...
    for li_ndx in xrange(f_element.attributes().size()):
        # obtém o atributo
        l_attr = f_element.attributes().item(li_ndx).toAttr()

        # associa o atributo ao valor
        # ldct_root[str(l_attr.name()).upper()] = l_attr.value()
        ldct_root[str(l_attr.name()).upper()] = l_attr.value()

    # retorna o dicionário de dados
    return ldct_root

# -------------------------------------------------------------------------------------------------
def parse_trafego(f_element):
    """
    helper function to the constructor, parses xml entries

    @param f_element: element to parse
    """
    # inicia o dicionário de dados
    ldct_tmp = {}

    # handle indicativo
    if "indicativo" == f_element.tagName():
        ldct_tmp["indicativo"] = f_element.text()

    # handle designador
    elif "designador" == f_element.tagName():
        ldct_tmp["designador"] = f_element.text()

    # handle ssr
    elif "ssr" == f_element.tagName():
        ldct_tmp["ssr"] = f_element.text()

    # handle origem
    elif "origem" == f_element.tagName():
        ldct_tmp["origem"] = f_element.text()

    # handle destino
    elif "destino" == f_element.tagName():
        ldct_tmp["destino"] = f_element.text()

    # handle procedimen
    elif "procedimento" == f_element.tagName():
        ldct_tmp["procedimento"] = f_element.text()

    # handle nivel
    elif "nivel" == f_element.tagName():
        ldct_tmp["nivel"] = f_element.text()

    # handle altitude
    elif "altitude" == f_element.tagName():
        ldct_tmp["altitude"] = f_element.text()

    # handle velocidade
    elif "velocidade" == f_element.tagName():
        ldct_tmp["velocidade"] = f_element.text()

    # handle proa
    elif "proa" == f_element.tagName():
        ldct_tmp["proa"] = f_element.text()

    # handle temptrafego
    elif "temptrafego" == f_element.tagName():
        ldct_tmp["temptrafego"] = f_element.text()

    # handle numsg
    elif "numsg" == f_element.tagName():
        ldct_tmp["numsg"] = f_element.text()

    # handle tempmsg
    elif "tempmsg" == f_element.tagName():
        ldct_tmp["tempmsg"] = f_element.text()

    # handle rvsm
    elif "rvsm" == f_element.tagName():
        ldct_tmp["rvsm"] = f_element.text()

    # handle rota
    elif "rota" == f_element.tagName():
        ldct_tmp["rota"] = f_element.text()

    # handle eet
    elif "eet" == f_element.tagName():
        ldct_tmp["eet"] = f_element.text()

    # handle niveltrj
    elif "niveltrj" == f_element.tagName():
        ldct_tmp["niveltrj"] = f_element.text()

    # handle veltrj
    elif "veltrj" == f_element.tagName():
        ldct_tmp["veltrj"] = f_element.text()

    # handle posição
    elif "coord" == f_element.tagName():
        ldct_tmp["coord"] = __parse_crd(f_element)

    # retorna o dicionário de dados
    return ldct_tmp

# < the end >--------------------------------------------------------------------------------------
