"""
Funtions to read, crop video frames
"""
from __future__ import division
import subprocess as sp
import json
import numpy
from PIL import Image
import math
import termcolor
import matplotlib.pyplot as plt
import argparse

FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"


def frame_size(input_file):
    """
    Get video frame_size
    eg : ffprobe -v error -show_entries stream=width,height \
          -of default=noprint_wrappers=1
    """
    command = [FFPROBE_BIN,
               '-v', 'error',
               '-show_entries', 'stream=width,height',
               '-of', 'default=noprint_wrappers=1',
               '-print_format', 'json',
               input_file]
    output = sp.check_output(command).decode("utf-8", "ignore")
    # print(str(output))
    output = json.loads(output)
    output = output['streams'][0]
    return output


def frame_reader(input_file, time):
    """
    Given framenumber return the frame
    eg :
    i = vr.frame_reader('/home/aswin/Videos/BACKUP/smoking videos/8 Year Old \
    Boy Smokes  8 Jahre Alter Junge Raucht_0.mp4', '0.19446', 1)
    """
    command = [FFMPEG_BIN,
               '-ss', time,
               '-i', input_file,
               '-vframes', '1',
               '-f', 'image2pipe',
               '-pix_fmt', 'rgb24',
               '-vcodec', 'rawvideo',
               '-loglevel', 'quiet',
               '-']
    try:
        pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
    except:
        print(termcolor.colored("Pipe Failed",'red'))
        pass
    # take the size from the frame_size
    size = frame_size(input_file)
    raw_image = pipe.stdout.read(size['width']*size['height']*3)
    # transform the byte read into a numpy array
    image = numpy.fromstring(raw_image, dtype='uint8')
    try:
        image = image.reshape((size['height'], size['width'], 3))
    except:
        print(termcolor.colored("Reshape Failed", 'red'))
        pass
    # throw away the data in the pipe's buffer.
    pipe.stdout.flush()
    pipe.terminate()
    return image


def print_hist(frame, n):
    print("print_hist")
    plt.figure(n)
    plt.subplot(2, 1, 1)
    plt.imshow(frame)
    plt.title('img')

    plt.subplot(2, 1, 2)
    plt.hist(frame.ravel(), bins=256, range=(0.0, 255.0))
    plt.title('histogram')

    plt.tight_layout()


def process_frames(input_file, start_time, end_time):
    """Read video and get histogram of frames"""
    step = 2 * 0.04
    start_time = int(start_time/step)*step + step
    end_time = int(end_time/step)*step + step
    diff = end_time - start_time
    if diff < 0 :
        raise ValueError
    current_frame = frame_reader(input_file, str(start_time))
    slots = []
    for fr in range(0, int(diff/step)):
        current_time = start_time+fr*step
        hist_1, _ = numpy.histogram(current_frame.ravel(), bins=32)
        next_frame = frame_reader(input_file, str(current_time+step))
        hist_2, _ = numpy.histogram(next_frame.ravel(), bins=32)
        mean = numpy.mean(numpy.absolute(hist_1 - hist_2))
        if mean > 3000:
            print(current_time)
            slots.append(current_time)
            print(termcolor.colored(mean, "red"))
        current_frame = next_frame
    return slots

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-st', '--start_time')
    parser.add_argument('-et', '--end_time')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()
    slots = process_frames(args.file, float(args.start_time), float(args.end_time))
    with open(args.output, 'w+') as data:
        json.dump(slots, data)
