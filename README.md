# Where are you?

Responsive HTML adaptation of the story in `unnamed-file-331.pdf` (Nal’ibali, Edition 150). Original text by Ann Walton, illustrations by Rico, Xitsonga translation by Tsakani Nkwe.

`dist/index.html` is the buildless website. Serve `dist/` with any static web server. `where-are-you.html` is the portable single-file reader, with its styles, scripts, and illustrations embedded; it can be opened directly.

The 16 original booklet pages are restored to reading order from PDF pages 5, 6, 11 and 12. Text remains selectable and responsive, with both source languages, page anchors, language selection, and adjustable text size. No print imposition is retained.

## Source extraction

Python 3 with PyMuPDF and Pillow is required only to repeat extraction and generation. The delivered website has no runtime dependencies.

- `scripts/extract_story.py` recovers text and artwork from the original PDF.
- `story-source.json` records the booklet order, source coordinates, and extracted paragraphs.
- `scripts/build.py` generates `dist/index.html`.
- `scripts/package.py` generates the portable reader and ZIP.

The source PDF remains unchanged and is linked in the reader.

## Parallel reader and letter order

The reader now aligns all 36 English/Xitsonga paragraph pairs in two columns at 12 pt, including on narrow screens. Paragraph numbering follows the Xitsonga narrative (1–34), followed by the two back-cover paragraphs (35–36). The cover shares stage 1. English passages spanning the original page boundaries are aligned with their corresponding Xitsonga paragraphs. Original illustrations and all 16 page anchors remain.

The textarea uses cumulative Cyrillic targets: `1 к т` enables k→к and t→т from paragraph 1; `3 а` adds a→а from paragraph 3. Blank lines and CRLF are supported. Repeated targets use their earliest paragraph. Invalid lines show their line numbers and retain the last valid rendering. An empty schedule leaves the original Latin text. Changes persist locally; **Автопорядок** restores the computed schedule and **Латиница** shows the untouched source.

The default introduces one new target per paragraph. A maximum-weight assignment maximizes the number of replaced source characters over the 34 narrative paragraphs, with the constraint that each target occurs in its introduction paragraph. This is optimal for that coverage metric and fixed pacing, not a validated pedagogical optimum. The 25 stages end at paragraph 25, leaving 9 narrative paragraphs for continued exposure.

Replacement is an approximate character substitution, not a phonetic transcription: sw is treated as one unit and maps to ш; x maps to щ, k to к, and q is left unchanged. Other digraphs remain character sequences, w/v both map to в, c to ч, and j to дж. An unintroduced sw remains intact even if s or w is already enabled. The optimizer counts sw as two replaced source characters. The visible correspondence table makes the choices inspectable. See the [Tsonga alphabet chart](https://www.omniglot.com/charts/tsonga.pdf) for the original sounds. All Cyrillic characters in the reading text receive the contrasting color.

Build/package require only Python's standard library; repeat extraction still needs PyMuPDF and Pillow. Run `python3 scripts/build.py`, `node scripts/check_reader.cjs`, and `python3 scripts/package.py` after changes.
