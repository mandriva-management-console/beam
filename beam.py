#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: beam.py 63 2010-02-12 08:35:00Z nicolas $
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

"""BeaM Main page

"""
__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 63 $"
__date__      = "$Date: 2007-05-14 19:32:52 +0200 (lun, 14 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import sys
import os
from time import time

# GTK API
import pygtk
pygtk.require('2.0')
import gtk
import gobject

# goes to the right place
__localpath__ = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(__localpath__)

# initialize i18n stuff
import gettext
from beam_consts import BEAM_APP_NAME, BEAM_I18N_FOLDER, BEAM_LRS_THREAD_AWAKE, BEAM_SELECTOR_STYLE
gettext.install(BEAM_APP_NAME, os.path.join(__localpath__, BEAM_I18N_FOLDER), True)

# LRS API
import lbx_utils
from lbx_lrs_net import lrs_net_init
from lbx_gtk_widgets import LbxBook, get_widget_r, lbx_error
from lbx_lrs_net import \
    lrs_get_next_tocken, lrs_get_next_tockens, lrs_send_ack
from lbx_lrs_cmd import halt_backup

# BeaM Stuff
from beam_pages import \
    PageGo, PageKindButton, PageKindFolder, PagePart, PageSelectOp, PageSummary, PageSvgName

