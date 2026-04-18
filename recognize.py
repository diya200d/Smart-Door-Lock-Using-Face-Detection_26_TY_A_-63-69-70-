
import cv2
import os
import numpy as np
import requests
import time
import threading
 
# ===== ESP32 CONFIG =====
ESP32_IP   = "10.157.83.216"
ESP32_PORT = 80
 
COOLDOWN       = 4    # seconds between repeated commands
OPEN_THRESHOLD = 65   # lower = stricter face match
UNLOCK_HOLD    = 3    # must match ESP32 delay(3000)
 
 
def send_esp32_command(cmd):
    """Send command to ESP32 in a background thread so camera never freezes."""
    def _send():
        url = f"http://{ESP32_IP}:{ESP32_PORT}/{cmd}"
        for attempt in range(3):          # retry up to 3 times
            try:
                r = requests.get(url, timeout=8.0)   # increased from 3 -> 8 sec
                r.raise_for_status()
                print(f"✓ Sent {cmd} -> Status {r.status_code}  Response: {r.text[:60]}")
                return
            except requests.RequestException as e:
                print(f"✗ Attempt {attempt+1}/3 failed: {e}")
                time.sleep(0.5)
        print(f"✗ All retries failed for {cmd}")
 
    threading.Thread(target=_send, daemon=True).start()
 
 
# ===== LOAD DATASET =====
dataset_path = "dataset"
 
if not os.path.exists(dataset_path):
    print(f"Dataset folder '{dataset_path}' not found! Run enroll_user.py first.")
    exit()
 
recognizer = cv2.face.LBPHFaceRecognizer_create()
 
labels        = {}
faces_list    = []
labels_list   = []
current_label = 0
 
for name in sorted(os.listdir(dataset_path)):
    user_path = os.path.join(dataset_path, name)
    if not os.path.isdir(user_path):
        continue
    count = 0
    for file in os.listdir(user_path):
        img_path = os.path.join(user_path, file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            faces_list.append(img)
            labels_list.append(current_label)
            count += 1
    if count > 0:
        labels[current_label] = name
        print(f"  Loaded {count} images for '{name}' (label {current_label})")
        current_label += 1
 
if not faces_list:
    print("No faces enrolled! Run enroll_user.py first.")
    exit()
 
recognizer.train(faces_list, np.array(labels_list))
print(f"\n✓ Trained on {len(faces_list)} images across {len(labels)} user(s).\n")
 
# ===== START CAMERA =====
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera.")
    exit()
 
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
 
print("Face recognition started. Press 'q' to quit.\n")
 
last_sent      = ""
last_sent_time = 0
 
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed.")
        break
 
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
 
    frame_status    = "DENY"
    frame_color     = (0, 0, 255)
    frame_name      = "Unknown"
    best_confidence = 1000
 
    for (x, y, w, h) in faces:
        face_img     = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_img, (200, 200))
        label, confidence = recognizer.predict(face_resized)
 
        if confidence < best_confidence:
            best_confidence = confidence
            if confidence < OPEN_THRESHOLD:
                frame_status = "OPEN"
                frame_color  = (0, 255, 0)
                frame_name   = labels[label]
            else:
                frame_status = "DENY"
                frame_color  = (0, 0, 255)
                frame_name   = "Unknown"
 
        cv2.rectangle(frame, (x, y), (x+w, y+h), frame_color, 2)
        cv2.putText(frame, f"{confidence:.0f}", (x, y + h + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, frame_color, 1)
 
    # Overlay
    if frame_status == "OPEN":
        overlay_text = f"Access Granted: {frame_name}  ({best_confidence:.0f})"
    else:
        overlay_text = "Access Denied"
 
    cv2.putText(frame, overlay_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, frame_color, 2)
 
    # Send to ESP32 with cooldown
    now = time.time()
 
    if frame_status == "OPEN":
        open_cooldown = UNLOCK_HOLD + 1
        if last_sent != "OPEN" or (now - last_sent_time) > open_cooldown:
            send_esp32_command("OPEN")
            last_sent      = "OPEN"
            last_sent_time = now
 
    elif frame_status == "DENY":
        if last_sent != "DENY" or (now - last_sent_time) > COOLDOWN:
            send_esp32_command("DENY")
            last_sent      = "DENY"
            last_sent_time = now
 
    cv2.imshow("Smart Door Lock", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
cap.release()
cv2.destroyAllWindows()
print("Recognition stopped.")