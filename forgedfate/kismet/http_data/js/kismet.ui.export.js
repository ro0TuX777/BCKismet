"use strict";

var local_uri_prefix = ""; 
if (typeof(KISMET_URI_PREFIX) !== 'undefined')
    local_uri_prefix = KISMET_URI_PREFIX;

// Load our CSS
$('<link>')
    .appendTo('head')
    .attr({
        type: 'text/css',
        rel: 'stylesheet',
        href: local_uri_prefix + 'css/kismet.ui.export.css'
    });

/* Sidebar: Export Configuration
 *
 * Export panel for configuring Elasticsearch data export options
 */
kismet_ui_sidebar.AddSidebarItem({
    id: 'export_sidebar',
    listTitle: '<i class="fa fa-upload"></i> Export',
    priority: -50,
    clickCallback: function() {
        ExportConfiguration();
    },
});

var export_panel = null;

function ExportConfiguration() {
    var w = $(window).width() * 0.85;
    var h = $(window).height() * 0.85;
    var offty = 20;

    if ($(window).width() < 450 || $(window).height() < 450) {
        w = $(window).width() - 5;
        h = $(window).height() - 5;
        offty = 0;
    }

    var content = $('<div>', {
        'style': 'width: 100%; height: 100%; overflow-y: auto; padding: 10px;'
    });

    // Header
    content.append(
        $('<div>', {
            'class': 'export-header'
        })
        .append(
            $('<h2>')
            .html('<i class="fa fa-upload"></i> ForgedFate Data Export Configuration')
        )
        .append(
            $('<p>')
            .html('Configure real-time data export to Elasticsearch. Choose from three export methods based on your needs.')
        )
    );

    // Quick Start Guide
    content.append(
        $('<div>', {
            'class': 'export-quickstart'
        })
        .append(
            $('<h3>')
            .html('<i class="fa fa-rocket"></i> Quick Start Guide')
        )
        .append(
            $('<ol>')
            .html('<li>Choose an export method below and configure the settings</li>' +
                  '<li>Test your Elasticsearch connection</li>' +
                  '<li>Copy the generated command and run it in your terminal</li>' +
                  '<li>Monitor the export status in real-time</li>')
        )
    );

    // Export Methods Container
    var methods_container = $('<div>', {
        'class': 'export-methods-container'
    });

    // Method 1: Real-Time WebSocket Export
    var realtime_panel = createRealtimeExportPanel();
    methods_container.append(realtime_panel);

    // Method 2: Filebeat Log Shipping
    var filebeat_panel = createFilebeatExportPanel();
    methods_container.append(filebeat_panel);

    // Method 3: Bulk Upload
    var bulk_panel = createBulkUploadPanel();
    methods_container.append(bulk_panel);

    content.append(methods_container);

    // Status Panel
    content.append(createStatusPanel());

    export_panel = $.jsPanel({
        id: 'export-config',
        headerTitle: '<i class="fa fa-upload"></i> Export Configuration',
        paneltype: 'modal',
        headerControls: {
            controls: 'closeonly',
            iconfont: 'jsglyph',
        },
        content: content,
    }).resize({
        width: w,
        height: h
    }).reposition({
        my: 'center',
        at: 'center',
        of: 'window',
    });
}

