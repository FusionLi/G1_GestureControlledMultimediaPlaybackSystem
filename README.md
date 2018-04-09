# G1_GestureControlledMultimediaPlaybackSystem

Description of Your Design Tree
The all core design files are available on GitHub: https://github.com/FusionLi/G1_GestureControlledMultimediaPlaybackSystem

Repository Structure:
---------------------
- Main Hardware Design: /src/hardware
	- Camera IP: /src/hardware/camera_ip
		1. OV7670_top.v: Top level of PMOD Camera configuration and video decoding
		2. I2C_AV_config.v, I2C_Controller.v, I2C_OV7670_RGB444_Config.v, debounce.v and ov7670_capture.v: Camera configuration, video decoding
		3. vga444.v: RGB444 value extractions and output frames to VGA display
	- Area IP: /src/hardware/area_ip
		1. area.v: Hardware implementation of area based gesture recognition algorithm
	- Aspect ratio IP: /src/hardware/ratio_ip
		1. aspect_ratio.v: Hardware implementation of aspect ratio based gesture recognition algorithm

- Main Software Design: /src/hardware
	- Client: /src/hardware/client
		1. main.c: Ethernet setup and main send loop
		2. client.c: Connect callback, send callback and sent callback. Also read value from GPIO memory location and write it to send buffer.
	- Server: /src/hardware/server
		1. readserver.py:  Receives real-time area and aspect ratio results from FPGA, apply range comparison and produce gesture commands to multimedia player.
	- Multimedia Playback track:
		1. 0.mp3 ~ 10.mp3: All songs in the multimedia playlist
