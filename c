import cv2
import numpy as np
import mediapipe as mp
import pygame

# Initialize camera
cap = cv2.VideoCapture(0)

# Load coin image
coin_img = cv2.imread('coin.png', -1)

if coin_img is None:
    print("Error: Unable to load the coin image.")
    exit()

# Initialize MediaPipe hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize Pygame for sound effects
pygame.mixer.init()
coin_sound = pygame.mixer.Sound('coin_sound.wav')

# Initialize variables
score = 0
coin_x, coin_y = np.random.randint(0, cap.get(cv2.CAP_PROP_FRAME_WIDTH) - coin_img.shape[1]), 0  # Initial coin position

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from the camera.")
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform hand detection
    results = hands.process(frame_rgb)

    # If hands are detected, check for interactions with the falling coin
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                # Check if hand is open (for example)
                if landmark.visibility > 0.5:
                    hand_x = int(landmark.x * frame.shape[1])
                    hand_y = int(landmark.y * frame.shape[0])

                    # Check for interactions between hands and falling coin
                    if (hand_x >= coin_x and hand_x <= coin_x + coin_img.shape[1]) and (hand_y >= coin_y and hand_y <= coin_y + coin_img.shape[0]):
                        score += 1  # Increase score when hand catches the coin
                        coin_x, coin_y = np.random.randint(0, cap.get(cv2.CAP_PROP_FRAME_WIDTH) - coin_img.shape[1]), 0  # Reset coin position
                        coin_sound.play()  # Play coin sound when caught

    # Draw falling coin on the frame
    coin_y += 2  # Adjust the falling speed
    if coin_y > cap.get(cv2.CAP_PROP_FRAME_HEIGHT) - coin_img.shape[0]:
        coin_x, coin_y = np.random.randint(0, cap.get(cv2.CAP_PROP_FRAME_WIDTH) - coin_img.shape[1]), 0  # Reset coin position if it reaches the bottom

    # Overlay the coin on the frame
    overlay = frame.copy()
    overlay[coin_y:coin_y + coin_img.shape[0], coin_x:coin_x + coin_img.shape[1]] = coin_img[:, :, :3]
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    # Display score
    cv2.putText(frame, f'Score: {score}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display frame
    cv2.imshow('Catch the Coin', frame)

    # Check for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
