# Backend CLI Reference

The Stinercut backend provides a command-line interface for video processing operations.

## Usage

```bash
# Inside Docker container
docker-compose exec backend python3 cli.py <command> [options]

# Or enter container first
docker-compose exec backend bash
python3 cli.py <command> [options]
```

## Commands

### detect

Run video detection and analysis on a folder containing video files.

```bash
python3 cli.py detect <folder_path> [options]
```

**Arguments:**
- `folder_path` - Relative path to folder (e.g., `input/abc123`)

**Options:**
- `-v, --verbose` - Show detailed progress
- `-w, --workers <N>` - Number of parallel workers (default: 4)
- `-c, --coarse-interval <seconds>` - Coarse sampling interval (default: 10)
- `-f, --fine-interval <seconds>` - Fine sampling interval (default: 1)
- `--no-adaptive` - Disable adaptive sampling, sample every fine-interval

**Examples:**
```bash
# Basic detection
python3 cli.py detect input/abc123

# Verbose with 8 workers
python3 cli.py detect input/abc123 -v -w 8

# Custom sampling intervals
python3 cli.py detect input/abc123 -c 5 -f 0.5

# Disable adaptive sampling (slower but more accurate)
python3 cli.py detect input/abc123 --no-adaptive -f 0.5
```

---

### split

Split a video file at specified timestamps using keyframe-accurate cutting (no re-encoding).

```bash
python3 cli.py split <input_path> -t <timestamps...> [options]
```

**Arguments:**
- `input_path` - Relative path to video file (e.g., `input/abc123/video.mp4`)

**Options:**
- `-t, --timestamps <seconds...>` - Split points in seconds (required, multiple values)
- `-o, --output-dir <path>` - Output directory (default: same as input)
- `-v, --verbose` - Show detailed progress for each segment

**How it works:**
1. Analyzes the video to find all keyframe positions
2. For each requested timestamp, finds the nearest keyframe
3. Splits the video at keyframe boundaries using stream copy (lossless)
4. Creates N+1 output files for N timestamps

**Output naming:**
Files are named `{original}_part01.mp4`, `{original}_part02.mp4`, etc.

**Examples:**
```bash
# Split at 30 and 60 seconds (creates 3 files)
python3 cli.py split input/abc123/GH010042.MP4 -t 30 60

# Split at multiple points with custom output directory
python3 cli.py split input/abc123/GH010042.MP4 -t 30 60 90 120 -o output/splits

# Verbose mode to see each segment being created
python3 cli.py split input/abc123/GH010042.MP4 -t 30 60 -v
```

**Sample output:**
```
Splitting video: input/abc123/GH010042.MP4
Split points: [30.0, 60.0]
--------------------------------------------------
Analyzing keyframes...
Requested timestamps: [30.0, 60.0]
Snapped to keyframes: [29.96, 59.93]
--------------------------------------------------
Split complete: 3 segments created
  input/abc123/GH010042_part01.MP4 (29.96s, 45.2 MB)
  input/abc123/GH010042_part02.MP4 (29.97s, 44.8 MB)
  input/abc123/GH010042_part03.MP4 (120.07s, 180.1 MB)
--------------------------------------------------
Completed in 2.3 seconds
```

**Notes:**
- Timestamps are automatically snapped to the nearest keyframe
- If the nearest keyframe is more than 5 seconds away, a warning is displayed
- Splitting uses stream copy (no re-encoding), so it's very fast
- Output files maintain the same codec and quality as the source

---

### list

List import batches with optional status filter.

```bash
python3 cli.py list [options]
```

**Options:**
- `--status <status>` - Filter by status: `pending`, `analyzing`, `resolved`, `needs_manual`, `error`

**Examples:**
```bash
# List all recent batches
python3 cli.py list

# List only pending batches
python3 cli.py list --status pending

# List batches needing manual intervention
python3 cli.py list --status needs_manual
```

**Sample output:**
```
UUID                                 Status          Files      QRs   Falls
---------------------------------------------------------------------------
a1b2c3d4-e5f6-...                   resolved        5/5        2     2
f6e5d4c3-b2a1-...                   needs_manual    3/3        1     2
```

---

### slowmo

Convert a video to slow motion with source-matched encoding parameters.

```bash
python3 cli.py slowmo <input_path> [options]
```

**Arguments:**
- `input_path` - Relative path to video file (e.g., `input/abc123/video.mp4`)

**Options:**
- `-s, --speed <factor>` - Speed factor 0.1-1.0 (default: 0.5 = 2x slower)
- `-o, --output-dir <path>` - Output directory (default: same as input)
- `-v, --verbose` - Show detailed progress

**How it works:**
1. Analyzes source video encoding parameters (codec, bitrate, profile, level, fps)
2. Applies slow motion using FFmpeg `setpts` filter
3. Re-encodes with matched parameters for seamless joining with other clips
4. Removes audio from output

**Output naming:**
Files are named `{original}_slowmo_{factor}x.mp4`

**Examples:**
```bash
# Convert to 2x slower (0.5x speed)
python3 cli.py slowmo input/abc123/GH010042.MP4

# Convert to 4x slower (0.25x speed)
python3 cli.py slowmo input/abc123/GH010042.MP4 -s 0.25

# Custom output directory
python3 cli.py slowmo input/abc123/GH010042.MP4 -s 0.5 -o output/slowmo
```

**Sample output:**
```
Converting to slow motion: input/abc123/GH010042.MP4
Speed factor: 0.5x (2.0x slower)
--------------------------------------------------
Original duration: 10.00s
Output duration: 20.00s
Encoding (this may take a while)...
--------------------------------------------------
Conversion complete!
  Output: input/abc123/GH010042_slowmo_0.5x.MP4
  Duration: 20.00s
  Size: 45.2 MB
--------------------------------------------------
Completed in 35.2 seconds
```

**Notes:**
- Re-encoding is required (slower than split, but necessary for speed change)
- Output matches source encoding for seamless concat with other video parts
- Audio is removed from output
- Processing time depends on video length and resolution

---

## Exit Codes

- `0` - Success
- `1` - Error (check output for details)

## Environment

All paths are relative to `/videodata` inside the container. The CLI automatically resolves paths using this base directory.
