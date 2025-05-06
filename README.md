# Vertical Video Enhancer

A web application that transforms traditional 16:9 horizontal video clips into vertical 9:16 format by placing the original content at the top or bottom of the frame and using AI to generate extended content for the remaining space.

![Vertical Video Enhancer Demo](https://placeholder.com/your-demo-image.gif)

## Features

- **Video Conversion**: Upload horizontal 16:9 videos and convert them to vertical 9:16 format
- **AI-Generated Extensions**: Automatically extends the scene with sky or ground content
- **Positioning Options**: Place original content at top or bottom of vertical frame
- **Processing Options**: Balance between speed and quality with keyframe processing
- **Web Interface**: Simple interface for uploading, processing, and downloading videos

## How It Works

1. **Upload**: User uploads a standard horizontal video
2. **Processing**: 
   - The original video frames are extracted
   - Each frame is processed by AI to extend either the top or bottom
   - The extended frames are combined into a new vertical video
3. **Result**: Users can preview and download the new vertical video

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (optional, for better video encoding)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vertical-video-enhancer.git
   cd vertical-video-enhancer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the API key (optional):
   - Get an API key from [Stability AI](https://stability.ai/) (recommended)
   - Create a `.env` file in the project root with:
     ```
     STABILITY_API_KEY=your_api_key_here
     ```
   - Without an API key, the application will use Hugging Face's free API with some limitations

## Usage

1. Start the Flask server:
   ```
   python backend/main.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the web interface to:
   - Upload a video file
   - Choose placement (top/bottom)
   - Adjust extension settings
   - Process and download the enhanced video

## Configuration Options

- **Extension Position**: Place the original video at the top (extend bottom) or bottom (extend top)
- **Extension Amount**: Control how much the video is extended (50%-200% of original height)
- **Processing Method**:
  - Regular processing: Process every frame for highest quality
  - Keyframe processing: Process only keyframes and interpolate between them for faster results

## API Endpoints

The application provides a simple RESTful API:

- `POST /upload`: Upload and process a video
  - Form parameters:
    - `file`: Video file
    - `position`: "top" or "bottom"
    - `extension_ratio`: Float between 0.5 and 2.0
    - `use_keyframes`: "true" or "false"
    - `keyframe_interval`: Integer (if using keyframes)
    - `sample_rate`: Integer (if not using keyframes)
  - Response: JSON with output video URL

- `GET /api/stats`: Get processing statistics
  - Response: JSON with stats like number of videos processed

## Limitations

- Processing time depends on video length, frame rate, and chosen settings
- Large files may take several minutes to process
- Free API tiers have usage limits

## License

MIT License

## Acknowledgements

- Built with [Flask](https://flask.palletsprojects.com/)
- Uses [OpenCV](https://opencv.org/) for video processing
- AI image generation powered by [Stability AI](https://stability.ai/) and [Hugging Face](https://huggingface.co/)
- Front-end uses [Bootstrap 5](https://getbootstrap.com/)