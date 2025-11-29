# Change: Add Audio Compilation

## Why
Professional skydiving videos need background music with intelligent mixing. The original stinercut has sophisticated audio compilation: mixing background music with original audio, special music during freefall phase, volume adjustments, and fade effects.

## What Changes
- Port audiocompiler.py to Python service
- Implement multi-track audio mixing (background + original + freefall)
- Implement volume adjustment and normalization
- Implement fade in/out effects
- Implement freefall-aware audio switching
- Add UI for audio configuration (track selection, volume, fades)

## Impact
- Affected specs: `audio-processing` (new capability)
- Affected code:
  - `backend/services/audio_compiler.py` - Audio mixing service
  - `backend/services/video_processor.py` - Integrate audio step
  - `frontend/templates/project/show.html.twig` - Audio settings UI
