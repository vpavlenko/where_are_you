"""Build the unnumbered A4 practice sheets for жиза.

Install ReportLab, uharfbuzz and svglib before running this script.
"""

from collections import Counter
from pathlib import Path
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, shapeStr
from reportlab.pdfgen.canvas import Canvas

from zhiza_lesson_illustrations import FLUENT_LICENSE, draw_object

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "handouts/fonts"
OUTPUT = ROOT / "output/pdf/zhiza-practice-a4.pdf"
# Retain the original A5 layout coordinates for proportional enlargement.
W, H = A5
MARGIN = 34
WIDTH = W - 2 * MARGIN
INK = "#151515"
BLUE = "#00658a"
GREEN = "#397020"
RUST = "#8d4023"
FAINT = "#d7dadd"

COLOURS = {
    "red": "#ee524e",
    "yellow": "#f6cc43",
    "green": "#75bd50",
}
COLOUR_TEXT = {
    "red": "#c81932",
    "yellow": "#9f6d00",
    "green": "#237a21",
}
# Preserve the author's Xitsonga-based cues, including script and stress marks.
PHONICS = (
    ("па пи пы пэ пе", "pa pyi pы pe pye"),
    ("са си сы сэ се", "sa si sы se sye"),
    ("та ти ты тэ те", "ta tsi tы te tsye"),
    ("ма ми мы мэ ме", "ma mi mы me mye"),
)
COLOUR_WORDS = (
    ("red", "кра́сный", "krasni"),
    ("yellow", "жёлтый", "жolti"),
    ("green", "зелёный", "zilyoni"),
)
KNOWN_WORDS = (
    ("mango", "ма́нго", None),
    ("avocado", "авока́до", None),
    ("pen", "ру́чка", None),
    ("book", "кни́га", None),
)
NEW_WORDS = (
    ("notebook", "тетра́дь", "tsitratsi"),
    ("gum", "жва́чка", "жыvácuka"),
    ("sun", "со́лнце", "sontse"),
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
# Chepisi: Nal'ibali Ed. 168, p. 13.
# https://nalibali.org/wp-content/uploads/2025/07/unnamed-file-212.pdf#page=13
# Meal terms: DSAC glossary and Nal'ibali.
CHORUS = (
    ("Жва́чка на за́втрак,", "жыvacka na zaftrak", "Chepisi hi xifihlulo,"),
    ("Ко́ла на у́жин.", "kola na uжыn", "Coca-Cola hi xilalelo."),
    ("Я так уста́ла,", "ya tak ustala", "Ndzi (girl) karhele ngopfu."),
    ("Ты мне не ну́жен.", "tы mnye nye nuжеn", "Wena (boy) a ndzi ku lavi."),
)
GLOSSES = (
    ("жва́чка", "chepisi"),
    ("на", "hi"),
    ("за́втрак", "xifihlulo"),
    ("ко́ла", "Coca-Cola"),
    ("у́жин", "xilalelo"),
    ("я", "ndzi"),
    ("так", "ngopfu"),
    ("уста́ла", "ndzi karhele"),
    ("ты", "wena"),
    ("мне", "eka mina"),
    ("не", "a … -i"),
    ("ну́жен", "wa laveka"),
)

# Dialogues and column positions from page 10 of the жиза booklet.
WHERE_DIALOGUES = (
    (60.93, 166.88, 94.34, (
        ("— Паш, где Ми́ша?", "— Pasw, gdzye Miswa?"),
        ("— Там.", "— Tam."),
        ("— А где Са́ша?", "— A gdzye Saswa?"),
        ("— Я не зна́ю.", "— Ya nye znayu."),
    )),
    (28.35, 179.15, 197.47, (
        ("— Вита́ль, ты зна́ешь, где\nжёлтая кни́га?", "— Vhitali, tы znayisw, gdzye жоlti kniga?"),
        ("— Нет.", "— Nyet."),
        ("— А где кра́сная ру́чка?", "— A gdzye krasni rucka?"),
        ("— Там.", "— Tam."),
    )),
    (32.10, 200.19, 314.99, (
        ("— Вита́ль, ты зна́ешь ру́сский?", "— Vhitali, tы znayisw ruski?"),
        ("— Да. Я ру́сский. А ты?", "— Da. Ya ruski. A tы?"),
        ("— Нет, я не зна́ю.", "— Nyet, ya nye znayu."),
    )),
    (84.57, 229.94, 400.22, (
        ("— Саш, ты зна́ешь тсо́нгу?", "— Sasw, tы znayisw tsongu?"),
        ("— Нет.", "— Nyet."),
    )),
)
FOOD_DIALOGUE = (
    "— Я ем манго. А ты что ешь?",
    "— Я ем авокадо.",
)
VERBS = (
    (("я ем", "ya yem"), ("ты ешь", "tы yesw"), "dya"),
    (("я зна́ю", "ya znayu"), ("ты зна́ешь", "tы znayisw"), "tiva"),
    (("я пишу́", "ya piswú"), ("ты пи́шешь", "tы piswыsw"), "tsala"),
    (("я иду́", "ya idú"), ("ты идёшь", "tы idzyósw"), "famba"),
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


def vocabulary_heading(c, xitsonga, russian, cue, top):
    x = MARGIN
    for label, font, colour in (
        (xitsonga, "Bold", RUST),
        (russian, "Bold", INK),
        (cue, "Sans", BLUE),
    ):
        write(c, label, x, top, 11, font, colour)
        x += pdfmetrics.stringWidth(label, font, 11) + 10


def phonics_and_review(c):
    heading(c, "Phonics", 57, 27)
    for index, (russian, cue) in enumerate(PHONICS):
        phonics_row(c, russian, cue, 86 + index * 33)
    write(c, "Say with other consonants", MARGIN, 222, 11)
    phonics_row(c, "жа жо жу же жи", "жа жo жu же жы", 252)

    heading(c, "Review", 325, 27)
    vocabulary_heading(c, "Mihlovo", "Цвета́", "tsivhitá", 348)
    for index, (colour, russian, cue) in enumerate(COLOUR_WORDS):
        x = MARGIN + index * WIDTH / 3
        c.setFillColor(HexColor(COLOURS[colour]))
        c.circle(x + 7, H - 369, 7, stroke=0, fill=1)
        write(c, russian, x + 21, 370, 12, "Bold", COLOUR_TEXT[colour])
        write(c, cue, x + 21, 385, 10, colour=COLOUR_TEXT[colour])

    vocabulary_heading(c, "Swilo", "Предме́ты", "piridimyetы", 412)
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


def song(c):
    heading(c, "Жва́чка", 63, 34)
    write(c, "Алёна Швец", MARGIN, 88, 12, "Bold", GREEN)
    write(c, "Can someone try to read first?", MARGIN, 125, 12)
    write(c, "Припе́в", MARGIN, 154, 16, "Bold")
    for index, (russian, cue, xitsonga) in enumerate(CHORUS):
        top = 185 + index * 47
        write(c, russian, MARGIN, top, 16, "Bold")
        write(c, cue, MARGIN, top + 16, 10.5, colour=BLUE)
        write(c, xitsonga, MARGIN + 190, top, 11, "Literata")
        rule(c, top + 26)

    write(c, "Marito", MARGIN, 384, 17, "Bold")
    for index, (russian, xitsonga) in enumerate(GLOSSES):
        column, row = divmod(index, 6)
        x = MARGIN + column * 184
        top = 414 + row * 25
        write(c, russian, x, top, 12, "Bold")
        write(c, xitsonga, x + 65, top, 10.5, "Literata")


def where(c):
    scale = .92
    source_left, source_top = 28.35, 54.18
    heading_top = 56
    body = 10.4 * scale
    highlights = {
        "жёлтая": COLOUR_TEXT["yellow"],
        "жоlti": COLOUR_TEXT["yellow"],
        "кра́сная": COLOUR_TEXT["red"],
        "krasni": COLOUR_TEXT["red"],
    }
    color_words = re.compile("(" + "|".join(re.escape(word) for word in highlights) + ")")

    def dialogue_line(value, x, top, colour):
        for part in color_words.split(value):
            if part:
                write(c, part, x, top, body, colour=highlights.get(part, colour))
                x += pdfmetrics.stringWidth(part, "Sans", body)

    heading(c, "Где?", heading_top, 22 * scale)
    write(c, "Kwihi?", MARGIN + (106.59 - source_left) * scale, heading_top, 11.4 * scale, colour=RUST)
    for russian_x, cue_x, baseline, rows in WHERE_DIALOGUES:
        left = MARGIN + (russian_x - source_left) * scale
        right = MARGIN + (cue_x - source_left) * scale
        top = heading_top + (baseline - source_top) * scale
        for russian, cue in rows:
            lines = russian.splitlines()
            for index, line in enumerate(lines):
                dialogue_line(line, left, top + index * 14.4 * scale, INK)
            dialogue_line(cue, right, top, BLUE)
            top += (17.9 + (len(lines) - 1) * 14.4) * scale

    for index, line in enumerate(FOOD_DIALOGUE):
        write(c, line, MARGIN, 423 + index * 18, body)

    for index, (first, second, xitsonga) in enumerate(VERBS):
        top = 464 + index * 28
        rule(c, top - 12, right=MARGIN + 282)
        for x, (russian, cue) in ((MARGIN, first), (MARGIN + 104, second)):
            write(c, russian, x, top, 11)
            write(c, cue, x, top + 11, 9, colour=BLUE)
        write(c, xitsonga, MARGIN + 222, top, 11, colour=RUST)


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
    c = Canvas(str(OUTPUT), pagesize=A4, pageCompression=1, invariant=1, initialFontName="Sans")
    c.setTitle("жиза · Phonics, Review, Жвачка, Где?")
    c.setSubject(
        "Mango, avocado and pen illustrations adapted from Microsoft Fluent UI Emoji.\n"
        + FLUENT_LICENSE.read_text(encoding="utf-8").strip()
    )
    c.setViewerPreference("PrintScaling", "None")
    paper_width, paper_height = A4
    scale = min(paper_width / W, paper_height / H)
    for page in (phonics_and_review, colour_exercise, song, where):
        c.saveState()
        c.translate((paper_width - W * scale) / 2, (paper_height - H * scale) / 2)
        c.scale(scale, scale)
        page(c)
        c.restoreState()
        c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
