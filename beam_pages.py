# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: beam_pages.py 60 2010-02-11 13:45:42Z nicolas $
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

"""BeaM Pages
"""

# GTK bindings
import pygtk
pygtk.require('2.0')
import gtk

# misc modules
import os
import string
import re

# misc functions
from socket import gethostname
from datetime import datetime

# LRS modules
import lbx_utils
import lbx_lrs_cmd
import lbx_lrs_image

# LRS functions
from lbx_diskinfo import get_parts
from lbx_gtk_widgets import \
    LbxPage, LbxImgButton, LbxImgToggleButton, LbxComboBox, LbxNavButton, \
    LbxImgCheckButton, get_widget_r

# BeaM modules
import beam_text
from beam_consts import BEAM_LRS_SAVE_FOLDER, BEAM_LRS_IMG_GRUBFILE

class PageSelectOp(LbxPage):
    """ Page used to select the operation (save, restore, ...)"""
    def __init__(self, book=None):
        # init ancestor
        LbxPage.__init__(
            self,
            "select_op",
            beam_text.titles['select_op'],
            beam_text.summaries['select_op'],
            book
        )

        # summon 2 buttons
        button_svg = LbxImgButton(_('<b><u>B</u></b>ackup'), 'gtk-media-record')
        button_rst = LbxImgButton(_('<b><u>R</u></b>estore'), 'gtk-media-play')
        button_svg.add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('B')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        button_rst.add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('D')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        button_svg.set_name("button_svg")
        button_rst.set_name("button_rst")

        # add them to a vbox
        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        button_box.add(button_svg)
        button_box.add(button_rst)

        # add the vbox to the page
        self.get_contentbox().pack_start(button_box, True, False)

class PageGo(LbxPage):
    """ Page used to display the status of the operation (save, restore, ...)"""

    def _cb_show(self, widget):
        """ Re-init progress bar when shown"""
        widget = widget # cheats pylint
        get_widget_r(self, "%s_progress_bar" % self.mode).set_text('')
        get_widget_r(self, "%s_progress_bar" % self.mode).set_fraction(0)

    def __init__(self, mode, book=None):
        """ init page """
        # init ancestor
        LbxPage.__init__(self,
            '%s_go' % mode,
            beam_text.titles['%s_go' % mode],
            beam_text.summaries['%s_go' % mode],
            book)

        # keep track of selected mode
        self.mode = mode

        # get labels
        # TODO: alternative labels when restoring
        label_src = gtk.Label(_("Partition currently backuped:"))
        label_dst = gtk.Label(_("Destination directory:"))
        label_rate = gtk.Label(_("Averate rate:"))
        label_eltime = gtk.Label(_("Elapsed time:"))
        label_remtime = gtk.Label(_("Remaining time:"))

        entry_src = gtk.Label()
        entry_src.set_name('%s_entry_src' % mode)
        entry_src.set_size_request(300, -1)
        entry_dst = gtk.Label()
        entry_dst.set_name('%s_entry_dst' % mode)
        entry_dst.set_size_request(300, -1)
        entry_rate = gtk.Label()
        entry_rate.set_name('%s_entry_rate' % mode)
        entry_rate.set_size_request(300, -1)
        entry_eltime = gtk.Label()
        entry_eltime.set_name('%s_entry_eltime' % mode)
        entry_eltime.set_size_request(300, -1)
        entry_remtime = gtk.Label()
        entry_remtime.set_name('%s_entry_remtime' % mode)
        entry_remtime.set_size_request(300, -1)

        align1 = gtk.Alignment(0.5, 0, 1, 1)
        align1.set_padding(0, 0, 10, 10)
        align1.add(entry_src)
        align2 = gtk.Alignment(0.5, 0, 1, 1)
        align2.set_padding(0, 0, 10, 10)
        align2.add(entry_dst)
        align3 = gtk.Alignment(0.5, 0, 1, 1)
        align3.set_padding(0, 0, 10, 10)
        align3.add(entry_rate)
        align4 = gtk.Alignment(0.5, 0, 1, 1)
        align4.set_padding(0, 0, 10, 10)
        align4.add(entry_eltime)
        align5 = gtk.Alignment(0.5, 0, 1, 1)
        align5.set_padding(0, 0, 10, 10)
        align5.add(entry_remtime)

        table = gtk.Table(2, 5, False)
        table.attach(label_src,
                0, 1, 0, 1,
                gtk.SHRINK,
                gtk.SHRINK
        )
        table.attach(label_dst,
                0, 1, 1, 2,
                gtk.SHRINK,
                gtk.SHRINK
        )
        table.attach(label_rate,
                0, 1, 2, 3,
                gtk.SHRINK,
                gtk.SHRINK
        )
        table.attach(label_eltime,
                0, 1, 3, 4,
                gtk.SHRINK,
                gtk.SHRINK
        )
        table.attach(label_remtime,
                0, 1, 4, 5,
                gtk.SHRINK,
                gtk.SHRINK
        )
        table.attach(align1,
                1, 2, 0, 1,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK|gtk.FILL
        )
        table.attach(align2,
                1, 2, 1, 2,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK|gtk.FILL
        )
        table.attach(align3,
                1, 2, 2, 3,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK|gtk.FILL
        )
        table.attach(align4,
                1, 2, 3, 4,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK|gtk.FILL
        )
        table.attach(align5,
                1, 2, 4, 5,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK|gtk.FILL
        )

        # summon prog bar
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_name("%s_progress_bar" % mode)

        align_prog = gtk.Alignment(0.5, 0, 0.5, 1)
        align_prog.set_padding(0, 0, 10, 10)
        align_prog.add(self.progress_bar)

        self.get_contentbox().pack_start(table, True, True)
        self.get_contentbox().pack_start(align_prog, False, True, 5)

        # add the VBox itself
        self.connect("show", self._cb_show)
        self.get_contentbox().pack_start(LbxNavButton(
            (
            (_("<b><u>C</u></b>ancel"), 'gtk-go-back'),
            (_("<b><u>Q</u></b>uit"), 'gtk-go-forward')
            )
            ), False, True)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('C')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('Q')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )

