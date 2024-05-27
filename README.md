# AsciiCam

This project captures frames from a real camera, converts them into ASCII art, and streams the ASCII art video to a virtual camera. The virtual camera can be used in various applications, such as video conferencing software, to display the ASCII art video feed.

## Prerequisites

Before running the program, ensure you have the following installed:

- Python 3.6 or later
- OBS Studio 30.1.2
- Required Python libraries:
  - `opencv-python`
  - `numpy`
  - `pillow`
  - `pyvirtualcam`

You can install the required Python libraries using the following command:

```bash
pip install opencv-python numpy pillow pyvirtualcam
```

Additionally, you need the Consolas.ttf font file in the same directory as the script. You can replace this with any other monospaced font by updating the font_path variable.

## Running the Program

1. Clone the repository or download the script to your local machine.
2. Ensure your webcam is connected and working.
3. Open a terminal and navigate to the directory containing the script.
4. Run the script using the following command:

    ```bash
    python ascii_art_virtual_camera.py
    ```

### Key Components

- **`setup()`**: Initializes the ASCII characters and precomputes the necessary dimensions for the ASCII art.
- **`image_to_ascii(image)`**: Converts an image to ASCII art.
- **`ascii_to_image()`**: Converts ASCII art back to an image format.
- **`image_to_ascii_image(startImage)`**: Integrates the ASCII conversion functions to generate the final image.
- **`capture_and_process_frames(frame_queue, stop_event, fps_queue)`**: Captures frames from the real camera, processes them into ASCII art, and adds them to a queue.
- **`display_frames(frame_queue, cam, stop_event, fps_queue)`**: Displays the processed frames on the virtual camera and calculates FPS.

## How It Works

1. **Initialization**:
    - The script sets up the camera and prepares ASCII character images.
    - It clears the terminal for a clean output.

2. **Frame Capture and Processing**:
    - Frames are captured from the real camera.
    - Each frame is resized, converted to grayscale, normalized, and mapped to ASCII characters.

3. **Displaying Frames**:
    - The processed ASCII art frames are displayed on the virtual camera.
    - FPS is calculated and displayed in the terminal.

4. **Multithreading**:
    - The script uses two threads: one for capturing and processing frames, and another for displaying frames.
    - Queues are used to manage frames and processing times between threads.

## Stopping the Program

To stop the program, press `Ctrl+C` in the terminal. This will signal the threads to stop and clean up resources before exiting.

## Troubleshooting

- **No Camera Detected**: Ensure your webcam is connected and recognized by your operating system.
- **Low FPS**: The ASCII art conversion is computationally intensive. Adjust `block_font_size` for better performance.
- **Font Issues**: Ensure the specified font file exists. You can replace `Consolas.ttf` with any monospaced font available on your system.

# Copyright Statement

All rights reserved.

This software and its source code are the property of the author. 
You may use, modify, and distribute this software under the terms of the [MIT License](LICENSE).
