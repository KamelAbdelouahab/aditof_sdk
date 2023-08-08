import aditofpython as tof
import numpy as np
import cv2

width   = 640
height  = 480
cameras = []
types   = []
modes   = []
status  = [False, False, False, False]

out_pipeline = ("appsrc ! video/x-raw, format=BGR ! queue ! videoconvert ! video/x-raw, format=BGRx ! "
                " nvvidconv ! omxh264enc ! video/x-h264, out-format=(string)byte-out ! "
                " h264parse ! rtph264pay pt=96 config-interval=1 ! "
                " udpsink host=10.42.0.1 port=8888 sync=false ")

out_writer = cv2.VideoWriter(out_pipeline, 0, 30, (2*width, 2*height))
if not out_writer.isOpened():
    print('VideoWriter not opened')
    exit(0)

if __name__ == "__main__":
    tof_system = tof.System()
    tof_system.getCameraList(cameras)
    cameras[1].initialize()
    cameras[2].initialize()
    
    # Get modes and frame types
    cameras[1].getAvailableModes(modes)
    cameras[1].getAvailableFrameTypes(types)
    
    # Set to depth / nir :
    cameras[1].setFrameType(types[0]) 
    cameras[2].setFrameType(types[0])
    
    # Set mode to near
    cameras[1].setMode(modes[1]) 
    cameras[2].setMode(modes[1])    
    
    # Frame slots
    frame1 = tof.Frame()
    frame2 = tof.Frame()
    
    # Capture
    while(True):
        # Request frames from cameras
        status[1] = cameras[1].requestFrame(frame1)
        status[2] = cameras[2].requestFrame(frame2)
        if not status[1]:
            print("Camera 1 failure")
            break        
        if not status[2]:
            print("Camera 2 failure")
            break
        
        # Put it in numpy format
        depth_raw1 = cv2.flip(np.array(frame1.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False), 0)
        depth_raw2 = cv2.flip(np.array(frame2.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False), 0)
        nir_raw1   = cv2.flip(np.array(frame1.getData(tof.FrameDataType.IR),    dtype="uint16", copy=False), 0)
        nir_raw2   = cv2.flip(np.array(frame2.getData(tof.FrameDataType.IR),    dtype="uint16", copy=False), 0)
        
        # Post process NIR
        nir_raw   = cv2.vconcat([nir_raw1, nir_raw2])
        cv2.normalize(nir_raw, nir_raw, 0, 65000, cv2.NORM_MINMAX)
        nir = np.uint8(np.right_shift(nir_raw, 8))
        
        # Post process Depth
        depth_raw = cv2.vconcat([depth_raw1, depth_raw2])
        cv2.normalize(depth_raw, depth_raw, 0, 65000, cv2.NORM_MINMAX)
        depth = np.uint8(np.right_shift(depth_raw, 8))
        
        # Combine 4 frames        
        nir   = cv2.cvtColor(nir, cv2.COLOR_GRAY2RGB)
        depth = cv2.applyColorMap(depth, cv2.COLORMAP_RAINBOW)
        o     = cv2.hconcat([depth, nir])
        
        # Send to H264 Pipeline
        out_writer.write(o)
        
    out_writer.release()
    print("Done !") 
    
    