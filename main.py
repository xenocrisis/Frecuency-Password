import numpy as np
import tkinter as tk
import customtkinter as ctk
import numpy as np
import pyaudio
from time import sleep

# Gui Components
root = ctk.CTk()
root.title('Experimental audio passwd')
root.geometry("250x200")
root.resizable(0,0)

Labelfq = ctk.CTkLabel(master=root, text='Frecuency:', font=('', 25))
Labelfq.pack(anchor='center', pady=15)

LabelStatus = ctk.CTkLabel(master=root, text='Status: Locked 🔒')
LabelStatus.pack(anchor='center')

Button = ctk.CTkButton(master=root, text='Unlock', command=lambda: listening())
Button.pack(anchor='center')

Entry = ctk.CTkEntry(master=root)
Entry.pack(anchor='center', pady=5)
Entry.insert(0, string='440, 440, 440, 440')

# Configuration
NOTE_MIN = 0       # C4
NOTE_MAX = 2000       # A4
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?
SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

# Functions
def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)

def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP

imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

# Allocate space to run an FFT. 
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# Initialize audio
def listening():

  passwd = Entry.get().replace(' ', '').split(',')
  passwd = [ int(x) for x in passwd]

  stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=FSAMP,input=True, frames_per_buffer=FRAME_SIZE)
  stream.start_stream()

  window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

  # FQ Detection
  fqh = []
  i = 0
  while stream.is_active():
      buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
      buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)
      fft = np.fft.rfft(buf * window)
      freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP
      Labelfq.configure(text='Frecuency: ' + str(int(freq)) + 'Hz')
      print(fqh)
      print(passwd)
      if fqh[-len(passwd):] == passwd:
          LabelStatus.configure(text='Status: Bypass 🔓')
      fqh.append(int(freq))
      if i == 10:
        stream.stop_stream()
      i += 1
      sleep(0.1)
  

root.mainloop()