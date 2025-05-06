# Uses AI to generate top/bottom image extensions
import os
import requests
from PIL import Image, ImageFilter, ImageOps
import io
import base64
import random
import numpy as np
import cv2
import time

class AIImageExtender:
    def __init__(self):
        """Initialize the image extender with optional API key"""
        # Local cache for similar extension requests
        self.extension_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def extend_frame(self, image, position="bottom", extension_ratio=1.0):
        """
        Extend the image frame either at top or bottom
        
        Args:
            image: PIL Image object
            position: "top" or "bottom" - where to add the extension
            extension_ratio: How much to extend relative to original height
            
        Returns:
            PIL Image with extension
        """
        width, height = image.size
        extension_height = int(height * extension_ratio)
        
        # Create a padded canvas
        if position == "bottom":
            new_img = Image.new("RGB", (width, height + extension_height), (0, 0, 0))
            new_img.paste(image, (0, 0))
            
            # Generate the extension using local method
            extension = self._generate_extension_locally(image, position, width, extension_height)
            new_img.paste(extension, (0, height))
            
        else:  # top
            new_img = Image.new("RGB", (width, height + extension_height), (0, 0, 0))
            new_img.paste(image, (0, extension_height))
            
            # Generate the extension using local method
            extension = self._generate_extension_locally(image, position, width, extension_height)
            new_img.paste(extension, (0, 0))
        
        return new_img
    
    def _generate_extension_locally(self, image, position, width, extension_height):
        """
        Generate an extension using local image processing techniques
        
        Args:
            image: PIL Image object to extend
            position: "top" or "bottom"
            width: Width of extension
            extension_height: Height of extension
            
        Returns:
            PIL Image of the extension
        """
        # Check cache first using a hash of the edge pixels
        if position == "bottom":
            edge_region = image.crop((0, image.height - 20, width, image.height))
        else:
            edge_region = image.crop((0, 0, width, 20))
        
        # Create a simple hash for the edge region
        edge_hash = str(np.array(edge_region).sum())
        cache_key = f"{position}_{width}_{extension_height}_{edge_hash}"
        
        if cache_key in self.extension_cache:
            self.cache_hits += 1
            print(f"[Cache hit] Using cached extension for similar frame")
            return self.extension_cache[cache_key]
        
        self.cache_misses += 1
        
        # Method 1: Reflection and blur
        if position == "bottom":
            # For bottom extension, create reflection and gradient
            reflection_height = min(image.height, extension_height * 2)
            reflection_region = image.crop((0, image.height - reflection_height, width, image.height))
            reflection = ImageOps.flip(reflection_region)
            
            # Blur the reflection and adjust brightness
            reflection = reflection.filter(ImageFilter.GaussianBlur(radius=5))
            
            # Create gradient mask for smooth transition
            gradient = Image.new('L', (width, reflection_height), 0)
            for y in range(reflection_height):
                # Gradient gets darker as we go down
                gradient_value = int(255 * (1 - y / reflection_height))
                for x in range(width):
                    gradient.putpixel((x, y), gradient_value)
            
            # Apply gradient mask
            reflection.putalpha(gradient)
            
            # Create base extension image
            extension = Image.new("RGB", (width, extension_height), self._get_dominant_color(image, 'bottom'))
            
            # Calculate paste position to align with the bottom of the original image
            paste_y = 0
            if reflection_height < extension_height:
                # If reflection is smaller than needed extension, center it
                paste_y = (extension_height - reflection_height) // 2
            
            # Paste reflection onto extension
            extension.paste(reflection, (0, paste_y), reflection.getchannel('A'))
            
        else:  # top extension
            # For top extension, mirror and blur the top portion
            reflection_height = min(image.height, extension_height * 2)
            reflection_region = image.crop((0, 0, width, reflection_height))
            reflection = ImageOps.flip(reflection_region)
            
            # Blur the reflection and adjust brightness
            reflection = reflection.filter(ImageFilter.GaussianBlur(radius=5))
            
            # Create gradient mask for smooth transition
            gradient = Image.new('L', (width, reflection_height), 0)
            for y in range(reflection_height):
                # Gradient gets darker as we go up
                gradient_value = int(255 * (y / reflection_height))
                for x in range(width):
                    gradient.putpixel((x, y), gradient_value)
            
            # Apply gradient mask
            reflection.putalpha(gradient)
            
            # Create base extension image
            extension = Image.new("RGB", (width, extension_height), self._get_dominant_color(image, 'top'))
            
            # Calculate paste position
            paste_y = extension_height - reflection_height
            if paste_y < 0:
                paste_y = 0
            
            # Paste reflection onto extension
            extension.paste(reflection, (0, paste_y), reflection.getchannel('A'))
        
        # Store in cache for future similar frames
        self.extension_cache[cache_key] = extension
        
        # Limit cache size to avoid memory issues
        if len(self.extension_cache) > 100:
            # Remove oldest items
            oldest_keys = list(self.extension_cache.keys())[:20]
            for key in oldest_keys:
                del self.extension_cache[key]
        
        return extension
    
    def _get_dominant_color(self, image, position):
        """Get dominant color from edge of image for seamless extension"""
        if position == 'bottom':
            # Sample from bottom edge
            edge = image.crop((0, image.height - 10, image.width, image.height))
        else:
            # Sample from top edge
            edge = image.crop((0, 0, image.width, 10))
        
        # Convert to numpy array for processing
        np_img = np.array(edge)
        
        # Reshape and compute average color
        pixels = np_img.reshape(-1, 3)
        
        # Simple approach: average the pixels
        avg_color = tuple(map(int, np.mean(pixels, axis=0)))
        
        # More sophisticated approach: find dominant color cluster
        # You could use K-means clustering here for better results
        
        return avg_color