# Change: Add Video Transitions

## Why
Professional video editing requires smooth transitions between clips. The original stinercut supports crossfade and slide transitions between video segments, creating a polished viewing experience.

## What Changes
- Implement TransitionService for generating transition segments
- Extract last frame of previous clip and first frame of next clip
- Generate crossfade transition video between frames
- Generate slide transition video (push effect)
- Insert transition segments during concatenation
- Add UI for transition type selection and duration

## Impact
- Affected specs: `transitions` (new capability)
- Affected code:
  - `backend/services/transition_service.py` - Transition generation
  - `backend/services/video_processor.py` - Insert transitions in pipeline
  - `frontend/templates/project/show.html.twig` - Transition settings UI
