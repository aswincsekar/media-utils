"""
Funtions to read, crop video frames
"""
from __future__ import division
import subprocess as sp
import json
import numpy
import termcolor
import argparse
import cv2
import random
import time
import glob
import os
import PIL
import xlsxwriter
from PIL import Image
import tesserocr
from tesserocr import PyTessBaseAPI
from scipy import stats
import matplotlib.pyplot as plt


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
    print(str(output))
    output = json.loads(output)
    output = output['streams'][0]
    return output


def frame_rate(input_file):
    command = [FFPROBE_BIN,
               '-v', 'error',
               '-show_entries', 'stream=r_frame_rate',
               '-of', 'default=noprint_wrappers=1',
               '-print_format', 'json',
               input_file]
    output = sp.check_output(command).decode("utf-8", "ignore")
    print(str(output))
    output = json.loads(output)
    output = output['streams'][0]
    return output


def total_frames(input_file):
    command = [FFPROBE_BIN,
               '-v', 'error',
               '-count_frames', '-select_streams', 'v:0',
               '-show_entries', 'stream=nb_read_frames',
               '-of', 'default=nokey=1:noprint_wrappers=1',
               '-print_format', 'json',
               input_file]
    output = sp.check_output(command).decode("utf-8", "ignore")
    print(str(output))
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
    print(time)
    command = [FFMPEG_BIN,
               '-ss', time,
               '-i', input_file,
               # '-vframes', '1',
               '-ss', '0.04',
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


def frames_format(frame):
    frames = frame % 25
    seconds = int(frame / 25) % 60
    mins = int(int(frame / 25) / 60) % 60
    hours = int(int(int(frame / 25) / 60) / 60)
    tim = "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, mins, seconds, frames)
    return tim


def get_bottom_border(input_file):
    cap = cv2.VideoCapture(input_file)
    values = []
    for i in range(10):
        cap.set(2,random.random())
        (_, current_frame) = cap.read()
        edge = cv2.Canny(current_frame, 0, 200)
        # plt.figure(i)
        # plt.imshow(edge)
        shape = edge.shape
        # print(shape)
        for i in range(shape[0]):
            inv_value = shape[0] - i -1
            sum_value = sum(edge[inv_value,:])
            if sum_value > 0:
                # print(sum_value)
                # print(sum_value/(256*shape[1]))
                # if sum_value/(256*shape[1]) > 0.2:
                values.append(inv_value + 1)
                break
    # plt.show()
    print(values)
    np_value = numpy.array(values)
    height = int(stats.mode(np_value)[0][0]) + 2
    # print(height)
    return height


def find_and_replace(t):
    t = t.replace('O', '0')
    t = t.replace('o', '0')
    t = t.replace('u', '0')
    # print(t)
    return t


def get_initial_time(input_file, frames):
    cap = cv2.VideoCapture(input_file)
    values = []
    for i in range(10):
        frac = random.randrange(frames)
        cap.set(2, frac/frames)
        (_, current_frame) = cap.read()
        upper_image = Image.fromarray(current_frame[29:46,130:232,:])
        # upper_image = upper_image.filter(PIL.ImageFilter.SHARPEN)
        # plt.imshow(upper_image)
        # plt.show()
        with PyTessBaseAPI() as api:
            api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
            api.ReadConfigFile('banner/tess-config')
            api.SetImage(upper_image )
            words = api.GetUTF8Text()
            # print(words)
            time = words[0:11]
            time = find_and_replace(time)
            time_split = time.split(':')
            # print(time_split)
            try:
                initial_frame_no = ((int(time_split[0])*60 + int(time_split[1]))*60 + int(time_split[2]))*25 + int(time_split[3])
            except IndexError:
                continue
            except ValueError:
                continue
            values.append(int((initial_frame_no - frac)/25))
    np_value = numpy.array(values)
    time = int(stats.mode(np_value)[0][0])
    return time*25


def process_frames(input_file):
    """
        Read video and get histogram of frames
        18:08 to 37:16 = 19:08 = 19*25 + 8 = 475 + 8 = 483
    """

    frames = total_frames(input_file)['nb_read_frames']
    slots = []
    formatted_slots = []
    cap = cv2.VideoCapture(input_file)
    height = get_bottom_border(input_file)
    # print(height)
    initial_frame = get_initial_time(input_file, int(frames))
    print(frames_format(initial_frame))
    prev_right = -3
    trigger = False
    trigger_left = False
    checkEmptyTrigger = False
    emptyTriggerCount = 0
    left_count = 0
    for i in range(int(frames)):
        (_,current_frame) = cap.read()
        try:
            section_left = current_frame[height:height+10, 341:351, :]
            section_right = current_frame[height:height+10, 0:10, :]
        except TypeError:
            continue

        if numpy.mean(section_left) > 13 :
            checkEmptyTrigger = False
            emptyTriggerCount = 0
            if not trigger:
                print(frames_format(initial_frame+i))
                if (slots == []) or ((initial_frame + i) - slots[-1] > 1):
                    # new trigger on the right
                    print("appended")
                    slots.append(initial_frame + i)
                    formatted_slots.append(frames_format(initial_frame+i))
                    prev_right = i
                # else :
                #     slots.pop()
                #     prev_right = slots[-1]
                trigger = True
                print(numpy.mean(section_left))
        else:
            if trigger or i == prev_right + 1:
                checkEmptyTrigger = True
                emptyTriggerCount = 0
            elif checkEmptyTrigger:
                emptyTriggerCount += 1

            if emptyTriggerCount == 5 and i - prev_right < 10:
                checkEmptyTrigger = False
                emptyTriggerCount = 0
                print("-----------------------------------------------")
                print("popped : emptyTriggerCount")
                print(frames_format(initial_frame+i))
                print("-----------------------------------------------")
                slots.pop()
                formatted_slots.pop()
                trigger = False

        if trigger:
            if numpy.mean(section_right) > 10 :
                left_count = 0
                trigger_left = True
            elif trigger_left :
                left_count += 1

            if left_count == 5:
                slots.append(initial_frame + i)
                formatted_slots.append(frames_format(initial_frame + i))
                print("-----------------------------------------------")
                print("end frame added")
                print(frames_format(initial_frame + i))
                print("-----------------------------------------------")
                left_count = 0
                trigger = False
                trigger_left = False
        else :
            trigger_left = False
            left_count = 0

    return formatted_slots


def write_to_xlsx(file, dest):
    # Create a workbook and add a worksheet.
    file = os.path.basename(file)
    name = file.split('.')[0] + ".xlsx"
    name = os.path.join(dest, name)
    workbook = xlsxwriter.Workbook(name)
    worksheet = workbook.add_worksheet()

    # rearrange dict keys
    keys = list(data.keys())
    keys.sort()
    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0

    # Iterate over the data and write it out row by row.
    for value in keys:
        timings = data[value]
        worksheet.write(row, col, value)
        row += 1
        for i in range(int(len(timings) / 2)):
            time_in = timings[2 * i]
            time_out = timings[2 * i + 1]
            worksheet.write(row, 1, time_in)
            worksheet.write(row, 2, time_out)
            row += 1
    workbook.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder')
    parser.add_argument('-m', '--mode')
    parser.add_argument('-d', '--dest')

    args = parser.parse_args()

    if args.mode == 'single':
        folder = args.folder
        files = glob.glob(os.path.join(folder,'*.mpg'))
        print(files)
        folder_name = folder.split("/")[-2]
        print(folder_name)
        data = {}
        for file in files:
            print(os.path.basename(file))
            start = time.time()
            slots = process_frames(file)
            print( time.time() - start)
            data[os.path.basename(file)] = slots
        file_name = folder_name+'.json'
        with open(os.path.join(args.dest,file_name), 'w+') as pointer:
            json.dump(data, pointer, indent=4)
        write_to_xlsx(file_name, args.dest)

    elif args.mode =="multi":
        main_folder = args.folder
        for folder in os.listdir(main_folder):
            folder_path = os.path.join(main_folder, folder)
            print(folder)
            files = glob.glob(os.path.join(folder_path, '*.mpg'))
            data = {}
            for file in files:
                print(os.path.basename(file))
                start = time.time()
                slots = process_frames(file)
                print(time.time() - start)
                data[os.path.basename(file)] = slots
            file_name = folder + '.json'
            with open(os.path.join(args.dest, file_name), 'w+') as pointer:
                json.dump(data, pointer, indent=4)

