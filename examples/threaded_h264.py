from collections.abc import Callable, Iterable, Mapping
from typing import Any
import aditofpython as tof
import numpy as np
import cv2
import time
import argparse
import queue
import threading

width, height, fps, num_cams = 640, 480, 30, 4
cameras = []
# Encoder data
bitrate = 1000000
host = "10.42.0.1"
port = 8888

class FxtofCam(threading.Thread):
    def __init__(self, camera, queue):
        super().__init__()
        self.camera = camera
        self.queue = queue
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
                
        
    # def getFrameDepth(self):
    #     status = self.camera.requestFrame(self.frame)
    #     if not status:
    #         print(f"Camera failure")
    #         self.queue.put(np.zeros((width, height), dtype="uint16"))
    #     self.queue.put(np.array(self.frame.getData(tof.FrameDataType.Depth), 
    #                          dtype="uint16", copy=False))
        
    def run(self):
        while True:
            status = self.camera.requestFrame(self.frame)
            depth_raw =  np.array(self.frame.getData(tof.FrameDataType.Depth), 
                                 dtype="uint16", copy=False) 
            depth_uint8 = np.uint8(self.depth_scale * depth_raw)
            self.queue.put(cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW))

class VideoStreamer(threading.Thread):
    def __init__(self, queue, host="10.42.0.1", port=8888, bitrate=1000000, fps=30, width=640, height=480) -> None:
        super().__init__()
        self.queue = queue
        self.out_pipeline = ( f" appsrc ! video/x-raw, format=BGR ! queue !"
                              f" videoconvert ! video/x-raw, format=BGRx ! "
                              f" nvvidconv ! omxh264enc bitrate={bitrate} ! "
                              f" video/x-h264, out-format=(string)byte-out ! "
                              f" h264parse ! rtph264pay pt=96 config-interval=1 ! "
                              f" udpsink host={host} port={port} sync=false ")        
        self.out_writer = cv2.VideoWriter(self.out_pipeline, 0, fps, (width, height))
        if not self.out_writer.isOpened():
            print('VideoStreamer not opened')
    
    def run(self):
        while True:
            # Check empty
            self.out_writer.write(self.queue.get())
        
        
            
        
        
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description= "FXTOF Viewer / Sma-RTy 2023")
    parser.add_argument('-c', '--cam',  help = "Camera ID. Ranges from 0 to 3", default=0, type=int)
    args = parser.parse_args()
    cam_id  = args.cam
    
    # Init TOF System
    tof_system = tof.System()
    tof_system.getCameraList(cameras)
    camera = cameras[cam_id]
    
    # Init out pipeline
    
    # Init thread data
    q = queue.Queue()
    thread_cam1   = FxtofCam(camera=camera, queue=q)
    thread_stream = VideoStreamer(queue=q)
    
    # Start the threads.
    thread_cam1.start()
    thread_stream.start()
    # Start the out stream
    
    
    #Wait for the threads to finish
    #thread1.join()
    exit(0)
    
    
    
    