# Plugin Hooks

This document lists all available hooks that plugins can implement.

## Execution

* Hooks are executed in the event loop thread.
* A hook can be either a regular function or an `async def` coroutine function.
* Regular hooks must be lightweight, because they block the event loop while running.
  Heavy work should be done in an `async def` hook with `await asyncio.to_thread(...)`.
* A running pipeline can be cancelled by a newer one. A cancelled pipeline
  never calls `output_text` and `finish` hooks, so state that should be applied only
  for finished pipelines has to be committed in the `finish` hook.

## OCR Hooks

### `watchdocr.image_grabber_pipeline.image_process`
* **Trigger**: After screen image grabbing.
* **Input/Output**: `PIL.Image`
* **Extra kwargs**: `ctx=WatchdOcrRuntimeContext`

### `watchdocr.processor_pipeline.start`
* **Trigger**: On processor pipeline start.
* **Input/Output**: `WatchdOcrRuntimeContext`

### `watchdocr.processor_pipeline.finish`
* **Trigger**: On processor pipeline finish. Not called for cancelled pipelines.
* **Input/Output**: `WatchdOcrRuntimeContext`

### `watchdocr.processor_pipeline.output_text`
* **Trigger**: On processor pipeline text output. Not called for cancelled pipelines.
* **Input/Output**: `str`