class PageSummary(LbxPage):
    """ Page used to display a summary of what will be done """
    # TODO: organize source :D
    def _cb_show(self, widget=None, data=None):
        """ refresh summary when shown"""
        widget = widget # cheats pylint
        summary = get_widget_r(self, "summary")
        # TODO: handle rst mode
        if self.mode == 'svg':
            summary.set_text(_("Image « <b><u>%s</u></b> »\nstored in <b>%s</b> ") % \
                (self.book.get_page("svg_name").get_imagename(),
                self.book.get_page("svg_kind").get_target())
            )
        summary.set_justify(gtk.JUSTIFY_CENTER)
        summary.set_use_markup(True)

    def launch_backup(self, widget=None, data=None):
        """ called when the user starts a backup"""
        widget = widget # cheats pylint
        savepath = os.path.join(
            self.book.get_page("svg_kind").get_target(),
            self.book.get_page("svg_name").get_imagename().\
                translate(string.maketrans(" /*:?!", "______"))
        )
        binpath = os.path.join(
            os.getcwd(),
            'lrs-bin',
            'revobin'
        )
        exclude = string.join(
            self.book.get_page("svg_part").get_selected_parts(),
            '\n'
        )
        name = self.book.get_page("svg_name").get_imagename()
        desc = self.book.get_page("svg_name").get_imagedesc()
        self.get_toplevel().lrs_pid = lbx_lrs_cmd.run_backup(
            savepath,
            binpath,
            exclude,
            name,
            desc,
            self.get_toplevel()
        )

    def launch_restore(self, widget=None, data=None):
        """ called when the user starts a restore"""
        widget = widget # cheats pylint
        savepath = self.book.get_page("rst_kind").get_source()
        binpath = os.path.join(
            os.getcwd(),
            'lrs-bin',
            'revobin'
        )
        newlines = []
        # TODO: conf file is generated here, should be handled in LS modules
        if lbx_lrs_image.is_lrs_image(savepath):
            fd_grub_file = open(os.path.join(
                savepath,
                BEAM_LRS_SAVE_FOLDER,
                BEAM_LRS_IMG_GRUBFILE
            ))
            for line_grub_file in fd_grub_file:
                line_grub_file = line_grub_file.strip("\n")
                for line in \
                    self.book.get_page("rst_part").get_selected_parts():
                    if re.match('^#', line, 1): # line should be commented
                        if line == ('#%s' % line_grub_file):
                            line_grub_file = line # comment out the current line
                            break
                    else: # line should be uncommented
                        if line_grub_file == ('#%s' % line):
                            line_grub_file = line # uncomment the current line
                            break
                newlines.append(line_grub_file)
        fd_grub_file.close()

        fd_grub_file = open(os.path.join(
            savepath,
            BEAM_LRS_SAVE_FOLDER,
            BEAM_LRS_IMG_GRUBFILE
        ), 'w')
        fd_grub_file.write('\n'.join(newlines))
        fd_grub_file.close()
        self.get_toplevel().lrs_pid = lbx_lrs_cmd.run_restore(
            savepath,
            binpath,
            self.get_toplevel()
        )

    def __init__(self, mode, book=None):
        """ init page """
        LbxPage.__init__(self,
            '%s_summary' % mode,
            beam_text.titles['%s_summary' % mode],
            beam_text.summaries['%s_summary' % mode],
            book)

        self.mode = mode
        summary = gtk.Label()
        summary.set_name("summary")

        align = gtk.Alignment(0, 1, 1, 1)
        align.add(summary)

        self.get_contentbox().pack_start(align, True, True)
        self.get_contentbox().pack_start(gtk.HSeparator(), False, False, 5)
        self.get_contentbox().pack_start(LbxNavButton(
            (
                (_("<b><u>P</u></b>revious"), 'gtk-go-back'),
                (_("<b><u>G</u></b>o"), 'gtk-go-forward')
            )
            ), False, True)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('P')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('G')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        self.connect(
            "show",
            self._cb_show,
            None
        )

        if self.mode == 'svg':
            get_widget_r(self, "navbutton_1").connect(
                "clicked",
                self.launch_backup,
                None
            )
        elif self.mode == 'rst':
            get_widget_r(self, "navbutton_1").connect(
                "clicked",
                self.launch_restore,
                None
            )

