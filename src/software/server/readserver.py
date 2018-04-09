import socket
import time
import pyglet
import threading
import queue
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from random import shuffle
import math

PLAY_START = 25
PLAY_END = 33
PAUSE_START = 18
PAUSE_END = 22.5
NEXT_START = 33
NEXT_END = 13
VDOWN_START = 30
VDOWN_END = 82
VUP_START = 82
VUP_END = 180
MIN = 3
VOLUME_STEP = 3

VOLUME_MAX = -10
VOLUME_MIN = -63

VUP_RATIO = 110
VDOWN_RATIO = 50

fluc_counter = 0

def get_result(area, ratio):
    if area > MIN and area < PAUSE_START:
        if ratio < VDOWN_END and ratio > VDOWN_START:
            print("***VOLUME DOWN***")
            return 5
        elif ratio >= VUP_START and ratio < VUP_END:
            print("***VOLUME UP***")
            return 4
    elif area >= PAUSE_START:
        if area > PLAY_START and area < PLAY_END:
            print("***PLAY***")
            return 2
        elif area >= NEXT_START:
            print("***NEXT***")
            return 3
        elif area > PAUSE_START and area < PAUSE_END:
            print("***PAUSE***")
            return 1
        elif area > PAUSE_END and area < PLAY_START:
            if(ratio < 80):
                print("***PLAY***")
                return 2
            else:
                print("***PAUSE***")
                return 1
    else:
        return 0

def change_volume(ratio, direction, start, volume):
    global VDOWN_RATIO
    global VUP_RATIO
    global fluc_counter
    print('***ratio: ' + str(ratio) + ' VUP_RATIO: ' + str(VUP_RATIO) + ' VDOWN_RATIO: ' + str(VDOWN_RATIO) + ' start: ' + str(start))
    # increase volume
    power_percentage = math.pow(1.0717, start)
    power_percentage_max = math.pow(1.0717, VOLUME_MAX)
    power_percentage_min = math.pow(1.0717, VOLUME_MIN)
    if ratio < VDOWN_RATIO:
        VDOWN_RATIO = ratio
    elif ratio > VUP_RATIO:
        VUP_RATIO = ratio

    if direction == 2:
        volume_ratio = (ratio - VDOWN_RATIO) / (VUP_RATIO - VDOWN_RATIO)
        volume_step = power_percentage_max - power_percentage
    # decrease volume
    elif direction == 1:
        volume_ratio = (VUP_RATIO - ratio) / (VUP_RATIO - VDOWN_RATIO)
        volume_step =  power_percentage_min - power_percentage

    # if (ratio - last_ratio) > 0:
    #     # increase
    #     volume_change = VOLUME_STEP
    # elif (ratio - last_ratio) < 0:
    #     # decrease
    #     volume_change = -1 * VOLUME_STEP
    if volume_step > 0:
        if fluc_counter >= 0:
            fluc_counter += 1
        else:
            fluc_counter = 1;
    elif volume_step < 0:
        if fluc_counter <= 0:
            fluc_counter -= 1
        else:
            fluc_counter = -1;
    volume_change = power_percentage + volume_step * volume_ratio

    volume_change = math.log(volume_change, 1.0717)
    if volume_change < VOLUME_MIN:
        volume_change = VOLUME_MIN
    elif volume_change > VOLUME_MAX:
        volume_change = VOLUME_MAX
    print("value:", volume_change)
    if fluc_counter == 2:
        volume.SetMasterVolumeLevel(volume_change, None)
        fluc_counter = 1
        print("***",fluc_counter)
    elif fluc_counter == -2:
        volume.SetMasterVolumeLevel(volume_change, None)
        fluc_counter = -1
        print("***", fluc_counter)


def setup_server(player, volume):
    PORT = 7
    BUFFER_SIZE = 10
    SERVER_VALUE = bytes.fromhex('DEADBEEF')
    # Set up socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Allow re-binding the same port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to port on any interface
        sock.bind(('0.0.0.0', PORT))
        sock.listen(1)  # allow backlog of 1
        ratio_queue = []
        area_queue = []
        volume_queue = []
        volume_loop = 0
        volume_start = 0
        # last_volume = 0
        print("BEGIN LISTENING ON PORT", PORT)
        # Begin listening for connections
        oldtime = time.time()
        state = 0
        lastRatio = 0
        lastArea = 0
        while True:
            conn, addr = sock.accept()
            with conn:
                # Receive and handle command
                data = conn.recv(BUFFER_SIZE)
                currtime = time.time()
                if (currtime - oldtime) > 0.1:
                    oldtime = currtime
                    data = data[:-1].decode("utf-8")
                    tokens = data.split(":")
                    ratio = int(tokens[0].strip())
                    area = int(tokens[1].strip())
                    if area == 0:
                        ratio = 0
                    print("data:", data)
                    if volume_loop:
                        if len(volume_queue) < 7 or len(volume_queue) == 0:
                            volume_queue.append(ratio)
                        elif len(volume_queue) >= 7:
                            volume_average = (sum(volume_queue) - min(volume_queue))/ (7 - 1)
                            if volume_average < VDOWN_START or volume_average > VUP_END or area > PAUSE_START or area < MIN:
                                volume_loop = 0
                                volume_start = 0
                            else:
                                change_volume(volume_average, volume_loop, volume_start, volume)
                                # last_volume = volume_average
                            volume_queue = []
                    else:
                        if lastRatio == 0 and ratio != 0 and lastArea == 0 and area != 0 and len(ratio_queue) == 0:
                            ratio_queue.append(ratio)
                            area_queue.append(area)
                        elif 0 < len(ratio_queue) < 12:
                            ratio_queue.append(ratio)
                            area_queue.append(area)
                        elif len(ratio_queue) >= 12:
                            effective_ratio_queue = ratio_queue[2:]
                            effective_area_queue = area_queue[2:]
                            ratio_count = 10 - effective_ratio_queue.count(0)
                            area_count = 10 - effective_area_queue.count(0)
                            if ratio_count == 0 or area_count == 0:
                                ratio_avg = 0
                                area_avg = 0
                            else:
                                ratio_avg = sum(effective_ratio_queue) / ratio_count
                                area_avg = sum(effective_area_queue) / area_count
                            cmd = get_result(area_avg, ratio_avg)
                            if state == 1:
                                if cmd == 1:
                                    state = 0
                                    player.pause()
                                    print("PAUSE")
                                elif cmd == 3:
                                    player.next_source()
                                    print("NEXT")
                                elif cmd == 4:
                                    # volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel() + VOLUME_STEP, None)
                                    volume_loop = 1
                                    global VUP_RATIO
                                    # VUP_RATIO = ratio_avg
                                    volume_start = volume.GetMasterVolumeLevel()
                                    print("VOLUME UP")
                                elif cmd == 5:
                                    # volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel() - VOLUME_STEP, None)
                                    volume_loop = 2
                                    global VDOWN_RATIO
                                    # VDOWN_RATIO = ratio_avg
                                    volume_start = volume.GetMasterVolumeLevel()
                                    print("VOLUME DOWN")
                                else:
                                    print("NO ACTION")
                            else:
                                if cmd == 2:
                                    state = 1
                                    player.play()
                                    print("PLAY")
                                else:
                                    print("NO ACTION")
                            print(">>>>>>>>>>>>average ratio: ", ratio_avg, " area:", area_avg)

                            ratio_queue = []
                            area_queue = []
                    lastRatio = ratio
                    lastArea = area
                conn.send(SERVER_VALUE)
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()


def audio_control():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    player = pyglet.media.Player()
    play_list = ['2.mp3', '3.mp3', '4.mp3', '5.mp3', '6.mp3', '7.mp3']
    shuffle(play_list)
    for song in play_list:
        source = pyglet.media.load(song)
        player.queue(source)

    player.eos_action = pyglet.media.SourceGroup.loop
    t1 = threading.Thread(target=setup_server, args=(player, volume))
    t1.start()
    pyglet.app.run()


if __name__ == "__main__":
    audio_control()