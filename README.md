ECE532 Group1 Project

Description of Your Design Tree
The all core design files are available on GitHub: https://github.com/FusionLi/G1_GestureControlledMultimediaPlaybackSystem

Main Hardware Design: /src/hardware
Camera IP: /src/hardware/camera_ip
	OV7670_top.v: Top level of PMOD Camera configuration and video decoding
	I2C_AV_config.v, I2C_Controller.v, I2C_OV7670_RGB444_Config.v, debounce.v and ov7670_capture.v: Camera configuration, video decoding
	vga444.v: RGB444 value extractions and output frames to VGA display
Area IP: /src/hardware/area_ip
	area.v: Hardware implementation of area based gesture recognition algorithm
Aspect ratio IP: /src/hardware/ratio_ip
	aspect_ratio.v: Hardware implementation of aspect ratio based gesture recognition algorithm

Main Software Design: /src/hardware
Client: /src/hardware/client
	main.c: Ethernet setup and main send loop
	client.c: Connect callback, send callback and sent callback. Also read value from GPIO memory location and write it to send buffer.
Server: /src/hardware/server
	readserver.py:  Receives real-time area and aspect ratio results from FPGA, apply range comparison and produce gesture commands to multimedia player.
Multimedia Playback track:
	0.mp3 ~ 10.mp3: All songs in the multimedia playlist
