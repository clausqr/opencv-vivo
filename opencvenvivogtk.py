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

# For compatibility with cv docs:
cv = cv2

default_script_file = "placeholder_script.py"
placeholder_text = "Failed to load placeholder script " + default_script_file

gi.require_version("Gtk", "3.0")
# noinspection PyPep8
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

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