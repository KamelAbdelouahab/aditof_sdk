import aditofpython as tof
import numpy as np
import cv2
import time

# FXTOF Data
width   = 640
height  = 480
num_cam = 4
cameras = []
types   = []
modes   = []
details = [False, False, False, False]
status  = [False, False, False, False]

# Encoder data
bitrate = 8000000
host = "10.42.0.1"
port = 8888

out_pipeline = ( "appsrc ! video/x-raw, format=BGR ! queue ! videoconvert ! video/x-raw, format=BGRx ! "
                f" nvvidconv ! omxh264enc bitrate={bitrate} ! video/x-h264, out-format=(string)byte-out ! "
                " h264parse ! rtph264pay pt=96 config-interval=1 ! "
                f" udpsink host={host} port={port} sync=false ")

out_writer = cv2.VideoWriter(out_pipeline, 0, 30, (2*width, 2*height))
if not out_writer.isOpened():
    print('VideoWriter not opened')
    exit(0)

def getScalingValues(cameraDetails):
    camera_range = cameraDetails.depthParameters.maxDepth
    bit_count = cameraDetails.bitCount
    max_value_of_IR_pixel = 2 ** bit_count - 1
    distance_scale_ir = 255.0 / max_value_of_IR_pixel
    distance_scale_depth = 255.0 / camera_range
    return distance_scale_ir, distance_scale_depth

if __name__ == "__main__":
    tof_system = tof.System()
    tof_system.getCameraList(cameras)
    for c in range(1, num_cam):
        cameras[c].initialize()
    
    # Get modes and frame types
    cameras[0].getAvailableModes(modes)
    for c in range(1, num_cam):
        cameras[c].getAvailableFrameTypes(types)
    
    # Set to depth / nir :
    for c in range(1, num_cam):
        cameras[c].setFrameType(types[0]) 
    
    # Set mode to near
    for c in range(1, num_cam):
        cameras[c].setMode(modes[1]) 
    

    # Enable noise reduction
    smallSignalThreshold = 100
    for c in range(1, num_cam):
        cameras[c].setControl("noise_reduction_threshold", str(smallSignalThreshold))
    
    # Get Scale values for post-proc
    camera_details = tof.CameraDetails()
    for c in range(1, num_cam):
        cameras[c].getDetails(camera_details)
    
    nir_scale, depth_scale = getScalingValues(camera_details)
    nir_scale = 0.125
    print(nir_scale)
    print(depth_scale)
        
    # Frame slots
    frame     = [tof.Frame(), tof.Frame(), tof.Frame(), tof.Frame()]
    depth_raw = np.zeros((num_cam, height, width), dtype="uint16")
    depth     = np.zeros((2*height, 2*width), dtype="uint16")
    nir_raw   = np.zeros((num_cam, height, width), dtype="uint16")
    
    # Capture
    while(True):
        # Request frames from cameras and put them in numpy
        for c in range(1, num_cam):
            status[c] = cameras[c].requestFrame(frame[c])
            if not status[c]:
                print(f"Camera {c} failure")
                break
            depth_raw[c, ...] = np.array(frame[c].getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        
        #depth = depth_raw.transpose(2,0,1).reshape(num_cam,-1)
        depth[0:height,        0:width]       = depth_raw[0, :, :]
        depth[height:2*height, 0:width]       = cv2.flip(depth_raw[1, :, :], 0)
        depth[0:height,        width:2*width] = cv2.flip(depth_raw[2, :, :], 0)
        depth[height:2*height, width:2*width] = depth_raw[3, :, :]
       
        # # Post process NIR
        # nir_raw   = cv2.vconcat([nir_raw1, nir_raw2])
        # # cv2.normalize(nir_raw, nir_raw, 0, 65000, cv2.NORM_MINMAX)
        # # nir = np.uint8(np.right_shift(nir_raw, 8))
        # nir_raw = nir_scale * nir_raw
        # nir = np.uint8(nir_raw)
        
        # Post process Depth
        depth_uint8 = np.uint8(depth_scale * depth)
        depth_color = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_RAINBOW)
                
        # Send to H264 Pipeline
        out_writer.write(depth_color)
        time.sleep(0.1)
        
    out_writer.release()
    print("Done !") 
    
    