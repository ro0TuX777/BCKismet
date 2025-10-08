# ForgedFate Export GUI Guide

## 🎯 Overview

The new **Export** feature in the ForgedFate Kismet web interface provides an easy-to-use GUI for configuring all three Elasticsearch export methods. Access it through the hamburger menu (☰) in the top-left corner of the web interface.

## 📍 How to Access

1. **Start ForgedKismet** using your desktop shortcut or command line
2. **Open web browser** and navigate to `http://localhost:2501`
3. **Click the hamburger menu** (☰) in the top-left corner
4. **Select "Export"** from the menu

## 🚀 Export Methods Available

### Option 1: Real-Time WebSocket Export
**Best for:** Live monitoring, real-time dashboards, immediate data analysis

**Configuration Fields:**
- **Kismet Host**: Server hostname/IP (default: localhost)
- **Kismet Port**: WebSocket port (default: 2501)
- **Update Rate**: How often to fetch updates in seconds (default: 5)
- **Elasticsearch Hosts**: Your ES cluster URLs
- **ES Username/Password**: Authentication credentials
- **Index Prefix**: ES index naming prefix (default: kismet)
- **Offline Mode**: Store locally when ES unavailable

**Features:**
- ✅ Test Connection button
- ✅ Generate Command button
- ✅ Copy to clipboard functionality
- ✅ Real-time status monitoring

### Option 2: Filebeat Log Shipping
**Best for:** Reliable log shipping, automatic retry, production environments

**Configuration Fields:**
- **Elasticsearch URL**: Full ES cluster URL
- **ES Username/Password**: Authentication credentials
- **Device Name**: Source device identifier (default: dragon-os-box)
- **Log Directory**: Kismet log path (default: /opt/kismet/logs)

**Features:**
- ✅ Automatic Filebeat installation and configuration
- ✅ Multi-log type support (WiFi, Bluetooth, GPS, etc.)
- ✅ Automatic retry and error handling
- ✅ Production-ready reliability

### Option 3: Bulk Upload from Logs
**Best for:** Historical data import, one-time uploads, data migration

**Configuration Fields:**
- **Elasticsearch URL**: Full ES cluster URL
- **ES Username/Password**: Authentication credentials
- **Log Directory**: Directory with Kismet log files
- **Index Prefix**: ES index naming prefix (default: kismet)

**Features:**
- ✅ Process existing .kismetdb files
- ✅ Bulk upload for efficiency
- ✅ Historical data migration
- ✅ Progress monitoring

## 🔧 How to Use

### Step 1: Choose Your Export Method
Select the method that best fits your use case:
- **Real-time**: For live monitoring and dashboards
- **Filebeat**: For production log shipping
- **Bulk**: For historical data import

### Step 2: Configure Settings
Fill in the required fields for your chosen method:
- Elasticsearch connection details
- Authentication credentials
- Device/log directory paths

### Step 3: Test Connection
Click **"Test Connection"** to verify:
- Elasticsearch accessibility
- Authentication credentials
- Network connectivity

### Step 4: Generate Command
Click the appropriate button to generate the command:
- **"Generate Command"** (Real-time)
- **"Setup Filebeat"** (Filebeat)
- **"Generate Upload Command"** (Bulk)

### Step 5: Copy and Execute
1. **Copy the generated command** using the copy button
2. **Open a terminal** on your system
3. **Paste and run the command**
4. **Monitor the output** for success/error messages

## 📊 Status Monitoring

The **Export Status Monitor** section shows:
- Active export processes
- Connection health
- Data transfer rates
- Error notifications
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues:

**"Please configure valid Elasticsearch hosts"**
- Update the Elasticsearch URL field with your actual cluster address
- Ensure the URL includes protocol (https://) and port

**"Connection test failed"**
- Check if Elasticsearch is running and accessible
- Verify username/password credentials
- Check network connectivity and firewall settings

**"No items specified to show in contextMenu"**
- Refresh the web page and try again
- Check browser console for JavaScript errors

### Getting Help:

1. **Check the command output** for specific error messages
2. **Verify Elasticsearch is running**: `curl -u username:password https://your-elasticsearch:9200`
3. **Test Kismet connectivity**: Ensure the web interface loads properly
4. **Review log files** in `/opt/kismet/logs/` for detailed error information

## 🎉 Success Indicators

You'll know the export is working when you see:
- ✅ "Connection test successful" messages
- ✅ Generated commands without errors
- ✅ Data appearing in your Elasticsearch indices
- ✅ Status monitor showing active connections

## 📝 Example Workflows

### For Development/Testing:
1. Use **Real-Time Export** with offline mode enabled
2. Test with local Elasticsearch instance
3. Monitor real-time data flow

### For Production:
1. Use **Filebeat Integration** for reliability
2. Configure proper authentication
3. Set up monitoring and alerting

### For Data Migration:
1. Use **Bulk Upload** for existing logs
2. Process historical data first
3. Switch to real-time for ongoing data

## 🔗 Related Files

- **JavaScript**: `/kismet/http_data/js/kismet.ui.export.js`
- **CSS**: `/kismet/http_data/css/kismet.ui.export.css`
- **Export Scripts**: 
  - `/kismet/kismet_elasticsearch_export.py`
  - `/kismet/filebeat_integration.py`
  - `/forgedfate/kismet_bulk_upload.py`

The Export GUI provides a user-friendly interface to all the powerful export capabilities of ForgedFate, making it easy to get your wireless monitoring data into Elasticsearch for analysis and visualization!
