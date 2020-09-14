from threading import Thread
from time import sleep
import sys
import numpy as np
import cv2
import cProfile  # for profiling checkbox, TBI

# local imports:
from sharedevents import EVENTS

# For compatibility with cv docs:
cv = cv2


class ImageProcessorDispatcher:

    def __init__(self, queue_in, queue_out):
        self.src = None
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.miniscript = None
        self.t = Thread(target=self.watch_queue)
        print('Starting "Process" thread!')
        self.t.daemon = True
        self.t.start()
        self.msg = "Not run yet"

    def _process_image_grabbed(self, img):
        self.src = np.array(img, dtype=np.uint8)
        self._process_image()

    def _process_miniscript_edit(self, new_miniscript):
        if new_miniscript != self.miniscript:
            self.miniscript = new_miniscript
            # print(" New miniscript:\n" + self.miniscript)
            self._process_image()

    def _process_image(self):

        # # catch first run empty
        # self._update_miniscript_if_none()

        src = np.copy(self.src)
        src = src[:, :, 0:3]

        try:
            process_function_candidate = self.miniscript
            process_function = compile(process_function_candidate, '<string>', 'exec')
            img = src
            _locals = locals()
            _globals = globals()
            exec(process_function, _globals, _locals)
            # cProfile.runctx(process_function, _globals, _locals, 'profile.cprof')
            if 'dst' in _locals:
                self.dst = _locals['dst']
                self.msg = _locals['msg']
            else:
                self.dst = np.zeros_like(src)
                self.msg = "'dst' variable not returned"

        except:
            print("Code error:", sys.exc_info()[0])
            self.dst = np.zeros_like(src)
            self.msg = "Code error: " + str(sys.exc_info()[0])

        # print("self._external_callback returned ok")
        if self.dst.ndim == 2:
            # "Grayscale"
            print(' image was in grayscale, converting to BGR')
            self.dst = cv2.cvtColor(self.dst, cv2.COLOR_GRAY2BGR)
        elif self.dst.ndim == 4:
            # "Grayscale"
            print(' image had alpha channel, removing')
            self.dst = self.dst[:, :, 0:2]

        # self.gui.set_dst(self.dst)
        self.queue_out.put((EVENTS.image_processed, self.dst, self.msg))

    def watch_queue(self):
        while True:
            try:
                ev = self.queue_in.get(block=True, timeout=0.001)
                # print('Event in Process!')
                if ev[0] == EVENTS.image_grabbed:
                    img = ev[1]
                    try:
                        print(' "ImageProcessorDispatcher.watch_queue()" got image from queue, processing')
                        self._process_image_grabbed(img)
                    except BaseException as e:
                        print('Exception in watch_queue when calling _process_image_grabbed:\n{!r}'.format(e))
                if ev[0] == EVENTS.miniscript_edit:
                    miniscript = ev[1]
                    try:
                        print(' "ImageProcessorDispatcher.watch_queue()" got new miniscript from queue, processing')
                        self._process_miniscript_edit(miniscript)
                    except BaseException as e:
                        print('Exception in ImageProcessorDispatcher.watch_queue() when calling '
                              '_process_miniscript_edit:\n{!r}'.format(e))
            except:
                sleep(0.001)

            sleep(0.005)
