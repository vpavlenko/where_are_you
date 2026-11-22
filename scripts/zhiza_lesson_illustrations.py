"""Render the sourced SVG illustrations in the жиза practice sheets."""

from io import BytesIO
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor, black, linearlyInterpolatedColor, white
from svglib.svglib import svg2rlg


ART_DIR = Path(__file__).resolve().parents[1] / "handouts/zhiza-practice"
FLUENT_LICENSE = ART_DIR / "FLUENT-LICENSE.txt"

# Each entry gives the vocabulary colour followed by the original fills to tint.
# A negative amount darkens the exercise colour and a positive amount lightens it.
ARTWORK = {
    "mango": ("#efae56", {"#FFB02E": 0}),
    "avocado": ("#adc369", {"#C3EF3C": 0}),
    "pen": ("#59aabc", {"#0074BA": 0, "#F9C23C": 0.65}),
    "book": ("#dc7a65", {"fill:#333333": 0}),
    "notebook": ("#8ca879", {
        "#ffff00": 0,
        "#ffcc00": -0.18,
        "#ff6600": -0.24,
        "#d45500": -0.38,
        "#ff7f2a": -0.14,
    }),
    "gum": ("#e07da0", {
        "#4a8930": -0.24,
        "#67bf43": 0,
        "#7ba851": 0,
        "#9bd16a": 0.32,
        "#c83737": -0.24,
    }),
    "sun": ("#f5ce5c", {"#fef500": 0}),
    "head": ("#edb498", {"#fca": 0}),
    "hair": ("#aa7150", {"#7f3f00": 0}),
}


def draw_object(canvas, key, center_x, center_y, size, color=None):
    """Place one sourced vector in the requested square and apply its tint."""
    default, recipe = ARTWORK[key]
    base = HexColor(color or default)
    svg = (ART_DIR / f"{key}.svg").read_text(encoding="utf-8")
    for original, amount in recipe.items():
        tint = linearlyInterpolatedColor(base, black if amount < 0 else white, 0, 1, abs(amount))
        prefix, _, _ = original.partition("#")
        svg = svg.replace(original, f"{prefix}#{tint.hexval()[2:]}")
    drawing = svg2rlg(BytesIO(svg.encode("utf-8")))
    scale = 0.88 * size / max(drawing.width, drawing.height)
    canvas.saveState()
    canvas.translate(center_x - drawing.width * scale / 2, center_y - drawing.height * scale / 2)
    canvas.scale(scale, scale)
    renderPDF.draw(drawing, canvas, 0, 0)
    canvas.restoreState()
