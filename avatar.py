import os
import argparse
from PIL import Image, ImageDraw
import zipfile

def split_avatars(input_path, rows=8, cols=8, output_dir="avatars_circles"):
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the image
    img = Image.open(input_path).convert("RGBA")
    img_width, img_height = img.size

    # Avatar size
    avatar_w = img_width // cols
    avatar_h = img_height // rows

    count = 1
    for row in range(rows):
        for col in range(cols):
            left = col * avatar_w
            upper = row * avatar_h
            right = left + avatar_w
            lower = upper + avatar_h

            # Crop rectangular tile
            avatar_tile = img.crop((left, upper, right, lower))

            # Find the largest centered square in the tile
            tile_w, tile_h = avatar_tile.size
            min_side = min(tile_w, tile_h)
            left_sq = (tile_w - min_side) // 2
            upper_sq = (tile_h - min_side) // 2
            right_sq = left_sq + min_side
            lower_sq = upper_sq + min_side
            avatar_square = avatar_tile.crop((left_sq, upper_sq, right_sq, lower_sq))

            # Create circular mask
            mask = Image.new("L", (min_side, min_side), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, min_side, min_side), fill=255)

            # Apply mask
            avatar_circle = Image.new("RGBA", (min_side, min_side))
            avatar_circle.paste(avatar_square, (0, 0), mask=mask)

            # Save
            avatar_circle.save(os.path.join(output_dir, f"avatar_{count}.png"))
            count += 1

    # Create ZIP file
    zip_path = f"{output_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(output_dir):
            zipf.write(os.path.join(output_dir, file), file)

    print(f"✅ Done! Saved {count-1} circular avatars in '{output_dir}'")
    print(f"📦 Zipped avatars saved at: {zip_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split avatar grid into circular PNGs.")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("--rows", type=int, default=8, help="Number of rows in grid (default: 8)")
    parser.add_argument("--cols", type=int, default=8, help="Number of columns in grid (default: 8)")
    parser.add_argument("--output", type=str, default="avatars_circles", help="Output folder name")

    args = parser.parse_args()
    split_avatars(args.input, args.rows, args.cols, args.output)
