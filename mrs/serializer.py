# Mrs
# Copyright 2008-2011 Brigham Young University
#
# This file is part of Mrs.
#
# Mrs is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Mrs is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Mrs.  If not, see <http://www.gnu.org/licenses/>.
#
# Inquiries regarding any further use of Mrs, please contact the Copyright
# Licensing Office, Brigham Young University, 3760 HBLL, Provo, UT 84602,
# (801) 422-9339 or 422-3821, e-mail copyright@byu.edu.

from __future__ import division, print_function

from collections import namedtuple


Serializer = namedtuple('Serializer', ('dumps', 'loads'))

def key_serializer(serializer):
    """A decorator to specify a serializer for map or reduce functions."""
    def wrapper(f):
        f.key_serializer = serializer
        return f
    return wrapper

def value_serializer(serializer):
    """A decorator to specify a serializer for map or reduce functions."""
    def wrapper(f):
        f.value_serializer = serializer
        return f
    return wrapper

###############################################################################
# str <-> bytes

def str_loads(b):
    return b.decode('utf-8')

def str_dumps(s):
    return s.encode('utf-8')

str_serializer = Serializer(str_dumps, str_loads)

###############################################################################
# int <-> bytes

def int_loads(b):
    return int(b.decode('utf-8'))

def int_dumps(i):
    return str(i).encode('utf-8')

int_serializer = Serializer(int_dumps, int_loads)

# vim: et sw=4 sts=4
