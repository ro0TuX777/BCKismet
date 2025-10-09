# Kismet Data Sources - Complete Summary

## 📡 Connected Data Sources

### WiFi Adapters (3 Total)
| Interface | Device | Type | Status |
|-----------|--------|------|--------|
| `wlp0s20f3` | Intel AX211 | Internal WiFi | ✅ Configured |
| `wlx9cefd5f62bbe` | MediaTek Panda Wireless (0e8d:7961) | USB WiFi | ✅ Configured |
| `wlx8c902da2e062` | TP-Link Archer T2U PLUS (RTL8821AU) | USB WiFi | ✅ Configured |

### Bluetooth (1 Total)
| Interface | Device | Type | Status |
|-----------|--------|------|--------|
| `hci0` | Intel AX211 Bluetooth (8087:0033) | Internal BT | ✅ Configured |

### SDR (1 Total)
| Device | Serial Number | Type | Status |
|--------|---------------|------|--------|
| HackRF One | 0000000000000000436c63dc2f2e2e63 | SDR (1d50:6089) | ✅ Configured |

**Total Data Sources: 5 devices**

## 📊 Captured Data (Latest Session)

**Database:** `Kismet-20251008-17-46-01-1.kismet` (6.6 MB)

| PHY Type | Device Count |
|----------|--------------|
| IEEE802.11 (WiFi) | 86 devices |
| Bluetooth | 26 devices |
| **Total** | **112 devices** |

## ✅ Exported JSON Files

Location: `/home/dragos/rf-kit/logs/kismet/Kismet-20251008-17-46-01-1/`

- `wifi.devices.json` - 1.8 MB (86 WiFi devices)
- `bluetooth.devices.json` - 202 KB (26 Bluetooth devices)

## 🔧 Configuration Files

### 1. Kismet Site Config
**Location:** `/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf`

```conf
# WiFi interfaces - ALL adapters
source=wlp0s20f3:name=WiFi-Internal-AX211:hop=true
source=wlx9cefd5f62bbe:name=WiFi-Panda-MediaTek:hop=true
source=wlx8c902da2e062:name=WiFi-TPLink-Archer:hop=true

# Bluetooth
source=hci0:name=Bluetooth-AX211:type=linuxbluetooth

# SDR - HackRF One
source=hackrf-0000000000000000436c63dc2f2e2e63:name=HackRF-One:type=hackrf

# GPS
source=gpsd:host=localhost,port=2947:name=GPS-GPSD:priority=100
```

### 2. Filebeat Config
**Location:** `/etc/filebeat/filebeat.yml`

Monitors paths:
- `/home/dragos/rf-kit/logs/kismet/Kismet-*/bluetooth.devices.json`
- `/home/dragos/rf-kit/logs/kismet/Kismet-*/wifi.devices.json`

Exports to: `kismet-sdr-default` index in Elasticsearch

### 3. Systemd Service
**Location:** `/home/dragos/rf-kit/kismet/kismet-autostart.service`

Auto-starts Kismet on boot with all data sources enabled.

## 🚀 Running a Kismet Scan

### Manual Scan (Current Method)

1. **Start Kismet manually:**
   ```bash
   cd /home/dragos/Downloads/kismet/forgedfate
   kismet --override=kismet_site.conf
   ```

2. **Let it run for desired duration** (e.g., 60 seconds, 5 minutes, etc.)

3. **Find the latest database:**
   ```bash
   ls -lt /home/dragos/Downloads/kismet/forgedfate/Kismet-*.kismet | head -1
   ```

4. **Export to JSON:**
   ```bash
   cd /home/dragos/rf-kit
   python3 kismet/kismet_to_json_exporter.py /path/to/Kismet-<session>.kismet
   ```

5. **Restart Filebeat to pick up new data:**
   ```bash
   sudo systemctl restart filebeat
   ```

6. **Verify data in Elasticsearch:**
   ```bash
   curl -k -u "vinson:ERC8mkm1nqf@anf0uwc" -s \
     "https://172.18.18.20:9200/kismet-sdr-default/_count" | jq '.count'
   ```

### Automated Scan (TODO)

Create a script similar to KrakenSDR and Pluto SDR test scripts:
- Start Kismet
- Run for specified duration
- Stop Kismet
- Export latest database to JSON
- Restart Filebeat
- Verify data export

## ⚠️ Current Issues

### 1. Kismet Startup Issue
**Problem:** Kismet hangs when probing interfaces and doesn't fully start data sources.

**Workaround:** Use existing Kismet databases that were captured successfully.

**Root Cause:** Unknown - possibly permissions, interface configuration, or driver issues.

### 2. WiFi Data Not in Elasticsearch
**Problem:** WiFi JSON data cannot be imported due to field mapping mismatch.

**Details:**
- Existing Elasticsearch index expects `first_seen` and `last_seen` as Unix timestamps (long)
- Exported JSON uses ISO date strings
- Error: `failed to parse field [first_seen] of type [long]`

**Solution:** Need to:
1. Delete `kismet-sdr-default` index
2. Recreate with correct field mappings (date type instead of long)
3. Re-export all data

### 3. HackRF Not Tested
**Status:** HackRF One is detected and configured in Kismet, but not tested for actual data capture.

**Note:** HackRF requires different handling than WiFi/Bluetooth - it's an SDR that can tune to specific frequencies.

## 📈 Data Export Pipeline

```
┌─────────────────┐
│  Kismet Scan    │
│  (WiFi + BT)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ .kismet Database│
│   (SQLite)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Export Script   │
│ (Python)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Files     │
│ (wifi/bt.json)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Filebeat      │
│  (Monitoring)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Elasticsearch   │
│ (kismet-sdr-*)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Kibana Dashboard│
│  (Visualization)│
└─────────────────┘
```

## 🎯 Next Steps

1. **Fix Elasticsearch field mappings** to accept WiFi data
2. **Debug Kismet startup issue** to enable live data capture
3. **Test HackRF data source** for SDR spectrum analysis
4. **Create automated scan script** similar to KrakenSDR/Pluto tests
5. **Create comprehensive Kismet dashboard** showing WiFi + Bluetooth data
6. **Set up systemd service** for auto-start on boot

## 📝 Files Created

- `kismet/kismet_to_json_exporter.py` - Export .kismet DB to JSON
- `kismet/kismet-autostart.service` - Systemd service for auto-start
- `kismet/KISMET_AUTO_START_SETUP.md` - Auto-start documentation
- `kismet/KISMET_DATA_SOURCES_SUMMARY.md` - This file
- `/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf` - Kismet config with all sources

## 🔗 Related Systems

- **KrakenSDR**: Direction finding, spectrum analysis (5x RTL-SDR)
- **Pluto SDR**: RF spectrum analysis (325 MHz - 3.8 GHz)
- **Kismet**: WiFi/Bluetooth device detection and tracking

All three systems export data to Elasticsearch and have dashboards in Kibana.

**Kibana URL:** https://172.18.18.20:5601/app/dashboards

