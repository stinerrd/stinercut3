## 1. Backend Service
- [ ] 1.1 Create `backend/services/transition_service.py`
- [ ] 1.2 Implement frame extraction (last frame of clip A, first frame of clip B)
- [ ] 1.3 Implement crossfade transition generation using FFmpeg blend filter
- [ ] 1.4 Implement slide transition generation (push left/right effect)
- [ ] 1.5 Generate transition video at correct resolution and codec

## 2. FFmpeg Operations
- [ ] 2.1 Extract frame: ffmpeg -i video.mp4 -vf "select=eq(n\,FRAME)" -vframes 1 frame.jpg
- [ ] 2.2 Crossfade: ffmpeg -loop 1 -i a.jpg -loop 1 -i b.jpg -filter_complex "blend=..."
- [ ] 2.3 Slide: ffmpeg with xfade filter for push effect
- [ ] 2.4 Match output to source video parameters

## 3. Integration with VideoProcessor
- [ ] 3.1 Add transition creation step to pipeline
- [ ] 3.2 Insert transition segments between clips during concatenation
- [ ] 3.3 Update concat list to include transition files
- [ ] 3.4 Cache transitions (reuse if same dimensions/codec)

## 4. Frontend UI
- [ ] 4.1 Add transition settings section to project page
- [ ] 4.2 Add transition type selector (none/crossfade/slide)
- [ ] 4.3 Add transition duration input (0.5-2 seconds)
- [ ] 4.4 Show preview thumbnails of transition effect

## 5. Verification
- [ ] 5.1 Test crossfade transition between 2 clips
- [ ] 5.2 Test slide transition between 2 clips
- [ ] 5.3 Test transitions with 5+ clips
- [ ] 5.4 Test transition with different resolutions
- [ ] 5.5 Test no transitions (direct concatenation)
