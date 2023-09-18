import aditofpython as tof
import numpy as np
import cv2
import multiprocessing
import queue
import coloredlogs, logging
logging.basicConfig()
log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
coloredlogs.install()
import time

class FxtofCam(multiprocessing.Process):
    def __init__(self, camera, q, mode='nir'):
        super().__init__()
        self.camera  = camera
        self.queue   = q
        self.types   = []
        self.modes   = []
        self.frame   = tof.Frame()
        self.smallSignalThreshold = 100    
        self.depth_scale = 0.085
        self.mode = mode
                
        self.camera.initialize()
        self.camera.getAvailableModes(self.modes)
        self.camera.getAvailableFrameTypes(self.types)
        self.camera.setFrameType(self.types[0]) 
        self.camera.setMode(self.modes[1])
        
        self.camera.setControl("noise_reduction_threshold", str(self.smallSignalThreshold))
        self.camera_details = tof.CameraDetails()
        self.camera.getDetails(self.camera_details)
        log.info(f"Ready !")
        if 'nir' in self.mode:
            self.run = self.run_nir
        else:
            self.run = self.run_depth
                        
    def run_depth(self):
        log.info("Running depth ...")
        while True:
            start = time.time()
            status = self.camera.requestFrame(self.frame)
            end = time.time()
            log.debug(f"Capture time = {1000*(end-start):.3f}ms")
            start = time.time()
            depth_raw =  np.array(self.frame.getData(tof.FrameDataType.Depth), 
                                 dtype="uint16", copy=False) 
            depth_uint8 = np.uint8(self.depth_scale * depth_raw)
            data = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW)
            end = time.time()
            log.debug(f"Improc time = {1000*(end-start):.3f}ms")
            try:
                self.queue.put_nowait(data)
            except queue.Full:
                log.warning("Skipped frame. Full FIFO")

    def run_nir(self):
        log.info("Running IR ...")
        while True:
            start = time.time()
            status = self.camera.requestFrame(self.frame)
            end = time.time()
            log.debug(f"Capture time = {1000*(end-start):.3f}ms")
            start = time.time()
            nir_raw =  np.array(self.frame.getData(tof.FrameDataType.IR), 
                                 dtype="uint16", copy=False) 
            cv2.normalize(nir_raw, nir_raw, 0, 255, cv2.NORM_MINMAX)
            data = cv2.cvtColor(cv2.equalizeHist(np.uint8(nir_raw)), cv2.COLOR_GRAY2BGR)
            #data = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW)
            end = time.time()
            log.debug(f"Improc time = {1000*(end-start):.3f}ms")
            try:
                self.queue.put_nowait(data)
            except queue.Full:
                log.warning("Skipped frame. Full FIFO")
#            count +=1
            #time.sleep(0.10)
#            log.debug(f"Pushed frame {count}")

