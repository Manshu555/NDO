# Setup Guide

## System Requirements

- **Python**: 3.10 or later
- **OS**: Windows, Linux, or macOS (for Python model)
- **NS-3**: 3.36+ required only for packet-level simulation (Linux/WSL only)

## Python Dependencies

```bash
pip install numpy scipy matplotlib pandas pytest
```

Tested versions:
- numpy 1.26.4
- scipy 1.17.1
- matplotlib 3.10.9
- pandas 3.0.3
- pytest 9.1.0

## NS-3 Setup (Optional)

NS-3 does not run natively on Windows. If you need NS-3 packet-level simulation:

### Option 1: Native Linux / WSL
```bash
# Install NS-3 dependencies
sudo apt-get install build-essential python3-dev cmake g++ git

# Clone NS-3
git clone https://gitlab.com/nsnam/ns-3-dev.git
cd ns-3-dev

# Build
./ns3 configure --enable-examples --enable-tests
./ns3 build

# Verify DSDV module
./ns3 run "dsdv-manet --PrintHelp"

# Copy our scenario
cp /path/to/NDO/simulator/ns3_dsdv_scenario.cc scratch/dsdv-manet-gwo.cc
./ns3 build
```

### Option 2: Docker
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y build-essential python3 cmake git
RUN git clone https://gitlab.com/nsnam/ns-3-dev.git /ns3
WORKDIR /ns3
RUN ./ns3 configure && ./ns3 build
```

### Verifying NS-3 DSDV Parameters

The following attributes are confirmed in NS-3's DSDV implementation:

```bash
# Check available attributes
./ns3 run "dsdv-manet --PrintAttributes=ns3::dsdv::RoutingProtocol"
```

Expected configurable attributes:
- `PeriodicUpdateInterval` (Time, default: 15s)
- `SettlingTime` (Time, default: 6s)
- `MaxQueueLen` (uint32_t)
- `MaxQueueTime` (Time)

## Running Without NS-3

The project works fully with the Python model backend:

```bash
# Quick test
python main.py --mode smoke

# Full pipeline
python main.py --mode full
```

All results will be clearly labelled as coming from the Python model.
