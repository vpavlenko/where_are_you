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