class MainWindow(gtk.Window):
    """ App main class"""
    def __init__(self):
        """ init main window"""

        # init ancestor
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        book = LbxBook()
        book.pid = None
        book.set_name("book")
        # summons our pages
        book.add_page(PageSelectOp(book))

        if (BEAM_SELECTOR_STYLE == 'button'):
            book.add_page(PageKindButton('svg', book))
        elif (BEAM_SELECTOR_STYLE == 'folder'):
            book.add_page(PageKindFolder('svg', book))
        book.add_page(PagePart('svg', book))
        book.add_page(PageSvgName(book))
        book.add_page(PageSummary('svg', book))
        book.add_page(PageGo('svg', book))

        book.add_page(PagePart('rst', book))
        if (BEAM_SELECTOR_STYLE == 'button'):
            book.add_page(PageKindButton('rst', book))
        elif (BEAM_SELECTOR_STYLE == 'folder'):
            book.add_page(PageKindFolder('rst', book))
        book.add_page(PageSummary('rst', book))
        book.add_page(PageGo('rst', book))

        book.show()

        self.lrs_pid = None
        self.socket = None
        self.lastbytes = 0

        # define pages travel
        get_widget_r(
            book.get_page("select_op"),
            "button_svg").connect("clicked",
                lambda self: book.show_page("svg_part"))
        get_widget_r(
            book.get_page("select_op"),
            "button_rst").connect("clicked",
                lambda self: book.show_page("rst_kind"))
        get_widget_r(
            book.get_page("svg_part"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("select_op"))
        get_widget_r(
            book.get_page("svg_part"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("svg_kind"))
        get_widget_r(
            book.get_page("svg_kind"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("svg_part"))
        get_widget_r(
            book.get_page("svg_kind"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("svg_name"))
        get_widget_r(
            book.get_page("svg_name"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("svg_kind"))
        get_widget_r(
            book.get_page("svg_name"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("svg_summary"))
        get_widget_r(
            book.get_page("svg_summary"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("svg_name"))
        get_widget_r(
            book.get_page("svg_summary"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("svg_go"))
        get_widget_r(
            book.get_page("svg_go"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("svg_summary"))
        get_widget_r(
            book.get_page("svg_go"),
            "navbutton_0").connect("clicked",
                lambda self:
                    halt_backup(self.get_toplevel().lrs_pid))
        get_widget_r(
            book.get_page("svg_go"),
            "navbutton_1").connect("clicked", self._cb_quit)
        get_widget_r(
            book.get_page("rst_kind"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("select_op"))
        get_widget_r(
            book.get_page("rst_kind"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("rst_part"))
        get_widget_r(
            book.get_page("rst_part"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("rst_kind"))
        get_widget_r(
            book.get_page("rst_part"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("rst_summary"))
        get_widget_r(
            book.get_page("rst_summary"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("rst_part"))
        get_widget_r(
            book.get_page("rst_summary"),
            "navbutton_1").connect("clicked",
                lambda self: book.show_page("rst_go"))
        get_widget_r(
            book.get_page("rst_go"),
            "navbutton_0").connect("clicked",
                lambda self: book.show_page("rst_summary"))
        get_widget_r(
            book.get_page("rst_go"),
            "navbutton_0").connect("clicked",
                lambda self:
                    halt_backup(self.get_toplevel().lrs_pid))
        get_widget_r(
            book.get_page("rst_go"),
            "navbutton_1").connect("clicked", self._cb_quit)
        self.connect("destroy", self._cb_quit)

        # define our window
        #self.set_default_size(750, 550)
        self.set_geometry_hints(None, 750, 440, -1, -1)
        #self.set_resizable(False)
        self.add(book)
        self.set_title('Linbox Rescue Server')

        # display page #1
        book.show_page("select_op")
        self.backupdata = {}
        self.reset_data()

        self.add_accel_group(book.accel_group)
        self.show()

    def reset_data(self):
        """ Refresh data using thoses send by LRS binaries"""
        self.backupdata['startbytes'] = 0
        self.backupdata['currentbytes'] = 0
        self.backupdata['lastbytes'] = 0
        self.backupdata['usedbytes'] = 0
        self.backupdata['totalbytes'] = 0
        self.backupdata['usedblocks'] = 0
        self.backupdata['totalblocks'] = 0
        self.backupdata['starttime'] = 0
        self.backupdata['lasttime'] = 0
        self.backupdata['currenttime'] = 0
        self.backupdata['totaltime'] = 0
        self.backupdata['source'] = ''
        self.backupdata['target'] = ''
        self.backupdata['tool'] = ''

        self.backupdata['starttime'] = 0
        self.backupdata['lasttime'] = 0
        self.backupdata['currenttime'] = 0
        self.backupdata['endtime'] = 0

    def _cb_quit(self, widget=None):
        """ terminate the main window"""
        halt_backup(self.lrs_pid)
        gtk.main_quit()

    def _cb_refresh_backupdata(self, source, condition):
        """ refresh progress window using collected data"""
        (myconnection, addr) = source.accept()
        command = lrs_get_next_tocken(myconnection)
        data = lrs_get_next_tockens(myconnection)
        if (command == "init_backup"):
            self.backupdata['source'] = data[0]
            self.backupdata['target'] = data[1]
            self.backupdata['totalblocks'] = int(data[2])
            self.backupdata['totalbytes'] = int(data[2]) * 512
            self.backupdata['usedblocks'] = int(data[3])
            self.backupdata['usedbytes'] = int(data[3]) * 512
            self.backupdata['tool'] = data[4]

            self.backupdata['startbytes'] = 0
            self.backupdata['currentbytes'] = self.backupdata['startbytes']
            self.backupdata['lastbytes'] = self.backupdata['startbytes']

            self.backupdata['starttime'] = time()
            self.backupdata['lasttime'] = self.backupdata['starttime']
            self.backupdata['currenttime'] = self.backupdata['starttime']
        elif (command == "init_restore"):
            self.backupdata['source'] = data[0]
            self.backupdata['target'] = data[1]
            self.backupdata['usedbytes'] = int(data[3]) * 1024
            self.backupdata['startbytes'] = 0
            self.backupdata['currentbytes'] = self.backupdata['startbytes']
            self.backupdata['lastbytes'] = self.backupdata['startbytes']
            self.backupdata['starttime'] = time()
            self.backupdata['lasttime'] = self.backupdata['starttime']
            self.backupdata['currenttime'] = self.backupdata['starttime']
        elif (command == "refresh_file"):
            self.backupdata['source'] = data[0]
            self.backupdata['target'] = data[3]
        elif (command == "refresh_backup_progress"):
            self.backupdata['currentbytes'] = int(data[0])
            self.backupdata['currenttime'] = time()
        elif (command == "close"):
            self.backupdata['currentbytes'] = self.backupdata['usedbytes']
        elif (command == "misc_error"):
            lbx_error(data[0], data[1])
            lrs_send_ack(myconnection)
            get_widget_r(self, "book").show_page("select_op")
            return True
        elif (command == "backup_write_error"):
            lbx_error('Error', command)
            lrs_send_ack(myconnection)
            return True
        else:
            lbx_error(command, "UNKNOWN CLIENT COMMAND : %s" % command)
            lrs_send_ack(myconnection)
            self._cb_halt_backup()
            get_widget_r(self, "book").show_page("select_op")
            return True
        lrs_send_ack(myconnection)
        return True

    def _cb_halt_backup(self):
        """ stops a running backup"""
        lbx_lrs_cmd.halt_backup(self.lrs_pid)

    def _cb_refresh_backupdisplay(self):

        elapsed_bytes = \
            self.backupdata['currentbytes'] - self.backupdata['lastbytes']
        elapsed_time = \
            self.backupdata['currenttime'] - self.backupdata['lasttime']
        total_bytes = \
            self.backupdata['currentbytes'] - self.backupdata['startbytes']
        total_time = \
            self.backupdata['currenttime'] - self.backupdata['starttime']

        remaining_bytes = \
            self.backupdata['usedbytes'] - self.backupdata['currentbytes']

        try:
            remaining_time = total_time * (
                float(self.backupdata['usedbytes']) /
                self.backupdata['currentbytes'] -
                1
            )
        except ZeroDivisionError:
            remaining_time = 0

        try:
            overall_rate = total_bytes / total_time
        except ZeroDivisionError:
            overall_rate = 0

        try:
            instant_rate = elapsed_bytes / elapsed_time
        except ZeroDivisionError:
            instant_rate = 0

        try:
            percent_prog = float(self.backupdata['currentbytes']) / \
                self.backupdata['usedbytes'] * 100
        except ZeroDivisionError:
            percent_prog = 0

        for i in ('svg', 'rst'):
            get_widget_r(self, "%s_entry_src" % i).set_text(
                '%d min %02d secs (%s)' % \
                (
                    total_time // 60,
                    total_time % 60,
                    lbx_utils.human_readable(self.backupdata['currentbytes'])
                )
            )
            get_widget_r(self, "%s_entry_src" % i).\
                set_text(self.backupdata['source'])
            get_widget_r(self, "%s_entry_dst" % i).\
                set_text(self.backupdata['target'])
            get_widget_r(self, "%s_entry_eltime" % i).set_text(
                '%d min %02d secs (%s)' % \
                (
                    total_time // 60,
                    total_time % 60,
                    lbx_utils.human_readable(self.backupdata['currentbytes'])
                )
            )
            get_widget_r(self, "%s_entry_rate" % i).set_text(
                '%s (instant = %s)' % \
                (
                    lbx_utils.human_readable(overall_rate, 'B/s'),
                    lbx_utils.human_readable(instant_rate, 'B/s')
                )
            )
            get_widget_r(self, "%s_entry_remtime" % i).set_text(
                '%d min %02d secs (%s)' % \
                (
                    remaining_time // 60,
                    remaining_time % 60,
                    lbx_utils.human_readable(remaining_bytes)
                )
            )

            self.lastbytes = 0
            get_widget_r(self, "%s_progress_bar" % i).set_text(
                "Backupping %s : %d%%" % \
                (self.backupdata['source'], percent_prog)
            )
            get_widget_r(self, "%s_progress_bar" % i).set_fraction(
                float(percent_prog) / 100
            )

        self.backupdata['lasttime']  = self.backupdata['currenttime']
        self.backupdata['lastbytes'] = self.backupdata['currentbytes']

        return True

    def main(self):

        # begin to listen
        self.socket = lrs_net_init()

        # gather results when available
        gobject.io_add_watch(
            self.socket,
            gtk.gdk.INPUT_READ,
            self._cb_refresh_backupdata
        )

        # refresh display
        gobject.timeout_add(
            BEAM_LRS_THREAD_AWAKE,
            self._cb_refresh_backupdisplay
        )

        gtk.main()
        sys.exit()

if __name__ == "__main__":
    main = MainWindow()
    main.main()

