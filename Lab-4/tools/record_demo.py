"""Capture actual game frames with scripted keys; no game rules are altered.
Usage: python tools/record_demo.py /path/to/game before|after output.mp4
The after recording mixes bundled WAVs at their actual game event times.
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import sys, random, subprocess, wave, struct
from pathlib import Path
import pygame
root, mode, output = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve()
sys.path.insert(0, str(root))
# Pick a reproducible initial food position for a short eating demonstration.
if mode == 'after':
    free = [(x,y) for x in range(30) for y in range(30) if (x,y) not in [(15,15),(14,15),(13,15)]]
    for seed in range(100000):
        random.seed(seed)
        random.choice([(x,y) for x in range(30) for y in range(30)])
        if random.choice(free) == (17,15):
            random.seed(seed)
            break
else:
    random.seed(42)
import main as app
class DemoClock:
    def tick(self, fps): return 1000 / 60
app.clock = DemoClock()
output.parent.mkdir(parents=True, exist_ok=True)
raw = output.with_suffix('.silent.mp4')
proc = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','600x660','-framerate','60','-i','-','-an','-c:v','libx264','-crf','22','-pix_fmt','yuv420p',str(raw)], stdin=subprocess.PIPE)
canvas = pygame.Surface((600,660))
font = pygame.font.Font(None,22)
frame = 0
sound_events = []
if mode == 'after':
    real_sound = app.engine.play_sound
    def play_sound(name):
        sound_events.append((frame / 60, name))
        real_sound(name)
    app.engine.play_sound = play_sound

def capture():
    global frame
    if frame >= 600: return
    canvas.fill((24,24,28))
    canvas.blit(app.SCREEN,(0,0))
    if mode == 'before':
        action = 'Moving right' if frame < 45 else 'Left pressed: unfair self-collision; no game-over screen'
    else:
        action = ('Left pressed: reversal ignored; eat food' if frame < 110 else
                  'Game over: score and replay options' if frame < 180 else
                  '2 pressed: Medium replay' if frame < 360 else '3 pressed: Hard replay')
    canvas.blit(font.render(f'{mode.upper()} | Automated gameplay capture',True,(255,255,255)),(12,611))
    canvas.blit(font.render(action,True,(220,220,220)),(12,637))
    proc.stdin.write(pygame.image.tobytes(canvas,'RGB'))
    if frame in (70,145,200,400):
        pygame.image.save(canvas, str(output.parent / f'{mode}_{frame}.png'))
    events = {45: pygame.K_LEFT} if mode == 'before' else {20: pygame.K_LEFT,180: pygame.K_2,360: pygame.K_3}
    if frame in events:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=events[frame]))
    frame += 1
    if frame == 600:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
pygame.display.flip = capture
app.main()
proc.stdin.close()
assert proc.wait() == 0
if mode == 'after':
    rate=44100
    audio=[0]*(rate*10)
    for time,name in sound_events:
        with wave.open(str(root/'assets'/f'{name}.wav'),'rb') as w:
            data=w.readframes(w.getnframes())
        samples=struct.unpack('<'+'h'*(len(data)//2),data)
        offset=round(time*rate)
        for i,value in enumerate(samples):
            if offset+i<len(audio): audio[offset+i]=max(-32768,min(32767,audio[offset+i]+value))
    wav=output.with_suffix('.wav')
    with wave.open(str(wav),'wb') as w:
        w.setparams((1,2,rate,0,'NONE','not compressed'))
        w.writeframes(struct.pack('<'+'h'*len(audio),*audio))
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-i',str(wav),'-c:v','copy','-c:a','aac','-t','10',str(output)],check=True)
    raw.unlink(); wav.unlink()
else:
    raw.rename(output)
print('Captured',frame,'frames; sound events:',sound_events)
