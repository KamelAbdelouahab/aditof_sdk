/*
 * BSD 3-Clause License
 *
 * Copyright (c) 2019, Analog Devices, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
#ifndef TARGET_DEFINITIONS_H
#define TARGET_DEFINITIONS_H

// // Camera 0 - J9
// static const char *EEPROM_DEV_PATH      = "/sys/bus/i2c/devices/31-0056/eeprom";
// static const char *TEMP_SENSOR_DEV_PATH = "/sys/class/hwmon/hwmon1/temp1_input";
// static const char *CAPTURE_DEVICE_NAME  = "vi-output, addi9036 30-0064|vi-output, addi9036 34-0064";
// static const char *DRIVER_PATH          = "/dev/video0|/dev/video1";
// static const char *SUBDEV_PATH          = "/dev/v4l-subdev0|/dev/v4l-subdev2";


// // Camera 1 - J10
// static const char *EEPROM_DEV_PATH      = "/sys/bus/i2c/devices/31-0056/eeprom";
// static const char *TEMP_SENSOR_DEV_PATH = "/sys/class/hwmon/hwmon1/temp1_input";
// static const char *CAPTURE_DEVICE_NAME  = "vi-output, addi9036 31-0064|vi-output, addi9036 35-0064";
// static const char *DRIVER_PATH          = "/dev/video2|/dev/video3";
// static const char *SUBDEV_PATH          = "/dev/v4l-subdev4|/dev/v4l-subdev6";

// // Camera 2 - J12
// static const char *EEPROM_DEV_PATH      = "/sys/bus/i2c/devices/32-0056/eeprom";
// static const char *TEMP_SENSOR_DEV_PATH = "/sys/class/hwmon/hwmon1/temp1_input";
// static const char *CAPTURE_DEVICE_NAME  = "vi-output, addi9036 32-0064|vi-output, addi9036 36-0064";
// static const char *DRIVER_PATH          = "/dev/video4|/dev/video5";
// static const char *SUBDEV_PATH          = "/dev/v4l-subdev8|/dev/v4l-subdev10";

// // Camera 3 - J11
// static const char *EEPROM_DEV_PATH      = "/sys/bus/i2c/devices/33-0056/eeprom";
// static const char *TEMP_SENSOR_DEV_PATH = "/sys/class/hwmon/hwmon1/temp1_input";
// static const char *CAPTURE_DEVICE_NAME  = "vi-output, addi9036 33-0064|vi-output, addi9036 37-0064";
// static const char *DRIVER_PATH          = "/dev/video6|/dev/video7";
// static const char *SUBDEV_PATH          = "/dev/v4l-subdev12|/dev/v4l-subdev14";

static const int  NUM_CAMERAS = 4;

static const char *EEPROM_DEV_PATH[NUM_CAMERAS]      // One of my FXTOFs has tricky eeprom. Using EEPROM at 31 
    = {"/sys/bus/i2c/devices/31-0056/eeprom",
       "/sys/bus/i2c/devices/31-0056/eeprom",
       "/sys/bus/i2c/devices/31-0056/eeprom",
       "/sys/bus/i2c/devices/31-0056/eeprom"};
   
static const char *TEMP_SENSOR_DEV_PATH[NUM_CAMERAS] // One of my FXTOFs has tricky temp sensor. Using only a single device
    = {"/sys/class/hwmon/hwmon1/temp1_input",
       "/sys/class/hwmon/hwmon1/temp1_input",
       "/sys/class/hwmon/hwmon1/temp1_input",
       "/sys/class/hwmon/hwmon1/temp1_input"};

static const char *CAPTURE_DEVICE_NAME[NUM_CAMERAS]  
    = {"vi-output, addi9036 30-0064|vi-output, addi9036 34-0064",
       "vi-output, addi9036 31-0064|vi-output, addi9036 35-0064",
       "vi-output, addi9036 32-0064|vi-output, addi9036 36-0064",
       "vi-output, addi9036 33-0064|vi-output, addi9036 37-0064"};


static const char *DRIVER_PATH[NUM_CAMERAS]          
    = {"/dev/video0|/dev/video1",
       "/dev/video2|/dev/video3",
       "/dev/video4|/dev/video5",
       "/dev/video6|/dev/video7"};

static const char *SUBDEV_PATH[4]          
    = {"/dev/v4l-subdev0|/dev/v4l-subdev2",
       "/dev/v4l-subdev4|/dev/v4l-subdev6",
       "/dev/v4l-subdev8|/dev/v4l-subdev10",
       "/dev/v4l-subdev12|/dev/v4l-subdev14"};


#endif // TARGET_DEFINITIONS_H
