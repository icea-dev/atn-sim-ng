"""@package asterix
EUROCONTROL ASTERIX encoder

A library that encodes in the EUROCONTROL ASTERIX format as
specified in the document EUROCONTROL-SPEC-0149.
Edition Number: 2.1
Edition Date: 14/04/2013

Category specifications Xml files in the "config/" directory were taken from
https://github.com/CroatiaControlLtd/asterix/tree/master/install/config
These files were public under GPLv3 license.
"""

__copyright__ = '''\
The MIT License (MIT)

Copyright (c) 2014 Vitor Augusto Ferreira Santa Rita

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#TODO: evaluate if better using lxml for performance
from xml.dom import minidom
import os
import traceback

## verbose[int]: Debug information.
verbose = 0

#TODO: check files against "config/asterix.dtd" structure
## filenames[dict string]: XML files.
filenames = \
    {1: 'asterix_cat001_1_1.xml',
     2: 'asterix_cat002_1_0.xml',
     8: 'asterix_cat008_1_0.xml',
    10: 'asterix_cat010_1_1.xml',
    19: 'asterix_cat019_1_2.xml',
    20: 'asterix_cat020_1_7.xml',
    #21: 'asterix_cat021_0_23.xml',
    21: 'asterix_cat021_0_26.xml',
    #21: 'asterix_cat021_1_8.xml',
    23: 'asterix_cat023_0_13.xml',
    30: 'asterix_cat030_6_2.xml',
    31: 'asterix_cat031_6_2.xml',
    #32: 'asterix_cat032_6_2.xml',
    32: 'asterix_cat032_7_0.xml',
    34: 'asterix_cat034_1_26.xml',
    48: 'asterix_cat048_1_14.xml',
    #62: 'asterix_cat062_0_17.xml',
    #62: 'asterix_cat062_1_9.xml',
    62: 'asterix_cat062_1_16.xml',
    #62: 'asterix_cat062_1_7.xml',
    63: 'asterix_cat063_1_3.xml',
    65: 'asterix_cat065_1_3.xml',
    #65:'asterix_cat065_1_2.xml',
    242: 'asterix_cat242_1_0.xml',
    #252: 'asterix_cat252_6_2.xml',
    252: 'asterix_cat252_7_0.xml'}  # ,
    #252: 'asterix_cat252_6_1.xml'}


def load_asterix_category_format(k):
    """
    Return a Document object representing the content of the document from the given input.

    Args:
        k (int): The ASTERIX category.

    Returns:
        xml.dom.minidom: The Document Object Model interface.

    """
    global filenames
    try:
        # Look for file in current executing directory
        path_filename1 = filenames[k]

        # On default directory (absolute)
        path_filename2 = "/opt/atn-sim/configs/asterix/" + filenames[k]

        # On default directory (relative)
        path_filename3 = os.path.dirname(os.path.realpath(__file__)) + "../../../config/asterix/" + filenames[k]

        if os.path.isfile(path_filename1):
            # print "Loading file '%s'" % path_filename1
            return minidom.parse(path_filename1)

        if os.path.isfile(path_filename2):
            # print "Loading file '%s'" % path_filename2
            return minidom.parse(path_filename2)

        if os.path.isfile(path_filename3):
            # print "Loading file '%s'" % path_filename3
            return minidom.parse(path_filename3)

        return None

    except:
        traceback.print_exc()

    return None


def encode(asterix):
    """
    Encodes a dictionary (asterix) in the EUROCONTROL ASTERIX category.

    Args:
        asterix (dict): A dictionary with data block of ASTERIX category.

    Returns:
        asterix_record (buffer): Data block buffer.

    """
    assert type(asterix) is dict

    asterix_record = 0

    #priority_asterix_cat = [21, 34]
    for k, v in asterix.iteritems():
    #for k in priority_asterix_cat:
        v = asterix[k]
        record = 0
        n_octets_data_record = 0
        cat = 0

        ctf = load_asterix_category_format(k)

        if ctf is None:
            continue

        if verbose >= 1:
            print 'encoding cat', k

        cat = k

        for cat_tree in ctf.getElementsByTagName('Category'):

            if k != int(cat_tree.getAttribute('id')):
                continue

            for data_record in v:
                ll_db, db = encode_category(k, data_record, cat_tree)

                #TODO: use maximum datablock size
                record <<= ll_db * 8
                record += db
                n_octets_data_record += ll_db

                if verbose >= 1:
                    print "Tamanho do bloco de dados ", ll_db

            break

        # Record header ( CAT + LEN )
        record += (cat << (n_octets_data_record * 8 + 16))
        record += ((1 + 2 + n_octets_data_record) << ((n_octets_data_record) * 8))

        asterix_record <<= (1 + 2 + n_octets_data_record) * 8
        asterix_record += record

    return asterix_record


def encode_category(cat, did, tree):
    """
    Encodes the record from the given category (cat).

    Args:
        cat (int): The given category.
        did (dict): The dictionary with data to encode.
        tree (Document object): The specification for ASTERIX category.

    Returns:
         (n_octets_data_record, data_record) (tuples): The caetgory record size and record.

    """
    if did == {}:
        return 0, 0

    mdi = {}
    for c in tree.getElementsByTagName('DataItem'):
        di = c.getAttribute('id')
        if di.isdigit():
            di = int(di)
        rule = c.getAttribute('rule')
        if di in did:
            if verbose >= 1:
                print 'encoding dataitem', di
            l, v = encode_dataitem(did[di], c)
            mdi[di] = l, v
        else:
            if rule == 'mandatory' and verbose >= 1:
                print 'absent mandatory dataitem', di

    data_record = 0L
    n_octets_data_record = 0
    sorted_mdi_keys = sorted(mdi.keys())

    fspec_bits = []
    uap_tree = tree.getElementsByTagName('UAP')[0]
    for cn in uap_tree.childNodes:
        if cn.nodeName != 'UAPItem':
            continue

        uapi_value = cn.firstChild.nodeValue

        if uapi_value.isdigit():
            uapi_value = int(uapi_value)

        if uapi_value in sorted_mdi_keys:
            fspec_bits.append(int(cn.getAttribute('bit')))
            l, v = mdi[uapi_value]
            data_record <<= l * 8
            data_record += v
            n_octets_data_record += l

    if fspec_bits == []:
        print 'no dataitems identified'
        return 0, 0

    # FSPEC for data record
    max_bit = max(fspec_bits)
    n_octets_fspec = max_bit / 8 + 1

    # Fn
    fspec = 0
    for i in fspec_bits:
        fspec += (1 << (n_octets_fspec * 8 - 1 - i))

    # FX
    for i in range(n_octets_fspec - 1):
        fspec += (1 << ((n_octets_fspec - 1 - i) * 8))

    data_record += (fspec << (n_octets_data_record * 8))
    n_octets_data_record += n_octets_fspec

    return n_octets_data_record, data_record


def encode_dataitem(dfd, tree):
    """Returns the encoded Data Item.

    Encodes the Data Item in the data field of record according to the rules
    defined in the XML file.

    Args:
        dfd (dict): The dictionary with Data Item values.
        tree (Document object): The specification for ASTERIX category.

    Returns:
        (length, value) (tuples): The Data Field size and Data Field.

    """
    assert type(dfd) is dict or type(dfd) is list
    for c in tree.getElementsByTagName('DataItemFormat'):
        for d in c.childNodes:
            if d.nodeName == 'Fixed':
                return encode_fixed(dfd, d)
            else:
                if d.nodeName == 'Variable':
                    return encode_variable(dfd, d)
                else:
                    if d.nodeName == 'Repetitive':
                        return encode_repetitive(dfd, d)
                    else:
                        if d.nodeName == 'Compound':
                            return encode_compound(dfd, d)


def encode_fixed(bd, tree):
    """
    Returns the encoded Data Item as a fixed length Data Field.

    Args:
        dfd (dict): The dictionary with Data Item values.
        tree (Document object): The rules to encode Data Item.

    Returns:
        (length, value) (tuples): The Data Field size and Data Field.

    """
    length = int(tree.getAttribute('length'))
    value = 0
    has_encoded = False
    for cn in tree.childNodes:
        if cn.nodeName != 'Bits':
            continue

        key = cn.getElementsByTagName('BitsShortName')[0].firstChild.nodeValue
        bits_unit = cn.getElementsByTagName('BitsUnit')

        if key in bd and key != 'FX':
            has_encoded = True

            assert (cn.getAttribute('bit') == '' and (cn.getAttribute('from') != '' and cn.getAttribute('to') != '')) or (cn.getAttribute('bit') != '' and (cn.getAttribute('from') == '' and cn.getAttribute('to') == ''))

            bit_ = cn.getAttribute('bit')
            if bit_ != '':
                bit_ = int(bit_)
                shift_left = bit_ - 1
                mask = 0x1
            else:
                from_ = int(cn.getAttribute('from'))
                to_ = int(cn.getAttribute('to'))
                if from_ < to_:  # swap values
                    x = to_
                    to_ = from_
                    from_ = x
                shift_left = to_ - 1
                mask = (1 << (from_ - to_ + 1)) - 1

            v = bd[key]

            if len(bits_unit):
                scale = bits_unit[0].getAttribute('scale')
                v = int(v / float(scale))

            #TODO: consider 'encode' attr
            value += ((v & mask) << shift_left)
        else:
            if key != 'FX' and verbose >= 2:
                print 'field', key, 'absent in input'

    if has_encoded is False:
        return 0, 0

    return length, value


def encode_variable(db, tree):
    """
    Returns the encoded Data Item as a variable length Data Field.

    Args:
        dfd (dict): The dictionary with Data Item values.
        tree (Document object): The rules to encode Data Item.

    Returns:
        (length, value) (tuples): The Data Field size and Data Field.

    """
    variable = None
    length = 0
    for cn in tree.childNodes:
        if cn.nodeName == 'Fixed':
            l, v = encode_fixed(db, cn)
            assert l <= 1
            if l > 0:
                if v % 2 == 1:  # remove FX
                    v -= 1

                length += 1
                if variable is None:
                    variable = v
                else:
                    variable += 1  # add FX
                    variable <<= 8
                    variable += v
            else:
                break

    return length, variable


def encode_repetitive(db, tree):
    """
    Returns the encoded Data Item as a repetitive Data Field.

    Args:
        dfd (dict): The dictionary with Data Item values.
        tree (Document object): The rules to encode Data Item.

    Returns:
        (length, value) (tuples): The Data Field size and Data Field.

    """
    found = False
    cn = None
    for cn in tree.childNodes:
        if cn.nodeName == 'Fixed':
            found = True
            break  # found

    if found is False:
        if verbose >= 1:
            print 'Repetitive node not found'
        return 0, 0

    assert type(db) is list
    length = 0
    value = 0
    rep = len(db)
    for i in range(rep):
        l, v = encode_fixed(db[i], cn)
        assert l > 0

        length += l
        value <<= (8 * l)
        value += v

    value += (rep << (8 * length))  # add REP header
    return length + 1, value


def encode_compound(db, tree):
    """
    Returns the encoded Data Item as a compound Data Field.

    Args:
        dfd (dict): The dictionary with Data Item values.
        tree (Document object): The rules to encode Data Item.

    Returns:
        (length, value) (tuples): The Data Field size and Data Field.

    """
    length = 0
    data = 0
    sf = 0
    subfields = []
    for cn in tree.childNodes:
        l = 0
        if cn.nodeName == 'Variable':
            l, v = encode_variable(db, cn)
        else:
            if cn.nodeName == 'Fixed':
                l, v = encode_fixed(db, cn)
            else:
                if cn.nodeName == 'Repetitive':
                    l, v = encode_repetitive(db, cn)
                else:
                    if cn.nodeName == 'Variable':
                        l, v = encode_variable(db, cn)
                    else:
                        if cn.nodeName == 'Compound':
                            l, v = encode_compound(db, cn)

        if l > 0:
            subfields.append(sf)
            length += l
            data <<= (8 * l)
            data += v

        sf += 1

    n_octets = max(subfields) / 7 + 1
    primary_subfield = 0
    for i in sorted(subfields):  # subfields
        primary_subfield += (1 << (8 * (i / 7) + (8 - (i % 7))))
    for i in range(n_octets - 1):  # FX
        primary_subfield += (1 << 8 * (i + 1))

    data += (primary_subfield << (8 * length))

    return length + n_octets, data
