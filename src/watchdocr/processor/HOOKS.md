# Plugin Hooks

This document lists all available hooks that plugins can implement.

## OCR Hooks

### `watchdocr.image_grabber_pipeline.image_process`
* **Trigger**: After screen image grabbing.
* **Input/Output**: `PIL.Image`
* **Extra kwargs**: `ctx=WatchdOcrRuntimeContext`

### `watchdocr.processor_pipeline.finish`
* **Trigger**: On processor pipeline finish.
* **Input/Output**: `WatchdOcrRuntimeContext`

### `watchdocr.processor_pipeline.output_text`
* **Trigger**: On processor pipeline text output.
* **Input/Output**: `str`
