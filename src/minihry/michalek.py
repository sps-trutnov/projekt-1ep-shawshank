## ToDo input a kontrola řešení, časovač odpovědi

import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    DATA_ROOT = '.'
else:
    DATA_ROOT = '..'

import pygame as pg
import random
import time

pg.init()
pg.mixer.init()

def main():
    theme = pg.mixer.Sound(DATA_ROOT + "/data/music/minigame_theme.mp3")
    UKOL="Vzpočti Diskriminant"
    BARVA_POZADI = (0, 20, 0)
    okno = pg.display.set_mode((736,448))
    pg.display.set_caption(UKOL)
    ukol_barva = (255, 255, 0)
    ukol_barva_alt = (255, 0, 0)
    ub = ukol_barva

    seznam_zadani = {"2x² - 11x + 14 = 0":"9",
                     "3x² + 6x + 5 = 0":"-24",
                     "x² + 4x - 16 = 0":"80",
                     "4x² - 8x - 87 = 0":"1456",
                     "2x² + 5x - 4 = 0":"57",
                     "5x² - 12x + 58 = 0":"-1016",
                     "x² + 7x + 5 = 0":"29",
                     "3x² - 8x + 5 = 0":"4",
                     }
    klice = list(seznam_zadani)
    notazek = random.randint(1, 5)

    while notazek > 0:
        zadani = random.choice(klice)
        klice.remove(zadani)
        reseni = seznam_zadani[zadani]
        odpovezeno = False
        spravneb = (0, 25, 0)
        odpoved = ""
        spravne = ""
        vysledek = True
        while not odpovezeno:
            if not pg.mixer.get_busy():
                theme.play()
            udalost = pg.event.get()
            stisknuto = pg.key.get_pressed()
            for u in udalost:
                if u.type == pg.QUIT:
                    pg.quit()
                    pg.mixer.quit()
                    sys.exit()
                elif u.type == pg.KEYDOWN and not odpovezeno:
                    if u.key == pg.K_RETURN:
                        odpovezeno = True
                    elif u.key == pg.K_BACKSPACE:
                        if len(odpoved)>0:
                            odpoved = odpoved[:-1]
                    else:
                        odpoved += u.unicode
                        
            if odpovezeno == True:
                if odpoved == reseni:
                    spravne = "Správně"
                    spravneb = (0, 255, 0)
                else:
                    spravne = "Špatně"
                    spravneb = (255, 0, 0)
                    vysledek = False
                    
            if ub == ukol_barva:
                ub = ukol_barva_alt
            else:
                ub = ukol_barva
                    
            
            font = pg.font.SysFont("Comic Sans MS", 42)
            uloha = font.render(zadani, True, (255, 255, 255))
            odpovedin = font.render(odpoved, True, (255, 255, 255))
            spravneout = font.render(spravne, True, (spravneb))
            zbotazky = font.render(str(notazek), True, (255, 255, 0))
            ukol = font.render(UKOL, True, ub)
            
            okno.fill(BARVA_POZADI)
            okno.blit(ukol, (0, 380))
            okno.blit(uloha, (0,0))
            okno.blit(odpovedin, (0, 50))
            okno.blit(spravneout, (0, 108))
            okno.blit(zbotazky, (689, 0))
                
            pg.display.update()
        time.sleep(0.5)
        notazek = notazek - 1
    theme.stop()
    return vysledek