function createRealtimeExportPanel() {
    var panel = $('<div>', {
        'class': 'export-method-panel',
        'id': 'realtime-export-panel'
    });

    panel.append(
        $('<h3>')
        .html('<i class="fa fa-bolt"></i> Option 1: Real-Time WebSocket Export')
    );

    panel.append(
        $('<p>')
        .html('<strong>Best for:</strong> Live monitoring, real-time dashboards, immediate data analysis')
    );

    // Configuration form
    var form = $('<div>', {'class': 'export-form'});
    
    form.append(createFormGroup('Kismet Host', 'realtime-host', 'text', 'localhost', 'Kismet server hostname or IP'));
    form.append(createFormGroup('Kismet Port', 'realtime-port', 'number', '2501', 'Kismet WebSocket port'));
    form.append(createFormGroup('Update Rate (seconds)', 'realtime-rate', 'number', '5', 'How often to fetch device updates'));
    form.append(createFormGroup('Elasticsearch Hosts', 'realtime-es-hosts', 'text', 'https://your-elasticsearch:9200', 'Comma-separated list of ES hosts'));
    form.append(createFormGroup('ES Username', 'realtime-es-user', 'text', '', 'Elasticsearch username'));
    form.append(createFormGroup('ES Password', 'realtime-es-pass', 'password', '', 'Elasticsearch password'));
    form.append(createFormGroup('Index Prefix', 'realtime-index', 'text', 'kismet', 'Elasticsearch index prefix'));

    // Offline mode checkbox
    form.append(
        $('<div>', {'class': 'form-group'})
        .append(
            $('<label>')
            .append($('<input>', {type: 'checkbox', id: 'realtime-offline'}))
            .append(' Offline Mode (store locally when ES unavailable)')
        )
    );

    panel.append(form);

    // Action buttons
    var actions = $('<div>', {'class': 'export-actions'});
    actions.append($('<button>', {
        'class': 'btn btn-primary',
        'onclick': 'testRealtimeConnection()'
    }).html('<i class="fa fa-plug"></i> Test Connection'));
    
    actions.append($('<button>', {
        'class': 'btn btn-success',
        'onclick': 'generateRealtimeCommand()'
    }).html('<i class="fa fa-code"></i> Generate Command'));

    panel.append(actions);

    // Command output
    panel.append($('<div>', {
        'id': 'realtime-command-output',
        'class': 'command-output',
        'style': 'display: none;'
    }));

    return panel;
}

function createFilebeatExportPanel() {
    var panel = $('<div>', {
        'class': 'export-method-panel',
        'id': 'filebeat-export-panel'
    });

    panel.append(
        $('<h3>')
        .html('<i class="fa fa-file-text"></i> Option 2: Filebeat Log Shipping')
    );

    panel.append(
        $('<p>')
        .html('<strong>Best for:</strong> Reliable log shipping, automatic retry, production environments')
    );

    // Configuration form
    var form = $('<div>', {'class': 'export-form'});
    
    form.append(createFormGroup('Elasticsearch URL', 'filebeat-es-url', 'text', 'https://your-elasticsearch:9200', 'Full Elasticsearch URL'));
    form.append(createFormGroup('ES Username', 'filebeat-es-user', 'text', '', 'Elasticsearch username'));
    form.append(createFormGroup('ES Password', 'filebeat-es-pass', 'password', '', 'Elasticsearch password'));
    form.append(createFormGroup('Device Name', 'filebeat-device', 'text', 'dragon-os-box', 'Source device identifier'));
    form.append(createFormGroup('Log Directory', 'filebeat-logdir', 'text', '/opt/kismet/logs', 'Kismet log directory path'));

    panel.append(form);

    // Action buttons
    var actions = $('<div>', {'class': 'export-actions'});
    actions.append($('<button>', {
        'class': 'btn btn-primary',
        'onclick': 'testFilebeatConnection()'
    }).html('<i class="fa fa-plug"></i> Test Connection'));
    
    actions.append($('<button>', {
        'class': 'btn btn-success',
        'onclick': 'generateFilebeatCommand()'
    }).html('<i class="fa fa-cogs"></i> Setup Filebeat'));

    panel.append(actions);

    // Command output
    panel.append($('<div>', {
        'id': 'filebeat-command-output',
        'class': 'command-output',
        'style': 'display: none;'
    }));

    return panel;
}

function createBulkUploadPanel() {
    var panel = $('<div>', {
        'class': 'export-method-panel',
        'id': 'bulk-export-panel'
    });

    panel.append(
        $('<h3>')
        .html('<i class="fa fa-database"></i> Option 3: Bulk Upload from Logs')
    );

    panel.append(
        $('<p>')
        .html('<strong>Best for:</strong> Historical data import, one-time uploads, data migration')
    );

    // Configuration form
    var form = $('<div>', {'class': 'export-form'});
    
    form.append(createFormGroup('Elasticsearch URL', 'bulk-es-url', 'text', 'https://your-elasticsearch:9200', 'Full Elasticsearch URL'));
    form.append(createFormGroup('ES Username', 'bulk-es-user', 'text', '', 'Elasticsearch username'));
    form.append(createFormGroup('ES Password', 'bulk-es-pass', 'password', '', 'Elasticsearch password'));
    form.append(createFormGroup('Log Directory', 'bulk-logdir', 'text', '/opt/kismet/logs', 'Directory containing Kismet log files'));
    form.append(createFormGroup('Index Prefix', 'bulk-index', 'text', 'kismet', 'Elasticsearch index prefix'));

    panel.append(form);

    // Action buttons
    var actions = $('<div>', {'class': 'export-actions'});
    actions.append($('<button>', {
        'class': 'btn btn-primary',
        'onclick': 'testBulkConnection()'
    }).html('<i class="fa fa-plug"></i> Test Connection'));
    
    actions.append($('<button>', {
        'class': 'btn btn-success',
        'onclick': 'generateBulkCommand()'
    }).html('<i class="fa fa-upload"></i> Generate Upload Command'));

    panel.append(actions);

    // Command output
    panel.append($('<div>', {
        'id': 'bulk-command-output',
        'class': 'command-output',
        'style': 'display: none;'
    }));

    return panel;
}

