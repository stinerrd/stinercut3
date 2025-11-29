## 1. Device List Component
- [ ] 1.1 Create device list template/partial
- [ ] 1.2 Display device mount path
- [ ] 1.3 Display media type (video/photo/multi/empty/none)
- [ ] 1.4 Display video file count
- [ ] 1.5 Display photo file count
- [ ] 1.6 Show "detected at" timestamp

## 2. Import Action
- [ ] 2.1 Add "Import" button for each device
- [ ] 2.2 Disable import button for empty/none devices
- [ ] 2.3 Link import button to import workflow (future feature)
- [ ] 2.4 Show loading state during import

## 3. WebSocket Connection
- [ ] 3.1 Create JavaScript WebSocket client
- [ ] 3.2 Connect to ws://backend/ws/devices on page load
- [ ] 3.3 Handle "device_added" messages - add device to list
- [ ] 3.4 Handle "device_removed" messages - remove device from list
- [ ] 3.5 Handle connection errors and reconnection

## 4. Initial Load
- [ ] 4.1 Fetch current devices from GET /api/devices on page load
- [ ] 4.2 Populate device list with existing devices
- [ ] 4.3 Show empty state when no devices connected

## 5. UI States
- [ ] 5.1 Show "No devices connected" when list is empty
- [ ] 5.2 Show device type icon (video camera, photo, etc.)
- [ ] 5.3 Highlight newly added devices briefly
- [ ] 5.4 Animate device removal

## 6. Styling
- [ ] 6.1 Style device list cards/rows
- [ ] 6.2 Style media type badges
- [ ] 6.3 Style import button
- [ ] 6.4 Ensure responsive design

## 7. Verification
- [ ] 7.1 Test device appears when USB inserted
- [ ] 7.2 Test device disappears when USB removed
- [ ] 7.3 Test page refresh loads existing devices
- [ ] 7.4 Test WebSocket reconnection after disconnect
