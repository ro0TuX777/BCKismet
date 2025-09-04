2025-08-27 13:35:34,244 - INFO - 🚀 Starting Simple Kismet Upload...
2025-08-27 13:35:34,388 - INFO - ✅ Connection successful (403 expected for write-only user)
2025-08-27 13:35:34,389 - INFO - Searching for logs in: .
2025-08-27 13:35:34,391 - INFO - Searching for logs in: /home/bc_test/.kismet
2025-08-27 13:35:34,391 - INFO - Found 1 kismetdb files
2025-08-27 13:35:34,391 - INFO -   - Kismet-20250724-13-40-20-1.kismet
2025-08-27 13:35:34,391 - INFO - Processing kismetdb file: Kismet-20250724-13-40-20-1.kismet
2025-08-27 13:35:34,391 - INFO - Processing 8 tables from Kismet-20250724-13-40-20-1.kismet
2025-08-27 13:35:34,391 - INFO - Extracted 1 records from table KISMET
2025-08-27 13:35:34,394 - INFO - Extracted 100 records from table devices
2025-08-27 13:35:34,397 - INFO - Extracted 100 records from table packets
2025-08-27 13:35:34,397 - INFO - Extracted 1 records from table datasources
2025-08-27 13:35:34,398 - INFO - Extracted 3 records from table alerts
2025-08-27 13:35:34,399 - INFO - Extracted 100 records from table messages
2025-08-27 13:35:34,401 - INFO - Extracted 100 records from table snapshots
2025-08-27 13:35:34,401 - INFO - Attempting upload to: filebeat-7.17.0-2025.08.27-000001
2025-08-27 13:35:34,438 - WARNING - Upload failed: 403 - {"error":{"root_cause":[{"type":"security_exception","reason":"action [indices:admin/auto_create] is
2025-08-27 13:35:34,439 - WARNING - ❌ Single document test failed for filebeat-7.17.0-2025.08.27-000001
2025-08-27 13:35:34,439 - INFO - Attempting upload to: filebeat-2025.08.27
2025-08-27 13:35:34,478 - WARNING - Upload failed: 403 - {"error":{"root_cause":[{"type":"security_exception","reason":"action [indices:admin/auto_create] is
2025-08-27 13:35:34,480 - WARNING - ❌ Single document test failed for filebeat-2025.08.27
2025-08-27 13:35:34,480 - INFO - Attempting upload to: kismet-2025.08.27
2025-08-27 13:35:34,527 - WARNING - Upload failed: 403 - {"error":{"root_cause":[{"type":"security_exception","reason":"action [indices:admin/auto_create] is
2025-08-27 13:35:34,527 - WARNING - ❌ Single document test failed for kismet-2025.08.27
2025-08-27 13:35:34,528 - INFO - Attempting upload to: logstash-2025.08.27
2025-08-27 13:35:34,564 - WARNING - Upload failed: 403 - {"error":{"root_cause":[{"type":"security_exception","reason":"action [indices:admin/auto_create] is
2025-08-27 13:35:34,564 - WARNING - ❌ Single document test failed for logstash-2025.08.27
2025-08-27 13:35:34,565 - ERROR - Failed to upload to any index
2025-08-27 13:35:34,565 - INFO - 🎉 Upload complete!
2025-08-27 13:35:34,565 - INFO - Files processed: 1
2025-08-27 13:35:34,565 - INFO - Documents uploaded: 0
2025-08-27 13:35:34,565 - INFO - Errors: 1
2025-08-27 13:35:34,565 - INFO - Runtime: 0.3 seconds
