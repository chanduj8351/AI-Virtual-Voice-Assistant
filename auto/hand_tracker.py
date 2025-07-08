import cv2
import pyautogui
import numpy as np
from cvzone.HandTrackingModule import HandDetector

class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.8):
        # Initialize the webcam
        self.cap = cv2.VideoCapture(0)
        
        # Initialize the HandDetector
        self.detector = HandDetector(maxHands=max_hands, detectionCon=detection_confidence)
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Webcam resolution (default to 640x480, adjust if needed)
        self.webcam_width = 640
        self.webcam_height = 480

        # Thresholds
        self.select_min_threshold = 10  # Minimum threshold for selection
        self.select_max_threshold = 30  # Maximum threshold for selection
        self.drag_min_threshold = 15    # Minimum threshold for dragging
        self.drag_max_threshold = 55    # Maximum threshold for dragging
        self.right_click_threshold = 10  # Threshold for right-click detection

        # State for detecting drag, selection, and right-click
        self.touch_detected = False
        self.dragging = False
        self.right_click_triggered = False

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def move_cursor_and_interact(self):
        while True:
            # Capture frame from webcam
            success, img = self.cap.read()
            img = cv2.flip(img, 1)

            # Detect hand(s)
            hands, img = self.detector.findHands(img)

            if hands:
                # Get the first hand detected
                hand = hands[0]
                lmList = hand['lmList']  # List of landmarks

                # Get the index finger tip, thumb tip, and middle finger tip positions
                index_finger_tip = lmList[8][:2]
                thumb_tip = lmList[4][:2]
                middle_finger_tip = lmList[12][:2]

                # Calculate distances between thumb and index finger tips, and index and middle finger tips
                distance_thumb_index = self.calculate_distance(index_finger_tip, thumb_tip)
                distance_index_middle = self.calculate_distance(index_finger_tip, middle_finger_tip)

                # Normalize the index finger position to be within the screen bounds
                normalized_index_x = min(max(index_finger_tip[0], 0), self.webcam_width)
                normalized_index_y = min(max(index_finger_tip[1], 0), self.webcam_height)

                # Map the normalized position to screen dimensions
                screen_x = int(normalized_index_x * self.screen_width / self.webcam_width)
                screen_y = int(normalized_index_y * self.screen_height / self.webcam_height)

                # Move the mouse cursor
                pyautogui.moveTo(screen_x, screen_y)

                # Check for click (select) action
                if self.select_min_threshold < distance_thumb_index < self.select_max_threshold:
                    if not self.touch_detected:
                        pyautogui.click()
                        self.touch_detected = True
                        print("Selection performed")
                # Check for drag action
                elif self.drag_min_threshold < distance_thumb_index < self.drag_max_threshold:
                    if not self.dragging:
                        pyautogui.mouseDown()
                        self.dragging = True
                        self.touch_detected = True
                        print("Drag started")
                        print(screen_x, screen_y)
                elif distance_thumb_index > self.drag_max_threshold:
                    if self.dragging:
                        pyautogui.mouseUp()
                        self.dragging = False
                        self.touch_detected = False
                        print("Drag ended")
                else:
                    self.touch_detected = False

                # Check for right-click action
                if distance_index_middle < self.right_click_threshold:
                    if not self.right_click_triggered:
                        pyautogui.rightClick()
                        self.right_click_triggered = True
                        print("Right click performed")
                else:
                    self.right_click_triggered = False

                # Visual feedback on the webcam feed
                cv2.circle(img, (int(index_finger_tip[0]), int(index_finger_tip[1])), 15, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (int(thumb_tip[0]), int(thumb_tip[1])), 15, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (int(middle_finger_tip[0]), int(middle_finger_tip[1])), 15, (0, 255, 0), cv2.FILLED)
                
                # Highlight the cursor position with green color
                cv2.circle(img, (screen_x, screen_y), 10, (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f"Dist Thumb-Index: {distance_thumb_index:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(img, f"Dist Index-Middle: {distance_index_middle:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # Display the webcam image
            cv2.imshow("Image", img)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close windows
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    hand_tracker = HandTracker()
    hand_tracker.move_cursor_and_interact()
