# NS-3 DSDV Configurable Parameters

## Overview

This document identifies which DSDV parameters can be configured through
NS-3's supported APIs, based on the NS-3 DSDV module source code
(`src/dsdv/model/dsdv-routing-protocol.h` and `.cc`).

## Confirmed Configurable Attributes

These are exposed as `ns3::TypeId::Attribute` in the NS-3 DSDV implementation
and can be set via `DsdvHelper::Set()` or `Config::SetDefault()`.

### 1. PeriodicUpdateInterval

- **Type**: `ns3::TimeValue`
- **Default**: 15 seconds
- **Description**: Interval between full routing table broadcasts
- **API**:
  ```cpp
  DsdvHelper dsdv;
  dsdv.Set("PeriodicUpdateInterval", TimeValue(Seconds(10.0)));
  ```
- **Effect**: Lower values increase route freshness but add overhead

### 2. SettlingTime

- **Type**: `ns3::TimeValue`
- **Default**: 6 seconds
- **Description**: Time to wait before accepting route changes, reducing oscillation
- **API**:
  ```cpp
  dsdv.Set("SettlingTime", TimeValue(Seconds(3.0)));
  ```
- **Effect**: Lower values allow faster route convergence but may cause instability

### 3. MaxQueueLen

- **Type**: `ns3::UintegerValue`
- **Default**: Varies by NS-3 version (typically 64)
- **Description**: Maximum number of packets in the DSDV send buffer
- **API** (version-dependent):
  ```cpp
  // May be set as an attribute or through the routing protocol object
  dsdv.Set("MaxQueueLen", UintegerValue(128));
  ```
- **Note**: Check your NS-3 version. In some versions, this attribute name
  may differ or not be directly accessible via `DsdvHelper::Set()`.

### 4. MaxQueueTime

- **Type**: `ns3::TimeValue`
- **Default**: 30 seconds (varies by version)
- **Description**: Maximum time a packet can wait in the send buffer
- **API** (version-dependent):
  ```cpp
  dsdv.Set("MaxQueueTime", TimeValue(Seconds(60.0)));
  ```
- **Note**: Same version-dependent availability as MaxQueueLen.

## Parameters NOT Tuned

The following are part of DSDV's core protocol logic and are NOT tuned:

| Parameter | Reason |
|-----------|--------|
| Sequence number increment | Fixed at +2 per self-originated update (DSDV spec) |
| Route selection rule | Highest seq_num → lowest hop_count (DSDV correctness) |
| Triggered update behaviour | Protocol-defined response to topology changes |

## Version Compatibility

The NS-3 C++ scenario (`ns3_dsdv_scenario.cc`) uses `PeriodicUpdateInterval`
and `SettlingTime` which are available across all NS-3 versions with DSDV.

`MaxQueueLen` and `MaxQueueTime` lines are commented out in the scenario code
with instructions to uncomment after verifying availability in your NS-3 version:

```cpp
// Uncomment after verifying your NS-3 version supports these attributes:
// dsdv.Set("MaxQueueLen", UintegerValue(maxQueueLen));
// dsdv.Set("MaxQueueTime", TimeValue(Seconds(maxQueueTime)));
```

## How to Check Your Version

```bash
cd /path/to/ns-3
grep -n "AddAttribute" src/dsdv/model/dsdv-routing-protocol.cc
```

This will list all TypeId attributes registered by the DSDV routing protocol.
