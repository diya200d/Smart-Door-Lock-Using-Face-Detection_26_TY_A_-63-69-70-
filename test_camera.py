import cv2

for i in range(3):  # Try 0,1,2
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera opened successfully at index {i}")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            cv2.imshow(f"Camera {i}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        break
    else:
        print(f"Cannot open camera at index {i}")
        cap.release()