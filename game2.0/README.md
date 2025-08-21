# Enhanced AR Coin Game
An immersive **Augmented Reality Hand-Tracking Game** that combines computer vision with
interactive gameplay.
Use your **webcam** and hand movements to catch coins, avoid bombs, and collect power-ups in
this skill-based arcade experience.
---
## Features
### Core Gameplay
- **Hand Tracking Control**: Use your webcam to detect hand movements – no keyboard/mouse
needed!
- **Dual-Hand Support**: Play with both hands simultaneously with separate colored trails
- **Catch Golden Coins**: Touch coins with your finger to score points
- **Avoid Red Bombs**: Dodge bombs or face game over (unless protected)
- **Dynamic Difficulty**: Speed increases with score and combo achievements
### Advanced Features
- **Combo System**: Chain consecutive catches for speed bonuses & special effects
- **Power-Up System**: 4 different power-ups with unique abilities
- **Gesture Controls**: Special hand gestures for instant power activation
- **Particle Effects**: Beautiful visual feedback for all interactions
- **Achievement System**: 8 unlockable achievements with persistent tracking
- **Persistent Data**: High scores, statistics, and achievements saved between sessions
---
## Installation
### Prerequisites
```bash
pip install opencv-python mediapipe pygame numpy
```
### Required Files
Place these audio files in the same directory (optional):
- `background.wav` – Background music
- `coin_sound.wav` – Coin collection sound
- `game-over.wav` – Game over sound
- `bomb_explosion.wav` – Bomb explosion sound
- `powerup.wav` – Power-up collection sound
- `combo.wav` – Combo achievement sound
- `achievement.wav` – Achievement unlock sound
Optional images (for custom sprites):
- `coin.png` (60x60px)
- `bomb.png` (70x70px)
---
## How to Play
### Basic Controls
- **Start the Game**: Run the Python script
- **Position Yourself**: Sit 2–3 feet from webcam with good lighting
- **Move Your Hands**: Use index finger to touch falling objects
- **Catch Coins**: Golden coins increase your score & combo
- **Avoid Bombs**: Red bombs end the game (unless shielded)
### Keyboard Controls
- `Q`: Quit game
- `R`: Restart game (when game over)
- `A`: Show achievements list (when game over)
---
## Power-Up System
### Available Power-Ups
- **Speed Boost (Cyan 'S')**: Slows down falling objects
- **Magnet (Purple 'M')**: Attracts coins from distance
- **Shield (Green 'S')**: Protects from one bomb
- **Double Points (Yellow '2X')**: Doubles coin score
### Gesture Controls 
- ✌**Peace Sign**: Activate shield
-  **Fist**: Destroy all bombs
-  **Thumbs Up**: Slow-motion mode
---
##  Combo System
- Catch coins consecutively to build **combo streaks**
- Missing a coin resets combo
- Higher combos = faster speed & extra challenge
**Speed Bonuses:**
- Combo 5–9: +1 speed
- Combo 10–14: +3 speed
- Combo 15+: +5 speed
**Combo Benefits:**
- Special sound at 5+ combo
- Border warning at 9 combo
- Achievement unlock at 10+ combo
---
##  Achievement System
Unlock milestones:
- **First Blood**: Catch your first coin
- **Speed Demon**: Reach speed level 10
- **Bomb Dodger**: Avoid 50 bombs
- **Perfectionist**: No missed coins in a game
- **Combo Master**: 10+ combo streak
- **Centurion**: Score 100+ points
- **Survivor**: Survive 2 minutes
- **Power Hunter**: Collect 10 power-ups
---
##  Game Statistics
Tracks & saves:
- High scores + leaderboard (top 10)
- Total games played
- Coins caught / bombs avoided
- Playtime & best combo
- Achievement progress
---
##  Visual Features
- **Hand Tracking**: Separate colored trails & smooth fading effects
- **Special Effects**:
- Golden sparkles for coins
- Red explosions for bombs
- Screen shake for collisions
- Animated power-up icons
- Real-time UI stats
---
##  Technical Requirements
### Hardware
- Webcam (USB or built-in)
- Good lighting (bright & even)
- 2–3 feet distance from camera
### Software
- Python 3.7+
- OpenCV 4.0+
- MediaPipe 0.8+
- Pygame 2.0+
- NumPy
---
## Troubleshooting
- **Hand not detected**: Improve lighting & clean lens
- **Lag/FPS issues**: Lower video resolution
- **No audio**: Ensure sound files are in same folder
- **Game too fast/slow**: Tweak `initial_fall_speed`
**Performance Tips:**
- Use solid background
- Place camera at chest height
- Keep both hands visible
---
##  File Structure
```text
game2.0/
├── game_2.0.py
├── game_data.json
├── background.wav
├── coin_sound.wav
├── game-over.wav
├── bomb_explosion.wav
├── powerup.wav
├── combo.wav
├── achievement.wav
├── coin.png
├── bomb.png
└── README.md

```
---
##  Tips for High Scores
- Master **combos** – safer than chasing every coin
- Use **power-ups smartly** – save shields for late game
- Learn **gesture controls** – instant clutch moves
- Use **both hands** for max coverage
- Don’t risk combos – sometimes skipping is better
- Watch **speed scaling** at high combos
---
##  Updates & Modifications
### Easy Customizations
- Change `initial_fall_speed` for difficulty
- Adjust `max_missed_coins` for leniency
- Resize `coin_size`, `bomb_size`
- Tweak combo speed bonuses
### Adding New Features
- Add new types to `POWERUP_TYPES`
- Add achievements in `ACHIEVEMENTS`
- Extend `detect_gesture()` for more controls
- Enhance particle system visuals
---
##  Credits
This game showcases:
- **Computer Vision** with OpenCV + MediaPipe
- **Game Development** with Pygame
- **Data Persistence** with JSON
- **UI Design** with OpenCV drawing functions
- **Real-Time Processing** & optimization techniques