# Change: Add Watermarks and Overlays

## Why
Professional videos need branding. The original stinercut supports logo watermark overlay and PAX (passenger) welcome screens with animated name display. These add a personalized, professional touch to skydiving videos.

## What Changes
- Implement WatermarkService for logo overlay
- Implement PaxScreenService for passenger name welcome screens
- Support SVG template rendering with name substitution
- Convert PAX screen to video segment
- Add watermark position configuration (corners)
- Add UI for watermark and PAX name settings

## Impact
- Affected specs: `overlays` (new capability)
- Affected code:
  - `backend/services/watermark_service.py` - Logo overlay
  - `backend/services/pax_screen_service.py` - PAX welcome screen
  - `backend/services/video_processor.py` - Integrate overlay step
  - `frontend/templates/project/show.html.twig` - Overlay settings UI
