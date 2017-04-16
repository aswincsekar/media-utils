import argparse
import PIL
import cv2
from tesserocr import PyTessBaseAPI, PSM
import argparse

def get_words(file):
    with PyTessBaseAPI(psm=PSM.OSD_ONLY) as api:
        api.SetImageFile(file)

        os = api.DetectOS()
        print(os)
        # print("Orientation: {orientation}\nOrientation confidence: {oconfidence}\n"
        #       "Script: {script}\nScript confidence: {sconfidence}").format(**os)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    args = parser.parse_args()
    get_words(args.file)