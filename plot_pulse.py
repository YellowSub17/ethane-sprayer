import numpy as np
import matplotlib.pyplot as plt
import glob



# fnames = glob.glob('./cycles/pico_output120s_*')[::2]

fnames = [
        # # './cycles/pico_output120s_T10.11kHz.txt',
        # # './cycles/pico_output120s_T10.12MHz.txt',

        # './cycles/pico_output120s_T24.52Hz.txt',
        # './cycles/pico_output120s_T254.84Hz.txt',
        './cycles/pico_output120s_T239.01kHz.txt',
        # './cycles/pico_output120s_T2.55MHz.txt',
        './cycles/pico_output120s_T10.12MHz.txt',
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





cycles1 = np.loadtxt(
    fnames[0],
    dtype=np.int64,
    converters={-1: lambda s: int(s.strip())},
    usecols=-1,
)


cycles2 = np.loadtxt(
    fnames[1],
    dtype=np.int64,
    converters={-1: lambda s: int(s.strip())},
    usecols=-1,
)




# Convert cycle differences into unwrapped continuous cycles
diffs1 = np.diff(cycles1)

# Detect wrap-arounds (negative jumps)
overflows1 = np.where(diffs1 < 0, 2**32, 0)
cumulative_overflow1 = np.cumsum(np.insert(overflows1, 0, 0))

unwrapped_cycles1 = cycles1 + cumulative_overflow1

# Convert unwrapped cycles to elapsed time (assuming default 125 MHz system clock)
time_seconds1 = unwrapped_cycles1 / 125_000_000



# Convert cycle differences into unwrapped continuous cycles
diffs2 = np.diff(cycles2)

# Detect wrap-arounds (negative jumps)
overflows2 = np.where(diffs2 < 0, 2**32, 0)
cumulative_overflow2 = np.cumsum(np.insert(overflows2, 0, 0))

unwrapped_cycles2 = cycles2 + cumulative_overflow2

# Convert unwrapped cycles to elapsed time (assuming default 125 MHz system clock)
time_seconds2 = unwrapped_cycles2 / 125_000_000

plt.figure()
plt.plot(time_seconds1, label='239.01kHz')
plt.plot(time_seconds2, label='10.12MHz')
plt.legend()



# Set total collection duration
DURATION_SEC = 120.0

def analyze_capture(raw_cycles, name="Dataset"):
    # 1. Unwrap cycles (handling 32-bit overflow)
    cycles = np.array(raw_cycles, dtype=np.int64)
    overflows = np.where(np.diff(cycles) < 0, 2**32, 0)
    unwrapped_cycles = cycles + np.cumsum(np.insert(overflows, 0, 0))

    # 2. Total counts and elapsed cycles
    total_events = len(unwrapped_cycles)
    total_cycles = unwrapped_cycles[-1] - unwrapped_cycles[0]

    # 3. Derived metrics using the known 120s window
    measured_pico_clk_mhz = (total_cycles / DURATION_SEC) / 1e6
    measured_event_rate_khz = (total_events / DURATION_SEC) / 1e3

    # 4. Generate absolute time array (in seconds) for plotting
    time_array = (unwrapped_cycles - unwrapped_cycles[0]) / (total_cycles / DURATION_SEC)

    print(f"--- {name} Results ---")
    print(f"Total Events: {total_events}")
    print(f"Measured Pico Clock: {measured_pico_clk_mhz:.3f} MHz")
    print(f"Measured Event Rate: {measured_event_rate_khz:.2f} kHz")

    return time_array, unwrapped_cycles, np.diff(cycles)

time1, cycles1, diff1 = analyze_capture(cycles1, "239.01kHz Run")
time2, cycles2, diff2 = analyze_capture(cycles2, "10.12MHz Run")

# plt.figure()
# plt.plot(time1, cycles1)
# plt.plot(time2, cycles2)

print(np.mean(diff1[100:600]))
print(np.mean(diff2[100:600]))
plt.figure()
plt.plot(diff1)
plt.plot(diff2)

import numpy as np
import matplotlib.pyplot as plt

# 1. Take difference on the unwrapped data to remove overflow spikes completely
clean_diffs_blue = np.diff(cycles1)
clean_diffs_orange = np.diff(cycles1)

# 2. Plot clean inter-arrival times
plt.figure(figsize=(10, 5))
plt.plot(clean_diffs_blue, label="239.01 kHz", alpha=0.7)
plt.plot(clean_diffs_orange, label="10.12 MHz", alpha=0.7)
plt.ylabel("Clock Cycles Between Pulses")
plt.xlabel("Event Index")
plt.legend()
plt.title("Inter-Pulse Interval Jitter & Noise")
plt.show()



plt.show()
