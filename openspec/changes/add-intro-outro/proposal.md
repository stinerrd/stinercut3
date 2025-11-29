# Change: Add Intro and Outro Videos

## Why
Professional videos need branded opening and closing sequences. The original stinercut supports prepending intro videos and appending outro videos, with intelligent scaling to handle different aspect ratios using blurred background fill.

## What Changes
- Implement IntroOutroService for video preparation
- Scale and pad intro/outro to match main video dimensions
- Handle aspect ratio mismatches with blur background effect
- Concatenate: intro + main content + outro
- Add UI for intro/outro selection

## Impact
- Affected specs: `intro-outro` (new capability)
- Affected code:
  - `backend/services/intro_outro_service.py` - Video preparation
  - `backend/services/video_processor.py` - Final concatenation step
  - `frontend/templates/project/show.html.twig` - Intro/outro settings UI
