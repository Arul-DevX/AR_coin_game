import cv2
import numpy as np
import random
import mediapipe as mp
import pygame
import json
import os
import time
import math
from datetime import datetime
from collections import deque

# Initialize pygame
pygame.mixer.init()

# --- Game Classes ---
class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 30
        self.max_life = 30
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        return self.life > 0
    
    def draw(self, frame):
        alpha = self.life / self.max_life
        color = tuple(int(c * alpha) for c in self.color)
        cv2.circle(frame, (int(self.x), int(self.y)), 3, color, -1)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.size = 50
        self.duration = 300  # frames
        
    def update(self, fall_speed):
        self.y += fall_speed
        return self.y < 800  # Return False if off screen

class GameStats:
    def __init__(self):
        self.games_played = 0
        self.total_coins_caught = 0
        self.total_bombs_avoided = 0
        self.total_time_played = 0
        self.best_combo = 0
        self.achievements = set()

# --- Load Assets ---
def load_audio():
    sounds = {}
    try:
        pygame.mixer.music.load('background.wav')
        pygame.mixer.music.play(-1)
        sounds['coin'] = pygame.mixer.Sound('coin_sound.wav')
        sounds['game_over'] = pygame.mixer.Sound('game-over.wav')
        sounds['bomb'] = pygame.mixer.Sound('bomb_explosion.wav')
        sounds['powerup'] = pygame.mixer.Sound('powerup.wav')
        sounds['combo'] = pygame.mixer.Sound('combo.wav')
        sounds['achievement'] = pygame.mixer.Sound('achievement.wav')
    except pygame.error as e:
        print(f"Audio loading error: {e}")
    return sounds

def load_game_data():
    """Load persistent game data"""
    try:
        if os.path.exists("game_data.json"):
            with open("game_data.json", 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'high_score': 0,
        'stats': {
            'games_played': 0,
            'total_coins_caught': 0,
            'total_bombs_avoided': 0,
            'total_time_played': 0,
            'best_combo': 0,
            'achievements': []
        },
        'leaderboard': []
    }

