# pico

Code for the pico


## Build

```

sudo apt update
sudo apt install -y cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
cd ~/ethane-sprayer/pico
git submodule update --init --recursive

mkdir build
cd build
cmake ..
make -j4
```
