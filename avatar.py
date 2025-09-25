import cv2
import numpy as np
from PIL import Image, ImageDraw
import os
from pathlib import Path

def extract_avatars_from_grid(image_path, output_folder='avatars'):
    """
    Extract individual circular avatars from a grid image.
    
    Args:
        image_path: Path to the input PNG image
        output_folder: Folder where individual avatars will be saved
    """
    
    # Create output directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Load the image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # If image has alpha channel, use it; otherwise create one
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # Convert to RGB for circle detection
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    
    # Convert to grayscale for circle detection
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=80,  # Minimum distance between circle centers
        param1=50,   # Higher threshold for Canny edge detector
        param2=30,   # Accumulator threshold for circle centers
        minRadius=40,  # Minimum circle radius
        maxRadius=70   # Maximum circle radius
    )
    
    if circles is None:
        print("No circles detected. Trying alternative method...")
        circles = detect_circles_alternative(gray)
    
    if circles is not None:
        # Round the circle parameters and convert to integers
        circles = np.uint16(np.around(circles))
        
        # Sort circles by position (top to bottom, left to right)
        circle_list = []
        for circle in circles[0, :]:
            circle_list.append(circle)
        
        # Sort by row first (y-coordinate), then by column (x-coordinate)
        circle_list.sort(key=lambda c: (c[1], c[0]))
        
        # Group circles into rows based on y-coordinate proximity
        rows = []
        current_row = []
        row_y = None
        y_threshold = 30  # Maximum y-difference to be considered same row
        
        for circle in circle_list:
            if row_y is None or abs(circle[1] - row_y) < y_threshold:
                current_row.append(circle)
                if row_y is None:
                    row_y = circle[1]
            else:
                # Sort current row by x-coordinate
                current_row.sort(key=lambda c: c[0])
                rows.append(current_row)
                current_row = [circle]
                row_y = circle[1]
        
        # Don't forget the last row
        if current_row:
            current_row.sort(key=lambda c: c[0])
            rows.append(current_row)
        
        # Flatten the sorted circles back into a single list
        sorted_circles = []
        for row in rows:
            sorted_circles.extend(row)
        
        print(f"Detected {len(sorted_circles)} avatars")
        
        # Extract each avatar
        for idx, (x, y, r) in enumerate(sorted_circles, 1):
            # Create a mask for the circular region
            mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            
            # Calculate bounding box for the circle
            x_min = max(0, x - r)
            x_max = min(img.shape[1], x + r)
            y_min = max(0, y - r)
            y_max = min(img.shape[0], y + r)
            
            # Crop the region
            cropped = img[y_min:y_max, x_min:x_max].copy()
            mask_cropped = mask[y_min:y_max, x_min:x_max]
            
            # Convert to PIL Image
            pil_img = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGRA2RGBA))
            
            # Create a new image with transparent background
            output_size = (r * 2, r * 2)
            output_img = Image.new('RGBA', output_size, (0, 0, 0, 0))
            
            # Create circular mask for the output
            mask_output = Image.new('L', output_size, 0)
            mask_draw = ImageDraw.Draw(mask_output)
            mask_draw.ellipse([0, 0, output_size[0]-1, output_size[1]-1], fill=255)
            
            # Calculate paste position to center the cropped image
            paste_x = r - (x - x_min)
            paste_y = r - (y - y_min)
            
            # Paste the cropped image onto the output
            output_img.paste(pil_img, (paste_x, paste_y))
            
            # Apply the circular mask
            output_img.putalpha(mask_output)
            
            # Save the individual avatar
            output_path = os.path.join(output_folder, f'avatar_{idx}.png')
            output_img.save(output_path, 'PNG')
            print(f"Saved avatar_{idx}.png")
    
    else:
        print("No circles could be detected in the image")
        return False
    
    print(f"\nExtraction complete! {len(sorted_circles)} avatars saved to '{output_folder}/' folder")
    return True

def detect_circles_alternative(gray):
    """
    Alternative method to detect circles if HoughCircles fails.
    Uses contour detection to find circular shapes.
    """
    # Apply threshold
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    circles = []
    for contour in contours:
        # Calculate area and perimeter
        area = cv2.contourArea(contour)
        if area < 1000:  # Skip small contours
            continue
        
        # Fit a circle to the contour
        (x, y), radius = cv2.minEnclosingCircle(contour)
        
        # Check if the contour is circular enough
        circularity = 4 * np.pi * area / (cv2.arcLength(contour, True) ** 2)
        if circularity > 0.7 and 40 < radius < 70:
            circles.append([x, y, radius])
    
    if circles:
        return np.array([circles], dtype=np.float32)
    return None

def main():
    """
    Main function to run the avatar extraction.
    """
    # Input image path
    image_path = 'avatar_grid.png'  # Change this to your image path
    
    # Output folder
    output_folder = 'avatars'
    
    # Check if input file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        print("Please ensure the image file is in the correct location.")
        return
    
    # Extract avatars
    try:
        success = extract_avatars_from_grid(image_path, output_folder)
        if success:
            print("\n✅ Success! Check the 'avatars' folder for the extracted images.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()