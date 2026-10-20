import csv
import matplotlib.pyplot as plt

t, a, b = [], [], []
with open("shot.csv") as f:
    for row in csv.reader(f):
        if len(row) == 4 and row[0] == "AN":
            t.append(int(row[1]) / 1000)      # ms
            a.append(int(row[2]) / 4095 * 3.3)
            b.append(int(row[3]) / 4095 * 3.3)

plt.plot(t, a, label="Gate A")
plt.plot(t, b, label="Gate B")
plt.xlabel("time since opening (ms)")
plt.ylabel("AO (V)")
plt.legend()
plt.show()