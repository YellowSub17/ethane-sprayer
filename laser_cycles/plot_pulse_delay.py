
import numpy as np
import matplotlib.pyplot as plt
import glob
import re


files = glob.glob('./double_pulse/*')





delays = []
mean_cycles = []
std_cycles = []

for file in files:

    match = re.search(r"delay(\d+)ns", file)
    delay_us = int(match.group(1))*1e-3

    delay_data = np.loadtxt(file)*8e-9*1e6

    delays.append(delay_us)
    mean_cycles.append(delay_data.mean())
    std_cycles.append(delay_data.std())


delays = np.array(delays)
mean_cycles = np.array(mean_cycles)
std_cycles = np.array(std_cycles)

# Get indices that would sort delays
sort_indices = np.argsort(delays)

# Apply sorted indices and chop off the last element [:-1]
delays = delays[sort_indices]
mean_cycles = mean_cycles[sort_indices]
std_cycles = std_cycles[sort_indices]

x_fit = delays[-7:]
y_fit = mean_cycles[-7:]
# Fit a degree 1 polynomial (slope, intercept)
m, c = np.polyfit(x_fit, y_fit, 1)
y_fit_line = m * x_fit + c

# 2. Calculate sum of squared residuals and total sum of squares
ss_res = np.sum((y_fit - y_fit_line) ** 2)
ss_tot = np.sum((y_fit - np.mean(y_fit)) ** 2)

# 3. Compute R-squared
r_squared = 1 - (ss_res / ss_tot)

print(f"R^2: {r_squared:.4f}")






plt.figure()
plt.errorbar(delays, mean_cycles, yerr=std_cycles, linestyle='', marker='.')
plt.plot(x_fit, y_fit_line)
plt.hlines(y=np.mean(mean_cycles[:4]), xmin=delays[0], xmax=delays[3])

# plt.hlines(y=np.mean(mean_cycles[14:18]),  xmin=delays[14], xmax=delays[17])

# plt.axvspan(xminDAC Switching & Saturation Zone

plt.axvspan(ymin=0, ymax=0.2, xmin=0.0, xmax=0.31, color='black', alpha=0.1, label=f'Dead zone: {np.mean(mean_cycles[:4])*1e3} ns')
plt.axvspan(ymin=0.05, ymax=0.8, xmin=0.31, xmax=1.25, color='green', alpha=0.1, label='DAC Switching & Saturation Zone')
plt.xlim([0.0,1.85])
plt.ylim([0.0,1.85])
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel('Input signal delay [us]')
plt.ylabel('Measured delay from cycles [us]')
plt.legend()
plt.tight_layout()

plt.figure()
plt.errorbar(delays, mean_cycles, yerr=std_cycles, linestyle='', marker='.')
plt.plot(x_fit, y_fit_line, label=f'Fit: y={m:.3f}x+{c:3f}\nR$^2$: {r_squared:.7f}\nMean STD: {np.mean(std_cycles[-7:])*1e3:0.3f} ns')
plt.xlim([1.25,5.1])
plt.ylim([1.25,5.1])
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel('Input signal delay [us]')
plt.ylabel('Measured delay from cycles [us]')

plt.legend()
plt.tight_layout()



plt.show()








