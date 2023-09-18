
import aditofpython as tof
import numpy as np
import cv2
import argparse
import multiprocessing
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'lib'))

from lib.fxtof_camera import FxtofCam
from lib.video_streamer import VideoStreamer
from lib.stream_aggregator import StreamAggregator

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


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description= "FXTOF Viewer / Sma-RTy 2023")
    parser.add_argument('-c', '--cam',  help = "Camera ID. Ranges from 0 to 3", default=0, type=int)
    args = parser.parse_args()
    cam_id  = args.cam
    
    # Init TOF System
    tof_system = tof.System()
    tof_system.getCameraList(cameras)

    q_cam1        = multiprocessing.Queue(maxsize=2)
    q_cam2        = multiprocessing.Queue(maxsize=2)
    q_cam3        = multiprocessing.Queue(maxsize=2)
    q_aggr        = multiprocessing.Queue(maxsize=2)
    # q_aggr        = manager.Queue()
    
    # Init Camera procs
    proc_cam1   = FxtofCam(camera=cameras[1], q=q_cam1)
    #time.sleep(0.010)
    proc_cam2   = FxtofCam(camera=cameras[2], q=q_cam2)
    #proc_cam3   = FxtofCam(camera=cameras[3], q=q_cam3)
    
    proc_aggr   = StreamAggregator([q_cam1, q_cam2], q_aggr)
    proc_stream = VideoStreamer(q=q_aggr, width=2*640, bitrate=10000000)
    
    # Start the procs.
    proc_cam1.start()
    #time.sleep(0.010)
    proc_cam2.start()
    #proc_cam3.start()
    proc_aggr.start()
    proc_stream.run()
    
    
    # Wait for the procs to finish
    # proc_cam1.join()
    # # #proc_aggr.join()
    # proc_stream.join()
    # exit(0)
    
    
    
    