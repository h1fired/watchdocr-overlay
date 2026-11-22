# WatchdOcr

A screen overlay that recognizes text inside a user-selected part of the screen, optionally translates it, and draws the result back over the original text.

## Language

### Recognition

**Selection Area**:
The rectangle of the screen the user selected for recognition.
_Avoid_: Zone, region, boundings (in conversation)

**Recognition**:
One pass of grabbing the Selection Area and running OCR on it.
_Avoid_: Scan, detection

**Recognition Scale**:
The factor the grabbed image is shrunk by before OCR; either **Adaptive** (chosen from the smallest text height of the previous Recognition of the same Selection Area, never enlarging) or **Original** (no shrinking).
_Avoid_: Resolution, zoom, quality

**OCR Box**:
The quadrilateral around one recognized line of text, in Selection Area coordinates.
_Avoid_: Bounding box, region, rect

**Part**:
The text of a single OCR Box, original or translated.
_Avoid_: Line, chunk, segment

### Modes

**Onetime mode**:
A workflow where one Recognition runs each time the user releases a new Selection Area.

**Live mode**:
A workflow where Recognition repeats on a fixed interval over the same Selection Area.
_Avoid_: Realtime, continuous

### Display

**Visual Hint**:
The drawing placed over one OCR Box: a background that hides the original text, plus the Part drawn on top.
_Avoid_: Overlay box, label

**Visual Hint Style**:
The way Visual Hints are drawn; either **Solid** (plain dark background, default text color) or **Simple Inpaint** (background reconstructed from the surrounding image, text in the detected original color).
_Avoid_: Theme, mode

**Text Color Detection**:
Estimating the original text color and background color of each OCR Box from the grabbed image; used only by the Simple Inpaint style.
