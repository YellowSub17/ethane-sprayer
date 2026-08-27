import numpy as np
import matplotlib.pyplot as plt


cycles = np.loadtxt("pico-out.txt", usecols=5, dtype=np.int64)



plt.figure()
plt.plot(cycles, marker='.')
plt.show()
