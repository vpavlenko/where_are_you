"""Build the unnumbered A5 practice sheets for жиза.

Install ReportLab and uharfbuzz before running this script.
"""

from collections import Counter
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, shapeStr
from reportlab.pdfgen.canvas import Canvas

from zhiza_lesson_illustrations import draw_object

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "handouts/fonts"
OUTPUT = ROOT / "output/pdf/zhiza-practice-a5.pdf"
W, H = A5
MARGIN = 34
WIDTH = W - 2 * MARGIN
INK = "#151515"
BLUE = "#00658a"
GREEN = "#397020"
FAINT = "#d7dadd"
SONG_URL = "https://www.youtube.com/watch?v=t-QCaEA_N6k"

COLOURS = {
    "red": "#ee524e",
    "yellow": "#f6cc43",
    "green": "#75bd50",
}
PHONICS = (
    ("па пи пы пэ пе", "pa pyi pы pe pye"),
    ("са си сы сэ се", "sa si sы se sye"),
    ("та ти ты тэ те", "ta tsi tы te tsye"),
    ("ма ми мы мэ ме", "ma mi mы me mye"),
)
COLOUR_WORDS = (
    ("red", "кра́сный", "krásni"),
    ("yellow", "жёлтый", "жólti"),
    ("green", "зелёный", "zilyóni"),
)
KNOWN_WORDS = (
    ("mango", "ма́нго", None),
    ("avocado", "авока́до", None),
    ("pen", "ру́чка", None),
    ("book", "кни́га", None),
)
NEW_WORDS = (
    ("notebook", "тетра́дь", "tsitrát’"),
    ("gum", "жва́чка", "жvácka"),
    ("sun", "со́лнце", "sóntse"),
    ("head", "голова́", "galavá"),
    ("hair", "во́лосы", "vólasы"),
)
EXERCISE = (
    (("pen", "green"), ("gum", "red"), ("mango", "yellow"), ("notebook", "green")),
    (("gum", "yellow"), ("mango", "green"), ("book", "red"), ("sun", "yellow")),
    (("head", "red"), ("book", "yellow"), ("avocado", "green"), ("sun", "red")),
    (("hair", "green"), ("mango", "red"), ("notebook", "yellow"), ("book", "green")),
    (("avocado", "yellow"), ("gum", "green"), ("pen", "red"), ("hair", "yellow")),
    (("notebook", "red"), ("pen", "yellow"), ("head", "green"), ("hair", "red")),
)
CHORUS = (
    ("Жва́чка на за́втрак,", "Жvácka na záftrak,", "Chewing gum for breakfast,"),
    ("Ко́ла на у́жин.", "Kóla na úжыn.", "Cola for dinner."),
    ("Я так уста́ла,", "Ya tak ustála,", "I’m so tired."),
    ("Ты мне не ну́жен.", "Tы mnye nye núжыn.", "I don’t need you."),
)
GLOSSES = (
    ("жва́чка", "chewing gum"),
    ("на", "for (here)"),
    ("за́втрак", "breakfast"),
    ("ко́ла", "cola"),
    ("у́жин", "dinner"),
    ("я", "I"),
    ("так", "so"),
    ("уста́ла", "got tired (fem.)"),
    ("ты", "you (sing.)"),
    ("мне", "to me"),
    ("не", "not"),
    ("ну́жен", "needed (masc.)"),
)


def write(c, value, x, top, size, font="Sans", colour=INK, centered=False):
    c.setFont(font, size)
    c.setFillColor(HexColor(colour))
    if "\u0301" in value:
        # The fonts use mark positioning to place Cyrillic stress above a vowel.
        value = shapeStr(value, font, size)
        if centered:
            x -= pdfmetrics.stringWidth(value, font, size) / 2
        c.drawString(x, H - top, value)
        return
    draw = c.drawCentredString if centered else c.drawString
    draw(x, H - top, value)


def rule(c, top, left=MARGIN, right=W - MARGIN):
    c.setStrokeColor(HexColor(FAINT))
    c.setLineWidth(0.55)
    c.line(left, H - top, right, H - top)


def heading(c, value, top=65, size=30):
    write(c, value, MARGIN, top, size, "Display")


def picture(c, key, x, top, size, colour=None):
    draw_object(c, key, x, H - top, size, COLOURS.get(colour))


def phonics_row(c, russian, cue, top):
    for index, (syllable, sound) in enumerate(zip(russian.split(), cue.split(), strict=True)):
        x = MARGIN + (index + 0.5) * WIDTH / 5
        write(c, syllable, x, top, 17, "Bold", centered=True)
        write(c, sound, x, top + 13, 10, colour=BLUE, centered=True)


def vocabulary_row(c, words, top, size):
    for index, (key, russian, cue) in enumerate(words):
        x = MARGIN + (index + 0.5) * WIDTH / len(words)
        picture(c, key, x, top, size)
        write(c, russian, x, top + size / 2 + 13, 11, "Bold", centered=True)
        if cue:
            write(c, cue, x, top + size / 2 + 27, 10, colour=BLUE, centered=True)


