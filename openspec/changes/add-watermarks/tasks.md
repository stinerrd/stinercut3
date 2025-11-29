## 1. Watermark Service
- [ ] 1.1 Create `backend/services/watermark_service.py`
- [ ] 1.2 Implement logo overlay using FFmpeg overlay filter
- [ ] 1.3 Support position options: top-left, top-right, bottom-left, bottom-right
- [ ] 1.4 Support opacity configuration
- [ ] 1.5 Support watermark scaling relative to video size
- [ ] 1.6 Handle PNG watermarks with transparency

## 2. PAX Screen Service
- [ ] 2.1 Create `backend/services/pax_screen_service.py`
- [ ] 2.2 Implement SVG template loading
- [ ] 2.3 Implement name substitution in SVG template
- [ ] 2.4 Convert SVG to video using FFmpeg
- [ ] 2.5 Support animated text effects
- [ ] 2.6 Generate PAX screen at output resolution

## 3. FFmpeg Operations
- [ ] 3.1 Watermark: overlay=x=(main_w-overlay_w-10):y=(main_h-overlay_h-10)
- [ ] 3.2 PAX screen: loop SVG frames, add fade in/out
- [ ] 3.3 Prepend PAX screen to main video

## 4. Integration with VideoProcessor
- [ ] 4.1 Add watermark step to pipeline (after concatenation)
- [ ] 4.2 Add PAX screen generation step (before concatenation)
- [ ] 4.3 Insert PAX screen at beginning of video

## 5. Frontend UI
- [ ] 5.1 Add watermark settings section
- [ ] 5.2 Add watermark selector (from assets)
- [ ] 5.3 Add position dropdown
- [ ] 5.4 Add opacity slider
- [ ] 5.5 Add PAX name input field
- [ ] 5.6 Add PAX template selector (from assets)
- [ ] 5.7 Add "Enable PAX welcome screen" checkbox

## 6. Verification
- [ ] 6.1 Test watermark overlay in all positions
- [ ] 6.2 Test watermark with transparency
- [ ] 6.3 Test PAX screen generation
- [ ] 6.4 Test PAX screen with different names
- [ ] 6.5 Test combined watermark + PAX screen
