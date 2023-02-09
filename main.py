import sounddevice as sd
import numpy as np
import scipy.fftpack
import os

# General settings
SAMPLE_FREQ = 44100 # sample frequency in Hz
WINDOW_SIZE = 44100 # window size of the DFT in samples
WINDOW_STEP = 21050 # step size of window
windowSamples = [0 for _ in range(WINDOW_SIZE)]

last_fq = []

def callback(indata, frames, time, status):
  global windowSamples
  if status:
    print(status)
  if any(indata):
    windowSamples = np.concatenate((windowSamples,indata[:, 0])) # append new samples
    windowSamples = windowSamples[len(indata[:, 0]):] # remove old samples
    magnitudeSpec = abs( scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2] )

    for i in range(int(62/(SAMPLE_FREQ/WINDOW_SIZE))):
      magnitudeSpec[i] = 0 #suppress mains hum

    maxFreq = np.argmax(magnitudeSpec) * (SAMPLE_FREQ/WINDOW_SIZE)

    # os.system('cls' if os.name=='nt' else 'clear')
    print(f"FQ {maxFreq}")

    if last_fq[-4:] == [440, 440, 440, 440]:
        print('Unlocked')
    print(last_fq)
    last_fq.append(int(maxFreq))

  else:
    print('no input')

try:
  with sd.InputStream(channels=1, callback=callback,
    blocksize=WINDOW_STEP,
    samplerate=SAMPLE_FREQ):
    while True:
      pass
except Exception as e:
    print(str(e))
