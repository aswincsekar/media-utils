import stft
import scipy
import numpy
import scipy.io.wavfile as wav
import matplotlib.pylab as pylab
import argparse

parser =argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-d', '--dest')

args = parser.parse_args()

filepath = args.file
destination_filename = args.dest

fs, audio = wav.read(filepath)
print(audio.shape)
X = stft.spectrogram(audio,framelength=4096, transform=[scipy.fftpack.fft, numpy.fft.fft])
print (X.shape)

fig = pylab.figure()
ax = pylab.Axes(fig, [0,0,1,1])
ax.set_axis_off()
fig.add_axes(ax)
pylab.imshow(scipy.absolute(X[:][:]), origin='lower', aspect='auto', interpolation='nearest')
pylab.savefig(destination_filename)