class PagePart(LbxPage):
    """ Page used to select the partition(s) on which we want to operate """
    def _cb_toggle_button(self, widget=None, data=None):
        """ callback called when a box is (un)checked """

        if self.mode == 'svg': # SVG mode, add to selection unckecked buttons
            if not widget.get_active():
                if data not in self.selected_parts:
                    self.add_part_to_selection(data)
                    self.count_ckecked -= 1
                    if self.count_ckecked == 0:
                        get_widget_r(self, "navbutton_1").set_sensitive(False)
            else:
                self.del_part_from_selection(data)
                self.count_ckecked += 1
                if self.count_ckecked == 1:
                    get_widget_r(self, "navbutton_1").set_sensitive(True)
        elif self.mode == 'rst': # RST mode, checked button are uncommented,
                                 # unckecked buttons are commented
            if not widget.get_active(): # button goes from checked to unckecked
                                        # so comment partition
                self.del_part_from_selection(data)
                self.add_part_to_selection('#%s' % data)
                self.count_ckecked -= 1
                if self.count_ckecked == 0:
                    get_widget_r(self, "navbutton_1").set_sensitive(False)
            else:                       # button goes from unchecked to ckecked
                                        # so uncomment partition
                self.del_part_from_selection('#%s' % data)
                self.add_part_to_selection(data)
                self.count_ckecked += 1
                if self.count_ckecked == 1:
                    get_widget_r(self, "navbutton_1").set_sensitive(True)

    def _cb_show(self, widget=None, data=None):
        """ init page """
        if self.mode == 'rst': # restore move: summon widgets
            accel_int = 1
            self.clear_selected_parts()
            container = get_widget_r(widget, "container")

            # clean container
            for child in container:
                child.destroy()
            self.count_checked = 0

            # iterate over each part
            for (diskid, disk) in lbx_lrs_image.get_image_stats(
                self.book.get_page("rst_kind").get_source()
            )['disks'].items():
                button_box = gtk.VButtonBox()
                button_box.set_layout(gtk.BUTTONBOX_SPREAD)
                if (accel_int < 10):
                    button = LbxImgCheckButton(
                        _("<b><u>%d</u></b>. Partition Table") % accel_int
                        )
                    button.add_accelerator(
                        "clicked",
                        self.book.accel_group,
                        ord('%d' % accel_int),
                        0,
                        gtk.ACCEL_VISIBLE
                    )
                else:
                    button = LbxImgCheckButton(_("%d. Partition Table") %
                        (
                            accel_int
                        ))
                accel_int += 1

                button.set_active(1)
                self.count_ckecked    += 1
                self.add_part_to_selection(disk['line'])

                button_box.add(button)
                button.connect("clicked", self._cb_toggle_button, disk['line'])
                for (partid, part) in disk.items():
                    if type(partid) == type(1):
                        if (accel_int < 10):
                            button = LbxImgCheckButton(
                            _("<b><u>%d</u></b>. Partition #%d: type %s (%s)") %
                                (
                                    accel_int,
                                    partid + 1,
                                    part['kind'],
                                    lbx_utils.human_readable(
                                        part['size'],
                                        'o'
                                    )
                                ))
                            button.add_accelerator(
                                "clicked",
                                self.book.accel_group,
                                ord('%d' % accel_int),
                                0,
                                gtk.ACCEL_VISIBLE
                            )
                        else:
                            button = LbxImgCheckButton(
                                _("%d. Partition type %d (%s)") %
                                (
                                    accel_int,
                                    part['type'],
                                    lbx_utils.human_readable(
                                        part['size'],
                                        'o'
                                    )
                                ))
                        accel_int += 1

                        # toggle active if line is not commented out
                        button.set_active(1)
                        self.count_ckecked    += 1
                        self.add_part_to_selection(part['line'])

                        button_box.add(button)
                        button.connect(
                            "clicked",
                            self._cb_toggle_button,
                            part['line']
                        )
                frame = gtk.Frame(
                    _("Disk %d: Available partitions") % (diskid + 1)
                )
                frame.add(button_box)
                container.pack_start(frame, True, True)
            self.get_contentbox().show_all()

    def get_selected_parts(self):
        """ get selected parts    """
        self.selected_parts.sort(key=str.lower)
        return self.selected_parts

    def clear_selected_parts(self):
        """ get selected parts    """
        self.selected_parts = []

    def add_part_to_selection(self, part):
        """ add a part to the exclude list, part fmt is diskid:partid """
        if part not in self.selected_parts:
            self.selected_parts.append(part)

    def del_part_from_selection(self, part):
        """ del a part from the exclude list, part fmt is diskid:partid """
        if part in self.selected_parts:
            self.selected_parts.remove(part)

    def __init__(self, mode, book=None):
        LbxPage.__init__(self,
            '%s_part' % mode,
            beam_text.titles['%s_part' % mode],
            beam_text.summaries['%s_part' % mode],
            book)
        self.selected_parts = []
        self.count_ckecked = 0
        self.mode = mode
        self.count_checked = 0

        # will contain our frames (one frame per disk)
        box = gtk.VBox()
        box.set_name("container")

        # TODO: factorize checkbox code gen
        accel_int = 1
        count_disk = 0
        if mode == "svg": # do a save: iterate over current parts
            for disk in get_parts().values():
                if disk['parts'] == {}:
                    continue
                button_box = gtk.VButtonBox()
                button_box.set_layout(gtk.BUTTONBOX_SPREAD)
                # iterate over each part
                for part in disk['parts'].values():
                    if part['display']: # part must be displayed
                        if part['include']: # and is selectable
                            if (accel_int < 10):
                                button = LbxImgCheckButton(
                    _("<b><u>%d</u></b>. Partition « %s »: %s (%s)") %
                    (
                        accel_int,
                        part['name'],
                        part['desc'],
                        lbx_utils.human_readable(part['size'], 'o'),
                    )
                                )
                                button.add_accelerator(
                                    "clicked",
                                    self.book.accel_group,
                                    ord('%d' % accel_int),
                                    0,
                                    gtk.ACCEL_VISIBLE
                                )
                            else:
                                button = LbxImgCheckButton(
                    _("%d. Partition « %s »: %s (%s)") %
                    (
                        accel_int,
                        part['name'],
                        part['desc'],
                        lbx_utils.human_readable(part['size'], 'o'),
                    )
                                    )
                            accel_int += 1
                            button.set_active(1)
                            self.count_ckecked    += 1
                            self.del_part_from_selection(
                                "%s:%s" % (count_disk, part['num'])
                            )
                        else: # not selectable: disable it
                            button = LbxImgCheckButton(
                                _("Partition « %s »: %s (%s)") %
                                (
                                    part['name'],
                                    part['desc'],
                                    lbx_utils.human_readable(part['size'], 'o'),
                                ))
                            button.set_sensitive(0)
                            self.del_part_from_selection(
                                "%s:%s" %
                                (count_disk, part['num'])
                            )
                            self.add_part_to_selection(
                                "%s:%s" %
                                (count_disk, part['num'])
                            )
                        button_box.add(button)
                        button.connect(
                            "clicked",
                            self._cb_toggle_button,
                            "%s:%s" % (count_disk, part['num'])
                        )

                frame = gtk.Frame("%s « %s » (%s)" % \
                        (disk['desc'],
                         disk['name'],
                         lbx_utils.human_readable(disk['size'])
                         )
                )
                framealign = gtk.Alignment(0, 0.5, 0, 0)
                framealign.add(button_box)
                framealign.set_padding(0, 0, 20, 0)
                frame.add(framealign)

                box.pack_start(frame, True, True)
                count_disk += 1

        elif mode == 'rst':
            pass

        self.get_contentbox().pack_start(box, True, True)
        self.connect(
            "show",
            self._cb_show,
            None
        )
        self.get_buttonbox().pack_start(LbxNavButton(
            (
                (_("<b><u>P</u></b>revious"), 'gtk-go-back'),
                (_("<b><u>N</u></b>ext"), 'gtk-go-forward')
            )
            ), False, False)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('P')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('N')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )

class PageSvgName(LbxPage):
    """ page to give a name to the backup """
    def _cb_alter_text(self, widget=None):
        """ called to (dis-)able next page access"""
        if len(widget.get_text()) < 1:
            if get_widget_r(self, "navbutton_1") != None:
                get_widget_r(self, "navbutton_1").set_sensitive(False)
        else:
            if get_widget_r(self, "navbutton_1") != None:
                get_widget_r(self, "navbutton_1").set_sensitive(True)

    def get_imagename(self):
        """ return image name"""
        return get_widget_r(self, 'entry_name').get_text()

    def get_imagedesc(self):
        """ return image desc"""
        return get_widget_r(self, 'entry_desc').get_text()

    def __init__(self, book=None):
        """ init page"""
        LbxPage.__init__(self,
            "svg_name",
            beam_text.titles['svg_name'],
            beam_text.summaries['svg_name'],
            book
        )

        # to pre-fill fields
        hostname = gethostname()
        date = datetime.now().strftime("%Y-%d-%m %H:%M:%S")

        label_name = gtk.Label(_("Name:"))
        label_desc = gtk.Label(_("Description:"))
        gtk.Misc.set_alignment(label_name, 1, 0)
        gtk.Misc.set_alignment(label_desc, 1, 0)

        entry_name = gtk.Entry()
        entry_name.set_name('entry_name')
        entry_name.connect("changed", self._cb_alter_text)
        entry_name.set_text(_("%s %s") % (hostname, date) )

        entry_desc = gtk.Entry()
        entry_desc.set_name('entry_desc')
        entry_desc.set_text(_("Image of %s on %s") % (hostname, date) )

        align1 = gtk.Alignment(1, 0, 1, 1)
        align1.set_padding(0, 0, 5, 10)
        align1.add(label_name)
        align2 = gtk.Alignment(1, 0, 1, 1)
        align2.set_padding(0, 0, 5, 10)
        align2.add(label_desc)
        align3 = gtk.Alignment(0, 0, 1, 1)
        align3.set_padding(0, 0, 5, 10)
        align3.add(entry_name)
        align4 = gtk.Alignment(0, 0, 1, 1)
        align4.set_padding(0, 0, 5, 10)
        align4.add(entry_desc)

        table = gtk.Table(2, 2, False)
        table.attach(align1,
                0, 1, 0, 1,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK
        )
        table.attach(align2,
                0, 1, 1, 2,
                gtk.SHRINK|gtk.FILL,
                gtk.SHRINK
        )
        table.attach(align3,
                1, 2, 0, 1,
                gtk.EXPAND|gtk.FILL,
                gtk.SHRINK
        )
        table.attach(align4,
                1, 2, 1, 2,
                gtk.EXPAND|gtk.FILL,
                gtk.SHRINK
        )

        self.get_contentbox().pack_start(table, True, True, 5)
        self.get_buttonbox().pack_start(LbxNavButton(
            (
                (_("<b><u>P</u></b>revious"), 'gtk-go-back'),
                (_("<b><u>N</u></b>ext"), 'gtk-go-forward')
            )
            ), False, True)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('P')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('N')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )

class PageKindButton(LbxPage):
    """ Page used to select where we are going to save """
    def get_vol(self):
        """ get selected vol"""
        combo_vol = get_widget_r(self, "combo_vol")
        model = combo_vol.get_model()
        active = combo_vol.get_active()
        if (active>-1):
            return model[active][1]
        return None

    def get_part(self):
        """ get selected part"""
        combo_part = get_widget_r(self, "combo_part")
        model = combo_part.get_model()
        active = combo_part.get_active()
        if (active>-1):
            return model[active][1]
        return None

    def get_dir(self):
        """ get selected dir"""
        combo_vol = get_widget_r(self, "combo_dir")
        model = combo_vol.get_model()
        active = combo_vol.get_active()
        if (active>-1):
            return model[active][1]
        return None

    def get_image(self):
        """ get selected image"""
        combo_image = get_widget_r(self, "combo_image")
        model = combo_image.get_model()
        active = combo_image.get_active()
        if (active>-1):
            return model[active][1]
        return None

    def get_target(self):
        """ get target dir"""
        target = os.path.join(
            lbx_utils.get_part_mountpoint(self.get_part()),
            self.get_dir()
        )
        return target

    def get_source(self):
        """ get source dir"""
        source = os.path.join(
            lbx_utils.get_part_mountpoint(self.get_part()),
            self.get_dir(),
            self.get_image()
        )
        return source

    def cb_choose_usb(self, widget=None, data=None):
        """ called when USB is chosen"""
        if widget.get_active(): # button became active, disable others
            get_widget_r(self, "button_nfs").set_active(False)
            get_widget_r(self, "first_label").set_text(_("Volume"))
            get_widget_r(self, "second_label").set_text(_("Partition"))
            get_widget_r(self, "third_label").set_text(_("Directory"))
            get_widget_r(self, "fourth_label").set_text(_("Image"))

            combo_vol = get_widget_r(self, "combo_vol")
            combo_part = get_widget_r(self, "combo_part")
            combo_dir = get_widget_r(self, "combo_dir")
            combo_vol.connect("changed", self.cb_change_local_vol)
            combo_part.connect("changed", self.cb_change_local_part)
            combo_dir.connect("changed", self.cb_change_local_dir)

            mylist = []
            for directory in get_parts().values():
                if directory['parts'] != {}:
                    mylist.append(
                        (
                        '%s (%s, %s)' % (
                            directory['name'],
                            directory['desc'],
                            lbx_utils.human_readable(directory['size'])
                            ),
                        directory['name']
                        )
                    )
            combo_vol.set_items(mylist)
            combo_vol.set_active(0)

    def cb_choose_nfs(self, widget=None, data=None):
        """ called when NFS (network ?) is choosen"""
        if widget.get_active(): # button became active, disable others
            get_widget_r(self, "button_usb").set_active(False)
            get_widget_r(self, "first_label").set_text(_("Server"))
            get_widget_r(self, "second_label").set_text(_("Share"))
            get_widget_r(self, "third_label").set_text(_("Directory"))
            get_widget_r(self, "third_label").set_text(_("Image"))

    def cb_change_local_vol(self, widget=None, data=None):
        """ Called when storage method is chosen """
        p_tree_model = get_widget_r(self, "combo_part").get_model()
        p_tree_model.clear()
        for disk in get_parts().values():
            if (disk['name'] == self.get_vol()):
                for part in disk['parts'].values():
                    if ('mountpoint' in part.keys()):
                        p_tree_model.append(
                            ( '%s (%s)' % (part['name'],
                            part['desc']) ,
                            part['name'])
                        )
        get_widget_r(self, "combo_part").set_active(p_tree_model.__len__() - 1)

    def cb_change_local_part(self, widget=None, data=None):
        """ Called when local volume is chosen """
        p_tree_model = get_widget_r(self, "combo_dir").get_model()
        p_tree_model.clear()
        for disk in get_parts().values():
            for part in disk['parts'].values():
                if part['name'] == self.get_part():
                    p_tree_model.append(("(racine)", ""))
                    for directory in part['dirs']:
                        p_tree_model.append((directory, directory))
        get_widget_r(self, "combo_dir").set_active(p_tree_model.__len__() - 1)
        get_widget_r(self, "navbutton_1").set_sensitive(True)

    def cb_change_local_dir(self, widget=None, data=None):
        """ Called when local part is chosen """
        p_tree_model = get_widget_r(self, "combo_image").get_model()
        p_tree_model.clear()
        for disk in get_parts().values():
            for part in disk['parts'].values():
                if part['name'] == self.get_part():
                    for directory in part['dirs']:
                        full_dir = os.path.join(part['mountpoint'], directory)
                        try:
                            for image in os.listdir(full_dir):
                                image_path = os.path.join(
                                    full_dir,
                                    image
                                )
                                if os.path.isdir(image_path):
                                    if lbx_lrs_image.is_lrs_image(image_path):
                                        img = lbx_lrs_image.get_image_stats(
                                            image_path
                                        )
                                        display = "%s (%s)" % \
                                        (
                                            img['name'],
                                            lbx_utils.human_readable(
                                                img['size']
                                            )
                                        )
                                        p_tree_model.append(
                                            (display, image_path)
                                        )
                        except OSError:
                            pass
        get_widget_r(self, "combo_image").set_active(p_tree_model.__len__()-1)
        get_widget_r(self, "navbutton_1").set_sensitive(True)

    def __init__(self, mode, book=None):
        """ init widget"""
        # init ancestor
        LbxPage.__init__(self,
            '%s_kind' % mode,
            beam_text.titles['%s_kind' % mode],
            beam_text.summaries['%s_kind' % mode],
            book)

        # button use to save on a NFS share
        button_nfs = LbxImgToggleButton(_('NFS'), 'gtk-network')
        button_nfs.set_name("button_nfs")
        button_nfs.connect("clicked", self.cb_choose_nfs, None)
        button_nfs.set_active(False)

        # button use to save on a local dir
        button_usb = LbxImgToggleButton(
            _('<b><u>L</u></b>ocal'),
            'gtk-harddisk'
        )
        button_usb.set_name("button_usb")
        button_usb.connect("clicked", self.cb_choose_usb, None)
        button_usb.add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('L')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
        )

        # button box
        button_box = gtk.HButtonBox()
        button_box.set_border_width(10)
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        button_box.add(button_nfs)
        button_box.add(button_usb)

        # first control: Volume / server
        combo_vol = LbxComboBox(None, 200, 30, 10)
        combo_vol.set_name("combo_vol")
        combo_part = LbxComboBox(None, 200, 30, 10)
        combo_part.set_name("combo_part")
        combo_dir = LbxComboBox(None, 200, 30, 10)
        combo_dir.set_name("combo_dir")
        combo_image = LbxComboBox(None, 200, 30, 10)
        combo_image.set_name("combo_image")

        align1 = gtk.Alignment(0.5, 0, 0.5, 1)
        align1.set_padding(0, 0, 10, 10)
        align1.add(combo_vol)
        align2 = gtk.Alignment(0.5, 0, 0.5, 1)
        align2.set_padding(0, 0, 10, 10)
        align2.add(combo_part)
        align3 = gtk.Alignment(0.5, 0, 0.5, 1)
        align3.set_padding(0, 0, 10, 10)
        align3.add(combo_dir)
        align4 = gtk.Alignment(0.5, 0, 0.5, 1)
        align4.set_padding(0, 0, 10, 10)
        align4.add(combo_image)

        first_label = gtk.Label()
        first_label.set_name("first_label")
        second_label = gtk.Label()
        second_label.set_name("second_label")
        third_label = gtk.Label()
        third_label.set_name("third_label")
        fourth_label = gtk.Label()
        fourth_label.set_name("fourth_label")

        table_usb = gtk.Table(2, 4, False)
        table_usb.attach(first_label, 0, 1, 0, 1, gtk.SHRINK, gtk.SHRINK)
        table_usb.attach(second_label, 0, 1, 1, 2, gtk.SHRINK, gtk.SHRINK)
        table_usb.attach(third_label, 0, 1, 2, 3, gtk.SHRINK, gtk.SHRINK)
        table_usb.attach(fourth_label, 0, 1, 3, 4, gtk.SHRINK, gtk.SHRINK)
        table_usb.attach(align1, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL, gtk.FILL)
        table_usb.attach(align2, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.FILL)
        table_usb.attach(align3, 1, 2, 2, 3, gtk.EXPAND|gtk.FILL, gtk.FILL)
        table_usb.attach(align4, 1, 2, 3, 4, gtk.EXPAND|gtk.FILL, gtk.FILL)

        self.get_contentbox().pack_start(button_box, False)
        table_usb_align = gtk.Alignment(0.5, 0.5, 1, 1)
        table_usb_align.add(table_usb)
        table_usb_align.set_padding(0, 0, 10, 0)
        self.get_contentbox().pack_start(table_usb_align, True, True, 5)

        self.get_contentbox().pack_start(gtk.HSeparator(), False, False)
        self.get_buttonbox().pack_start(LbxNavButton(
            (
                (_("<b><u>P</u></b>revious"), 'gtk-go-back'),
                (_("<b><u>N</u></b>ext"), 'gtk-go-forward')
            )
            ), False, False)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('P')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('N')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").set_sensitive(False)
        self.set_no_show_all(True)

        if mode == 'svg':
            fourth_label.set_no_show_all(True)
            align4.set_no_show_all(True)


