import datetime
from multiprocessing import Queue
import gi
from threading import Thread
from time import sleep
from enum import Enum, auto
import sys
import io
import numpy as np
import cv2
from PIL import ImageTk, Image
import cProfile
import re

import matplotlib.pyplot as plt
import io
import urllib, base64

# project imports
from imgdisplaywindow import ImgDisplayWindow
from sharedevents import EVENTS

# fix for importing Gtk 3.0:
gi.require_version("Gtk", "3.0")
# noinspection PyPep8
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

# For compatibility with cv docs:
cv = cv2

default_script_file = "placeholder_script.py"


# noinspection PyCallByClass,PyArgumentList
class OpenCVenVivoGTK(Gtk.Window):
    def __init__(self, queue_in, queue_out):

        self.autograb = False
        self.parameters_txt = ["128", "128", "128", "128"]
        self.queue_in = queue_in
        self.queue_out = queue_out

        self.last_keypress_time = datetime.datetime.now()

        Gtk.Window.__init__(self, title='OpenCV Vivo GTK')
        self.set_default_size(640, 640)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        grid = Gtk.Grid()

        self.text_buffer = Gtk.TextBuffer()
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard.connect('owner-change', self.callBack)

        self.image = Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.MENU)

        button_copy_text = Gtk.Button.new_with_label("Copy Text")
        button_paste_text = Gtk.Button.new_with_label("Paste Text")
        button_copy_image = Gtk.Button.new_with_label("Copy Image")
        button_paste_image = Gtk.Button.new_with_label("Paste Image")
        button_process_image = Gtk.Button.new_with_label("Process Image")
        button_auto_grab = Gtk.CheckButton()
        button_auto_grab.set_label("Autograb")
        button_auto_grab.set_active(self.autograb)
        button_auto_grab.connect("toggled", self.autograb_toggled_cb)

        ads = list()
        h_scales = list()
        for p in self.parameters_txt:
            ad = Gtk.Adjustment(value=int(p), lower=0, upper=255, step_increment=5, page_increment=10, page_size=0)
            ads.append(ad)
            s = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad)
            s.set_digits(0)
            s.set_hexpand(True)
            s.set_valign(Gtk.Align.START)
            h_scales.append(s)

        self.add(grid)

        grid.attach(button_copy_text, 1, 1, 1, 1)
        grid.attach_next_to(button_paste_text, button_copy_text, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(button_copy_image, button_paste_text, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(button_paste_image, button_copy_image, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(button_process_image, button_paste_image, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(button_auto_grab, button_process_image, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(h_scales[0], button_copy_text, Gtk.PositionType.BOTTOM, 6, 1)
        for prev_s, s in zip(h_scales[:-1], h_scales[1:]):
            grid.attach_next_to(s, prev_s, Gtk.PositionType.BOTTOM, 6, 1)

        grid.attach_next_to(self.scrolled_window, h_scales[-1], Gtk.PositionType.BOTTOM, 6, 1)

        self.text_view = Gtk.TextView()
        self.text_view.set_monospace(True)
        self.text_buffer = self.text_view.get_buffer()

        with open(default_script_file, 'r') as file:
            placeholder_text = file.read()

        self.text_buffer.set_text(placeholder_text)
        self.text_buffer.connect('changed', self._changed)
        for i, s in enumerate(h_scales):
            s.connect("value-changed", self.scale_moved, i)

        self.scrolled_window.add(self.text_view)

        button_copy_text.connect("clicked", self.copy_text)
        button_paste_text.connect("clicked", self.paste_text)
        button_copy_image.connect("clicked", self.copy_image)
        button_paste_image.connect("clicked", self.paste_image)
        button_process_image.connect("clicked", self.reset_windows_cb)

        self.src = ImgDisplayWindow('src')
        self.dst = ImgDisplayWindow('dst')

        self.src.show_all()
        self.dst.show_all()

        thread = Thread(target=self.watch_queue)
        thread.daemon = True
        print('Starting "watch_queue" thread!')
        thread.start()

    def reset_windows_cb(self, *args):
        del self.dst
        self.dst = self.ImgDisplayWindow('dst')

    def scale_moved(self, scale, sn):

        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)

        # vs = self.scrolled_window.get_vadjustment()
        # vss = vs.get_value()
        # # cursor_mark = self.text_buffer.get_insert()
        # # cursor_iter = self.text_buffer.get_iter_at_mark(cursor_mark)
        # cp = self.text_buffer.props.cursor_position
        print(sn, scale.get_value())
        self.parameters_txt[sn] = str(int(scale.get_value()))
        text_modified = re.sub('s'+str(sn+1)+'=([0-9.]*) #@', 's'+str(sn+1)+'=' + self.parameters_txt[sn] + ' #@', text)


        # print("Horizontal scale is " + self.parameter_txt)

        GLib.idle_add(self.text_buffer.set_text, text_modified)
        # cursor_iter = self.text_buffer.get_iter_at_offset(cp)
        # GLib.idle_add(self.text_buffer.place_cursor, cursor_iter)
        # vs.set_value(vss)
        # GLib.idle_add(self.scrolled_window.set_vadjustment, vs)
        #print(vs)


        self._changed(None)


    def autograb_toggled_cb(self, *args):
        self.autograb = not self.autograb
        print("seting autograb=", self.autograb)

    def callBack(self, *args):
        # print("Clipboard changed. New value = " + self.clipboard.wait_for_text())
        if self.autograb:

            self.paste_image(None)

    @staticmethod
    def image2pixbuf(im):
        """Convert Pillow image to GdkPixbuf
        https://gist.github.com/mozbugbox/10cd35b2872628246140
        """
        data = im.tobytes()
        h, w, _ = im.shape
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              False, 8, w, h, w * 3)
        return pix.copy()

    def image2pixbuf2(im):
        # convert image from BRG to RGB (pnm uses RGB)
        im2 = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        # get image dimensions (depth is not used)
        height, width, depth = im2.shape
        pixl = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        # P6 is the magic number of PNM format,
        # and 255 is the max color allowed, see [2]
        pixl.write("P6 %d %d 255 " % (width, height) + im2.tostring())
        pix = pixl.get_pixbuf()
        pixl.close()
        return pix

    def watch_queue(self):
        while True:
            try:
                ev = self.queue_in.get(block=True, timeout=0.001)
                if ev[0] == EVENTS.image_processed:
                    img = ev[1]
                    msg = ev[2]
                    try:
                        img_pixbuf = self.image2pixbuf(img)
                        # print(img.shape)
                        # img_pixbuf = Gtk.gdk.pixbuf_new_from_array(img, Gtk.gdk.COLORSPACE_RGB, 8) not workin
                        self.dst.set_image(img_pixbuf, info_text=msg)
                        print(' "ClipboardWindow.watch_queue" got image from queue, showing')
                        # GLib.idle_add(self.dst.show_all)
                    except BaseException as e:
                        print('Exception in watch_queue when calling OpenCVenVivoGTK.watch_queue():\n{!r}'.format(e))
            except:
                sleep(0.001)


    def copy_text(self, _):
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        self.clipboard.set_text(text, -1)

    def paste_text(self, _):
        text = self.clipboard.wait_for_text()
        if text is not None:
            self.text_buffer.set_text(text)
        else:
            print("No text on the clipboard.")

    def copy_image(self, _):
        if self.image.get_storage_type() == Gtk.ImageType.PIXBUF:
            self.clipboard.set_image(self.image.get_pixbuf())
        else:
            print("No image has been pasted yet.")

    @staticmethod
    def pixbuf2image(pix):
        """Convert gdkpixbuf to PIL image
        https://gist.github.com/mozbugbox/10cd35b2872628246140
        """
        data = pix.copy().get_pixels()
        w = pix.props.width
        h = pix.props.height
        stride = pix.props.rowstride
        mode = "RGB"
        if pix.props.has_alpha:
            mode = "RGBA"
        im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
        return im

    def paste_image(self, _):
        image = self.clipboard.wait_for_image()
        if image is not None:
            self.src.show_all()
            self.src.set_image(image)
            image_for_np = np.array(self.pixbuf2image(image))
            self.queue_out.put((EVENTS.image_grabbed, image_for_np))
        else:
            print('No image on the clipboard.')

    def _changed(self, _):  # , iter, string, length):
        # timedelta_tol = datetime.timedelta(milliseconds=500)
        # keypress_timestamp = datetime.datetime.now()
        # if (keypress_timestamp - self.last_keypress_time) > timedelta_tol:
        #     self.last_keypress_time = keypress_timestamp
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        # print(text)
        # text_modified = text.replace("@", self.parameter_txt)
        # self.queue_out.queue.clear()
        while not self.queue_out.empty():
            try:
                self.queue_out.get(block=True, timeout=0.001)
                sleep(0.001)
            except:
                 pass
        self.queue_out.put((EVENTS.miniscript_edit, text), block=True, timeout=0.001)

