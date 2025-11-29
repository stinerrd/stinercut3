## 1. Backend Service
- [ ] 1.1 Create `backend/services/intro_outro_service.py`
- [ ] 1.2 Implement intro video preparation (scale, pad, format)
- [ ] 1.3 Implement outro video preparation (scale, pad, format)
- [ ] 1.4 Handle aspect ratio differences with blur background
- [ ] 1.5 Match output codec and parameters to main video

## 2. Aspect Ratio Handling
- [ ] 2.1 Detect aspect ratio mismatch
- [ ] 2.2 Create blurred background from intro/outro content
- [ ] 2.3 Scale video to fit within target dimensions
- [ ] 2.4 Overlay scaled video on blurred background
- [ ] 2.5 Center video in frame

## 3. FFmpeg Operations
- [ ] 3.1 Split filter for background and foreground
- [ ] 3.2 Scale filter for fitting content
- [ ] 3.3 Boxblur filter for background effect
- [ ] 3.4 Overlay filter for centering content

## 4. Integration with VideoProcessor
- [ ] 4.1 Add intro preparation step (if intro enabled)
- [ ] 4.2 Add outro preparation step (if outro enabled)
- [ ] 4.3 Modify final concatenation: intro + main + outro
- [ ] 4.4 Handle case: only intro, only outro, both, neither

## 5. Frontend UI
- [ ] 5.1 Add intro/outro settings section
- [ ] 5.2 Add intro video selector (from assets)
- [ ] 5.3 Add outro video selector (from assets)
- [ ] 5.4 Add "Enable intro" checkbox
- [ ] 5.5 Add "Enable outro" checkbox
- [ ] 5.6 Show preview thumbnails of selected videos

## 6. Verification
- [ ] 6.1 Test intro prepending
- [ ] 6.2 Test outro appending
- [ ] 6.3 Test both intro and outro
- [ ] 6.4 Test aspect ratio handling (16:9 intro on 4:3 main)
- [ ] 6.5 Test without intro/outro (direct output)