def phonics_and_review(c):
    heading(c, "Phonics", 57, 27)
    for index, (russian, cue) in enumerate(PHONICS):
        phonics_row(c, russian, cue, 86 + index * 33)
    write(c, "Say with other consonants", MARGIN, 222, 11)
    phonics_row(c, "жа жо жу же жи", "жa жo жu же жы", 252)
    write(c, "жи sounds like жы.", MARGIN, 283, 10, colour=BLUE)

    heading(c, "Review", 325, 27)
    write(c, "Colors", MARGIN, 348, 11, "Bold")
    for index, (colour, russian, cue) in enumerate(COLOUR_WORDS):
        x = MARGIN + index * WIDTH / 3
        c.setFillColor(HexColor(COLOURS[colour]))
        c.circle(x + 7, H - 369, 7, stroke=0, fill=1)
        write(c, russian, x + 21, 370, 12, "Bold")
        write(c, cue, x + 21, 385, 10, colour=BLUE)

    write(c, "Objects", MARGIN, 412, 11, "Bold")
    vocabulary_row(c, KNOWN_WORDS, 437, 35)
    write(c, "Но́вые слова́", MARGIN, 496, 11, "Bold")
    vocabulary_row(c, NEW_WORDS, 520, 34)


def colour_exercise(c):
    heading(c, "Упражнение", 60, 27)
    write(c, "Say the color and the object.", MARGIN, 86, 12)
    for row_index, row in enumerate(EXERCISE):
        top = 132 + row_index * 78
        for column_index, (key, colour) in enumerate(row):
            x = MARGIN + (column_index + 0.5) * WIDTH / 4
            picture(c, key, x, top, 54, colour)
        if row_index < len(EXERCISE) - 1:
            rule(c, top + 39)


def where(c):
    heading(c, "Где?", 74, 42)
    write(c, "gdzye?", MARGIN + 153, 60, 14, "Bold", BLUE)
    write(c, "Where?", MARGIN + 153, 77, 12)

    write(c, "Где жёлтая кни́га?", MARGIN, 123, 18, "Bold")
    write(c, "Вверху́.", MARGIN + 229, 123, 16, "Bold", GREEN)
    write(c, "А где кра́сная ру́чка?", MARGIN, 155, 18, "Bold")
    write(c, "Внизу́.", MARGIN + 229, 155, 16, "Bold", GREEN)

    rows = (
        ("вверху́", "at the top", (("book", "yellow"), ("gum", "red"), ("sun", "red"))),
        ("внизу́", "at the bottom", (("avocado", "green"), ("pen", "red"), ("notebook", "green"))),
    )
    for index, (russian, english, icons) in enumerate(rows):
        top = 231 + index * 104
        write(c, russian, MARGIN, top - 3, 15, "Bold", GREEN)
        write(c, english, MARGIN, top + 14, 11)
        for column_index, (key, colour) in enumerate(icons):
            picture(c, key, MARGIN + 129 + column_index * 91, top, 52, colour)
        rule(c, top + 38)

    write(c, "Ask and answer.", MARGIN, 426, 12, "Bold")
    for index, question in enumerate((
        "Где кра́сная жва́чка?",
        "Где зелёное авока́до?",
        "Где зелёная тетра́дь?",
    )):
        write(c, question, MARGIN, 457 + index * 37, 17)
        rule(c, 458 + index * 37, MARGIN + 208)


def song(c):
    heading(c, "Жва́чка", 63, 34)
    artist = "Алёна Швец · First listen ↗"
    write(c, artist, MARGIN, 88, 12, "Bold", GREEN)
    link_width = pdfmetrics.stringWidth(artist, "Bold", 12)
    c.linkURL(SONG_URL, (MARGIN, H - 91, MARGIN + link_width, H - 75))
    write(c, "Can someone try to read first?", MARGIN, 125, 12)
    write(c, "Припе́в", MARGIN, 154, 16, "Bold")
    for index, (russian, cue, english) in enumerate(CHORUS):
        top = 185 + index * 47
        write(c, russian, MARGIN, top, 16, "Bold")
        write(c, cue, MARGIN, top + 16, 10.5, colour=BLUE)
        write(c, english, MARGIN + 190, top, 11, "Literata")
        rule(c, top + 26)

    write(c, "Words", MARGIN, 384, 17, "Bold")
    for index, (russian, english) in enumerate(GLOSSES):
        column, row = divmod(index, 6)
        x = MARGIN + column * 184
        top = 414 + row * 25
        write(c, russian, x, top, 12, "Bold")
        write(c, english, x + 65, top, 10.5, "Literata")


def build():
    pairs = [pair for row in EXERCISE for pair in row]
    assert len(pairs) == len(set(pairs)) == 24
    assert Counter(colour for _, colour in pairs) == dict.fromkeys(COLOURS, 8)
    for name, filename in (
        ("Sans", "GolosText-Print-Regular-Stress.ttf"),
        ("Bold", "GolosText-Print-Bold-Stress.ttf"),
        ("Display", "DelaGothicOne-Regular.ttf"),
        ("Literata", "Literata-Print-Regular.ttf"),
    ):
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename), shapable=True))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(OUTPUT), pagesize=A5, pageCompression=1, invariant=1, initialFontName="Sans")
    c.setTitle("жиза · Phonics, Review, Где?, Жвачка")
    c.setViewerPreference("PrintScaling", "None")
    for page in (phonics_and_review, colour_exercise, where, song):
        page(c)
        c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
