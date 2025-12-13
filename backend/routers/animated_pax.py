"""
WebSocket handler for animated PAX intro generation.
"""
from database import get_db
from services.animated_pax_service import AnimatedPaxService


async def handle_animated_pax_intro(data: dict, send_message) -> dict:
    """
    Handle video:animated_pax_intro WebSocket command.

    Args:
        data: Command data containing:
            - template_id: int - ID of splashscreen with animation config
            - pax_name: str - Passenger name
            - output_path: str - Output directory
            - duration: float (optional) - Override template duration
            - video_dimensions: dict (optional) - width, height, fps, codec
        send_message: Async function to send WebSocket messages

    Returns:
        Result dict with success status and output file path
    """
    template_id = data.get('template_id')
    pax_name = data.get('pax_name')
    output_path = data.get('output_path')
    duration = data.get('duration')
    video_dimensions = data.get('video_dimensions')

    # Validate required fields
    if not template_id:
        return {"success": False, "error": "template_id is required"}
    if not pax_name:
        return {"success": False, "error": "pax_name is required"}
    if not output_path:
        return {"success": False, "error": "output_path is required"}

    async def progress_callback(event_type: str, event_data: dict):
        """Send progress updates via WebSocket."""
        await send_message({
            "type": f"video:{event_type}",
            "data": event_data
        })

    # Get database session
    db = next(get_db())

    try:
        service = AnimatedPaxService(db)
        result = await service.create_animated_intro(
            template_id=template_id,
            pax_name=pax_name,
            output_path=output_path,
            duration=duration,
            video_dimensions=video_dimensions,
            progress_callback=progress_callback
        )
        return result
    finally:
        db.close()
