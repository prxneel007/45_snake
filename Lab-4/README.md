# Lab 4 - Snake Game

CHIRRA YUKTHA PRANEEL | PES2UG24AM049 | 5th Sem AIML (A)

This is a Python/Pygame graphical Snake game launched from the terminal.
Move the snake, eat red food, grow and increase the score. Hitting a wall or
occupied body cell ends the game. The original assignment README is preserved
in ASSIGNMENT_README.md.

## Run on macOS (Python 3.10+)

From this Lab-4 directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Arrow keys or WASD move. Q/Esc or the window close button exits.
The first game starts on Easy. After Game Over, press 1 (Easy, 8 moves/sec),
2 (Medium, 12 moves/sec), or 3 (Hard, 20 moves/sec) to replay.

## Completed tasks

1. Collision fairness: block reversal and allow only one turn per movement step.
   Collision checks happen after the tail moves, making its vacated cell safe.
   Growth happens immediately; initial and respawned food avoid the snake.
   A full board ends with a win instead of an infinite food-spawning loop.
2. Game-over screen: show the final score, freeze movement and wait for input.
3. Replay: choose difficulty and reset score, body, food and movement timer.
   Movement uses elapsed time rather than counting rendering frames.
4. Sound: original synthesized eating and game-over WAVs; game-over sound plays
   once. Missing audio hardware does not stop the game.

## Verification

```bash
python -m unittest discover -s tests -v
```

Nine tests cover reversal and rapid input, safe tail movement, wall/self collision,
food/full-board behavior, immediate growth, waiting/quit, all replay speeds,
sound event counts, and an unavailable audio device. Tests use SDL dummy drivers.
The actual main loop also ran for both recorded demos. Human listening and physical
keyboard interaction on the student's Mac remain local checks.

## Deliverables and recording provenance

- videos/before.mp4: 10 seconds, preserved unmodified upstream commit 114601f.
- videos/after.mp4: 10 seconds, completed game including audible sound events.
- main.py, game/, assets/, requirements.txt: updated code and sound assets.
- Chat_History.pdf: user-facing conversation transcript through the packaging checkpoint.
- tools/record_demo.py: reproducible scripted recording harness (requires ffmpeg).

Both videos are automated captures of actual Pygame-rendered frames, with scripted
key events. They are not recordings of the student's physical screen. The before
video was generated from a preserved original checkout after the fixes were made;
the original bug was separately run and verified before editing. The after demo uses
a random seed to place the first food ahead of the snake, without altering game rules.
Audio is mixed from the game's WAV files at the actual sound-trigger times because
this environment has no physical audio output. Captions identify automated capture.

To meet a strict requirement for personally recorded before/after videos, record on
your Mac using the preserved original commit and completed version. Before: show
movement right, press Left immediately, then show the frozen game and terminal's
final-score message for the rest of the 10 seconds. After: demonstrate ignored reverse
input, eating/growth with sound, a wall collision and final score, then a difficulty
replay. Record system sound if your screen recorder supports it.

The repository README also asks for the complete chat page link. Add the real link
for this conversation to CHAT_LINK.txt. No link has been fabricated. The PDF is a
checkpoint transcript; append any later discussion before final submission.

## Explain in viva

- Snake stores its body as a list of grid coordinates, with the head first.
- On each movement, insert a new head and remove the tail unless food is eaten.
- Opposite directions would place the head in its neck, so they are ignored.
- A per-move turn guard stops two rapid keys from bypassing that check.
- GameEngine owns score, speed, game state, input, rendering and sound.
- Replay creates a fresh snake and food, resets score and chooses speed.
- Food chooses a free cell; if there are none, the player has filled the board.
