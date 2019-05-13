#!/bin/bash
set +x

sudo rmmod g_webcam

sudo media-ctl -v -d /dev/media1 -l '"msm_csiphy1":1->"msm_csid0":0[1],"msm_csid0":1->"msm_ispif0":0[1],"msm_ispif0":1->"msm_vfe0_rdi0":0[1]'
sudo media-ctl -v -d /dev/media1 -V '"ad903x 1-0064":0[fmt:SBGGR12/668x750 field:none],"msm_csiphy1":0[fmt:SBGGR12/668x750 field:none],"msm_csid0":0[fmt:SBGGR12/668x750 field:none],"msm_ispif0":0[fmt:SBGGR12/668x750 field:none],"msm_vfe0_rdi0":0[fmt:SBGGR12/668x750 field:none]'

sudo modprobe g_webcam streaming_maxpacket=2048

sudo ./uvc-gadget -r 3 -o 1 -a -n 4 
