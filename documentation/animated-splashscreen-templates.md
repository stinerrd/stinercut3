# Animated Splashscreen Templates

This guide explains how to create SVG templates with embedded animation configuration for generating animated PAX welcome screen videos.

## Overview

Animated splashscreen templates are SVG files with an embedded JSON configuration that defines:
- Layer extraction from SVG groups
- Text layers with custom fonts
- Keyframe animations (position, opacity)
- Easing functions

The system renders each layer to PNG, then uses FFmpeg to composite them with animations.

## SVG Template Structure

### Basic Requirements

1. **SVG with groups**: Organize visual elements into `<g>` elements with unique IDs
2. **Dimension placeholders**: Use `[[[WIDTH]]]` and `[[[HEIGHT]]]` for dynamic resolution
3. **Animation config**: Embed JSON in a `<script>` tag with `id="stinercut-animation"`

### Example SVG Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="[[[WIDTH]]]px" height="[[[HEIGHT]]]px"
     viewBox="0 0 1920 1080">

  <defs>
    <!-- Gradients, filters, styles -->
  </defs>

  <!-- Background layer -->
  <g id="background">
    <rect width="100%" height="100%" fill="#1a1a2e"/>
    <!-- Background elements -->
  </g>

  <!-- Animated elements -->
  <g id="plane">
    <!-- Plane graphic -->
  </g>

  <g id="skydiver">
    <!-- Skydiver graphic -->
  </g>

  <!-- Animation configuration -->
  <script type="application/json" id="stinercut-animation">
  {
    "version": "1.0",
    "name": "My Animated Template",
    "duration": 6.0,
    "layers": [...]
  }
  </script>
