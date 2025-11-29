## 1. Backend Service
- [ ] 1.1 Create `backend/services/freefall_detector.py`
- [ ] 1.2 Implement audio extraction with bandpass filter (800-1500 Hz)
- [ ] 1.3 Integrate audiowaveform tool for waveform JSON generation
- [ ] 1.4 Implement waveform smoothing algorithm (10 iterations)
- [ ] 1.5 Implement peak detection above noise threshold
- [ ] 1.6 Implement continuous segment detection
- [ ] 1.7 Calculate confidence score based on segment characteristics

## 2. Detection Algorithm
- [ ] 2.1 Port detection logic from original ffdetector.py
- [ ] 2.2 Calculate noise threshold from waveform data
- [ ] 2.3 Find segments with sustained high amplitude
- [ ] 2.4 Validate freefall duration (typically 25-50 seconds)
- [ ] 2.5 Return start_time, end_time, duration, confidence

## 3. Backend API
- [ ] 3.1 Add POST /api/projects/{id}/detect-freefall endpoint
- [ ] 3.2 Return JSON: {start, end, duration, confidence}
- [ ] 3.3 Store detected times in project settings

## 4. Frontend UI
- [ ] 4.1 Add "Detect Freefall" button to project page
- [ ] 4.2 Display detected timecodes
- [ ] 4.3 Add manual adjustment inputs for start/end times
- [ ] 4.4 Show confidence indicator
- [ ] 4.5 Add "Apply" button to save manual adjustments

## 5. Verification
- [ ] 5.1 Test detection on real skydiving video
- [ ] 5.2 Test detection accuracy (compare to manual identification)
- [ ] 5.3 Test with video without freefall (should return low confidence)
- [ ] 5.4 Test manual override functionality
