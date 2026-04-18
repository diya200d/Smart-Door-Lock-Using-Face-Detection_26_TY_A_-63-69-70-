import cv2
import os

name = input("Enter your name: ")

dataset_path = "dataset"
user_path = os.path.join(dataset_path, name)
os.makedirs(user_path, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

count = 0
print("Look straight. Capturing 25 images...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_img, (200, 200))

        count += 1
        cv2.imwrite(os.path.join(user_path, f"{count}.jpg"), face_resized)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Enrollment", frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or count >= 25:
        break

cap.release()
cv2.destroyAllWindows()
print(f"{name} enrolled with {count} images!")