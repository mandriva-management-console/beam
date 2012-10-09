# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_logging.py 52 2010-02-11 09:08:24Z nicolas $
#
# This file is part of BeaM
#
# BeaM is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# BeaM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2. If not, see <http://www.gnu.org/licenses/>.
#

"""Linbox Logger

"""
__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 52 $"
__date__      = "$Date: 2007-05-14 19:32:52 +0200 (lun, 14 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/tmp/lrs.log',
                    filemode='w')
