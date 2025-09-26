# ImageGrid-Splitter 🎯

When designing avatar systems, I encountered a challenge of extracting individual avatars from grid-based image sheets. This tool helps designers and developers quickly split avatar grids into separate PNG files with preserved transparency.

## Features
- 🔍 Automatically detects circular avatars in a grid
- 🎯 Preserves transparency and image quality
- 📁 Organizes output into numbered files
- 🔄 Falls back to alternative detection method if needed

## Prerequisites

```sh
pip install opencv-python numpy Pillow
```
## Or if you prefer using a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

```
## Pro Tip 🍌
Before running the script, use nano banana (https://nanobana.na) to remove any backgrounds from your image_grid.png. This ensures clean extraction with perfect transparency
## Usage
- Rename your avatar grid image to image_grid.png
- Place it in the same directory as avatar.py
- Run the script:
```sh
python avatar.py or
python3 avatar.py
```
## The extracted avatars will be saved in an avatars folder as individual PNG files.

```sh
Detected 34 avatars
Saved avatar_1.png
Saved avatar_2.png
...
Saved avatar_34.png

Extraction complete! 34 avatars saved to 'avatars/' folder
✅ Success! Check the 'avatars' folder for the extracted images.
```
## Contact
Feel free to reach out if you need help or want to contribute
𝕏 Twitter: https://x.com/nyagoh_