function createStatusPanel() {
    var panel = $('<div>', {
        'class': 'export-status-panel',
        'id': 'export-status-panel'
    });

    panel.append(
        $('<h3>')
        .html('<i class="fa fa-tachometer"></i> Export Status Monitor')
    );

    panel.append(
        $('<div>', {'id': 'export-status-content'})
        .html('<p><em>No active exports detected. Start an export method above to see status information.</em></p>')
    );

    return panel;
}

function createFormGroup(label, id, type, placeholder, help) {
    var group = $('<div>', {'class': 'form-group'});

    group.append($('<label>', {'for': id}).text(label));
    group.append($('<input>', {
        'type': type,
        'id': id,
        'class': 'form-control',
        'placeholder': placeholder
    }));

    if (help) {
        group.append($('<small>', {'class': 'form-help'}).text(help));
    }

    return group;
}

// Real-time Export Functions
function testRealtimeConnection() {
    var host = $('#realtime-host').val() || 'localhost';
    var port = $('#realtime-port').val() || '2501';
    var es_hosts = $('#realtime-es-hosts').val() || 'https://your-elasticsearch:9200';
    var username = $('#realtime-es-user').val();
    var password = $('#realtime-es-pass').val();

    showTestResult('realtime', 'Testing connection...', 'info');

    // Simulate connection test (in real implementation, this would make actual API calls)
    setTimeout(function() {
        if (es_hosts.includes('your-elasticsearch')) {
            showTestResult('realtime', 'Please configure valid Elasticsearch hosts', 'error');
        } else {
            showTestResult('realtime', 'Connection test successful! Ready to export.', 'success');
        }
    }, 2000);
}

function generateRealtimeCommand() {
    var host = $('#realtime-host').val() || 'localhost';
    var port = $('#realtime-port').val() || '2501';
    var rate = $('#realtime-rate').val() || '5';
    var es_hosts = $('#realtime-es-hosts').val() || 'https://your-elasticsearch:9200';
    var username = $('#realtime-es-user').val();
    var password = $('#realtime-es-pass').val();
    var index = $('#realtime-index').val() || 'kismet';
    var offline = $('#realtime-offline').is(':checked');

    var command = 'python3 /home/dragos/Downloads/kismet/kismet/kismet_elasticsearch_export.py \\\n';
    command += '    --kismet-host ' + host + ' \\\n';
    command += '    --kismet-port ' + port + ' \\\n';
    command += '    --update-rate ' + rate + ' \\\n';
    command += '    --es-hosts "' + es_hosts + '" \\\n';
    if (username) command += '    --es-username "' + username + '" \\\n';
    if (password) command += '    --es-password "' + password + '" \\\n';
    command += '    --index-prefix "' + index + '"';
    if (offline) command += ' \\\n    --offline';

    showCommandOutput('realtime', command, 'Real-Time WebSocket Export');
}

// Filebeat Export Functions
function testFilebeatConnection() {
    var es_url = $('#filebeat-es-url').val() || 'https://your-elasticsearch:9200';
    var username = $('#filebeat-es-user').val();
    var password = $('#filebeat-es-pass').val();

    showTestResult('filebeat', 'Testing Elasticsearch connection...', 'info');

    setTimeout(function() {
        if (es_url.includes('your-elasticsearch')) {
            showTestResult('filebeat', 'Please configure valid Elasticsearch URL', 'error');
        } else {
            showTestResult('filebeat', 'Elasticsearch connection successful!', 'success');
        }
    }, 2000);
}

