import aditofpython as tof
import numpy as np
import cv2
import time
import argparse

# FXTOF Data
width   = 640
height  = 480
num_cam = 4
cameras = []
types   = []
modes   = []

# Encoder data
bitrate = 8000000
host = "10.42.0.1"

def getScalingValues(cameraDetails):
    camera_range = cameraDetails.depthParameters.maxDepth
    bit_count = cameraDetails.bitCount
    max_value_of_IR_pixel = 2 ** bit_count - 1
    distance_scale_ir = 255.0 / max_value_of_IR_pixel
    distance_scale_depth = 255.0 / camera_range
    return distance_scale_ir, distance_scale_depth

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description= "FXTOF Viewer / Sma-RTy 2023")
    parser.add_argument('-c', '--cam',  help = "Camera ID. Ranges from 0 to 3", default=0, type=int)
    parser.add_argument('-p', '--port', help = "Stream port", default="8888")
    args = parser.parse_args()
    cam_id  = args.cam
    port    = args.port
    
    # Init cv2
    out_pipeline = ( "appsrc ! video/x-raw, format=BGR ! queue ! videoconvert ! video/x-raw, format=BGRx ! "
                    f" nvvidconv ! omxh264enc bitrate={bitrate} ! video/x-h264, out-format=(string)byte-out ! "
                    " h264parse ! rtph264pay pt=96 config-interval=1 ! "
                    f" udpsink host={host} port={port} sync=false ")

    out_writer = cv2.VideoWriter(out_pipeline, 0, 30, (width, height))
    if not out_writer.isOpened():
        print('VideoWriter not opened')
        exit(0)    
    
    # Init TOF System
    tof_system = tof.System()
    tof_system.getCameraList(cameras)
    camera = cameras[cam_id]
    camera.initialize()
    
    # Get modes and frame types
    camera.getAvailableModes(modes)
    camera.getAvailableFrameTypes(types)
    
    # Set to depth / nir :
    camera.setFrameType(types[0]) 
    
    # Set mode to near
    camera.setMode(modes[1]) 

    # Enable noise reduction
    smallSignalThreshold = 100
    camera.setControl("noise_reduction_threshold", str(smallSignalThreshold))
    
    # Get Scale values for post-proc
    camera_details = tof.CameraDetails()
    camera.getDetails(camera_details)
    nir_scale, depth_scale = getScalingValues(camera_details)
    nir_scale = 0.125
    
    # Frame place holder
    frame = tof.Frame()
    depth_raw = np.zeros((height, width), dtype="uint16")
    depth     = np.zeros((height, width), dtype="uint16")
    nir_raw   = np.zeros((height, width), dtype="uint16")
    nir       = np.zeros((height, width), dtype="uint16")
        
    # Capture
    while(True):
        status = camera.requestFrame(frame)
        if not status:
            print(f"Camera failure")
            break
        depth_raw = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        depth_uint8 = np.uint8(depth_scale * depth_raw)
        depth_color = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW)
                
        # Send to H264 Pipeline
        out_writer.write(depth_color)        
        #time.sleep(0.1)
        
    out_writer.release()
    print("Done !") 