from multiprocessing import Queue
from imgprocessdispatcher import ImageProcessorDispatcher
from opencvenvivogtk import OpenCVenVivoGTK

if __name__ == '__main__':
    print('starting OpenCV Vivo...')
    queue_into_process = Queue()
    queue_from_process = Queue()

    proc = ImageProcessorDispatcher(queue_from_process, queue_into_process)

    win = OpenCVenVivoGTK(queue_into_process, queue_from_process)

    # win.connect("destroy", Gtk.main_quit)

    win.show_all()

    win.main()
