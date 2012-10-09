# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: beam_text.py 56 2010-02-11 12:50:16Z nicolas $
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

"""""""""some text

"""""""""
#TODO: i18n

import gettext
import os
from beam_consts import *

titles = {}
titles['select_op']   = _('Welcome to BeaM')
titles['svg_part']    = _('Backup stage 1/3: what you want to save')
titles['svg_kind']    = _('Backup stage 2/3: where you want to save')
titles['svg_name']    = _('Backup stage 3/3: identification')
titles['svg_summary'] = _('Backup summary')
titles['svg_go']      = _('Backup in progress')
titles['rst_kind']    = _('Restore stage 1/2: which image to restore')
titles['rst_part']    = _('Restore stage 2/2: which parts to restore')
titles['rst_summary'] = _('Restore summary')
titles['rst_go']      = _('Restore in progress')

summaries = {}
summaries['select_op'] = _(
"""On the page you will be able to select what you want to do, i.e. either do a backup of some of your partitions, or restore a backup.

click on « Backup » to make an image.
click on « Restore » to restore an image."""
)
summaries['svg_part'] = """On this page you can choose which partition you want to backup.

Checked parts will be saved, and uncheckable parts can not be saved using the LRS.
Parts can be (un)checked by clicking on it, or by hitting the key correponding to the bold character in front of the line.

click on « Previous » (or hit <b>P</b>) to go back.
click on « Next » (or hit <b>N</b>) to continue."""
summaries['svg_kind'] = """On this page you can choose where you want to save your image:

click on « Previous » (or hit <b>P</b>) to go back.
click on « Next » (or hit <b>N</b>) to continue."""
summaries['svg_name'] = """On this page you can give a name and a description of the image you will make.

The following characters are not allowed in the name of the image: « » (<i>space</i>) and «/» (<i>slash</i>)

click on « Previous » (or hit <b>P</b>) to go back.
click on « Next » (or hit <b>N</b>) to continue."""
summaries['svg_summary'] = """On this page you will find a summary of what the LRS will do.

click on « Previous » (or hit <b>P</b>) to go back.
click on « Go » (or hit <b>G</b>) to continue."""
summaries['svg_go'] = """Your system is currently backuped.

click on « Cancel » (or hit <b>C</b>) to cancel backup.
click on « Quit » (or hit <b>Q</b>) to quit."""
summaries['rst_kind'] = """On this page you can choose which image you want to restore:

· Local (key « <b>L</b> ») for a local drive,
· NFS (key « <b>N</b> ») for a NFS Share.

click on « Previous » (or hit <b>P</b>) to go back.
click on « Next » (or hit <b>N</b>) to continue."""
summaries['rst_part'] = """On this page you can choose which partition(s) you want to restore:

Checked parts will be restored.
Parts can be (un)checked by clicking on it, or by hitting the key correponding to the bold character in front of the line.

click on « Previous » (or hit <b>P</b>) to go back.
click on « Next » (or hit <b>N</b>) to continue."""
summaries['rst_summary'] = """On this page you will find a summary of what the LRS will do.

click on « Previous » (or hit <b>P</b>) to go back.
click on « Go » (or hit <b>G</b>) to continue."""
summaries['rst_go'] = """Your system is currently restored.

click on « Cancel » (or hit <b>C</b>) to cancel restoration.
click on « Quit » (or hit <b>Q</b>) to quit."""
