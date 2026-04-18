# Smart Door Lock (Face Recognition + ESP32)
Smart Door Lock is a face-recognition-based access system that captures enrolled user faces, recognizes them in real time using OpenCV LBPH, and sends OPEN or DENY commands to an ESP32-controlled lock over HTTP.

## Features
- User enrollment from webcam (`enroll_user.py`)
- Local dataset storage in `dataset/<username>/`
- LBPH model training from stored images
- Real-time face recognition (`recognize.py`)
- Access decision: `OPEN` or `DENY`
- HTTP command communication to ESP32

  ## Project Files
- `enroll_user.py` - captures and saves user face images
- `recognize.py` - trains recognizer from local dataset and sends commands
- `test_camera.py` - checks webcam index
- `arduino_code.ino` - ESP32/Arduino Code

  ## Requirements
- Python 3.8+
- opencv-contrib-python
- numpy
- requests
Install dependencies:
```bash
pip install opencv-contrib-python numpy requests

## Usage
Test camera:
python test_camera.py
Enroll user faces:
python enroll_user.py
Start recognition + lock control:
python recognize.py
Press q to stop.

# How It Works
Capture face images for each user into the local dataset/ folder.
Train LBPH recognizer from these images.
Detect and recognize faces from live webcam feed.
If recognized confidently -> send OPEN to ESP32.
Otherwise -> send DENY.

