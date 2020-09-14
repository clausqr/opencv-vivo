from multiprocessing import Queue
from imgprocessdispatcher import ImageProcessorDispatcher
from opencvenvivogtk import OpenCVenVivoGTK

if __name__ == '__main__':

    print('starting OpenCV Vivo...')

    queue_into_img_processor = Queue()
    queue_from_img_processor = Queue()

    img_processor = ImageProcessorDispatcher(queue_from_img_processor, queue_into_img_processor)
    main_window = OpenCVenVivoGTK(queue_into_img_processor, queue_from_img_processor)

    main_window.start()
