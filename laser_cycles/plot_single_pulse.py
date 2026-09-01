import numpy as np
import matplotlib.pyplot as plt
import glob



# fnames = glob.glob('./cycles/pico_output120s_*')[::2]

fnames = [
        # # './cycles/pico_output120s_T10.11kHz.txt',
        # # './cycles/pico_output120s_T10.12MHz.txt',

        # './cycles/pico_output120s_T24.52Hz.txt',
        # './cycles/pico_output120s_T254.84Hz.txt',
        # './cycles/pico_output120s_T239.01kHz.txt',
        # # './cycles/pico_output120s_T2.55MHz.txt',
        # './cycles/pico_output120s_T10.12MHz.txt',

        # './cycles/pico_output120s_T30.08kHz2.txt',

        './cycles/pico_output120s_T254.84Hz.txt',
        './cycles/pico_output120s_T105.67Hz.txt'
        ]







plt.figure()
for fname in fnames:
    print(fname)
    cycles = np.loadtxt(
    fname,
    dtype=np.int64,
    converters={-1: lambda s: int(s.strip())},
    usecols=-1,
)
    plt.plot(cycles,marker='.', label=fname)
plt.legend()




plt.show()
