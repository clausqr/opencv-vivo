import gi
from threading import Thread
from time import sleep

gi.require_version("Gtk", "3.0")

# noinspection PyPep8
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf


# noinspection PyCallByClass,PyArgumentList
class ImgDisplayWindow(Gtk.Window):
    def __init__(self, title):
        Gtk.Window.__init__(self, title=title)
        # self.image = Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.MENU)
        self.image = Gtk.Image()
        self.statusbar = Gtk.Statusbar()
        self.context_id = self.statusbar.get_context_id("example")
        self.statusbar.push(
            self.context_id, "Initialization OK")

        self.grid = Gtk.Grid()
        self.grid.attach(self.image, 0, 0, 1, 1)
        self.grid.attach(self.statusbar, 0, 1, 1, 1)
        self.connect('delete-event', self.hide_on_delete)
        self.add(self.grid)

        thread = Thread(target=self.watch_queue)
        thread.daemon = True
        print('Starting "watch_queue" thread!')
        thread.start()

    def set_image(self, image, info_text=None):
        # print('got image h, w: ', image.props.height, image.props.width)
        print('setting image...', end='')
        if image is not None:
            # toda la magia GLib.idle_add()
            GLib.idle_add(self.show_all)
            GLib.idle_add(self.image.set_from_pixbuf, image)
            GLib.idle_add(self.statusbar.push, self.context_id, info_text)

        print('OK')

    def watch_queue(self, *args):
        sleep(0.005)