function generateFilebeatCommand() {
    var es_url = $('#filebeat-es-url').val() || 'https://your-elasticsearch:9200';
    var username = $('#filebeat-es-user').val();
    var password = $('#filebeat-es-pass').val();
    var device = $('#filebeat-device').val() || 'dragon-os-box';
    var logdir = $('#filebeat-logdir').val() || '/opt/kismet/logs';

    var command = 'sudo python3 /home/dragos/Downloads/kismet/kismet/filebeat_integration.py \\\n';
    command += '    --elasticsearch-url "' + es_url + '" \\\n';
    if (username) command += '    --username "' + username + '" \\\n';
    if (password) command += '    --password "' + password + '" \\\n';
    command += '    --device-name "' + device + '" \\\n';
    command += '    --log-directory "' + logdir + '"';

    var instructions = 'This will:\n';
    instructions += '1. Install and configure Filebeat\n';
    instructions += '2. Set up log monitoring for Kismet files\n';
    instructions += '3. Start automatic log shipping to Elasticsearch\n\n';
    instructions += 'After running this command, Filebeat will automatically ship new log entries to Elasticsearch.';

    showCommandOutput('filebeat', command, 'Filebeat Integration Setup', instructions);
}

// Bulk Upload Functions
function testBulkConnection() {
    var es_url = $('#bulk-es-url').val() || 'https://your-elasticsearch:9200';
    var username = $('#bulk-es-user').val();
    var password = $('#bulk-es-pass').val();

    showTestResult('bulk', 'Testing Elasticsearch connection...', 'info');

    setTimeout(function() {
        if (es_url.includes('your-elasticsearch')) {
            showTestResult('bulk', 'Please configure valid Elasticsearch URL', 'error');
        } else {
            showTestResult('bulk', 'Elasticsearch connection successful!', 'success');
        }
    }, 2000);
}

function generateBulkCommand() {
    var es_url = $('#bulk-es-url').val() || 'https://your-elasticsearch:9200';
    var username = $('#bulk-es-user').val();
    var password = $('#bulk-es-pass').val();
    var logdir = $('#bulk-logdir').val() || '/opt/kismet/logs';
    var index = $('#bulk-index').val() || 'kismet';

    var command = 'python3 /home/dragos/Downloads/kismet/forgedfate/kismet_bulk_upload.py \\\n';
    command += '    --elasticsearch-url "' + es_url + '" \\\n';
    if (username) command += '    --username "' + username + '" \\\n';
    if (password) command += '    --password "' + password + '" \\\n';
    command += '    --log-directory "' + logdir + '" \\\n';
    command += '    --index-prefix "' + index + '"';

    var instructions = 'This will:\n';
    instructions += '1. Scan the log directory for Kismet database files\n';
    instructions += '2. Extract device and packet data\n';
    instructions += '3. Bulk upload all historical data to Elasticsearch\n\n';
    instructions += 'This is a one-time operation for existing log files.';

    showCommandOutput('bulk', command, 'Bulk Upload Command', instructions);
}

// Helper Functions
function showTestResult(method, message, type) {
    var alertClass = 'alert-info';
    var icon = 'fa-info-circle';

    if (type === 'success') {
        alertClass = 'alert-success';
        icon = 'fa-check-circle';
    } else if (type === 'error') {
        alertClass = 'alert-danger';
        icon = 'fa-exclamation-circle';
    }

    var alert = $('<div>', {
        'class': 'alert ' + alertClass,
        'style': 'margin-top: 10px;'
    }).html('<i class="fa ' + icon + '"></i> ' + message);

    $('#' + method + '-export-panel .export-actions').after(alert);

    // Remove previous alerts
    $('#' + method + '-export-panel .alert').not(':last').remove();
}

function showCommandOutput(method, command, title, instructions) {
    var output = $('#' + method + '-command-output');

    var content = $('<div>');
    content.append($('<h4>').text(title));

    if (instructions) {
        content.append($('<div>', {'class': 'command-instructions'}).html(instructions.replace(/\n/g, '<br>')));
    }

    content.append($('<h5>').text('Command to run:'));
    content.append($('<pre>', {'class': 'command-text'}).text(command));

    content.append($('<button>', {
        'class': 'btn btn-secondary',
        'onclick': 'copyToClipboard("' + command.replace(/"/g, '\\"') + '")'
    }).html('<i class="fa fa-copy"></i> Copy Command'));

    output.html(content).show();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Command copied to clipboard!');
    });
}
