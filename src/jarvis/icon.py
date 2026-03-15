"""Generate Jarvis tray icons programmatically."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont


def _round_rect(draw: ImageDraw.ImageDraw, xy: tuple, radius: int, fill: str) -> None:
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def create_icon(state: str = "idle", size: int = 64) -> Image.Image:
    """Create a Jarvis tray icon.

    States: 'idle' (blue), 'recording' (red), 'transcribing' (amber).
    """
    colors = {
        "idle": ("#1a1a2e", "#00d4ff", "#0088aa"),
        "recording": ("#2e1a1a", "#ff4444", "#ff6666"),
        "transcribing": ("#2e2a1a", "#ffaa00", "#ffcc44"),
    }
    bg, primary, secondary = colors.get(state, colors["idle"])

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    padding = 2
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=bg,
        outline=primary,
        width=2,
    )

    center = size // 2

    if state == "recording":
        # Pulsing circle for recording
        r = size // 4
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=primary,
        )
    else:
        # "J" letter for Jarvis
        try:
            font = ImageFont.truetype("arial", size // 2)
        except OSError:
            font = ImageFont.load_default()

        draw.text(
            (center, center),
            "J",
            fill=primary,
            font=font,
            anchor="mm",
        )

    # Small dot indicator at bottom-right
    dot_r = size // 10
    dot_x = size - padding - dot_r - 4
    dot_y = size - padding - dot_r - 4
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=secondary,
    )

    return img
