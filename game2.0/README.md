Enhanced AR Coin Game - README
🎮 Game Overview
An immersive Augmented Reality Hand-Tracking Game that combines computer vision with interactive gameplay. Use your webcam and hand movements to catch coins, avoid bombs, and collect power-ups in this skill-based arcade experience.

✨ Features
🎯 Core Gameplay
Hand Tracking Control: Use your webcam to detect hand movements - no keyboard/mouse needed!

Dual-Hand Support: Play with both hands simultaneously with separate colored trails

Catch Golden Coins: Touch coins with your finger to score points

Avoid Red Bombs: Dodge bombs or face game over (unless protected)

Dynamic Difficulty: Speed increases with score and combo achievements

🌟 Advanced Features
Combo System: Chain consecutive catches for special effects and speed bonuses

Power-Up System: 4 different power-ups with unique abilities

Gesture Controls: Special hand gestures for instant power activation

Particle Effects: Beautiful visual feedback for all interactions

Achievement System: 8 unlockable achievements with persistent tracking

Persistent Data: High scores, statistics, and achievements saved between sessions

🚀 Installation
Prerequisites
bash
pip install opencv-python mediapipe pygame numpy
Required Files
Place these audio files in the same directory as the game (optional):

background.wav - Background music

coin_sound.wav - Coin collection sound

game-over.wav - Game over sound

bomb_explosion.wav - Bomb explosion sound

powerup.wav - Power-up collection sound

combo.wav - Combo achievement sound

achievement.wav - Achievement unlock sound

Optional Image Files
coin.png - Custom coin sprite (60x60px)

bomb.png - Custom bomb sprite (70x70px)

🎮 How to Play
Basic Controls
Start the Game: Run the Python script

Position Yourself: Sit 2-3 feet from your webcam with good lighting

Move Your Hands: Use your index finger to touch falling objects

Catch Coins: Golden coins increase your score and combo

Avoid Bombs: Red bombs end the game (unless you have shield protection)

Keyboard Controls
Q: Quit game

R: Restart game (when game over)

A: Show achievements list (when game over)

🔮 Power-Up System
Available Power-Ups
Speed Boost (Cyan 'S'): Slows down all falling objects

Magnet (Purple 'M'): Attracts coins from greater distances

Shield (Green 'S'): Protects from one bomb explosion

Double Points (Yellow '2X'): Doubles score for each coin caught

Gesture Controls 🤟
Peace Sign (✌️): Instantly activate shield protection

Fist (✊): Destroy all bombs on screen

Thumbs Up (👍): Activate slow-motion mode

🏆 Combo System
How Combos Work
Catch coins consecutively without missing any to build combo

Missing a coin resets combo to 0

High combos increase game speed for extra challenge

Speed bonuses:

Combo 5-9: +1 speed bonus

Combo 10-14: +3 speed bonus

Combo 15+: +5 speed bonus

Combo Benefits
Special sound effects at 5+ combo

Screen border warning at combo 9

Achievement unlock at 10+ combo

Progressive speed challenge

🏅 Achievement System
Unlock these achievements by reaching various milestones:

First Blood: Catch your first coin

Speed Demon: Reach speed level 10

Bomb Dodger: Avoid 50 bombs

Perfectionist: Complete game without missing coins

Combo Master: Get 10+ combo streak

Centurion: Score 100+ points

Survivor: Survive 2 minutes

Power Hunter: Collect 10 power-ups

📊 Game Statistics
The game tracks and saves:

High Scores: Best score achieved

Leaderboard: Top 10 scores with dates and stats

Detailed Statistics:

Total games played

Total coins caught

Total bombs avoided

Total playtime

Best combo achieved

Achievement progress

🎨 Visual Features
Hand Tracking
Separate Colored Trails: Each hand gets its own trail color

Hand Indicators: Colored circles show hand positions

Smooth Trail Effects: Fading trails follow hand movement

Special Effects
Particle Explosions: Golden sparkles for coins, red for bombs

Screen Shake: Impact feedback for bomb collisions

Pulsing Power-ups: Animated power-up icons

Dynamic UI: Real-time stats and power-up timers

⚙️ Technical Requirements
Hardware
Webcam: Any USB or built-in camera

Lighting: Good lighting for hand detection

Space: 2-3 feet from camera for optimal tracking

Software
Python 3.7+

OpenCV 4.0+

MediaPipe 0.8+

Pygame 2.0+

NumPy

🐛 Troubleshooting
Common Issues
Hand not detected: Ensure good lighting and clean camera lens

Lag/Low FPS: Close other applications, lower video resolution

Audio not working: Check audio files are in correct directory

Game too fast/slow: Adjust initial_fall_speed variable

Performance Tips
Good Lighting: Use bright, even lighting for best hand detection

Clean Background: Solid backgrounds work better than busy ones

Camera Position: Position camera at chest height, 2-3 feet away

Hand Position: Keep hands visible and within camera frame

📁 File Structure
text
game2.0/
├── game_2.0.py          # Main game file
├── game_data.json       # Saved game data (auto-generated)
├── background.wav       # Background music (optional)
├── coin_sound.wav       # Coin sound (optional)
├── game-over.wav        # Game over sound (optional)
├── bomb_explosion.wav   # Bomb sound (optional)
├── powerup.wav          # Power-up sound (optional)
├── combo.wav            # Combo sound (optional)
├── achievement.wav      # Achievement sound (optional)
├── coin.png            # Coin sprite (optional)
├── bomb.png            # Bomb sprite (optional)
└── README.md           # This file
🎯 Tips for High Scores
Master the Combo System: Focus on consecutive catches rather than risky coins

Use Power-ups Strategically: Save shields for challenging moments

Learn Gesture Controls: Quick gesture activation can save you in tight spots

Practice Hand Coordination: Use both hands to cover more screen area

Prioritize Safety: Better to miss one coin than break a high combo

Watch the Speed: High combos increase difficulty - play accordingly

🔄 Updates and Modifications
Easy Customizations
Modify initial_fall_speed for different difficulty

Adjust max_missed_coins for more/less forgiveness

Change coin_size, bomb_size for different object sizes

Modify combo speed bonuses in the speed calculation section

Adding New Features
The code is well-structured for extensions:

Add new power-up types in POWERUP_TYPES

Create new achievements in ACHIEVEMENTS

Implement new gesture recognition in detect_gesture()

Add visual effects in the particle system

🎊 Credits
This Enhanced AR Coin Game demonstrates:

Computer Vision with OpenCV and MediaPipe

Game Development with Pygame

Data Persistence with JSON

User Interface Design with OpenCV drawing functions

Real-time Processing and optimization techniques

Perfect for showcasing technical skills in computer vision, game development, and interactive applications!