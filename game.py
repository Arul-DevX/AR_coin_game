import cv2
import numpy as np
import random
import mediapipe as mp
import pygame
import json
import os

# Initialize pygame for background music and sound effects
pygame.mixer.init()

# --- Load Background Music ---
try:
    pygame.mixer.music.load('background.wav')
    pygame.mixer.music.play(-1)  # Play the music in a loop
except pygame.error as e:
    print(f"Could not load background music: {e}")

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize mediapipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# Game settings
coin_size = 60
bomb_size = 70
initial_fall_speed = 3
fall_speed = initial_fall_speed
score = 0
num_coins = 5
missed_coins = 0
max_missed_coins = 5
game_over = False

# High score system
HIGH_SCORE_FILE = "high_score.json"

def load_high_score():
    """Load high score from file"""
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return 0

def save_high_score(score):
    """Save high score to file"""
    try:
        data = {'high_score': score}
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Could not save high score: {e}")

# Load high score at startup
high_score = load_high_score()
final_score = 0  # Store final score when game ends

# --- Load Images ---
try:
    coin_image = cv2.imread('coin.png', cv2.IMREAD_UNCHANGED)
    coin_image = cv2.resize(coin_image, (coin_size, coin_size))
    bomb_image = cv2.imread('bomb.png', cv2.IMREAD_UNCHANGED)
    bomb_image = cv2.resize(bomb_image, (bomb_size, bomb_size))
except Exception as e:
    print(f"Error loading images: {e}")
    exit()

# --- Load Sound Effects ---
try:
    coin_sound = pygame.mixer.Sound('coin_sound.wav')
    game_over_sound = pygame.mixer.Sound('game-over.wav')
    new_high_score_sound = pygame.mixer.Sound('new_high_score.wav')  # Optional new high score sound
except pygame.error as e:
    print(f"Could not load sound effect: {e}")

# Desired new screen width
desired_screen_width = 1280

# Function to create a random coin position
def create_coin(screen_width):
    x = random.randint(0, screen_width - coin_size)
    y = 0
    return (x, y)

# Function to create a random bomb position
def create_bomb(screen_width):
    x = random.randint(0, screen_width - bomb_size)
    y = 0
    return (x, y)