def save_game_data(data):
    """Save persistent game data"""
    try:
        with open("game_data.json", 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Could not save game data: {e}")

# --- Initialize Game ---
sounds = load_audio()
game_data = load_game_data()

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Game settings
coin_size = 60
bomb_size = 70
powerup_size = 50
initial_fall_speed = 3
fall_speed = initial_fall_speed
score = 0
num_coins = 5
missed_coins = 0
max_missed_coins = 5
game_over = False
desired_screen_width = 1280

# Game state variables
combo_count = 0
max_combo = 0
game_start_time = time.time()
particles = []
powerups = []
active_powerups = {}
hand_trails = {}  # Dictionary to store trails for each hand
MAX_TRAIL_LENGTH = 20
screen_shake = 0
bombs_avoided = 0
coins_caught_this_game = 0

# Power-up effects
POWERUP_TYPES = {
    'speed': {'color': (0, 255, 255), 'duration': 300},  # Cyan - slow motion
    'magnet': {'color': (255, 0, 255), 'duration': 200}, # Magenta - attract coins
    'shield': {'color': (0, 255, 0), 'duration': 150},   # Green - bomb protection
    'double': {'color': (255, 255, 0), 'duration': 250}  # Yellow - double points
}

# Achievement definitions
ACHIEVEMENTS = {
    'first_coin': {'name': 'First Blood', 'desc': 'Catch your first coin'},
    'speed_demon': {'name': 'Speed Demon', 'desc': 'Reach speed level 10'},
    'bomb_dodger': {'name': 'Bomb Dodger', 'desc': 'Avoid 50 bombs'},
    'perfectionist': {'name': 'Perfectionist', 'desc': 'Complete game without missing coins'},
    'combo_master': {'name': 'Combo Master', 'desc': 'Get 10+ combo'},
    'centurion': {'name': 'Centurion', 'desc': 'Score 100+ points'},
    'survivor': {'name': 'Survivor', 'desc': 'Survive 2 minutes'},
    'powerup_collector': {'name': 'Power Hunter', 'desc': 'Collect 10 power-ups'}
}

def check_achievements(score, combo, bombs_avoided, game_time, powerups_collected):
    """Check and award achievements"""
    new_achievements = []
    current_achievements = set(game_data['stats']['achievements'])
    
    if coins_caught_this_game >= 1 and 'first_coin' not in current_achievements:
        new_achievements.append('first_coin')
    if fall_speed >= 13 and 'speed_demon' not in current_achievements:  # Speed 10+ 
        new_achievements.append('speed_demon')
    if bombs_avoided >= 50 and 'bomb_dodger' not in current_achievements:
        new_achievements.append('bomb_dodger')
    if missed_coins == 0 and score > 0 and 'perfectionist' not in current_achievements:
        new_achievements.append('perfectionist')
    if combo >= 10 and 'combo_master' not in current_achievements:
        new_achievements.append('combo_master')
    if score >= 100 and 'centurion' not in current_achievements:
        new_achievements.append('centurion')
    if game_time >= 120 and 'survivor' not in current_achievements:
        new_achievements.append('survivor')
    if powerups_collected >= 10 and 'powerup_collector' not in current_achievements:
        new_achievements.append('powerup_collector')
    
    for achievement in new_achievements:
        game_data['stats']['achievements'].append(achievement)
        try:
            sounds['achievement'].play()
        except:
            pass
    
    return new_achievements

def create_particles(x, y, color, count=10):
    """Create particle explosion effect"""
    for _ in range(count):
        velocity = (random.randint(-5, 5), random.randint(-8, -2))
        particles.append(Particle(x, y, color, velocity))

def create_coin(screen_width):
    x = random.randint(0, screen_width - coin_size)
    y = random.randint(-100, -coin_size)
    return (x, y)

def create_bomb(screen_width):
    x = random.randint(0, screen_width - bomb_size)
    y = random.randint(-100, -bomb_size)
    return (x, y)

def create_powerup(screen_width):
    x = random.randint(0, screen_width - powerup_size)
    y = random.randint(-100, -powerup_size)
    power_type = random.choice(list(POWERUP_TYPES.keys()))
    return PowerUp(x, y, power_type)

def check_touch(obj, hand_position, obj_size):
    obj_x, obj_y = obj
    hand_x, hand_y = hand_position
    distance = np.sqrt((obj_x + obj_size // 2 - hand_x)**2 + (obj_y + obj_size // 2 - hand_y)**2)
    
    # Magnet effect
    if 'magnet' in active_powerups:
        return distance < obj_size * 1.5
    
    return distance < obj_size // 2

def detect_gesture(hand_landmarks):
    """Detect hand gestures for special actions"""
    landmarks = hand_landmarks.landmark
    
    # Peace sign detection (index and middle finger up)
    index_tip = landmarks[8].y
    index_pip = landmarks[6].y
    middle_tip = landmarks[12].y
    middle_pip = landmarks[10].y
    ring_tip = landmarks[16].y
    ring_pip = landmarks[14].y
    
    index_up = index_tip < index_pip
    middle_up = middle_tip < middle_pip
    ring_down = ring_tip > ring_pip
    
    if index_up and middle_up and ring_down:
        return 'peace'
    
    # Fist detection (all fingers down)
    fingers_down = all(landmarks[tip].y > landmarks[pip].y 
                      for tip, pip in [(8,6), (12,10), (16,14), (20,18)])
    if fingers_down:
        return 'fist'
    
    # Thumbs up
    thumb_up = landmarks[4].y < landmarks[3].y
    if thumb_up and fingers_down:
        return 'thumbs_up'
    
    return 'normal'

def draw_powerup(frame, powerup):
    """Draw power-up with animated effects"""
    color = POWERUP_TYPES[powerup.type]['color']
    
    # Pulsing effect
    pulse = int(20 * math.sin(time.time() * 5))
    size = powerup.size + pulse
    
    # Draw power-up
    cv2.circle(frame, (int(powerup.x + powerup.size//2), int(powerup.y + powerup.size//2)), 
               size//2, color, -1)
    cv2.circle(frame, (int(powerup.x + powerup.size//2), int(powerup.y + powerup.size//2)), 
               size//2, (255, 255, 255), 2)
    
    # Draw power-up symbol
    center_x, center_y = int(powerup.x + powerup.size//2), int(powerup.y + powerup.size//2)
    if powerup.type == 'speed':
        cv2.putText(frame, 'S', (center_x-8, center_y+8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    elif powerup.type == 'magnet':
        cv2.putText(frame, 'M', (center_x-8, center_y+8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    elif powerup.type == 'shield':
        cv2.putText(frame, 'S', (center_x-8, center_y+8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    elif powerup.type == 'double':
        cv2.putText(frame, '2X', (center_x-12, center_y+8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

def draw_ui(frame, score, high_score, combo, fall_speed, missed_coins, max_missed_coins, fps):
    """Draw game UI with enhanced information"""
    # Score panel background
    cv2.rectangle(frame, (5, 5), (300, 120), (0, 0, 0), -1)
    cv2.rectangle(frame, (5, 5), (300, 120), (255, 255, 255), 2)
    
    # Main stats
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f'High: {high_score}', (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.putText(frame, f'Combo: {combo}', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f'Speed: {fall_speed}', (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    # Right side info
    cv2.rectangle(frame, (frame.shape[1]-200, 5), (frame.shape[1]-5, 120), (0, 0, 0), -1)
    cv2.rectangle(frame, (frame.shape[1]-200, 5), (frame.shape[1]-5, 120), (255, 255, 255), 2)
    
    cv2.putText(frame, f'Missed: {missed_coins}/{max_missed_coins}', (frame.shape[1]-195, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
    cv2.putText(frame, f'FPS: {fps}', (frame.shape[1]-195, 55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    # NEW: Add combo speed indicator
    if combo >= 10:
        cv2.putText(frame, 'HIGH COMBO SPEED!', (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    elif combo >= 5:
        cv2.putText(frame, 'Combo Speed+', (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
    # Active power-ups
    y_offset = 80
    for powerup_type, remaining in active_powerups.items():
        color = POWERUP_TYPES[powerup_type]['color']
        cv2.putText(frame, f'{powerup_type.upper()}: {remaining//60}s', 
                   (frame.shape[1]-195, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        y_offset += 20

def draw_game_over_screen(frame, final_score, high_score, is_new_high_score, game_time, new_achievements):
    """Enhanced game over screen"""
    frame_height, frame_width = frame.shape[:2]
    
    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    # Game Over title with glow effect
    for offset in range(3, 0, -1):
        cv2.putText(frame, 'GAME OVER', (frame_width // 2 - 150 + offset, frame_height // 2 - 100 + offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (50, 50, 50), 3)
    cv2.putText(frame, 'GAME OVER', (frame_width // 2 - 150, frame_height // 2 - 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    
    # Score information
    y_pos = frame_height // 2 - 40
    cv2.putText(frame, f'Final Score: {final_score}', (frame_width // 2 - 120, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    y_pos += 40
    if is_new_high_score:
        # Flashing new high score
        flash_color = (0, 255, 0) if int(time.time() * 3) % 2 else (255, 255, 255)
        cv2.putText(frame, 'NEW HIGH SCORE!', (frame_width // 2 - 140, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, flash_color, 2)
    else:
        cv2.putText(frame, f'High Score: {high_score}', (frame_width // 2 - 110, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Game statistics
    y_pos += 60
    cv2.putText(frame, f'Max Combo: {max_combo}', (frame_width // 2 - 100, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    y_pos += 30
    cv2.putText(frame, f'Time: {int(game_time)}s', (frame_width // 2 - 70, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    y_pos += 30
    cv2.putText(frame, f'Coins Caught: {coins_caught_this_game}', (frame_width // 2 - 110, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 215, 0), 2)
    
    # New achievements
    if new_achievements:
        y_pos += 50
        cv2.putText(frame, 'NEW ACHIEVEMENTS:', (frame_width // 2 - 130, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        for i, achievement in enumerate(new_achievements[:3]):  # Show max 3
            y_pos += 25
            achievement_name = ACHIEVEMENTS[achievement]['name']
            cv2.putText(frame, f'• {achievement_name}', (frame_width // 2 - 100, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Controls
    cv2.putText(frame, 'Press R to Restart | Q to Quit', (frame_width // 2 - 160, frame_height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def update_powerups():
    """Update active power-up timers"""
    global active_powerups
    expired_powerups = []
    
    for powerup_type in list(active_powerups.keys()):
        active_powerups[powerup_type] -= 1
        if active_powerups[powerup_type] <= 0:
            expired_powerups.append(powerup_type)
    
    for powerup_type in expired_powerups:
        del active_powerups[powerup_type]

def draw_hand_trail(frame):
    """Draw separate glowing trails for each hand"""
    for hand_id, trail in hand_trails.items():
        if len(trail) > 1:
            # Create a unique color for each hand
            colors = [(0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 255, 0)]  # Cyan, Magenta, Green, Yellow
            trail_color = colors[hand_id % len(colors)]
            
            for i in range(len(trail) - 1):
                if i < len(trail) - 1:
                    alpha = (i + 1) / len(trail)  # Fade effect
                    thickness = int(8 * alpha)
                    if thickness > 0:
                        cv2.line(frame, trail[i], trail[i + 1], trail_color, thickness)

def apply_screen_shake(frame):
    """Apply screen shake effect"""
    global screen_shake
    if screen_shake > 0:
        shake_x = random.randint(-screen_shake, screen_shake)
        shake_y = random.randint(-screen_shake, screen_shake)
        
        # Create transformation matrix for shake
        rows, cols = frame.shape[:2]
        M = np.float32([[1, 0, shake_x], [0, 1, shake_y]])
        frame = cv2.warpAffine(frame, M, (cols, rows))
        screen_shake -= 1
    
    return frame

# Initialize game variables
screen_width = None
screen_height = None
coins = None
bombs = []
bomb_spawn_timer = 0
powerup_spawn_timer = 0
last_frame_time = time.time()
fps = 0
powerups_collected = 0
new_achievements_this_game = []

# Load images with error handling
coin_image = None
bomb_image = None

try:
    coin_image = cv2.imread('coin.png', cv2.IMREAD_UNCHANGED)
    if coin_image is not None:
        coin_image = cv2.resize(coin_image, (coin_size, coin_size))
    bomb_image = cv2.imread('bomb.png', cv2.IMREAD_UNCHANGED)
    if bomb_image is not None:
        bomb_image = cv2.resize(bomb_image, (bomb_size, bomb_size))
except Exception as e:
    print(f"Error loading images: {e}")

# Main game loop
while True:
    frame_start_time = time.time()
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]

    # Initialize game objects
    if screen_width is None:
        resize_factor = desired_screen_width / frame_width
        resized_frame_height = int(frame_height * resize_factor)
        screen_width = desired_screen_width
        screen_height = resized_frame_height
        coins = [create_coin(screen_width) for _ in range(num_coins)]

    # Resize frame
    frame = cv2.resize(frame, (desired_screen_width, int(frame_height * desired_screen_width / frame_width)))

    if not game_over:
        # Calculate dynamic fall speed WITH COMBO BONUS
        base_speed = initial_fall_speed + (score // 7)

        # High combo speed boost - NEW CODE
        combo_speed_bonus = 0
        if combo_count >= 15:
            combo_speed_bonus = 5  # Extreme speed at 15+ combo
        elif combo_count >= 10:
            combo_speed_bonus = 3  # High speed at 10+ combo
        elif combo_count >= 5:
            combo_speed_bonus = 1  # Moderate speed at 5+ combo

        # Apply combo speed bonus
        base_speed += combo_speed_bonus

        # Apply power-up effects
        current_fall_speed = base_speed
        if 'speed' in active_powerups:
            current_fall_speed = max(1, base_speed // 3)  # Slow motion

        fall_speed = current_fall_speed

        
        # Update power-ups
        update_powerups()
        
        # Spawn power-ups randomly
        powerup_spawn_timer += 1
        if powerup_spawn_timer > 300 and random.random() < 0.3:  # 30% chance every 5 seconds
            powerups.append(create_powerup(screen_width))
            powerup_spawn_timer = 0

        # Update and draw coins
        for i, (coin_x, coin_y) in enumerate(coins):
            # Draw coin (use circle if image not available)
            if coin_image is not None and (coin_y >= 0 and coin_y + coin_size <= frame.shape[0] and 
                                          coin_x >= 0 and coin_x + coin_size <= frame.shape[1]):
                try:
                    alpha_coin = coin_image[:, :, 3] / 255.0
                    alpha_frame = 1.0 - alpha_coin
                    for c in range(0, 3):
                        frame[coin_y:coin_y + coin_size, coin_x:coin_x + coin_size, c] = (
                            alpha_coin * coin_image[:, :, c] +
                            alpha_frame * frame[coin_y:coin_y + coin_size, coin_x:coin_x + coin_size, c])
                except:
                    pass
            else:
                # Fallback: draw circle
                cv2.circle(frame, (coin_x + coin_size//2, coin_y + coin_size//2), 
                          coin_size//2, (0, 215, 255), -1)
            
            coins[i] = (coin_x, coin_y + fall_speed)
            
            if coin_y > frame.shape[0]:
                coins[i] = create_coin(screen_width)
                missed_coins += 1
                combo_count = 0  # Reset combo on miss
                if missed_coins >= max_missed_coins:
                    game_over = True
                    final_score = score
                    game_time = time.time() - game_start_time

        # Update and draw bombs
        bomb_spawn_timer += 1
        if bomb_spawn_timer > 180 and len(bombs) < 3:  # Spawn bomb every 3 seconds, max 3
            bombs.append(create_bomb(screen_width))
            bomb_spawn_timer = 0

        # Update bombs (iterate backwards to safely remove items)
        for i in range(len(bombs) - 1, -1, -1):
            bomb_x, bomb_y = bombs[i]
            
            # Draw bomb
            if bomb_image is not None and (bomb_y >= 0 and bomb_y + bomb_size <= frame.shape[0] and 
                                          bomb_x >= 0 and bomb_x + bomb_size <= frame.shape[1]):
                try:
                    alpha_bomb = bomb_image[:, :, 3] / 255.0
                    alpha_frame = 1.0 - alpha_bomb
                    for c in range(0, 3):
                        frame[bomb_y:bomb_y + bomb_size, bomb_x:bomb_x + bomb_size, c] = (
                            alpha_bomb * bomb_image[:, :, c] +
                            alpha_frame * frame[bomb_y:bomb_y + bomb_size, bomb_x:bomb_x + bomb_size, c])
                except:
                    pass
            else:
                # Fallback: draw circle
                cv2.circle(frame, (bomb_x + bomb_size//2, bomb_y + bomb_size//2), 
                          bomb_size//2, (0, 0, 255), -1)
            
            # Update bomb position
            new_bomb_y = bomb_y + fall_speed
            
            if new_bomb_y > frame.shape[0]:
                # Remove bomb if it goes off screen
                bombs.pop(i)
                bombs_avoided += 1
            else:
                # Update bomb position
                bombs[i] = (bomb_x, new_bomb_y)

        # Update and draw power-ups (iterate backwards to safely remove items)
        for i in range(len(powerups) - 1, -1, -1):
            powerup = powerups[i]
            if powerup.update(fall_speed):
                draw_powerup(frame, powerup)
            else:
                powerups.pop(i)

        # Hand detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_hands = hands.process(rgb_frame)

        gesture_detected = 'normal'
        if result_hands.multi_hand_landmarks:
            for hand_id, hand_landmarks in enumerate(result_hands.multi_hand_landmarks):
                # Detect gestures
                gesture_detected = detect_gesture(hand_landmarks)
                
                # Handle special gestures
                if gesture_detected == 'peace' and 'shield' not in active_powerups:
                    active_powerups['shield'] = 300
                    try:
                        sounds['powerup'].play()
                    except:
                        pass
                elif gesture_detected == 'fist':
                    # Destroy all bombs
                    if bombs:
                        bombs.clear()
                        bombs_avoided += len(bombs)
                        create_particles(frame_width//2, frame_height//2, (255, 0, 0), 20)
                elif gesture_detected == 'thumbs_up' and 'speed' not in active_powerups:
                    active_powerups['speed'] = 200
                    try:
                        sounds['powerup'].play()
                    except:
                        pass

                # Get hand position
                index_finger_tip = hand_landmarks.landmark[8]
                hand_x = int(index_finger_tip.x * desired_screen_width)
                hand_y = int(index_finger_tip.y * frame.shape[0])
                hand_position = (hand_x, hand_y)
                
                # Add to specific hand trail
                if hand_id not in hand_trails:
                    hand_trails[hand_id] = deque(maxlen=MAX_TRAIL_LENGTH)
                hand_trails[hand_id].append(hand_position)
                
                # Draw hand indicator with unique color per hand
                hand_colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0)]  # Red, Blue, Green, Yellow
                hand_color = hand_colors[hand_id % len(hand_colors)]
                
                cv2.circle(frame, hand_position, 8, hand_color, -1)
                cv2.circle(frame, hand_position, 12, (255, 255, 255), 2)
                
                # Check coin collisions
                for i, coin_position in enumerate(coins):
                    if check_touch(coin_position, hand_position, coin_size):
                        # Score calculation
                        points = 1
                        if 'double' in active_powerups:
                            points *= 2
                        
                        score += points
                        combo_count += 1
                        max_combo = max(max_combo, combo_count)
                        coins_caught_this_game += 1
                        
                        # Particle effects - CORRECTED VERSION
                        create_particles(coin_position[0] + coin_size//2,
                                    coin_position[1] + coin_size//2, (255, 215, 0))
                        
                        # Sound effects
                        try:
                            if combo_count >= 10:
                                sounds['combo'].play()
                            else:
                                sounds['coin'].play()
                        except:
                            pass
                        
                        coins[i] = create_coin(screen_width)



                # Check power-up collisions (iterate backwards to safely remove items)
                for i in range(len(powerups) - 1, -1, -1):
                    powerup = powerups[i]
                    if check_touch((powerup.x, powerup.y), hand_position, powerup.size):
                        active_powerups[powerup.type] = POWERUP_TYPES[powerup.type]['duration']
                        powerups_collected += 1
                        create_particles(powerup.x + powerup.size//2, powerup.y + powerup.size//2, 
                                       POWERUP_TYPES[powerup.type]['color'])
                        try:
                            sounds['powerup'].play()
                        except:
                            pass
                        powerups.pop(i)

                # Check bomb collisions (iterate backwards to safely remove items)
                # Check bomb collisions (iterate backwards to safely remove items)
                for i in range(len(bombs) - 1, -1, -1):
                    bomb_position = bombs[i]
                    if check_touch(bomb_position, hand_position, bomb_size):
                        if 'shield' in active_powerups:
                            # Shield protects from bomb
                            del active_powerups['shield']
                            bombs.pop(i)
                            create_particles(bomb_position[0] + bomb_size//2, 
                                        bomb_position[1] + bomb_size//2, (0, 255, 0))
                        else:
                            # Game over from bomb
                            game_over = True
                            final_score = score
                            game_time = time.time() - game_start_time
                            screen_shake = 20
                            create_particles(bomb_position[0] + bomb_size//2, 
                                        bomb_position[1] + bomb_size//2, (255, 0, 0), 30)
                            try:
                                sounds['bomb'].play()
                            except:
                                pass

                        break  # Exit loop after collision

                # Draw hand landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            # Gradually fade out trails when no hands are detected
            for hand_id in list(hand_trails.keys()):
                if len(hand_trails[hand_id]) > 0:
                    hand_trails[hand_id].popleft()  # Remove oldest point
                if len(hand_trails[hand_id]) == 0:
                    del hand_trails[hand_id]  # Remove empty trails

        # Update particles
        particles = [p for p in particles if p.update()]
        for particle in particles:
            particle.draw(frame)

        # Draw hand trail
        draw_hand_trail(frame)

        # Check achievements
        current_game_time = time.time() - game_start_time
        new_achievements_this_game = check_achievements(score, combo_count, bombs_avoided, 
                                                       current_game_time, powerups_collected)

        # Calculate FPS
        current_time = time.time()
        fps = int(1.0 / (current_time - last_frame_time + 0.001))
        last_frame_time = current_time

        # Draw UI
        draw_ui(frame, score, game_data['high_score'], combo_count, fall_speed, 
                missed_coins, max_missed_coins, fps)
        
        # Apply screen shake
        frame = apply_screen_shake(frame)

    else:
        # Game over logic
        is_new_high_score = score > game_data['high_score']
        if is_new_high_score:
            game_data['high_score'] = score
        
        # Update statistics
        game_data['stats']['games_played'] += 1
        game_data['stats']['total_coins_caught'] += coins_caught_this_game
        game_data['stats']['total_bombs_avoided'] += bombs_avoided
        game_data['stats']['total_time_played'] += int(time.time() - game_start_time)
        if max_combo > game_data['stats']['best_combo']:
            game_data['stats']['best_combo'] = max_combo
        
        # Add to leaderboard
        leaderboard_entry = {
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'combo': max_combo,
            'time': int(time.time() - game_start_time)
        }
        game_data['leaderboard'].append(leaderboard_entry)
        game_data['leaderboard'] = sorted(game_data['leaderboard'], 
                                        key=lambda x: x['score'], reverse=True)[:10]
        
        # Save game data
        save_game_data(game_data)
        
        # Draw game over screen
        draw_game_over_screen(frame, score, game_data['high_score'], is_new_high_score, 
                            time.time() - game_start_time, new_achievements_this_game)

    # Show frame
    cv2.imshow('Enhanced AR Coin Game', frame)

    # Handle input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r') and game_over:
        # Reset game
        score = 0
        missed_coins = 0
        combo_count = 0
        max_combo = 0
        game_over = False
        fall_speed = initial_fall_speed
        coins_caught_this_game = 0
        bombs_avoided = 0
        powerups_collected = 0
        game_start_time = time.time()
        screen_shake = 0
        
        # Reset game objects
        coins = [create_coin(screen_width) for _ in range(num_coins)]
        bombs.clear()
        powerups.clear()
        active_powerups.clear()
        particles.clear()
        hand_trails.clear()  # Clear all hand trails
        new_achievements_this_game.clear()
        
        bomb_spawn_timer = 0
        powerup_spawn_timer = 0
    elif key == ord('a') and game_over:
        # Show achievements screen (optional feature)
        print("\n=== ACHIEVEMENTS ===")
        for achievement_id, data in ACHIEVEMENTS.items():
            status = "✓" if achievement_id in game_data['stats']['achievements'] else "✗"
            print(f"{status} {data['name']}: {data['desc']}")
        print("==================\n")
    # NEW: Warning effect when approaching high combo (add this before cv2.imshow)
    if combo_count == 9:  # About to hit 10
        # Flash the screen border - FIXED VERSION
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (255, 255, 0), 5)

# Cleanup
cap.release()
cv2.destroyAllWindows()

# Final save
save_game_data(game_data)