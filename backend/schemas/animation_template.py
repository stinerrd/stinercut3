"""
Pydantic schemas for animated PAX screen templates.

Animation config is embedded in SVG <script type="application/json" id="stinercut-animation">
"""
from typing import Optional
from pydantic import BaseModel, Field


class Keyframe(BaseModel):
    """Single keyframe in an animation."""
    time: float = Field(..., ge=0, description="Time in seconds")
    value: float = Field(..., description="Value at this keyframe")


class Animation(BaseModel):
    """Animation definition for a single property."""
    property: str = Field(..., description="Property to animate: x, y, opacity")
    keyframes: list[Keyframe] = Field(..., min_length=2)
    easing: str = Field(default="linear", description="Easing function: linear, ease-in, ease-out, ease-in-out")


class LayerInitial(BaseModel):
    """Initial state of a layer."""
    x: float = Field(default=0, description="Initial X position")
    y: float = Field(default=0, description="Initial Y position")
    opacity: float = Field(default=1.0, ge=0, le=1, description="Initial opacity")


class TextStyle(BaseModel):
    """Text styling options for text layers."""
    font_path: Optional[str] = Field(default=None, description="Path to TTF/OTF font file")
    font_size: int = Field(default=100, description="Font size in pixels")
    fill: str = Field(default="white", description="Text fill color")
    stroke: Optional[str] = Field(default=None, description="Stroke color (outline)")
    stroke_width: int = Field(default=0, description="Stroke width in pixels")


class Layer(BaseModel):
    """A single animatable layer in the template."""
    id: str = Field(..., description="Unique layer identifier")
    group_id: Optional[str] = Field(default=None, description="SVG <g> element ID to extract")
    type: Optional[str] = Field(default=None, description="Layer type: 'text' for dynamic text layers")
    content: Optional[str] = Field(default=None, description="Text content, supports {{pax_name}} placeholder")
    style: Optional[str] = Field(default=None, description="CSS class name for text styling (deprecated)")
    text_style: Optional[TextStyle] = Field(default=None, description="Text styling options")
    initial: LayerInitial = Field(default_factory=LayerInitial)
    animations: list[Animation] = Field(default_factory=list)


class AnimationConfig(BaseModel):
    """Root animation configuration embedded in SVG."""
    version: str = Field(default="1.0")
    name: Optional[str] = Field(default=None, description="Template name")
    duration: float = Field(..., gt=0, description="Total animation duration in seconds")
    layers: list[Layer] = Field(..., min_length=1)
