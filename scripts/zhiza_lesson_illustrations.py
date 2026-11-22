"""Small vector drawings for the жиза vocabulary handout."""

from math import cos, pi, sin

from reportlab.lib.colors import HexColor


INK = HexColor("#25201d")
PAPER = HexColor("#fff6df")
STEM = HexColor("#74884a")
PIT = HexColor("#b37a53")
HAIR = HexColor("#655047")


def path(canvas, points, fill=None):
    """Draw a path from coordinate pairs and cubic Bézier control points."""
    outline = canvas.beginPath()
    outline.moveTo(*points[0])
    for point in points[1:]:
        if len(point) == 2:
            outline.lineTo(*point)
        else:
            outline.curveTo(*point)
    if fill is not None:
        outline.close()
        canvas.setFillColor(fill)
    canvas.drawPath(outline, fill=fill is not None, stroke=1)


def mango(canvas, color):
    path(canvas, [
        (51, 77), (49, 84, 50, 90, 56, 95),
    ])
    path(canvas, [
        (53, 81), (64, 95, 78, 95, 90, 89),
        (80, 78, 66, 76, 53, 81),
    ], STEM)
    path(canvas, [
        (50, 81), (28, 88, 12, 70, 11, 47),
        (10, 27, 27, 12, 46, 10), (65, 8, 89, 22, 89, 42),
        (89, 53, 74, 53, 68, 64), (63, 74, 59, 78, 50, 81),
    ], color)
    path(canvas, [(23, 53), (25, 61, 29, 66, 33, 68)])


def avocado(canvas, color):
    points = [
        (48, 94), (35, 94, 31, 80, 26, 69),
        (20, 57, 10, 47, 11, 34), (12, 15, 31, 7, 49, 7),
        (72, 7, 89, 19, 89, 36), (89, 47, 80, 58, 74, 68),
        (66, 82, 62, 94, 48, 94),
    ]
    path(canvas, points, color)
    path(canvas, [
        (48, 83), (39, 83, 36, 71, 32, 63),
        (24, 49, 20, 43, 20, 34), (20, 20, 35, 16, 49, 16),
        (65, 16, 80, 23, 80, 36), (80, 45, 73, 55, 67, 64),
        (61, 76, 57, 83, 48, 83),
    ], color)
    canvas.setFillColor(PIT)
    canvas.ellipse(32, 24, 67, 59, fill=1, stroke=1)
    path(canvas, [(39, 41), (40, 47, 43, 50, 48, 52)])


def pen(canvas, color):
    canvas.saveState()
    canvas.translate(50, 50)
    canvas.rotate(-43)
    canvas.translate(-50, -50)
    canvas.setFillColor(color)
    canvas.roundRect(46, 85, 8, 11, 2, fill=1, stroke=1)
    path(canvas, [(42, 22), (47, 11), (53, 11), (58, 22)], PAPER)
    canvas.setFillColor(INK)
    canvas.roundRect(48, 5, 4, 6, 1, fill=1, stroke=0)
    canvas.setFillColor(color)
    canvas.roundRect(40, 21, 20, 67, 4, fill=1, stroke=1)
    canvas.line(41, 31, 59, 31)
    canvas.line(40, 70, 60, 70)
    path(canvas, [(56, 84), (65, 84), (65, 67), (65, 62, 63, 61, 60, 61)])
    canvas.restoreState()


def book(canvas, color):
    path(canvas, [
        (21, 23), (75, 16), (88, 22), (88, 75), (36, 81), (21, 74),
    ], color)
    path(canvas, [
        (24, 23), (76, 16), (84, 21), (84, 29), (32, 35), (24, 30),
    ], PAPER)
    path(canvas, [
        (20, 28), (17, 30, 16, 32, 16, 36), (16, 78),
        (16, 83, 19, 86, 24, 88), (88, 80), (88, 30), (76, 22),
    ], color)
    canvas.line(25, 31, 25, 84)
    path(canvas, [(41, 69), (71, 65), (71, 49), (41, 53)], PAPER)
    canvas.line(48, 61, 64, 59)


def notebook(canvas, color):
    canvas.setFillColor(PAPER)
    canvas.roundRect(25, 8, 56, 78, 5, fill=1, stroke=1)
    canvas.setFillColor(color)
    canvas.roundRect(22, 13, 56, 79, 5, fill=1, stroke=1)
    for y in (24, 38, 52, 66, 80):
        path(canvas, [(29, y + 3), (13, y + 9, 12, y - 5, 22, y - 5)])
    canvas.setFillColor(PAPER)
    canvas.roundRect(38, 55, 30, 18, 2, fill=1, stroke=1)
    canvas.line(44, 64, 62, 64)


