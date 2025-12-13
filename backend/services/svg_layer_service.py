"""
SVG Layer Extraction Service.

Extracts animation config and individual layer groups from animated SVG templates.
"""
import io
import json
import re
import subprocess
from typing import Optional
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

from schemas.animation_template import AnimationConfig, Layer, TextStyle


# Register SVG namespaces before parsing to avoid ns0 prefixes
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

# SVG namespace mapping
SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}


def _replace_dimensions(svg_content: str, width: int, height: int) -> str:
    """
    Replace dimension placeholders in SVG content.

    Args:
        svg_content: SVG string with [[[WIDTH]]] and [[[HEIGHT]]] placeholders
        width: Output width in pixels
        height: Output height in pixels

    Returns:
        SVG string with dimensions replaced
    """
    return svg_content.replace('[[[WIDTH]]]', str(width)).replace('[[[HEIGHT]]]', str(height))


def _clean_svg_namespaces(svg_str: str) -> str:
    """
    Clean SVG string by removing namespace prefixes and declarations.

    Removes:
    - xmlns declarations
    - ns0:, ns1:, ns2: etc prefixes on elements
    - Inkscape/Sodipodi specific namespaced attributes
    - Any attribute with namespace prefix (ns0:attr, ns1:attr, etc.)
    """
    # Remove namespace declarations
    svg_str = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', '', svg_str)
    # Remove ns0:, ns1: etc element prefixes
    svg_str = re.sub(r'<ns\d+:', '<', svg_str)
    svg_str = re.sub(r'</ns\d+:', '</', svg_str)
    # Remove ALL namespaced attributes (word:word="value" pattern)
    # This catches inkscape:, sodipodi:, ns0:, ns1:, ns2: etc.
    svg_str = re.sub(r'\s+\w+:\w+(?:-\w+)*="[^"]*"', '', svg_str)
    # Remove dc:, cc:, rdf: namespaced elements completely (metadata)
    svg_str = re.sub(r'<(?:dc|cc|rdf):[^>]*>.*?</(?:dc|cc|rdf):[^>]*>', '', svg_str, flags=re.DOTALL)
    svg_str = re.sub(r'<(?:dc|cc|rdf):[^/]*/?>', '', svg_str)
    # Remove metadata element
    svg_str = re.sub(r'<metadata[^>]*>.*?</metadata>', '', svg_str, flags=re.DOTALL)
    # Remove sodipodi:namedview
    svg_str = re.sub(r'<sodipodi:namedview[^>]*>.*?</sodipodi:namedview>', '', svg_str, flags=re.DOTALL)
    svg_str = re.sub(r'<sodipodi:namedview[^/]*/>', '', svg_str)
    return svg_str


def extract_animation_config(svg_content: str) -> Optional[AnimationConfig]:
    """
    Extract animation JSON from SVG <script> tag.

    Args:
        svg_content: Full SVG content string

    Returns:
        Parsed AnimationConfig or None if not found
    """
    pattern = r'<script[^>]*id="stinercut-animation"[^>]*>(.*?)</script>'
    match = re.search(pattern, svg_content, re.DOTALL)
    if match:
        try:
            config_dict = json.loads(match.group(1).strip())
            return AnimationConfig(**config_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid animation config in SVG: {e}")
    return None


def has_animation(svg_content: str) -> bool:
    """Check if SVG contains animation config."""
    return 'id="stinercut-animation"' in svg_content


def extract_svg_group(svg_content: str, group_id: str) -> str:
    """
    Extract a single <g> group from SVG by ID, preserving defs.

    Creates a standalone SVG containing only the specified group
    along with any necessary definitions (fonts, filters, gradients).

    Args:
        svg_content: Full SVG content string
        group_id: ID of the <g> element to extract

    Returns:
        Standalone SVG string containing only the specified group
    """
    # Parse the SVG
    # Remove script tag before parsing (contains JSON, not XML)
    svg_clean = re.sub(
        r'<script[^>]*id="stinercut-animation"[^>]*>.*?</script>',
        '',
        svg_content,
        flags=re.DOTALL
    )

    root = ET.fromstring(svg_clean)

    # Get SVG dimensions
    width = root.get('width', '1920')
    height = root.get('height', '1080')
    viewbox = root.get('viewBox', f'0 0 {width} {height}')

    # Find the target group
    target_group = root.find(f".//*[@id='{group_id}']")

    if target_group is None:
        raise ValueError(f"Group with id='{group_id}' not found in SVG")

    # Find defs section (contains fonts, filters, styles)
    defs = root.find('.//{http://www.w3.org/2000/svg}defs')
    if defs is None:
        defs = root.find('.//defs')

    # Build new SVG manually to avoid duplicate namespace issues
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="{viewbox}">'
    ]

    # Include defs if present
    if defs is not None:
        # Convert defs to string, removing any namespace prefixes
        defs_str = ET.tostring(defs, encoding='unicode')
        defs_str = _clean_svg_namespaces(defs_str)
        svg_parts.append(defs_str)

    # Include the target group
    group_str = ET.tostring(target_group, encoding='unicode')
    group_str = _clean_svg_namespaces(group_str)
    svg_parts.append(group_str)

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


def create_text_layer_svg(
    svg_content: str,
    text: str,
    style_class: str,
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    Create an SVG containing a text element with embedded font.

    Extracts the defs section (containing font and styles) from the template
    and creates a new SVG with just the text element at origin (0,0).

    Note: Text is positioned at origin within the SVG. FFmpeg overlay filter
    handles the actual positioning on the video frame.

    Args:
        svg_content: Original SVG template (contains font definitions)
        text: Text content to render
        style_class: CSS class name for styling (defined in template)
        width: SVG width
        height: SVG height

    Returns:
        SVG string with text element at origin
    """
    # Remove script tag before parsing
    svg_clean = re.sub(
        r'<script[^>]*id="stinercut-animation"[^>]*>.*?</script>',
        '',
        svg_content,
        flags=re.DOTALL
    )

    root = ET.fromstring(svg_clean)

    # Find defs section
    defs = root.find('.//{http://www.w3.org/2000/svg}defs')
    if defs is None:
        defs = root.find('.//defs')

    # Build new SVG with simple viewBox matching output dimensions
    # Text positioned at origin, FFmpeg handles actual positioning
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    ]

    # Include defs if present (extract just the style element for fonts)
    if defs is not None:
        defs_str = ET.tostring(defs, encoding='unicode')
        defs_str = _clean_svg_namespaces(defs_str)
        svg_parts.append(defs_str)

    # Escape text content for XML
    text_escaped = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Create text element at origin (0 + small offset for baseline)
    # Text y position is baseline, so use font-size as offset to make text visible
    svg_parts.append(f'<text x="0" y="100" class="{style_class}">{text_escaped}</text>')
    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


def svg_to_png_bytes(svg_string: str, width: int, height: int) -> bytes:
    """
    Convert SVG string to PNG bytes.

    Uses rsvg-convert for reliable rendering of complex SVGs with gradients.

    Args:
        svg_string: Complete SVG content
        width: Output width in pixels
        height: Output height in pixels

    Returns:
        PNG image as bytes
    """
    result = subprocess.run(
        ['rsvg-convert', '-w', str(width), '-h', str(height), '-f', 'png'],
        input=svg_string.encode('utf-8'),
        capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"rsvg-convert failed: {result.stderr.decode()}")
    return result.stdout


def render_text_to_png(
    text: str,
    text_style: TextStyle,
    width: int,
    height: int
) -> bytes:
    """
    Render text to PNG using Pillow with custom font.

    Args:
        text: Text content to render
        text_style: Text styling options (font, size, colors)
        width: Output width
        height: Output height

    Returns:
        PNG image as bytes with transparent background
    """
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load font
    if text_style.font_path:
        font = ImageFont.truetype(text_style.font_path, text_style.font_size)
    else:
        font = ImageFont.load_default()

    # Parse fill color
    fill = text_style.fill

    # Draw text at origin (FFmpeg overlay handles positioning)
    # Y offset by font size to account for baseline
    y_offset = int(text_style.font_size * 0.8)

    if text_style.stroke and text_style.stroke_width > 0:
        # Draw with stroke - Pillow's stroke can be memory intensive for large fonts
        # Use manual outline by drawing text multiple times
        stroke_color = text_style.stroke
        sw = text_style.stroke_width
        for dx in range(-sw, sw + 1):
            for dy in range(-sw, sw + 1):
                if dx != 0 or dy != 0:
                    draw.text((dx, y_offset + dy), text, font=font, fill=stroke_color)
        draw.text((0, y_offset), text, font=font, fill=fill)
    else:
        draw.text((0, y_offset), text, font=font, fill=fill)

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def render_layer_to_png(
    svg_content: str,
    layer: Layer,
    pax_name: str,
    width: int,
    height: int
) -> bytes:
    """
    Render a single layer to PNG.

    For group layers: extracts the SVG group and renders it.
    For text layers: renders text with Pillow using custom font.

    Args:
        svg_content: Full SVG template content
        layer: Layer definition
        pax_name: Passenger name for text substitution
        width: Output width
        height: Output height

    Returns:
        PNG image as bytes
    """
    if layer.type == 'text':
        # Text layer - render with Pillow for custom font support
        content = layer.content or ''
        content = content.replace('{{pax_name}}', pax_name)

        if layer.text_style:
            return render_text_to_png(content, layer.text_style, width, height)
        else:
            # Fallback to SVG text rendering (deprecated)
            svg_content = _replace_dimensions(svg_content, width, height)
            layer_svg = create_text_layer_svg(
                svg_content=svg_content,
                text=content,
                style_class=layer.style or '',
                width=width,
                height=height
            )
            return svg_to_png_bytes(layer_svg, width, height)

    elif layer.group_id:
        # Group layer - extract SVG group
        svg_content = _replace_dimensions(svg_content, width, height)
        layer_svg = extract_svg_group(svg_content, layer.group_id)
        return svg_to_png_bytes(layer_svg, width, height)

    else:
        raise ValueError(f"Layer '{layer.id}' has no group_id or type='text'")
