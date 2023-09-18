import numpy as np
import cv2
import threading
import coloredlogs, logging
logging.basicConfig()
log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
coloredlogs.install()
import time
import multiprocessing
import queue

class VideoStreamer():
    def __init__(self, q, host="10.42.0.1", port=8888, bitrate=1000000, fps=30, width=640, height=480) -> None:
        self.queue = q
        self.out_pipeline = ( f" appsrc ! video/x-raw, format=BGR ! queue !"
                              f" videoconvert ! video/x-raw, format=BGRx ! queue ! "
                              f" nvvidconv ! omxh264enc bitrate={bitrate} ! "
                              f" video/x-h264, out-format=(string)byte-out ! "
                              f" h264parse ! rtph264pay pt=96 config-interval=1 ! "
                              f" udpsink host={host} port={port} sync=false ")
        self.out_writer = cv2.VideoWriter(self.out_pipeline, 0, fps, (width, height), True)
        if not self.out_writer.isOpened():
            log.error('VideoStreamer not opened')
        log.info(f"Output stream destination -> {host}:{port}")
        log.info(f"Output stream data        -> {width}x{height} @{fps}")
        log.info(f"Output stream enconding   -> H264 / CBR = {bitrate}")
        log.info(f"Ready !")
        
    
    def run(self):
        log.info("Running ...")
        sample = self.queue.get()
        log.info(f"Queue data {sample.shape[1]}x{sample.shape[0]}")
        while(True): 
            data = self.queue.get()
            log.debug(f"FIFO get shape = {data.shape}")
            self.out_writer.write(data)