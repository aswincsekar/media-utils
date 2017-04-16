import json
import argparse


def nearest_member(number_array, n):
    if len(number_array) == 1:
        return number_array[0]
    elif number_array[int(len(number_array)/2)] > n :
        return nearest_member(number_array[0:int(len(number_array)/2)],n)
    else:
        return nearest_member(number_array[int(len(number_array)/2):len(number_array)],n)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audio')
    parser.add_argument('-v', '--video')

    args = parser.parse_args()

    with open(args.audio, "r+") as a:
        audio_data = json.load(a)

    with open(args.video, "r+") as v:
        video_data = json.load(v)

    for a in audio_data:
        n = nearest_member(video_data, a)
        print(str(a) + ":" + str(n))