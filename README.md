# atn-sim

Aeronautical Telecommunications Network (ATN) Simulator

## Quick Installation

The following procedures were tested on Ubuntu 12.04 and Ubuntu 14.04. If that is not your case, please refer to the Wiki for more details on the installation process.

```
git clone --recursive https://github.com/contemmcm/atn-sim
cd atn-sim
sudo make deps
make all
sudo make install
```

## Quick Start

Initialize CORE:

```
sudo service core-daemon start
```

Open the graphical user interface for CORE by executing:

```
core-gui
```

Then, open an scenario file (e.g., `configs/scenarios/DEMO1970.imn`) and start the simulation by pressing the green arrow button on the left menu.
