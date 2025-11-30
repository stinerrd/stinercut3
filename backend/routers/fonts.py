"""
Font conversion API endpoints.

Converts TTF/OTF fonts to SVG path definitions for use in splashscreens.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import tempfile
import os

router = APIRouter(prefix="/api/fonts", tags=["fonts"])

TARGET_HEIGHT = 60  # Match existing fonts (~60px height)
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ÖÄÜöäüß"

# Mapping for special characters to valid SVG IDs
# Umlauts and special chars can't be used directly in XML IDs
CHAR_TO_ID = {
    'Ö': 'Ouml',
    'Ä': 'Auml',
    'Ü': 'Uuml',
    'ö': 'ouml',
    'ä': 'auml',
    'ü': 'uuml',
    'ß': 'szlig',
}


@router.post("/convert")
async def convert_ttf_to_svg(file: UploadFile = File(...)):
    """
    Convert TTF/OTF font to SVG path definitions.

    Accepts a font file and returns SVG path elements with IDs like _A, _B, etc.
    The paths include transform attributes to scale and flip Y-axis for proper
    SVG rendering.

    Returns:
        JSON with success status, font_name, svg_paths string, and glyph_count
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.ttf', '.otf']:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Must be TTF or OTF"
        )

    # Read file contents
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=413,
            detail="File too large (max 10MB)"
        )

    # Save to temp file (fontTools needs file path)
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        font = TTFont(tmp_path)
        glyph_set = font.getGlyphSet()
        cmap = font.getBestCmap()

        if not cmap:
            raise HTTPException(
                status_code=400,
                detail="Font has no character mapping table"
            )

        # Get font metrics for scaling
        units_per_em = font['head'].unitsPerEm
        ascent = font['OS/2'].sTypoAscender if 'OS/2' in font else font['hhea'].ascent
        scale = TARGET_HEIGHT / units_per_em

        paths = []
        for char in CHARSET:
            code = ord(char)
            if code not in cmap:
                continue

            glyph_name = cmap[code]
            if glyph_name not in glyph_set:
                continue

            glyph = glyph_set[glyph_name]

            # Extract path using SVGPathPen
            pen = SVGPathPen(glyph_set)
            glyph.draw(pen)
            path_data = pen.getCommands()

            if path_data:
                # Transform: translate then scale with Y flip
                # SVG transforms apply right-to-left:
                # 1. scale(s, -s): scales and flips Y
                # 2. translate(0, ascent*scale): moves glyph into view
                scaled_ascent = ascent * scale
                transform = f"translate(0, {scaled_ascent:.2f}) scale({scale:.4f}, -{scale:.4f})"
                # Use mapped ID for special characters (umlauts, etc.)
                char_id = CHAR_TO_ID.get(char, char)
                paths.append(f'<path id="_{char_id}" d="{path_data}" transform="{transform}" />')

        font.close()

        if not paths:
            raise HTTPException(
                status_code=400,
                detail="No glyphs found for characters A-Z, a-z, 0-9"
            )

        return {
            "success": True,
            "font_name": os.path.splitext(file.filename)[0],
            "svg_paths": "\n".join(sorted(paths)),
            "glyph_count": len(paths)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Font conversion failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