class PageKindFolder(LbxPage):
    """ Page used to select where we are going to save """
    def get_target(self):
        """ get target dir"""
        return self.folder_name

    def get_source(self):
        """ get source dir"""
        return self.folder_name

    def cb_display_dialog(self, widget=None, data=None):
        """ called when USB is chosen"""

        dialog = gtk.FileChooserDialog(
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK
            )
        )
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        dialog.set_local_only(False)
        dialog.set_select_multiple(False)
        dialog.set_default_response(gtk.RESPONSE_OK)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.folder_name = dialog.get_filename()
            widget.set_label(self.folder_name)
            get_widget_r(self, "navbutton_1").set_sensitive(True)
        elif response == gtk.RESPONSE_CANCEL:
            widget.set_label(_('Click here to choose folder where the image will be written'))
        dialog.destroy()

    def __init__(self, mode, book=None):
        """ init widget"""
        # init ancestor
        LbxPage.__init__(self,
            '%s_kind' % mode,
            beam_text.titles['%s_kind' % mode],
            beam_text.summaries['%s_kind' % mode],
            book)

        # button use to save on a local dir
        button = LbxImgButton(None, 'gtk-harddisk')
        button.set_name("button")
        button.connect("clicked", self.cb_display_dialog, None)
        if mode == 'svg' :
            button.set_label(_('Click here to choose folder where the image will be written'))
        else:
            button.set_label(_('Click here to choose folder where the image is stored'))

        # label box
        label_box = gtk.HBox()

        first_label = gtk.Label()
        first_label.set_name("first_label")
        if mode == 'svg' :
            first_label.set_label("The image will be written in : ")
        else :
            first_label.set_label("The image will be read from : ")

        label_box.pack_start(first_label, False)
        label_box.pack_start(button, False)

        label_align = gtk.Alignment(0.5, 0.5, 0, 0)
        label_align.add(label_box)
        label_align.set_padding(0, 0, 10, 0)
        self.get_contentbox().pack_start(label_align, True, True, 5)
        self.get_buttonbox().pack_start(LbxNavButton(
            (
                (_("<b><u>P</u></b>revious"), 'gtk-go-back'),
                (_("<b><u>N</u></b>ext"), 'gtk-go-forward')
            )
            ), False, False)
        get_widget_r(self, "navbutton_0").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('P')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").add_accelerator(
            "clicked",
            self.book.accel_group,
            ord(_('N')),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE
            )
        get_widget_r(self, "navbutton_1").set_sensitive(False)
        self.set_no_show_all(True)

