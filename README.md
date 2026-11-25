# Zero File Generator

A small Python GUI utility that generates a `.txt` file filled with a chosen number of `0` characters (from `1` up to `80,000,000,000,000,000,000,000,000,000,000` / 80 nonillion), complete with a warning confirmation prompt before writing to disk.

## Features
- Simple `tkinter` GUI with input validation (`1` to `80 nonillion`)
- Warning dialog displaying target path and approximate size before creating the file
- Chunked ASCII file writing to keep memory usage low
- Progress bar and status updates during generation
