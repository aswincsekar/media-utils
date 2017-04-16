import json


def compress_timeline(time_array):
    """take the laplacian segments and merge closer by segments"""
    new_array = []
    buffer = [time_array[0]]
    for i in range(0,len(time_array)):
        if buffer[0] > time_array[i] - 3:
            buffer.append(time_array[i])
        else :
            new_array.append(buffer[int(len(buffer)/2)])
            buffer = [time_array[i]]
    return new_array


if __name__ == '__main__':
    with open("./output-segments.json", "r+") as f:
        data = json.load(f)
    compressed = compress_timeline(data)
    with open("./compressed-segments.json", "w+") as f:
        json.dump(compressed, f, indent=4)
    print(compressed)