def gum(canvas, color):
    canvas.saveState()
    canvas.translate(50, 50)
    canvas.rotate(-13)
    canvas.translate(-50, -50)
    canvas.setFillColor(PAPER)
    canvas.roundRect(59, 41, 35, 18, 4, fill=1, stroke=1)
    for x in (79, 85):
        canvas.line(x, 45, x, 55)
    path(canvas, [
        (8, 36), (16, 32), (23, 37), (31, 33), (72, 33),
        (77, 38), (77, 62), (72, 67), (31, 67), (23, 63),
        (16, 68), (8, 64),
    ], color)
    canvas.line(24, 37, 24, 63)
    path(canvas, [(35, 49), (41, 59), (50, 54), (59, 59), (67, 50)])
    canvas.restoreState()


def sun(canvas, color):
    canvas.setFillColor(color)
    for ray in range(8):
        angle = ray * pi / 4
        x, y = cos(angle), sin(angle)
        path(canvas, [
            (50 + 33 * x - 4 * y, 50 + 33 * y + 4 * x),
            (50 + 44 * x, 50 + 44 * y),
            (50 + 33 * x + 4 * y, 50 + 33 * y - 4 * x),
        ], color)
    canvas.circle(50, 50, 26, fill=1, stroke=1)


def head(canvas, color):
    path(canvas, [
        (35, 9), (38, 23, 35, 32, 27, 42), (16, 56, 21, 76, 34, 85),
        (47, 95, 69, 90, 77, 76), (82, 67, 77, 60, 86, 52),
        (92, 45, 81, 45, 80, 43), (78, 39, 82, 35, 77, 30),
        (75, 24, 72, 21, 63, 21), (55, 22, 56, 16, 60, 10),
    ], color)
    path(canvas, [
        (20, 57), (18, 76, 28, 91, 45, 94), (58, 97, 70, 90, 77, 77),
        (64, 80, 56, 74, 51, 65), (45, 65, 43, 53, 37, 54),
        (30, 56, 27, 50, 27, 42), (23, 46, 21, 50, 20, 57),
    ], HAIR)
    path(canvas, [(40, 52), (34, 54, 33, 43, 41, 42)])
    canvas.setFillColor(INK)
    canvas.circle(69, 60, 1.9, stroke=0, fill=1)


def hair(canvas, color):
    path(canvas, [
        (48, 93), (24, 94, 14, 78, 15, 60), (16, 42, 7, 27, 11, 16),
        (16, 8, 29, 13, 33, 9), (39, 18, 32, 34, 38, 44),
        (33, 51, 32, 59, 33, 68), (42, 67, 49, 72, 53, 79),
        (58, 69, 67, 64, 68, 53), (61, 40, 72, 34, 63, 13),
        (71, 19, 78, 1, 87, 13), (96, 25, 83, 41, 85, 57),
        (89, 81, 69, 98, 48, 93),
    ], color)
    path(canvas, [(42, 86), (22, 78, 27, 59, 24, 48), (21, 36, 16, 28, 20, 20)])
    path(canvas, [(61, 86), (77, 76, 79, 63, 75, 48), (73, 37, 83, 26, 80, 20)])


OBJECTS = {
    "mango": (mango, "#efae56"),
    "avocado": (avocado, "#adc369"),
    "pen": (pen, "#79bac6"),
    "book": (book, "#dc7a65"),
    "notebook": (notebook, "#8ca879"),
    "gum": (gum, "#e07da0"),
    "sun": (sun, "#f5ce5c"),
    "head": (head, "#edb498"),
    "hair": (hair, "#aa7150"),
}


def draw_object(canvas, key, center_x, center_y, size, color=None):
    """Draw one vocabulary object in a square of the requested point size."""
    draw, default = OBJECTS[key]
    canvas.saveState()
    canvas.translate(center_x - size / 2, center_y - size / 2)
    canvas.scale(size / 100, size / 100)
    canvas.setStrokeColor(INK)
    canvas.setLineWidth(2.6)
    canvas.setLineCap(1)
    canvas.setLineJoin(1)
    draw(canvas, HexColor(color or default))
    canvas.restoreState()
