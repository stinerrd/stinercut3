"""
Animated PAX Screen Service.

Creates animated PAX welcome screen videos using FFmpeg overlay filters
for high-performance rendering with minimal I/O.
"""
import asyncio
import os
import tempfile
from typing import Any, Callable, Optional

import ffmpeg
from sqlalchemy.orm import Session

from models.splashscreen import Splashscreen
from schemas.animation_template import AnimationConfig, Animation, Layer
from services.svg_layer_service import (
    extract_animation_config,
    render_layer_to_png,
)


class AnimatedPaxService:
    """Service for creating animated PAX screen intro videos."""

    def __init__(self, db: Session):
        self.db = db

    def _interpolate_keyframes(
        self,
        animations: list[Animation],
        prop: str,
        initial_value: float,
        duration: float
    ) -> str:
        """
        Generate FFmpeg expression from keyframes for a property.

        Args:
            animations: List of animations for this layer
            prop: Property name to interpolate (x, y, opacity)
            initial_value: Initial value if no animation defined
            duration: Total animation duration

        Returns:
            FFmpeg expression string
        """
        # Find animation for this property
        anim = None
        for a in animations:
            if a.property == prop:
                anim = a
                break

        if anim is None or len(anim.keyframes) < 2:
            return str(initial_value)

        keyframes = sorted(anim.keyframes, key=lambda k: k.time)
        easing = anim.easing or 'linear'

        # Build nested if expressions for each segment
        # FFmpeg expression: if(lt(t, time1), expr1, if(lt(t, time2), expr2, ...))
        segments = []

        for i in range(len(keyframes) - 1):
            start_kf = keyframes[i]
            end_kf = keyframes[i + 1]

            start_time = start_kf.time
            end_time = end_kf.time
            start_val = start_kf.value
            end_val = end_kf.value
            seg_duration = end_time - start_time

            if seg_duration <= 0:
                continue

            # Normalized time within segment: (t - start_time) / seg_duration
            t_norm = f"((t-{start_time})/{seg_duration})"

            # Apply easing
            if easing == 'ease-out':
                # ease-out: 1 - (1 - t)^2
                progress = f"(1-pow(1-{t_norm},2))"
            elif easing == 'ease-in':
                # ease-in: t^2
                progress = f"pow({t_norm},2)"
            elif easing == 'ease-in-out':
                # ease-in-out: t < 0.5 ? 2*t^2 : 1 - (-2*t+2)^2/2
                progress = f"if(lt({t_norm},0.5),2*pow({t_norm},2),1-pow(-2*{t_norm}+2,2)/2)"
            else:
                # linear
                progress = t_norm

            # Interpolated value: start + (end - start) * progress
            value_expr = f"({start_val}+({end_val}-{start_val})*{progress})"

            segments.append((end_time, value_expr))

        if not segments:
            return str(initial_value)

        # Build nested expression from end to start
        # Start with final value (after last keyframe)
        result = str(keyframes[-1].value)

        for i in range(len(segments) - 1, -1, -1):
            end_time, value_expr = segments[i]
            start_time = keyframes[i].time if i < len(keyframes) else 0

            if i == 0:
                # First segment: check if t >= start_time
                result = f"if(lt(t,{start_time}),{keyframes[0].value},if(lt(t,{end_time}),{value_expr},{result}))"
            else:
                # Middle segments
                result = f"if(lt(t,{end_time}),{value_expr},{result})"

        return result

    def _apply_layer_filters(
        self,
        stream: ffmpeg.nodes.FilterableStream,
        layer: Layer,
        duration: float
    ) -> ffmpeg.nodes.FilterableStream:
        """
        Apply opacity filters (fade in/out) to a layer stream.

        Args:
            stream: FFmpeg input stream for the layer
            layer: Layer definition with animations
            duration: Total animation duration

        Returns:
            Filtered stream with opacity effects applied
        """
        # Find opacity animation
        opacity_anim = None
        for anim in layer.animations:
            if anim.property == 'opacity':
                opacity_anim = anim
                break

        if opacity_anim and len(opacity_anim.keyframes) >= 2:
            kfs = sorted(opacity_anim.keyframes, key=lambda k: k.time)

            # Apply format=rgba first for alpha channel support
            stream = stream.filter('format', 'rgba')

            # Check for fade in (0 -> 1)
            if kfs[0].value < kfs[1].value:
                start_time = kfs[0].time
                fade_duration = kfs[1].time - kfs[0].time
                if fade_duration > 0:
                    stream = stream.filter(
                        'fade', t='in', st=start_time, d=fade_duration, alpha=1
                    )

            # Check for fade out (1 -> 0) in remaining keyframes
            if len(kfs) > 2 and kfs[-2].value > kfs[-1].value:
                start_time = kfs[-2].time
                fade_duration = kfs[-1].time - kfs[-2].time
                if fade_duration > 0:
                    stream = stream.filter(
                        'fade', t='out', st=start_time, d=fade_duration, alpha=1
                    )

        return stream

    def _build_filter_graph(
        self,
        input_streams: list[ffmpeg.nodes.FilterableStream],
        layers: list[Layer],
        duration: float
    ) -> ffmpeg.nodes.FilterableStream:
        """
        Build FFmpeg filter graph using ffmpeg-python.

        Args:
            input_streams: List of input streams (one per layer PNG)
            layers: List of layer definitions with animations
            duration: Total animation duration

        Returns:
            Final composed output stream
        """
        # Start with background layer (first input)
        output = input_streams[0]

        # Overlay each subsequent layer
        for i, layer in enumerate(layers[1:], start=1):
            layer_stream = input_streams[i]

            # Apply opacity filters to layer
            layer_stream = self._apply_layer_filters(layer_stream, layer, duration)

            # Get position expressions
            x_expr = self._interpolate_keyframes(
                layer.animations, 'x', layer.initial.x, duration
            )
            y_expr = self._interpolate_keyframes(
                layer.animations, 'y', layer.initial.y, duration
            )

            # Overlay this layer onto the current output
            output = ffmpeg.overlay(
                output, layer_stream,
                x=x_expr, y=y_expr, format='auto'
            )

        return output

    async def create_animated_intro(
        self,
        template_id: int,
        pax_name: str,
        output_path: str,
        duration: Optional[float] = None,
        video_dimensions: Optional[dict] = None,
        progress_callback: Optional[Callable[[str, dict], Any]] = None
    ) -> dict:
        """
        Create animated PAX screen intro video.

        Args:
            template_id: ID of splashscreen with embedded animation config
            pax_name: Passenger name for text substitution
            output_path: Output directory path
            duration: Override duration from template (optional)
            video_dimensions: Dict with width, height, fps, codec
            progress_callback: Async callback for progress updates

        Returns:
            dict with success, output_file, etc.
        """
        # Default dimensions
        if video_dimensions is None:
            video_dimensions = {}

        width = video_dimensions.get('width', 1920)
        height = video_dimensions.get('height', 1080)
        fps = video_dimensions.get('fps', 30)
        codec = video_dimensions.get('codec', 'libx264')

        async def report_progress(event_type: str, data: dict = None):
            if progress_callback:
                await progress_callback(event_type, data or {})

        try:
            await report_progress("animated_pax_intro_started", {
                "pax_name": pax_name,
                "template_id": template_id,
                "output_path": output_path
            })

            # Fetch template from database
            template = self.db.query(Splashscreen).filter(
                Splashscreen.id == template_id
            ).first()

            if not template:
                return {
                    "success": False,
                    "error": f"Template not found: {template_id}"
                }

            # Extract animation config from SVG
            config = extract_animation_config(template.svg_content)

            if not config:
                return {
                    "success": False,
                    "error": f"No animation config found in template {template_id}"
                }

            # Use provided duration or template duration
            final_duration = duration if duration is not None else config.duration

            await report_progress("parsed_config", {
                "template_name": template.name,
                "animation_name": config.name,
                "duration": final_duration,
                "layer_count": len(config.layers)
            })

            # Render each layer to PNG
            layer_pngs = []
            total_layers = len(config.layers)

            for i, layer in enumerate(config.layers):
                await report_progress("rendering_layer", {
                    "layer_id": layer.id,
                    "progress": (i + 1) / total_layers
                })

                png_bytes = await asyncio.to_thread(
                    render_layer_to_png,
                    template.svg_content,
                    layer,
                    pax_name,
                    width,
                    height
                )
                layer_pngs.append(png_bytes)

            await report_progress("building_filter", {
                "layer_count": len(layer_pngs)
            })

            # Generate video using FFmpeg
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write layer PNGs to temp files
                input_files = []
                for i, png_bytes in enumerate(layer_pngs):
                    png_path = os.path.join(tmpdir, f"layer_{i:02d}.png")
                    with open(png_path, 'wb') as f:
                        f.write(png_bytes)
                    os.chmod(png_path, 0o644)
                    input_files.append(png_path)

                # Ensure output directory exists
                os.makedirs(output_path, exist_ok=True)
                output_file = os.path.join(output_path, "animated_pax_screen.mp4")

                await report_progress("encoding_video", {
                    "output_file": output_file
                })

                # Create input streams (loop each PNG for duration)
                input_streams = [
                    ffmpeg.input(png_path, loop=1, t=final_duration)
                    for png_path in input_files
                ]

                # Build filter graph
                output_stream = self._build_filter_graph(
                    input_streams, config.layers, final_duration
                )

                # Configure output with encoding options
                output_stream = ffmpeg.output(
                    output_stream,
                    output_file,
                    vcodec=codec,
                    pix_fmt='yuv420p',
                    r=fps,
                    t=final_duration
                )

                # Run FFmpeg (overwrite output)
                try:
                    await asyncio.to_thread(
                        ffmpeg.run,
                        output_stream,
                        overwrite_output=True,
                        capture_stderr=True
                    )
                except ffmpeg.Error as e:
                    error_msg = e.stderr.decode() if e.stderr else str(e)
                    return {
                        "success": False,
                        "error": f"FFmpeg failed: {error_msg}"
                    }

            # Set file permissions
            os.chmod(output_file, 0o644)

            await report_progress("animated_pax_intro_completed", {
                "output_file": output_file,
                "pax_name": pax_name,
                "duration": final_duration
            })

            return {
                "success": True,
                "output_file": output_file,
                "pax_name": pax_name,
                "duration": final_duration
            }

        except Exception as e:
            await report_progress("animated_pax_intro_error", {"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }
