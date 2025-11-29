# Change: Add Freefall Detection

## Why
Tandem skydiving videos have distinct audio signatures during freefall (loud wind noise in 800-1500 Hz range). The original stinercut uses audio analysis to automatically detect freefall start/end times, enabling automatic audio mixing where freefall gets special music treatment.

## What Changes
- Port ffdetector.py algorithm to Python service
- Extract audio from video with bandpass filter (800-1500 Hz)
- Use audiowaveform tool to generate waveform data
- Analyze peaks to detect freefall phase
- Return start/end timecodes with confidence score
- Add API endpoint for freefall detection
- Add frontend UI to trigger detection and display/adjust results

## Impact
- Affected specs: `freefall-detection` (new capability)
- Affected code:
  - `backend/services/freefall_detector.py` - Detection algorithm
  - `backend/routers/projects.py` - Detection endpoint
  - `frontend/templates/project/show.html.twig` - Detection UI
