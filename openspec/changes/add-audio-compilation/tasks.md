## 1. Backend Service
- [ ] 1.1 Create `backend/services/audio_compiler.py`
- [ ] 1.2 Implement audio extraction from video
- [ ] 1.3 Implement background music loading and preparation
- [ ] 1.4 Implement multi-track mixing with FFmpeg amerge/amix
- [ ] 1.5 Implement volume adjustment per track
- [ ] 1.6 Implement fade in/out effects
- [ ] 1.7 Implement audio sample rate conversion

## 2. Freefall Audio Handling
- [ ] 2.1 Implement freefall phase audio switching
- [ ] 2.2 Mix freefall-specific audio during detected freefall period
- [ ] 2.3 Implement crossfade between main and freefall audio
- [ ] 2.4 Sync audio timing with video duration

## 3. Audio Processing Features
- [ ] 3.1 Implement audio normalization
- [ ] 3.2 Implement ducking (lower music during speech)
- [ ] 3.3 Implement audio delay/sync adjustment
- [ ] 3.4 Support multiple audio formats (MP3, WAV, AAC)

## 4. Integration with VideoProcessor
- [ ] 4.1 Add audio compilation step to processing pipeline
- [ ] 4.2 Replace video audio with compiled mix
- [ ] 4.3 Handle videos with no audio track

## 5. Frontend UI
- [ ] 5.1 Add audio settings section to project page
- [ ] 5.2 Add background music selector (from assets)
- [ ] 5.3 Add freefall audio selector (from assets)
- [ ] 5.4 Add volume slider (0-100%)
- [ ] 5.5 Add fade in/out duration inputs
- [ ] 5.6 Add "Keep original audio" checkbox

## 6. Verification
- [ ] 6.1 Test audio mixing with background music
- [ ] 6.2 Test freefall audio switching
- [ ] 6.3 Test volume adjustment
- [ ] 6.4 Test fade effects
- [ ] 6.5 Test audio sync with video
