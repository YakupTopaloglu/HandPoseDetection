import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import os

mp_hands = mp.solutions.hands

class HandTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("El Takibi Arayüzü")

        # Ekranın genişlik ve yüksekliğini al
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Pencerenin genişlik ve yüksekliğini ayarla
        window_width = 1000
        window_height = 800

        # Pencerenin ekranın ortasına yerleştirilmesi için x ve y koordinatlarını hesapla
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.label_text = tk.StringVar()
        self.label_text.set("Hareket Eden El: Bilinmiyor")

        self.canvas = tk.Canvas(root, width=600, height=500)
        self.canvas.pack()

        self.info_label = ttk.Label(root, textvariable=self.label_text, font=("Arial", 16))
        self.info_label.pack()

        self.capture_button = ttk.Button(root, text="Fotoğraf Çek", command=self.capture_image)
        self.capture_button.pack(pady=10)

        self.close_button = ttk.Button(root, text="Kapat", command=self.close_camera)
        self.close_button.pack(pady=10)

        self.video_capture = cv2.VideoCapture(0)
        self.hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)
        self.count = 0

        self.update_frame()

        # Bind keys
        self.root.bind("<c>", self.capture_image_key)
        self.root.bind("<q>", self.close_camera_key)

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            image.flags.writeable = False
            results = self.hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            label_text = "Hareket Eden El: Bilinmiyor"  # Default value

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handedness.classification[0].label
                    if label == "Left":
                        label_text = "Hareket Eden El: Sol"
                    elif label == "Right":
                        label_text = "Hareket Eden El: Sağ"

                    # Kameraya sağ veya sol yazısını ekle
                    cv2.putText(image, label_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                    # Kare içinde mi kontrol et
                    if self.check_finger_in_box(hand_landmarks):
                        print("İçinde")
                        cv2.rectangle(image, (200, 200), (400, 400), (0, 128, 0), 3)
                    else:
                        print("Dışında")
                        cv2.rectangle(image, (200, 200), (400, 400), (0, 0, 255), 3)

            self.label_text.set(label_text)

            # PIL formatına dönüştür
            image = Image.fromarray(image)
            image_tk = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
            self.canvas.image_tk = image_tk

        self.root.after(30, self.update_frame)

    def check_finger_in_box(self, hand_landmarks):
        index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
        index_finger_mcp_x = int(index_finger_mcp.x * 600)
        index_finger_mcp_y = int(index_finger_mcp.y * 500)
        pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
        pinky_mcp_x = int(pinky_mcp.x * 600)
        pinky_mcp_y = int(pinky_mcp.y * 500)
    
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        wrist_x = int(wrist.x * 600)
        wrist_y = int(wrist.y * 500)
    
        # Kare içinde mi kontrol et
        if 200 < index_finger_mcp_x < 400 and 200 < index_finger_mcp_y < 400 and \
           200 < pinky_mcp_x < 400 and 200 < pinky_mcp_y < 400 and \
           200 < wrist_x < 400 and 200 < wrist_y < 400:
            return True
        else:
            return False
            # Kare içinde mi kontrol et
            if 200 < index_finger_mcp_x < 400 and 200 < index_finger_mcp_y < 400:
                return True
            else:
                return False
    def crop_image(self, frame):
        # Kare içine alınacak bölgenin koordinatları
        x1, y1, x2, y2 = 200, 200, 400, 400

        # Kare içine alınacak bölgeyi kırp
        cropped_image = frame[y1:y2, x1:x2]

        return cropped_image
    def capture_image(self):
        ret, frame = self.video_capture.read()
        if ret:
            directory = r'/home/pi/Desktop/New/Resimler/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            while os.path.exists(os.path.join(directory, f"{self.count}.jpg")):
                self.count += 1
        cropped_image = self.crop_image(frame)
        cv2.imwrite(os.path.join(directory, f"{self.count}.jpg"), cropped_image)
        self.count += 1
        
        self.info_label.config(text=f"Fotoğraf çekildi. Hareket Eden El: {self.label_text.get()}")

    def capture_image_key(self, event):
        self.capture_image()

    def close_camera(self):
        self.video_capture.release()
        self.root.destroy()

    def close_camera_key(self, event):
        self.close_camera()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandTrackingApp(root)
    root.mainloop()
