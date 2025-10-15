import turtle
import cv2
import numpy as np
from PIL import Image

class CNCMachine:
    def __init__(self, speed=5):
        self.screen = turtle.Screen()
        self.screen.title("Virtual CNC Machine - Design Generator")
        self.screen.setup(width=800, height=800)
        self.screen.bgcolor("white")
        
        # Create the "cutting tool"
        self.tool = turtle.Turtle()
        self.tool.shape("circle")
        self.tool.shapesize(0.3, 0.3)
        self.tool.color("red")
        self.tool.speed(speed)
        
        # Create status display
        self.status = turtle.Turtle()
        self.status.hideturtle()
        self.status.penup()
        self.status.goto(0, 350)
        
    def update_status(self, msg):
        self.status.clear()
        self.status.write(msg, align="center", font=("Arial", 12, "normal"))
    
    def edge_detection(self, img_path, threshold1=50, threshold2=150):
        """Process image and extract edges using Canny edge detection"""
        self.update_status("Loading and processing image...")
        
        # Load image
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("Could not load image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, threshold1, threshold2)
        
        return edges, img.shape
    
    def extract_contours(self, edges):
        """Extract contours from edge-detected image"""
        self.update_status("Extracting design contours...")
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort by contour area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        return contours
    
    def scale_coordinates(self, contours, img_shape, canvas_size=600):
        """Scale image coordinates to turtle canvas coordinates"""
        h, w = img_shape[:2]
        scale = canvas_size / max(h, w)
        
        scaled_contours = []
        for contour in contours:
            scaled = []
            for point in contour:
                x, y = point[0]
                # Convert to turtle coordinates (center origin, y-axis flipped)
                tx = (x - w/2) * scale
                ty = (h/2 - y) * scale
                scaled.append((tx, ty))
            scaled_contours.append(scaled)
        
        return scaled_contours
    
    def draw_toolpath(self, contours, min_points=10):
        """Simulate CNC machine drawing the design"""
        self.update_status("CNC Machine Running - Drawing Design...")
        
        total_contours = len(contours)
        drawn = 0
        
        for i, contour in enumerate(contours):
            # Skip very small contours
            if len(contour) < min_points:
                continue
            
            # Move to start position (tool up)
            self.tool.penup()
            self.tool.goto(contour[0][0], contour[0][1])
            
            # Lower tool and start cutting
            self.tool.pendown()
            self.tool.color("blue")
            
            # Draw the contour
            for x, y in contour[1:]:
                self.tool.goto(x, y)
            
            # Close the contour
            self.tool.goto(contour[0][0], contour[0][1])
            
            drawn += 1
            
            # Update progress
            if drawn % 5 == 0:
                self.update_status(f"CNC Machine Running - Progress: {i+1}/{total_contours} paths")
        
        # Return to origin
        self.tool.penup()
        self.tool.goto(0, 0)
        self.tool.color("red")
        
        self.update_status(f"Design Complete! Drew {drawn} toolpaths")
    
    def generate_from_image(self, img_path, canvas_size=600):
        """Main function to generate CNC design from image"""
        try:
            # Process image
            edges, img_shape = self.edge_detection(img_path)
            
            # Extract contours
            contours = self.extract_contours(edges)
            
            # Scale to canvas
            scaled_contours = self.scale_coordinates(contours, img_shape, canvas_size)
            
            # Draw with CNC simulation
            self.draw_toolpath(scaled_contours)
            
            self.update_status("✓ CNC Design Complete - Click to close")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            print(f"Error processing image: {e}")
    
    def keep_window_open(self):
        """Keep the turtle window open"""
        self.screen.exitonclick()


# Usage example
if __name__ == "__main__":
    import os
    import tkinter as tk
    from tkinter import filedialog
    
    # Instructions for use
    print("=" * 60)
    print("Virtual CNC Machine Design Generator")
    print("=" * 60)
    print("\nInstructions:")
    print("1. A file dialog will open - select your design image")
    print("2. Watch the CNC simulation!")
    print("Supported formats: PNG, JPG, JPEG, BMP")
    print("=" * 60)
    
    # Create a hidden tkinter root window for file dialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # Open file dialog to select image
    print("\n📁 Please select an image file...")
    image_path = filedialog.askopenfilename(
        title="Select Design Image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
    )
    
    if not image_path:
        print("❌ No file selected. Exiting...")
        exit()
    
    # Verify file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found at {image_path}")
        exit()
    
    print(f"✓ Selected: {os.path.basename(image_path)}")
    print(f"✓ Full path: {image_path}")
    
    # Initialize CNC machine
    cnc = CNCMachine(speed=0)  # speed: 0=fastest, 10=slowest
    
    # Generate the design
    print("\n🔧 Processing image...")
    cnc.generate_from_image(image_path, canvas_size=600)
    
    # Keep window open
    cnc.keep_window_open()
