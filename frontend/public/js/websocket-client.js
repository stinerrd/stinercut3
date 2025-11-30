/**
 * WebSocket Event Client
 *
 * Provides a global WebSocket connection for bidirectional communication
 * with the backend hub. Supports event subscriptions, sending commands,
 * and automatic reconnection.
 *
 * Usage:
 *   // Subscribe to events
 *   window.App.ws.on('detector.status', function(data, message) {
 *       console.log('Detector status:', data);
 *   });
 *
 *   // Send commands
 *   window.App.ws.send('detector:enable');
 *   window.App.ws.send('detector:status', {}, 'detector');
 *
 *   // Unsubscribe
 *   window.App.ws.off('detector.status', handler);
 */
(function() {
    'use strict';

    var CLIENT_TYPE = 'frontend';
    var WS_URL = (window.App && window.App.websocketUrl) || 'ws://localhost:8002/ws';
    var RECONNECT_DELAY = 3000;

    var ws = null;
    var reconnectTimer = null;
    var handlers = {};
    var connectCallbacks = [];

    /**
     * Connect to WebSocket hub.
     */
    function connect() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            return;
        }

        var url = WS_URL + '?client_type=' + CLIENT_TYPE;

        try {
            ws = new WebSocket(url);
        } catch (e) {
            console.error('WebSocket connection failed:', e);
            scheduleReconnect();
            return;
        }

        ws.onopen = function() {
            console.log('WebSocket connected to', url);
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
                reconnectTimer = null;
            }
            // Fire connect callbacks
            connectCallbacks.forEach(function(cb) {
                try {
                    cb();
                } catch (e) {
                    console.error('WebSocket onConnect callback error:', e);
                }
            });
        };

        ws.onmessage = function(event) {
            var message;
            try {
                message = JSON.parse(event.data);
            } catch (e) {
                console.error('WebSocket: Invalid JSON received', e);
                return;
            }

            // Ignore messages from self
            if (message.sender === CLIENT_TYPE) {
                return;
            }

            console.log('WebSocket received:', message.command, message.data);

            // Dispatch to handlers by command
            var command = message.command;
            var eventHandlers = handlers[command] || [];

            eventHandlers.forEach(function(handler) {
                try {
                    handler(message.data, message);
                } catch (e) {
                    console.error('WebSocket handler error for', command, e);
                }
            });
        };

        ws.onclose = function(event) {
            console.log('WebSocket disconnected (code:', event.code + ')');
            ws = null;
            scheduleReconnect();
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            // onclose will be called after onerror
        };
    }

    /**
     * Schedule reconnection attempt.
     */
    function scheduleReconnect() {
        if (reconnectTimer) {
            return;
        }
        console.log('WebSocket reconnecting in', RECONNECT_DELAY / 1000, 'seconds...');
        reconnectTimer = setTimeout(function() {
            reconnectTimer = null;
            connect();
        }, RECONNECT_DELAY);
    }

    /**
     * Send a command to the WebSocket hub.
     *
     * @param {string} command - Command name (e.g., 'detector:enable')
     * @param {object} data - Optional command data
     * @param {string} target - Target client type (default: 'detector')
     * @returns {boolean} - True if sent successfully
     */
    function send(command, data, target) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket not connected, cannot send:', command);
            return false;
        }

        var message = {
            command: command,
            sender: CLIENT_TYPE,
            target: target || 'detector',
            data: data || {}
        };

        try {
            ws.send(JSON.stringify(message));
            console.log('WebSocket sent:', command, message.data);
            return true;
        } catch (e) {
            console.error('WebSocket send failed:', e);
            return false;
        }
    }

    /**
     * Subscribe to a command/event type.
     *
     * @param {string} command - Command name (e.g., 'detector.status')
     * @param {function} handler - Callback function(data, fullMessage)
     */
    function on(command, handler) {
        if (typeof handler !== 'function') {
            console.error('WebSocket.on: handler must be a function');
            return;
        }
        if (!handlers[command]) {
            handlers[command] = [];
        }
        handlers[command].push(handler);
    }

    /**
     * Unsubscribe from a command/event type.
     *
     * @param {string} command - Command name
     * @param {function} handler - Handler to remove
     */
    function off(command, handler) {
        if (!handlers[command]) {
            return;
        }
        var idx = handlers[command].indexOf(handler);
        if (idx > -1) {
            handlers[command].splice(idx, 1);
        }
    }

    /**
     * Register a callback to run when WebSocket connects.
     * If already connected, callback fires immediately.
     *
     * @param {function} callback - Function to call on connect
     */
    function onConnect(callback) {
        if (typeof callback !== 'function') {
            return;
        }
        connectCallbacks.push(callback);
        // If already connected, fire immediately
        if (ws && ws.readyState === WebSocket.OPEN) {
            try {
                callback();
            } catch (e) {
                console.error('WebSocket onConnect callback error:', e);
            }
        }
    }

    // Expose public API
    window.App = window.App || {};
    window.App.ws = {
        on: on,
        off: off,
        send: send,
        connect: connect,
        onConnect: onConnect
    };

    // Auto-connect on DOM ready
    document.addEventListener('DOMContentLoaded', connect);
})();
