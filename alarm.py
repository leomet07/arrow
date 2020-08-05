
import time
import pygame
pygame.mixer.init()
def play_alarm():
    pygame.mixer.music.load('alarm.wav')
    pygame.mixer.music.play(0)

    time.sleep(1)