</svg>
```

## Animation Configuration

### Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `version` | string | No | Config version (default: "1.0") |
| `name` | string | No | Template name for display |
| `duration` | float | Yes | Total animation duration in seconds |
| `layers` | array | Yes | List of layer definitions |

### Layer Definition

Each layer represents either an SVG group or a text element.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique layer identifier |
| `group_id` | string | No* | SVG `<g>` element ID to extract |
| `type` | string | No* | Set to `"text"` for text layers |
| `content` | string | No | Text content (supports `{{pax_name}}`) |
| `text_style` | object | No | Font and styling for text layers |
| `initial` | object | No | Initial position and opacity |
| `animations` | array | No | List of property animations |

*Either `group_id` or `type="text"` is required.

### Initial State

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `x` | float | 0 | Initial X position (pixels) |
| `y` | float | 0 | Initial Y position (pixels) |
| `opacity` | float | 1.0 | Initial opacity (0.0 - 1.0) |

### Text Style (for text layers)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `font_path` | string | null | Path to TTF/OTF font file |
| `font_size` | int | 100 | Font size in pixels |
| `fill` | string | "white" | Text fill color |
| `stroke` | string | null | Stroke/outline color |
| `stroke_width` | int | 0 | Stroke width in pixels |

### Animation Definition

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `property` | string | Yes | Property to animate: `x`, `y`, `opacity` |
| `keyframes` | array | Yes | List of keyframes (min 2) |
| `easing` | string | No | Easing function (default: "linear") |

### Keyframe

| Property | Type | Description |
|----------|------|-------------|
| `time` | float | Time in seconds |
| `value` | float | Value at this keyframe |

### Easing Functions

- `linear` - Constant speed
- `ease-in` - Start slow, end fast
- `ease-out` - Start fast, end slow
- `ease-in-out` - Start and end slow

## Complete Example

```json
{
  "version": "1.0",
  "name": "Skydiver Welcome",
  "duration": 6.0,
  "layers": [
    {
      "id": "background",
      "group_id": "background",
      "initial": { "x": 0, "y": 0, "opacity": 1.0 },
      "animations": []
    },
    {
      "id": "plane",
      "group_id": "plane",
      "initial": { "x": -400, "y": 0, "opacity": 1.0 },
      "animations": [
        {
          "property": "x",
          "keyframes": [
            { "time": 0.0, "value": -400 },
            { "time": 3.0, "value": 0 }
          ],
          "easing": "ease-out"
        }
      ]
    },
    {
      "id": "skydiver",
      "group_id": "skydiver_group",
      "initial": { "x": 0, "y": -400, "opacity": 0 },
      "animations": [
        {
          "property": "y",
          "keyframes": [
            { "time": 1.0, "value": -400 },
            { "time": 3.5, "value": 0 }
          ],
          "easing": "ease-out"
        },
        {
          "property": "opacity",
          "keyframes": [
            { "time": 1.0, "value": 0 },
            { "time": 1.5, "value": 1 }
          ],
          "easing": "linear"
        }
      ]
    },
    {
      "id": "pax_name",
      "type": "text",
      "content": "{{pax_name}}",
      "text_style": {
        "font_path": "/videodata/fonts/my-font.ttf",
        "font_size": 120,
        "fill": "white",
        "stroke": "#333333",
        "stroke_width": 2
      },
      "initial": { "x": 80, "y": 700, "opacity": 0 },
      "animations": [
        {
          "property": "opacity",
          "keyframes": [
            { "time": 3.0, "value": 0 },
            { "time": 4.0, "value": 1 }
          ],
          "easing": "linear"
        }
      ]
    },
    {
      "id": "subtitle",
      "type": "text",
      "content": "in the sky",
      "text_style": {
        "font_path": "/videodata/fonts/my-font.ttf",
        "font_size": 70,
        "fill": "white",
        "stroke": "#333333",
        "stroke_width": 1
      },
      "initial": { "x": 80, "y": 820, "opacity": 0 },
      "animations": [
        {
          "property": "opacity",
          "keyframes": [
            { "time": 4.0, "value": 0 },
            { "time": 5.0, "value": 1 }
          ],
          "easing": "linear"
        }
      ]
    }
  ]
}
```

## Layer Ordering

Layers are rendered in array order (first = bottom, last = top). Plan your layer order:

1. Background (static, bottom)
2. Animated graphics (middle)
3. Text overlays (top)

## Animation Tips

### Fade In Effect
```json
{
  "property": "opacity",
  "keyframes": [
    { "time": 2.0, "value": 0 },
    { "time": 3.0, "value": 1 }
  ]
}
```

### Slide In from Left
```json
{
  "initial": { "x": -500 },
  "animations": [{
    "property": "x",
    "keyframes": [
      { "time": 0, "value": -500 },
      { "time": 2.0, "value": 0 }
    ],
    "easing": "ease-out"
  }]
}
```

### Slide In from Top
```json
{
  "initial": { "y": -300 },
  "animations": [{
    "property": "y",
    "keyframes": [
      { "time": 1.0, "value": -300 },
      { "time": 3.0, "value": 0 }
    ],
    "easing": "ease-out"
  }]
}
```

### Delayed Appearance
Start animation at a later time by setting the first keyframe time > 0:
```json
{
  "property": "opacity",
  "keyframes": [
    { "time": 3.0, "value": 0 },
    { "time": 4.0, "value": 1 }
  ]
}
```

## Using Custom Fonts

1. Place TTF/OTF font files in `/videodata/fonts/`
2. Reference the font path in `text_style.font_path`
3. Fonts are loaded dynamically - no container restart needed

```json
{
  "type": "text",
  "content": "{{pax_name}}",
  "text_style": {
    "font_path": "/videodata/fonts/CustomFont.ttf",
    "font_size": 100,
    "fill": "white"
  }
}
```

## Creating from Inkscape

1. Create your design in Inkscape
2. Organize elements into groups (Object > Group)
3. Name groups via Object Properties (right-click > Object Properties)
4. Save as Plain SVG
5. Add dimension placeholders: replace `width="..."` and `height="..."` with `[[[WIDTH]]]px` and `[[[HEIGHT]]]px`
6. Add the `<script id="stinercut-animation">` block before `</svg>`
7. Store in database via splashscreen management

## API Usage

### CLI
```bash
python -m cli animated-pax-intro \
  --template-id 30 \
  --name "Max Mustermann" \
  --output /videodata/output/my-video
```

### WebSocket
```json
{
  "command": "video:animated_pax_intro",
  "target": "backend",
  "data": {
    "template_id": 30,
    "pax_name": "Max Mustermann",
    "output_path": "/videodata/output/my-video",
    "duration": 6.0,
    "video_dimensions": {
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "codec": "libx264"
    }
  }
}
```

## Troubleshooting

### Text not appearing
- Check `text_style.font_path` points to valid font file
- Verify `initial.opacity` is > 0 or has fade-in animation
- Check position is within frame bounds

### Group not found
- Verify `group_id` matches SVG `<g id="...">` exactly
- Check for namespace prefixes (remove `inkscape:` prefixes)

### Animation not smooth
- Increase video FPS (default 30)
- Use appropriate easing function
- Ensure keyframe times are spaced adequately

### Wrong resolution
- Use `[[[WIDTH]]]` and `[[[HEIGHT]]]` placeholders in SVG
- Pass correct dimensions via `video_dimensions`
