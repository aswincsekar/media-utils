import json
import argparse
import xlsxwriter
import glob
from collections import OrderedDict
import os


def frames_format(frame):
    frames = frame % 25
    seconds = int(frame / 25) % 60
    mins = int(int(frame / 25) / 60) % 60
    hours = int(int(int(frame / 25) / 60) / 60)
    tim = "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, mins, seconds, frames)
    return tim


def write_to_file(file, dest):
    with open(file, 'r+') as f:
        data = json.load(f)

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
            frames = timings[2 * i] % 25
            seconds = int(timings[2 * i] / 25) % 60
            mins = int(int(timings[2 * i] / 25) / 60) % 60
            hours = int(int(int(timings[2 * i] / 25) / 60) / 60)
            time_in = timings[2*i]
            frames = timings[2 * i + 1] % 25
            seconds = int(timings[2 * i + 1] / 25) % 60
            mins = int(int(timings[2 * i + 1] / 25) / 60) % 60
            hours = int(int(int(timings[2 * i + 1] / 25) / 60) / 60)
            time_out = timings[2*i + 1]
            worksheet.write(row, 1, time_in)
            worksheet.write(row, 2, time_out)
            row += 1
    workbook.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-fo', '--file')
    parser.add_argument('-fl', '--folder')
    parser.add_argument('-m', '--mode')
    parser.add_argument('-d', '--dest')

    args = parser.parse_args()
    if args.mode == "single":
        write_to_file(args.file)
    elif args.mode == "multi":
        folder = args.folder
        files = glob.glob(os.path.join(folder, '*.json'))
        for file in files:
            write_to_file(file, args.dest)