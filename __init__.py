# Mrs
# Copyright 2008 Brigham Young University
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
# Inquiries regarding any further use of the Materials contained on this site,
# please contact the Copyright Licensing Office, Brigham Young University,
# 3760 HBLL, Provo, UT 84602, (801) 422-9339 or 422-3821, e-mail
# copyright@byu.edu.

# TODO: fix the sample code in the following docstring:
"""Mrs: MapReduce - a Simple implementation

Your Mrs MapReduce program might look something like this:

def mapper(key, value):
    yield newkey, newvalue

def reducer(key, values):
    yield newvalue

if __name__ == '__main__':
    import mrs
    mrs.main(mapper, reducer)
"""

import datasets, job, master, parallel, registry, rpc, serial, slave, task, \
        util, version

from version import VERSION
from registry import Registry
from io import TextWriter, HexWriter
from cli import main, primary_impl, option_parser
from partition import hash_partition, mod_partition


# vim: et sw=4 sts=4