# Check if hand touches object (coin or bomb)
def check_touch(obj, hand_position, obj_size):
    obj_x, obj_y = obj
    hand_x, hand_y = hand_position
    distance = np.sqrt((obj_x + obj_size // 2 - hand_x)**2 + (obj_y + obj_size // 2 - hand_y)**2)
    return distance < obj_size // 2

def draw_game_over_screen(frame, current_score, high_score, is_new_high_score):
    """Draw the game over screen with scores"""
    frame_height, frame_width = frame.shape[:2]
    
    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Game Over title
    cv2.putText(frame, 'GAME OVER', (frame_width // 2 - 150, frame_height // 2 - 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    
    # Final Score
    cv2.putText(frame, f'Final Score: {current_score}', (frame_width // 2 - 120, frame_height // 2 - 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # High Score
    if is_new_high_score:
        cv2.putText(frame, 'NEW HIGH SCORE!', (frame_width // 2 - 140, frame_height // 2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'High Score: {high_score}', (frame_width // 2 - 110, frame_height // 2 + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, f'High Score: {high_score}', (frame_width // 2 - 110, frame_height // 2 + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Restart instruction
    cv2.putText(frame, 'Press R to Restart', (frame_width // 2 - 120, frame_height // 2 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# Initialize game variables
screen_width = None
screen_height = None
coins = None
bomb = None
bomb_falling = False
new_high_score_achieved = False

# Main game loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]

    # Initialize game objects once we have frame dimensions
    if screen_width is None:
        resize_factor = desired_screen_width / frame_width
        resized_frame_height = int(frame_height * resize_factor)
        
        screen_width = desired_screen_width
        screen_height = resized_frame_height
        
        coins = [create_coin(screen_width) for _ in range(num_coins)]
        bomb = create_bomb(screen_width)

    # Calculate padding for display
    resize_factor = desired_screen_width / frame_width
    resized_frame_height = int(frame_height * resize_factor)

    # Resize the frame to desired width
    frame = cv2.resize(frame, (desired_screen_width, resized_frame_height))

    if not game_over:
        # Increase falling speed based on the score
        fall_speed = initial_fall_speed + (score // 7)

        # Overlay coin images
        for i, (coin_x, coin_y) in enumerate(coins):
            if (coin_y >= 0 and coin_y + coin_size <= frame.shape[0] and 
                coin_x >= 0 and coin_x + coin_size <= frame.shape[1]):
                
                alpha_coin = coin_image[:, :, 3] / 255.0
                alpha_frame = 1.0 - alpha_coin
                try:
                    for c in range(0, 3):
                        frame[coin_y:coin_y + coin_size, coin_x:coin_x + coin_size, c] = (
                            alpha_coin * coin_image[:, :, c] +
                            alpha_frame * frame[coin_y:coin_y + coin_size, coin_x:coin_x + coin_size, c])
                except (IndexError, ValueError):
                    pass
            
            coins[i] = (coin_x, coin_y + fall_speed)
            
            if coin_y > frame.shape[0]:
                coins[i] = create_coin(screen_width)
                missed_coins += 1
                if missed_coins >= max_missed_coins:
                    game_over = True
                    final_score = score
                    # Check for new high score
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                        new_high_score_achieved = True
                        try:
                            new_high_score_sound.play()
                        except NameError:
                            pass
                    else:
                        try:
                            game_over_sound.play()
                        except NameError:
                            pass

        # Bomb logic
        if score % 2 == 0 and score > 0 and not bomb_falling:
            bomb_falling = True
            bomb = create_bomb(screen_width)
        
        if bomb_falling:
            bomb_x, bomb_y = bomb
            if (bomb_y >= 0 and bomb_y + bomb_size <= frame.shape[0] and 
                bomb_x >= 0 and bomb_x + bomb_size <= frame.shape[1]):
                
                alpha_bomb = bomb_image[:, :, 3] / 255.0
                alpha_frame = 1.0 - alpha_bomb
                try:
                    for c in range(0, 3):
                        frame[bomb_y:bomb_y + bomb_size, bomb_x:bomb_x + bomb_size, c] = (
                            alpha_bomb * bomb_image[:, :, c] +
                            alpha_frame * frame[bomb_y:bomb_y + bomb_size, bomb_x:bomb_x + bomb_size, c])
                except (IndexError, ValueError):
                    pass
            
            bomb = (bomb_x, bomb_y + fall_speed)
            
            if bomb_y > frame.shape[0]:
                bomb_falling = False

        # Hand detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_hands = hands.process(rgb_frame)

        if result_hands.multi_hand_landmarks:
            for hand_landmarks in result_hands.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[8]
                hand_x = int(index_finger_tip.x * desired_screen_width)
                hand_y = int(index_finger_tip.y * resized_frame_height)
                hand_position = (hand_x, hand_y)

                cv2.circle(frame, (hand_x, hand_y), 5, (0, 0, 255), -1)
                
                # Check if hand touches any coin
                for i, coin_position in enumerate(coins):
                    if check_touch(coin_position, hand_position, coin_size):
                        score += 1
                        try:
                            coin_sound.play()
                        except NameError:
                            pass
                        coins[i] = create_coin(screen_width)

                # Check if hand touches the bomb
                if bomb_falling and check_touch(bomb, hand_position, bomb_size):
                    game_over = True
                    final_score = score
                    # Check for new high score
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                        new_high_score_achieved = True
                        try:
                            new_high_score_sound.play()
                        except NameError:
                            pass
                    else:
                        try:
                            game_over_sound.play()
                        except NameError:
                            pass
                    bomb_falling = False
                
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Display current score and high score during gameplay
        cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'High Score: {high_score}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f'Speed: {fall_speed}', (desired_screen_width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Missed: {missed_coins}/{max_missed_coins}', (desired_screen_width - 200, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
    else:
        # Draw game over screen with scores
        draw_game_over_screen(frame, final_score, high_score, new_high_score_achieved)

    # Show frame
    cv2.imshow('AR Coin Game', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('r') and game_over:
        # Reset game
        score = 0
        missed_coins = 0
        game_over = False
        fall_speed = initial_fall_speed
        new_high_score_achieved = False
        coins = [create_coin(screen_width) for _ in range(num_coins)]
        bomb = create_bomb(screen_width)
        bomb_falling = False

# Release resources
cap.release()
cv2.destroyAllWindows()