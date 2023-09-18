from collections.abc import Callable, Iterable, Mapping
from typing import Any
import aditofpython as tof
import numpy as np
import cv2
import time
import argparse
import queue
import threading
import coloredlogs, logging
logging.basicConfig()
log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
coloredlogs.install()

width, height, fps, num_cams = 640, 480, 30, 4
cameras = []
# Encoder data
bitrate = 1000000
host = "10.42.0.1"
port = 8888


class FxtofCam(threading.Thread):
    def __init__(self, camera, q):
        super().__init__()
        self.camera  = camera
        self.queue   = q
        self.types   = []
        self.modes   = []
        self.frame   = tof.Frame()
        self.smallSignalThreshold = 100    
        self.depth_scale = 0.085
        
        
        self.camera.initialize()
        self.camera.getAvailableModes(self.modes)
        self.camera.getAvailableFrameTypes(self.types)
        self.camera.setFrameType(self.types[0]) 
        self.camera.setMode(self.modes[1])
        
        self.camera.setControl("noise_reduction_threshold", str(self.smallSignalThreshold))
        self.camera_details = tof.CameraDetails()
        self.camera.getDetails(self.camera_details)
        log.info(f"thread camera {camera} Ready !")
                        
    def run(self):
        while True:
            status = self.camera.requestFrame(self.frame)
            depth_raw =  np.array(self.frame.getData(tof.FrameDataType.Depth), 
                                 dtype="uint16", copy=False) 
            depth_uint8 = np.uint8(self.depth_scale * depth_raw)
            data = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW)
            self.queue.put(data)

class VideoStreamer(threading.Thread):
    def __init__(self, q, host="10.42.0.1", port=8888, bitrate=1000000, fps=30, width=640, height=480) -> None:
        super().__init__()
        self.queue = q
        self.out_pipeline = ( f" appsrc ! video/x-raw, format=BGR ! queue !"
                              f" videoconvert ! video/x-raw, format=BGRx ! "
                              f" nvvidconv ! omxh264enc bitrate={bitrate} ! "
                              f" video/x-h264, out-format=(string)byte-out ! "
                              f" h264parse ! rtph264pay pt=96 config-interval=1 ! "
                              f" udpsink host={host} port={port} sync=false ")        
        self.out_writer = cv2.VideoWriter(self.out_pipeline, 0, fps, (width, height))
        if not self.out_writer.isOpened():
            log.error('VideoStreamer not opened')
        log.info(f"Output stream destination -> {host}:{port}")
        log.info(f"Output stream data        -> {width}x{height} @{fps}")
        log.info(f"Output stream enconding   -> H264 / CBR = {bitrate}")
        log.info(f"Ready !")
        
    
    def run(self):
        sample = self.queue.get()
        log.info(f"Queue data {sample.shape[1]}x{sample.shape[0]}")
        while True:
            # Check empty
            self.out_writer.write(self.queue.get())
        
class StreamAggregator(threading.Thread):
    def __init__(self, q_in, q_out, width=640, height=480):
        super().__init__()
        self.queue_in   = q_in
        self.queue_out  = q_out
        self.num_queues = len(self.queue_in)
        self.data_out   = np.zeros((height, self.num_queues*width, 3), dtype=np.uint8)
        log.info(f"Aggregating {self.num_queues} streams")
        log.info(f"Output data shape: {self.data_out.shape}")
        log.info(f"thread StreamAggregator Ready !")
    
    def run(self):
        while True:
            for i in range(self.num_queues):
                self.data_out[:, i*width:(i+1)*width, :] = self.queue_in[i].get()
            self.queue_out.put(self.data_out)     
        
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description= "FXTOF Viewer / Sma-RTy 2023")
    parser.add_argument('-c', '--cam',  help = "Camera ID. Ranges from 0 to 3", default=0, type=int)
    args = parser.parse_args()
    cam_id  = args.cam
    
    # Init TOF System
    tof_system = tof.System()
    tof_system.getCameraList(cameras)
    
    q_cam1        = queue.Queue()
    q_cam2        = queue.Queue()
    q_cam3        = queue.Queue()
    q_aggr        = queue.Queue()
    
    # Init Camera threads
    thread_cam1   = FxtofCam(camera=cameras[1], q=q_cam1)
    thread_cam2   = FxtofCam(camera=cameras[2], q=q_cam2)
    thread_cam3   = FxtofCam(camera=cameras[3], q=q_cam3)
    
    thread_aggr   = StreamAggregator([q_cam1, q_cam3, q_cam2], q_aggr)
    thread_stream = VideoStreamer(q=q_aggr, width=3*640, bitrate=10000000)
    
    # Start the threads.
    thread_cam1.start()
    thread_cam2.start()
    thread_cam3.start()
    thread_aggr.start()
    thread_stream.start()
    
    
    #Wait for the threads to finish
    #thread1.join()
    exit(0)
    
    
    
    