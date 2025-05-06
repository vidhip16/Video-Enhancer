# Handles conversion: frame extraction, AI enhancement, merging
# Handles conversion: frame extraction, AI enhancement, merging
import os
import cv2
import tempfile
import numpy as np
from PIL import Image
import time
from pathlib import Path
from ai_extender import AIImageExtender

class VideoProcessor:
    """Class to process videos for vertical enhancement"""
    
    def __init__(self, output_path="static/output", api_key=None):
        """Initialize with output path and optional API key"""
        self.output_path = output_path
        self.ai_extender = AIImageExtender() # No API key needed now
        
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
    
    def process_video(self, video_path, position="bottom", extension_ratio=1.0, fps=None, sample_rate=1):
        """
        Process a video by extracting frames, extending them, and rebuilding
        
        Args:
            video_path: Path to the input video
            position: "top" or "bottom" - where to add the extension
            extension_ratio: How much to extend relative to original height
            fps: Frames per second for output (uses input fps if None)
            sample_rate: Process 1 out of every N frames (for speed)
        
        Returns:
            Path to the processed video
        """
        # Get video properties
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Use input fps if not specified
        fps = fps or input_fps
        
        # Calculate new dimensions
        extension_height = int(height * extension_ratio)
        new_height = height + extension_height
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract and process frames
            processed_frames = []
            frame_idx = 0
            
            print(f"Processing video with {frame_count} frames, sampling every {sample_rate} frames...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Only process every Nth frame based on sample_rate
                if frame_idx % sample_rate == 0:
                    print(f"Processing frame {frame_idx}/{frame_count}")
                    
                    # Convert OpenCV BGR to PIL RGB format
                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    # Extend the frame
                    extended_frame = self.ai_extender.extend_frame(
                        pil_frame, position, extension_ratio
                    )
                    
                    # Save the processed frame path
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:06d}.jpg")
                    extended_frame.save(frame_path)
                    processed_frames.append(frame_path)
                
                frame_idx += 1
            
            cap.release()
            
            # Create output video name
            input_filename = os.path.basename(video_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"{name}_vertical{ext}"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Create the output video
            self._frames_to_video(processed_frames, output_path, fps, (width, new_height))
            
            return output_path
    
    def _frames_to_video(self, frame_paths, output_path, fps, dimensions):
        """Convert a series of frames to a video"""
        width, height = dimensions
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID', 'H264', etc.
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_path in frame_paths:
            # Read the image
            img = cv2.imread(frame_path)
            
            # Write to video
            video_writer.write(img)
        
        video_writer.release()
        print(f"Video saved to {output_path}")
        
        # Try to convert to H.264 for better compatibility if ffmpeg is available
        try:
            temp_output = output_path + ".temp.mp4"
            # Add quotes around the file paths to handle spaces properly
            os.system(f'ffmpeg -i \"{output_path}\" -c:v libx264 -preset fast -crf 22 \"{temp_output}\"')
            os.replace(temp_output, output_path)
            print(f"Converted video to H.264 format")
        except Exception as e:
            print(f"Failed to convert to H.264: {e}")
    
    def process_video_keyframes(self, video_path, position="bottom", extension_ratio=1.0, keyframe_interval=24):
        """
        Process a video by only extending keyframes and interpolating between them
        
        Args:
            video_path: Path to the input video
            position: "top" or "bottom" - where to add the extension
            extension_ratio: How much to extend relative to original height
            keyframe_interval: Process 1 frame every N frames as keyframes
        
        Returns:
            Path to the processed video
        """
        # Get video properties
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate new dimensions
        extension_height = int(height * extension_ratio)
        new_height = height + extension_height
        
        # Create output video name
        input_filename = os.path.basename(video_path)
        name, ext = os.path.splitext(input_filename)
        output_filename = f"{name}_vertical{ext}"
        output_path = os.path.join(self.output_path, output_filename)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, new_height))
        
        # Process keyframes
        keyframes = {}
        frame_idx = 0
        
        # First pass: process keyframes
        print(f"First pass: Processing keyframes...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Only process keyframes
            if frame_idx % keyframe_interval == 0:
                print(f"Processing keyframe {frame_idx}/{frame_count}")
                
                # Convert OpenCV BGR to PIL RGB format
                pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Extend the frame
                extended_frame = self.ai_extender.extend_frame(
                    pil_frame, position, extension_ratio
                )
                
                # Convert back to OpenCV format
                keyframes[frame_idx] = cv2.cvtColor(np.array(extended_frame), cv2.COLOR_RGB2BGR)
            
            frame_idx += 1
        
        # Reset video capture
        cap.release()
        cap = cv2.VideoCapture(video_path)
        
        # Second pass: interpolate between keyframes and write video
        print(f"Second pass: Interpolating between keyframes...")
        frame_idx = 0
        prev_keyframe_idx = 0
        next_keyframe_idx = keyframe_interval
        
        # If we're extending at the top, we need to adjust where we paste the original frame
        y_offset = extension_height if position == "top" else 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # If we're at a keyframe, use the extended frame
            if frame_idx in keyframes:
                video_writer.write(keyframes[frame_idx])
                prev_keyframe_idx = frame_idx
                next_keyframe_idx = frame_idx + keyframe_interval
            else:
                # Otherwise, we need to interpolate
                if next_keyframe_idx in keyframes:
                    next_frame = keyframes[next_keyframe_idx]
                else:
                    # If we don't have the next keyframe, use the previous
                    next_keyframe_idx = frame_count  # won't be reached
                    next_frame = keyframes[prev_keyframe_idx]
                
                prev_frame = keyframes[prev_keyframe_idx]
                
                # Calculate interpolation factor
                if next_keyframe_idx > prev_keyframe_idx:
                    blend_factor = (frame_idx - prev_keyframe_idx) / (next_keyframe_idx - prev_keyframe_idx)
                else:
                    blend_factor = 0
                
                # Create a blank frame
                extended_frame = np.zeros((new_height, width, 3), dtype=np.uint8)
                
                # Only interpolate the extension area
                if position == "top":
                    # Interpolate the top part
                    extension_prev = prev_frame[:extension_height, :]
                    extension_next = next_frame[:extension_height, :]
                    extension = cv2.addWeighted(extension_prev, 1 - blend_factor, extension_next, blend_factor, 0)
                    
                    # Place the extension at the top
                    extended_frame[:extension_height, :] = extension
                    
                    # Place the original frame at the bottom
                    extended_frame[extension_height:, :] = frame
                else:  # bottom
                    # Interpolate the bottom part
                    extension_prev = prev_frame[height:, :]
                    extension_next = next_frame[height:, :]
                    extension = cv2.addWeighted(extension_prev, 1 - blend_factor, extension_next, blend_factor, 0)
                    
                    # Place the original frame at the top
                    extended_frame[:height, :] = frame
                    
                    # Place the extension at the bottom
                    extended_frame[height:, :] = extension
                
                # Write the interpolated frame
                video_writer.write(extended_frame)
            
            frame_idx += 1
        
        cap.release()
        video_writer.release()
        
        # Try to convert to H.264 for better compatibility if ffmpeg is available
        try:
            temp_output = output_path + ".temp.mp4"
            os.system(f'ffmpeg -i \"{output_path}\" -c:v libx264 -preset fast -crf 22 \"{temp_output}\"')
            os.replace(temp_output, output_path)
            print(f"Converted video to H.264 format")
        except Exception as e:
            print(f"Failed to convert to H.264: {e}")
        
        return output_path