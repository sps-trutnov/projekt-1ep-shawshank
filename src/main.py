'''
Útěk ze Střední průmyslové Shawshank

Top-down bludišťovka s minihrami. Unikněte ze školy, než zazvoní na hodinu!

Projekt studentů 1. ročníku oboru elektronické počítačové systémy, jaro 2022
'''

from email.headerregistry import Group
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    DATA_ROOT = '.'
else:
    DATA_ROOT = '..'

import os
import importlib
from map_generator import generate
from special_screens import screens_with_doors
from sprites import *
import time
from inventory import inventoryHasKey, inventoryHasBoots
from datetime import date

slozka_miniher = os.path.abspath("minihry")
sys.path.append(slozka_miniher)
minigames = []

for name in os.listdir(slozka_miniher):
    if ".py" in name:
        minigames.append(importlib.import_module(name.split(".")[0]))

pygame.init()
pygame.mixer.init()

#základní proměnné
game_map,master,minimap = generate()

clock = pygame.time.Clock()

#zvuky
jasot = pygame.mixer.Sound(DATA_ROOT + "/data/music/jásot.mp3")
rozmluva = pygame.mixer.Sound(DATA_ROOT + "/data/music/mírumilovná_rozmluva.mp3")
zvonek_0 = pygame.mixer.Sound(DATA_ROOT + "/data/music/zvonek_0.mp3")
zvonek_1 = pygame.mixer.Sound(DATA_ROOT + "/data/music/zvonek_1.mp3")
hall = pygame.mixer.Sound(DATA_ROOT + "/data/music/the_hall.mp3")
typing = pygame.mixer.Sound(DATA_ROOT + "/data/music/demonic_typing.mp3")
credits_file = DATA_ROOT + "/data/credits.txt"

#hud
mimimap_pos = (width - len(game_map[0])*20,heigth - len(game_map)*12)
ukazatel = pygame.image.load(DATA_ROOT + "/data/hud/ukazatel_na_mapce.png").convert_alpha()
counter_texture = pygame.image.load(DATA_ROOT + "/data/hud/counter.png").convert_alpha()
counter_surface = counter_texture.get_rect()

#fonty a rendery pro game over text
lost_font = pygame.font.Font(DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", 125)
lost_press_enter_font = pygame.font.Font(DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", 50)
lost_font_render = lost_font.render("GAME  OVER", True, (255, 0, 0))
lost_press_enter_font_render = lost_press_enter_font.render("PRESS   ENTER", True, (100, 0, 0))
lost_font_rect = lost_font_render.get_rect(center=(23*32/2, 14*32/2))
lost_press_enter_font_rect = lost_press_enter_font_render.get_rect(center=(23*32/2, 14*32/2 + 75))
lost_font_render.set_alpha(0)
lost_press_enter_font_render.set_alpha(0)

#fonty a rendery pro schoolEscaped text
won_font = pygame.font.Font(DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", 125)
won_press_enter_font = pygame.font.Font(DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", 50)
won_font_render = won_font.render("YOU  WON", True, (0, 0, 0))
won_press_enter_font_render = won_press_enter_font.render("PRESS   ENTER", True, (100, 100, 100))
won_font_rect = won_font_render.get_rect(center=(23*32/2, 14*32/2))
won_press_enter_font_rect = won_press_enter_font_render.get_rect(center=(23*32/2, 14*32/2 + 75))
won_font_render.set_alpha(0)
won_press_enter_font_render.set_alpha(0)

#proměné pro cheaty
clip = True
hitbox = False
show_minigame = True
cheat_code = None
cheat_timeout = 20
show_minimap = False
cheaty = False

#základní proměné pro hru
player_x = 23 * 32 / 2
player_y = 14 * 32 / 2
player_speed = 3
health_max = health = 5
mozne_prechody = []
interactive = pygame.sprite.Group()
player_movable = True
inSpecialRoom = False

default_time = 60
current_time = 60

halloween_Date = "09-31"
todayDate = date.today()

#sprity
hrac_display_grp = pygame.sprite.Group()
hrac_hitbox_grp = pygame.sprite.Group()
postavy_display_grp = pygame.sprite.Group()
player_instance = player(player_x, player_y)
hrac_display_grp.add(player_instance)
player_hitbox_instance = player_hitbox(player_x, player_y)
hrac_hitbox_grp.add(player_hitbox_instance)
hrac_hitbox = hrac_hitbox_grp.sprites()[0]
health_bar = Health_bar((23*32/2, 24), screen)

hrac_menu_grp = pygame.sprite.Group()
hrac_menu_grp.add(menuPlayer(320, player_y - 100))

janitor_menu_grp = pygame.sprite.Group()
janitor_menu_grp.add(menuJanitor(250, player_y + 100))

#inventář
inventoryKey_grp = pygame.sprite.Group()
invKey = inventoryHasKey(23*32-32-16-16, 16+8)
inventoryKey_grp.add(invKey)
inventoryBoots_grp = pygame.sprite.Group()
invBoots = inventoryHasBoots(23*32-16-8, 16+8)
inventoryBoots_grp.add(invBoots)

current_position = master

skolnik = janitor(player_instance)
postavy_display_grp.add(skolnik)
menu_state = None

ukolFont = pygame.font.SysFont("Consolas", 12)
ukolKlic = ukolFont.render("Najdi a seber klíč.", True, (255, 255, 255))
ukolBoty = ukolFont.render("Najdi a seber boty.", True, (255, 255, 255))
ukolVen = ukolFont.render("Uteč!", True, (255, 255, 255))

hasKlic = False
hasBoty = False
enterDelay = 0

#definice pro menu
backgroundMove = 0
menu_background = pygame.image.load(DATA_ROOT + "/data/menu/background.png")

playStartGameAnim = False

menuButtonDelay = 0

timeForSecondChance = 0
secondChance = False

#credits
delta_y = screen.get_rect().centery + 60

#výstup ze dveří
def vystup(pos):
    for line_ind,line in enumerate(game_map[pos[0]][pos[1]][0]):
        for symbol_ind,symbol in enumerate(line):
            if symbol == "1": return (symbol_ind*32+16,(line_ind+1)*32+16)
            elif symbol == "2": return ((symbol_ind-1)*32+16,line_ind*32+16)
            elif symbol == "3": return (symbol_ind*32+16,(line_ind-1)*32+16)
            elif symbol == "4": return ((symbol_ind+1)*32+16,line_ind*32+16)
            
inKeyRoom = False
inBootsRoom = False
            
#aktivace miniher
def play_minigame():
    hall.stop()
    zvonek_1.stop()
    zvonek_0.stop()
    if show_minigame:
        outcome = random.choice(minigames).main()
        screen = pygame.display.set_mode((width,heigth))
        pygame.display.set_caption("¤ Útěk ze střední průmyslové Shawshank ¤")
        player_hitbox_instance.rect.center = vystup(current_position)
        player_instance.rect.centerx = player_hitbox_instance.rect.centerx+4
        player_instance.rect.bottom = player_hitbox_instance.rect.bottom-2
        hall.play()
        zvonek_0.play()
        if outcome: return health
        else: return health-1
    else:
        player_hitbox_instance.rect.center = vystup(current_position)
        player_instance.rect.centerx = player_hitbox_instance.rect.centerx+4
        player_instance.rect.bottom = player_hitbox_instance.rect.bottom-2
        hall.play()
        zvonek_0.play()
        return health

#vytvoření textu
def text(text_size, text, x, y, text_color, text_font, align, sysfont):
    if sysfont:
        font = pygame.font.SysFont(text_font, text_size)
    else:        
        font = pygame.font.Font(text_font, text_size)
    text = font.render(text, True, text_color)
    text_rect = text.get_rect()
    if align == "topleft":
        text_rect.topleft = (x,y)
    if align == "midtop":
        text_rect.midtop = (x,y)
    if align == "topright":
        text_rect.topright = (x,y)
    if align == "midleft":
        text_rect.midleft = (x,y)
    if align == "center":
        text_rect.center = (x,y)
    if align == "midright":
        text_rect.midright = (x,y)
    if align == "bottomleft":
        text_rect.bottomleft = (x,y)
    if align == "midbottom":
        text_rect.midbottom = (x,y)
    if align == "midright":
        text_rect.midright = (x,y)
        
    screen.blit(text, text_rect)
    return text_rect
    
#načtení zdí speciálních místností
def specialni_zdi(mapka):
    global podlaha
    zdi = pygame.sprite.Group()
    interactive = pygame.sprite.Group()
    for radek_ind,radek in enumerate(mapka):
        for symbol_ind,symbol in enumerate(radek):
            if symbol == "6":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_0",mapka[2][1]))
            elif symbol == "9":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_1",mapka[2][1]))
            elif symbol == "12":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_2",mapka[2][1]))
            elif symbol == "15":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_3",mapka[2][1])) 
            elif symbol == "7":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_0",mapka[2][1])) 
            elif symbol == "10":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_1",mapka[2][1]))
            elif symbol == "13":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_2",mapka[2][1])) 
            elif symbol == "16":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_3",mapka[2][1]))  
            elif symbol == "8":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_0",mapka[2][1]))  
            elif symbol == "11":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_1",mapka[2][1]))  
            elif symbol == "14":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_2",mapka[2][1]))
            elif symbol == "17":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_3",mapka[2][1]))
            elif symbol == "29":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"skrinka_horizontalni",mapka[2][1]))
            elif symbol == "21":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"skrinka_vertikalni",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "23":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"skrinka_vertikalni_vrsek",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "25":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"kos",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "20":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"lavicka_horizontalni",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "19":
                zdi.add(zed((symbol_ind*32 + 5,radek_ind*32),"lavicka_horizontalni_konec_leva",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "42":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"lavicka_horizontalni_konec_prava",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "24"))
            elif symbol == "31":
                if not invBoots.completed:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"skrinka_horizontalni_zamek",mapka[2][1]))
                    interactive.add(zed((symbol_ind*32,radek_ind*32),"skrinka_horizontalni_zamek",mapka[2][1]))
                else:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"skrinka_horizontalni_otevrena",mapka[2][1]))
                    interactive.add(zed((symbol_ind*32,radek_ind*32),"skrinka_horizontalni_otevrena",mapka[2][1]))
            elif symbol == "35":
                if halloween_Date in str(todayDate):
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"odpatkove_pytle_biologické",mapka[2][1]))
                else:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"odpatkove_pytle",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
            elif symbol == "36":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"skrin",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
            elif symbol == "37":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"skrin_bok",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
            elif symbol == "38":
                if halloween_Date in str(todayDate):
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_dole",mapka[2][1]))
                else:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_dole_normalni",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
            elif symbol == "40":
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
                if not invKey.completed:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_stred_klic",mapka[2][1]))
                    interactive.add(zed((symbol_ind*32,radek_ind*32),"stul_stred_klic",mapka[2][1]))
                else:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_stred",mapka[2][1]))
                    interactive.add(zed((symbol_ind*32,radek_ind*32),"stul_stred",mapka[2][1]))
            elif symbol == "39":
                if halloween_Date in str(todayDate):
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_hore",mapka[2][1]))
                else:
                    zdi.add(zed((symbol_ind*32,radek_ind*32),"stul_hore_normalni",mapka[2][1]))
                podlaha.add(specialni_podlahy(screens_with_doors[1], True, symbol_ind, radek_ind, "34"))
    return zdi,interactive

#načtení podlahy speciálních místností
def specialni_podlahy(mapka, under, symbolpos, radekpos, symbol):
    podlaha = pygame.sprite.Group()
    dvere = pygame.sprite.Group()
    if under != True:
        for radek_ind,radek in enumerate(mapka):
            for symbol_ind,symbol in enumerate(radek):
                True
                if symbol == "18":
                    podlaha.add(zed((symbol_ind*32,radek_ind*32),"void",mapka[2][1]))
                elif symbol == "24":
                    podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_kachlicky",mapka[2][1]))
                elif symbol == "32":
                    podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_dark",mapka[2][1]))
                elif symbol == "33":
                    if halloween_Date in str(todayDate):
                        podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_dark_blood",mapka[2][1]))
                    else:
                        podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_dark_flek",mapka[2][1]))
                elif symbol == "34":
                    if halloween_Date in str(todayDate):
                        podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_dark_blooood",mapka[2][1]))
                    else:
                        podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha_dark_prkno",mapka[2][1]))
    else:
        if symbol == "24":
            podlaha.add(zed((symbolpos*32,radekpos*32),"podlaha_kachlicky",mapka[2][1]))
        if symbol == "34":
            podlaha.add(zed((symbolpos*32,radekpos*32),"podlaha_dark",mapka[2][1]))
    return podlaha,dvere
    
#načtení zdí specificky
def random_zdi(mapka,ind,door):
    global mozne_prechody
    zdi = pygame.sprite.Group()
    for radek_ind,radek in enumerate(mapka):
        for symbol_ind,symbol in enumerate(radek):
            if symbol == "6":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_0",mapka[2][1]))
            elif symbol == "9":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_1",mapka[2][1]))
            elif symbol == "12":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_2",mapka[2][1]))
            elif symbol == "15":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"zeď_3",mapka[2][1])) 
            elif symbol == "7":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_0",mapka[2][1])) 
            elif symbol == "10":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_1",mapka[2][1]))
            elif symbol == "13":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_2",mapka[2][1])) 
            elif symbol == "16":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnitřní_roh_3",mapka[2][1]))  
            elif symbol == "8":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_0",mapka[2][1]))  
            elif symbol == "11":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_1",mapka[2][1]))  
            elif symbol == "14":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_2",mapka[2][1]))
            elif symbol == "17":
                zdi.add(zed((symbol_ind*32,radek_ind*32),"vnější_roh_3",mapka[2][1]))
                
        if "1" in radek or "2" in radek or "3" in radek or "4" in radek:
            if door == "regular_door":
                mozne_prechody.append(ind)
    return zdi

#načtení obrazovek
def urceni_sprite_group(mapa):
    podlaha = pygame.sprite.Group()
    dvere = pygame.sprite.Group()
    for radek_ind,radek in enumerate(mapa[0]):
        for symbol_ind,symbol in enumerate(radek):
            if symbol == "18":
                podlaha.add(zed((symbol_ind*32,radek_ind*32),"void",mapa[2][1]))
            elif symbol == "5":
                podlaha.add(zed((symbol_ind*32,radek_ind*32),"podlaha",mapa[2][1]))
            elif symbol == "1":
                dvere.add(zed((symbol_ind*32,radek_ind*32),"dveře_0",mapa[2][1]))
            elif symbol == "2":
                dvere.add(zed((symbol_ind*32,radek_ind*32),"dveře_1",mapa[2][1]))
            elif symbol == "3":
                dvere.add(zed((symbol_ind*32,radek_ind*32),"dveře_2",mapa[2][1]))
            elif symbol == "4":
                dvere.add(zed((symbol_ind*32,radek_ind*32),"dveře_3",mapa[2][1]))
    return podlaha,dvere

wall_map = []
for line_ind,line in enumerate(game_map):
    new = []
    for something_ind,something in enumerate(line):
        if something != []:
            new.append(random_zdi(something[0],[line_ind,something_ind],something[2][1]))
        else: new.append(None)
    wall_map.append(new)
podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
zdi = wall_map[current_position[0]][current_position[1]]

#restart
def restart():
    global current_position,podlaha,dvere,zdi,minimap,game_map,wall_map,master, hasKlic, hasBoty
    game_map,master,minimap = generate()
    current_position = master
    player_hitbox_instance.rect.center = (width//2,heigth//2)
    
    wall_map = []
    for line_ind,line in enumerate(game_map):
        new = []
        for something_ind,something in enumerate(line):
            if something != []:
                new.append(random_zdi(something[0],[line_ind,something_ind],something[2][1]))
            else: new.append(None)
        wall_map.append(new)
        
    podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
    zdi = wall_map[current_position[0]][current_position[1]]
    invKey.completed = True
    invBoots.completed = True
    invBoots.unlocked = False
    inventoryKey_grp.update(False)
    inventoryBoots_grp.update("sebrat")
    inventoryBoots_grp.update("odemknout")
    
    hasKlic = False
    hasBoty = False

#kód pro ztmavení / zesvětlení obrazovky
fade_white = pygame.Surface((23*32, 14*32))
fade_black = pygame.Surface((23*32, 14*32))
fade_white.fill("white")
fade_black.fill("black")
pruhlednost = 0
pruhlednost_textu = 0
fade_white.set_alpha(pruhlednost)
fade_black.set_alpha(pruhlednost)
fade_speed = 10

#gamestates
inGame = False
gameLost = False
gameWon = False
inMenu = True
schoolEscaped = False
creditsRoll = False

#main loop
while True:
    #vypnutí okna
    pressed = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            pygame.mixer.quit()
    
    if menuButtonDelay > 0:
        menuButtonDelay -= 1
    if  enterDelay > 0:
        enterDelay -= 1
    
    if inMenu:
        secondChance = False
        
        #vypnout hru
        if pressed[pygame.K_ESCAPE]:
            if menuButtonDelay <= 0:
                if creditsRoll:
                    creditsRoll = False
                    jasot.stop()
                    inMenu = True
                    menuButtonDelay = 20
                else:
                    pygame.quit()
                    sys.exit()
                    pygame.mixer.quit()
            
        #poyb pozadí
        if backgroundMove <= 0:
            backgroundMove = menu_background.get_rect().width - 23 * 32
        else:
            backgroundMove -= 15
        screen.blit(menu_background,(0, 0), (backgroundMove, 0, menu_background.get_rect().width, menu_background.get_rect().height))
        if not pygame.mixer.get_busy():
            typing.play()
            
        #pohyb mezi tlačíky přes tab
        if pressed[pygame.K_TAB] and cheat_timeout < 0:
            if pressed[pygame.K_RSHIFT] or pressed[pygame.K_LSHIFT]:
                if menu_state == None: menu_state = 2
                elif menu_state != 0: menu_state -= 1
                else: menu_state = 2
            else:
                if menu_state == None: menu_state = 0
                elif menu_state != 2: menu_state += 1
                else: menu_state = 0
            cheat_timeout = 10
        
        janitor_menu_grp.update()
        janitor_menu_grp.draw(screen)
        
        hrac_menu_grp.update()
        hrac_menu_grp.draw(screen)
        
        #povrchy
        txt_bg = pygame.image.load(DATA_ROOT + "/data/menu/text_bg.png").convert_alpha()
        txt_bg_rect = txt_bg.get_rect(topright=(23*32, 0))
        start_highlight = pygame.image.load(DATA_ROOT + "/data/menu/start_highlight.png").convert_alpha()
        start_highlight_rect = start_highlight.get_rect(topright=(23*32 - 8, 8))
        credits_highlight = pygame.image.load(DATA_ROOT + "/data/menu/credits_highlight.png").convert_alpha()
        credits_highlight_rect = credits_highlight.get_rect(topright=(23*32 - 10, 13))
        exit_highlight = pygame.image.load(DATA_ROOT + "/data/menu/exit_highlight.png").convert_alpha()
        exit_highlight_rect = exit_highlight.get_rect(topright=(23*32 - 15, 15))
        
        #vykreslování textu
        screen.blit(txt_bg, txt_bg_rect)
        text(50, "START", 23*32 - 225, 100, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False)
        text(50, "CREDITS", 23*32 - 225, 200, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False)
        text(50, "EXIT", 23*32 - 225, 300, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False)
        
        #mačkání tlačítek
        if text(50, "START", 23*32 - 225, 100, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) or menu_state == 0:
            screen.blit(start_highlight, start_highlight_rect)
            menu_state = 0
            
        if text(50, "CREDITS", 23*32 - 225, 200, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) or menu_state == 1:
            screen.blit(credits_highlight, credits_highlight_rect)
            menu_state = 1
            
        if text(50, "EXIT", 23*32 - 225, 300, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) or menu_state == 2:
            screen.blit(exit_highlight, exit_highlight_rect)
            menu_state = 2
            
        if menuButtonDelay <= 0:
            if (text(50, "START", 23*32 - 225, 100, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]) or ((pressed[pygame.K_KP_ENTER] or pressed[pygame.K_RETURN]) and menu_state == 0):
                if not creditsRoll:
                    inMenu = False
                    inGame = True
                    menu_state = None
                    health = health_max
                    rozmluva.stop()
                    typing.stop()
                    hall.play()
                    zvonek_0.play()
                    
                    player_hitbox_instance.rect.centerx = -100
                    playerStartGameAnim = True
                    player_movable = False
                    
                    while pruhlednost <= 20:
                        pruhlednost += 0.1
                        fade_black.set_alpha(pruhlednost)
                        screen.blit(fade_black, (0, 0))
                        pygame.display.update()
                        pygame.time.wait(fade_speed)
                    
                    pruhlednost = 0
            
            if (text(50, "CREDITS", 23*32 - 225, 200, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]) or ((pressed[pygame.K_KP_ENTER] or pressed[pygame.K_RETURN]) and menu_state == 1):
                if not creditsRoll:
                    rozmluva.stop()
                    typing.stop()
                    hall.play()
                    zvonek_0.play()
                    #jasot.play()
                    creditsRoll = True
                    menu_state = None
                    
                    delta_y = screen.get_rect().centery + 60

            if (text(50, "EXIT", 23*32 - 225, 300, (255, 255, 255), DATA_ROOT + "/data/fonts/ARCADECLASSIC.TTF", "topleft", False).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]) or ((pressed[pygame.K_KP_ENTER] or pressed[pygame.K_RETURN]) and menu_state == 2):
                if not creditsRoll:
                    pygame.quit()
                    pygame.mixer.quit()
                    sys.exit()
        
        clock.tick(60)
    
    elif inGame:
        
        #do menu
        if pressed[pygame.K_ESCAPE]:
            if not secondChance:
                menuButtonDelay = 10
                timeForSecondChance = 300
                secondChance = True
                
            if secondChance:
                if menuButtonDelay <= 0 and timeForSecondChance > 0:
                    inGame = False
                    inMenu = True
                    menuButtonDelay = 20
                    
                    hall.stop()
                    zvonek_0.stop()
                    zvonek_1.stop()
                    rozmluva.stop()
                    restart()
                    current_time = default_time
                    health = health_max
                    
        if timeForSecondChance > 0:
            timeForSecondChance -= 1
        if timeForSecondChance <= 0:
            secondChance = False
        
        #text do menu je úplně dole
        
        #úvodní animace
        if playerStartGameAnim and player_hitbox_instance.rect.centerx <= 23*32/2:
            
            posun_x = 0
            posun_x += player_speed
            image = "player_r"
            
            player_hitbox_instance.posun_x(posun_x)
            player_instance.rect.centerx = player_hitbox_instance.rect.centerx
            
        elif playerStartGameAnim and player_hitbox_instance.rect.centerx >= 23*32/2:
            playerStartGameAnim = False
            player_movable = True
         
        cheat_timeout -= 1
         
        #cheaty
        
        #zapínací zkratka pro cheaty
        if pressed[pygame.K_d]:
            cheat_code = 1
        if pressed[pygame.K_e] and cheat_code == 1:
            cheat_code = 2
        if pressed[pygame.K_v] and cheat_code == 2:
            if cheaty: cheaty = False
            else: cheaty = True
            cheat_timeout = 20
            cheat_code = None

        #cheat keybindy
        if cheaty:
            if pressed[pygame.K_h] and cheat_timeout < 0:
                if hitbox == False:
                    hitbox = True
                    player_hitbox_instance.showHitBox()
                else:
                    hitbox = False
                    player_hitbox_instance.hideHitBox()
                cheat_timeout = 20
                    
            elif pressed[pygame.K_n] and cheat_timeout < 0:
                if clip: clip = False
                else: clip = True
                cheat_timeout = 20
                
            elif pressed[pygame.K_m] and cheat_timeout < 0:
                if show_minimap: show_minimap = False
                else: show_minimap = True
                cheat_timeout = 20
                
            elif pressed[pygame.K_g] and cheat_timeout < 0:
                health = 0
                cheat_timeout = 20
            
            elif pressed[pygame.K_t] and cheat_timeout < 0:
                current_time = default_time
                hall.stop()
                hall.play()
                cheat_timeout = 20
                
            elif pressed[pygame.K_1] and cheat_timeout < 0:
                inventoryKey_grp.update(False)
                inventoryBoots_grp.update("odemknout")
                if hasKlic:
                    hasKlic = False
                else:
                    hasKlic = True
                cheat_timeout = 20
                
            elif pressed[pygame.K_2] and cheat_timeout < 0:
                inventoryBoots_grp.update("sebrat")
                if hasBoty:
                    hasBoty = False
                else:
                    hasBoty = True
                cheat_timeout = 20
                
            elif pressed[pygame.K_3] and cheat_timeout < 0:
                inGame = False
                schoolEscaped = True
                cheat_timeout = 20
                hall.stop()
                
            elif pressed[pygame.K_4] and cheat_timeout < 0:
                if todayDate == halloween_Date:
                    todayDate = date.today()
                else:
                    todayDate = halloween_Date
                cheat_timeout = 20
                
            elif pressed[pygame.K_p] and cheat_timeout < 0:
                if show_minigame == False:
                    show_minigame = True
                else:
                    show_minigame = False
                cheat_timeout = 20

            elif pressed[pygame.K_r] and cheat_timeout < 0:
                if player_speed == 3:
                    player_speed = 10
                else:
                    player_speed = 3
                cheat_timeout = 20
        
            elif pressed[pygame.K_t] and cheat_timeout < 0:
                current_time = default_time
                hall.stop()
                hall.play()
                cheat_timeout = 20
                
            elif pressed[pygame.K_1] and cheat_timeout < 0:
                inventoryKey_grp.update(False)
            elif pressed[pygame.K_2] and cheat_timeout < 0:
                inventoryBoots_grp.update("sebrat")
                cheat_timeout = 20
                
            elif pressed[pygame.K_3] and cheat_timeout < 0:
                inGame = False
                schoolEscaped = True
                cheat_timeout = 20
                hall.stop()
                
            elif pressed[pygame.K_p] and cheat_timeout < 0:
                show_minigame = not show_minigame
                cheat_timeout = 20

        #pohyb
        posun_x = 0
        posun_y = 0
        if player_movable:
            if pressed[pygame.K_a]:
                posun_x -= player_speed
                image = "player_l"
            if pressed[pygame.K_d]:
                posun_x += player_speed
                image = "player_r"
            if pressed[pygame.K_w]:
                posun_y -= player_speed
                image = "player_b"
            if pressed[pygame.K_s]:
                posun_y += player_speed
                image = "player_f"
            
            player_hitbox_instance.posun_x(posun_x)
            
        #kolize se stolem a skříňkou
        if pygame.sprite.spritecollide(hrac_hitbox, interactive, False) and inSpecialRoom:
            for objekt in interactive:
                if objekt.textura == "stul_stred_klic" and not invKey.completed:
                    inventoryBoots_grp.update("odemknout")
                    inventoryKey_grp.update(False)
                    invBoots.unlocked = True;
                    hasKlic = True
                    zdi.remove(objekt)
                    zdi.add(zed((objekt.rect.x,objekt.rect.y),"stul_stred","×"))
                elif objekt.textura == "skrinka_horizontalni_zamek" and invKey.completed and not invBoots.completed:
                    inventoryBoots_grp.update("sebrat")
                    zdi.remove(objekt)
                    zdi.add(zed((objekt.rect.x,objekt.rect.y),"skrinka_horizontalni_otevrena","×"))
                    hasBoty = True

        #kolize se zdmi
        if clip:
            for wall in zdi:
                if wall.rect.collidepoint(player_hitbox_instance.rect.topleft) or wall.rect.collidepoint(player_hitbox_instance.rect.bottomleft):
                    player_hitbox_instance.rect.left = wall.rect.right+1
                if wall.rect.collidepoint(player_hitbox_instance.rect.topright) or wall.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                    player_hitbox_instance.rect.right = wall.rect.left-1
                    
        player_hitbox_instance.posun_y(posun_y)

        #kolize se stolem a skříňkou
        if pygame.sprite.spritecollide(hrac_hitbox, interactive, False) and inSpecialRoom: 
            for objekt in interactive:
                if objekt.textura == "stul_stred_klic" and not invKey.completed:
                    inventoryBoots_grp.update("odemknout")
                    inventoryKey_grp.update(False)
                    invBoots.unlocked = True;
                    hasKlic = True
                    zdi.remove(objekt)
                    zdi.add(zed((objekt.rect.x,objekt.rect.y),"stul_stred","×"))
                elif objekt.textura == "skrinka_horizontalni_zamek" and invKey.completed and not invBoots.completed:
                    inventoryBoots_grp.update("sebrat")
                    zdi.remove(objekt)
                    zdi.add(zed((objekt.rect.x,objekt.rect.y),"skrinka_horizontalni_otevrena","×"))
                    hasBoty = True
        if clip:
            for wall in zdi:
                if wall.rect.collidepoint(player_hitbox_instance.rect.topleft) or wall.rect.collidepoint(player_hitbox_instance.rect.topright):
                    player_hitbox_instance.rect.top = wall.rect.bottom+1
                if wall.rect.collidepoint(player_hitbox_instance.rect.bottomleft) or wall.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                    player_hitbox_instance.rect.bottom = wall.rect.top-1
        
        #pohyb mezi obrazovkami
        if not playerStartGameAnim:
            if player_hitbox_instance.rect.left < 0:
                if inSpecialRoom:
                    player_hitbox_instance.rect.center = prevPlayerPos
                    inSpecialRoom = False
                else:
                    player_hitbox_instance.rect.right = width
                    current_position[1] -=1
                
                podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
                zdi = wall_map[current_position[0]][current_position[1]]
                
                inKeyRoom = False
                inBootsRoom = False
                enterDelay = 50
            elif player_hitbox_instance.rect.right > width:
                if inSpecialRoom:
                    player_hitbox_instance.rect.center = prevPlayerPos
                    inSpecialRoom = False
                else:
                    player_hitbox_instance.rect.left = 0
                    current_position[1] +=1
                podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
                zdi = wall_map[current_position[0]][current_position[1]]
                
                inKeyRoom = False
                inBootsRoom = False
                enterDelay = 50
            elif player_hitbox_instance.rect.top < 0:
                if inSpecialRoom:
                    player_hitbox_instance.rect.center = prevPlayerPos
                    inSpecialRoom = False
                else:
                    player_hitbox_instance.rect.bottom = heigth
                    current_position[0] -=1
                podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
                zdi = wall_map[current_position[0]][current_position[1]]
                
                inKeyRoom = False
                inBootsRoom = False
                enterDelay = 50
            elif player_hitbox_instance.rect.bottom > heigth:
                if inSpecialRoom:
                    player_hitbox_instance.rect.center = prevPlayerPos
                    inSpecialRoom = False
                else:
                    player_hitbox_instance.rect.top = 0
                    current_position[0] +=1
                podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
                zdi = wall_map[current_position[0]][current_position[1]]
                
                inKeyRoom = False
                inBootsRoom = False
                enterDelay = 50
            
        #zbytek pohybu
        player_instance.rect.centerx = player_hitbox_instance.rect.centerx
        player_instance.rect.bottom = player_hitbox_instance.rect.bottom+1
        
        #kolize s dvermi
        if pygame.sprite.spritecollide(hrac_hitbox, dvere, False):
            for door in dvere:
                if door.door_type == "regular_door":
                    health = play_minigame()
                    current_time = default_time
                elif door.door_type == "KEY_ROOM":
                    if enterDelay <= 0:
                        player_hitbox_instance.rect.center = vystup(current_position)
                        player_instance.rect.centerx = player_hitbox_instance.rect.centerx+4
                        player_instance.rect.bottom = player_hitbox_instance.rect.bottom-2

                        prevPlayerPos = player_hitbox_instance.rect.center
                        player_hitbox_instance.rect.center = (500, 32)

                        podlaha,dvere = specialni_podlahy(screens_with_doors[1], False, 0, 0, "0")
                        zdi,interactive = specialni_zdi(screens_with_doors[1])
                        
                        inSpecialRoom = True
                        inKeyRoom = True
                    else:
                        if door.rect.collidepoint(player_hitbox_instance.rect.topleft) or door.rect.collidepoint(player_hitbox_instance.rect.bottomleft):
                            player_hitbox_instance.rect.left = door.rect.right+1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.topright) or door.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                            player_hitbox_instance.rect.right = door.rect.left-1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.topleft) or door.rect.collidepoint(player_hitbox_instance.rect.topright):
                            player_hitbox_instance.rect.top = door.rect.bottom+1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.bottomleft) or door.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                            player_hitbox_instance.rect.bottom = door.rect.top-1
                elif door.door_type == "LOCKER_ROOM":
                    if enterDelay <= 0:
                        player_hitbox_instance.rect.center = vystup(current_position)
                        player_instance.rect.centerx = player_hitbox_instance.rect.centerx+4
                        player_instance.rect.bottom = player_hitbox_instance.rect.bottom-2
                        
                        prevPlayerPos = player_hitbox_instance.rect.center
                        player_hitbox_instance.rect.center = (32, 200)
                        
                        podlaha,dvere = specialni_podlahy(screens_with_doors[0], False, 0, 0, "0")
                        zdi,interactive = specialni_zdi(screens_with_doors[0])
                        
                        inSpecialRoom = True
                        inBootsRoom = True
                    else:
                        if door.rect.collidepoint(player_hitbox_instance.rect.topleft) or door.rect.collidepoint(player_hitbox_instance.rect.bottomleft):
                            player_hitbox_instance.rect.left = door.rect.right+1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.topright) or door.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                            player_hitbox_instance.rect.right = door.rect.left-1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.topleft) or door.rect.collidepoint(player_hitbox_instance.rect.topright):
                            player_hitbox_instance.rect.top = door.rect.bottom+1
                        elif door.rect.collidepoint(player_hitbox_instance.rect.bottomleft) or door.rect.collidepoint(player_hitbox_instance.rect.bottomright):
                            player_hitbox_instance.rect.bottom = door.rect.top-1
                elif door.door_type == "EXIT":
                    player_hitbox_instance.rect.center = vystup(current_position)
                    player_instance.rect.centerx = player_hitbox_instance.rect.centerx+4
                    player_instance.rect.bottom = player_hitbox_instance.rect.bottom-2
                    
                    if invBoots.completed:
                        inGame = False
                        schoolEscaped = True
                        hall.stop()
        
        #vykreslování
        screen.fill("black")
        podlaha.draw(screen)
        zdi.draw(screen)
        dvere.draw(screen)
        if show_minimap:
            screen.blit(minimap,mimimap_pos)
            screen.blit(ukazatel,(current_position[1]*20+mimimap_pos[0],current_position[0]*12+mimimap_pos[1]))
        hrac_display_grp.update()
        hrac_display_grp.draw(screen)
        hrac_hitbox_grp.draw(screen)
        health_bar.vykresleni_baru()
        health_bar.vykresleni_predelu(health_max, health)
        health_bar.vykresleni_borderu()
        inventoryKey_grp.draw(screen)
        inventoryBoots_grp.draw(screen)
        counter_surface.topleft = (8,6)
        screen.blit(counter_texture, counter_surface)
        
        if hasKlic and not hasBoty:
            ukolKlic = ukolFont.render("Najdi a seber klíč.", True, (255, 255, 255))
            ukolBoty = ukolFont.render(">Najdi a seber boty.", True, (255, 255, 255))
            ukolVen = ukolFont.render("Uteč!", True, (200, 200, 200))
        elif hasBoty and hasKlic:
            ukolKlic = ukolFont.render("Najdi a seber klíč.", True, (255, 255, 255))
            ukolBoty = ukolFont.render("Najdi a seber boty.", True, (255, 255, 255))
            ukolVen = ukolFont.render(">Uteč!", True, (255, 255, 255))
        else:
            ukolKlic = ukolFont.render(">Najdi a seber klíč.", True, (255, 255, 255))
            ukolBoty = ukolFont.render("Najdi a seber boty.", True, (200, 200, 200))
            ukolVen = ukolFont.render("Uteč!", True, (200, 200, 200))

        screen.blit(ukolKlic, (23*32 - ukolKlic.get_rect().width - 5, 47))
        screen.blit(ukolBoty, (23*32 - ukolBoty.get_rect().width - 5, 47 + ukolBoty.get_rect().height + 5))
        screen.blit(ukolVen, (23*32 - ukolVen.get_rect().width - 5, 47 + 17 + ukolVen.get_rect().height + 5))
        
        #časomíra
        current_time -= 0.016
        if current_time > 21: text(30, (str(int(current_time))), 24, 25, "gray", "rockwellcondensedtučné", "center", True)
        elif current_time > 0 : text(30, (str(int(current_time))), 24, 25, "red", "rockwellcondensedtučné", "center", True)
        else:
            hall.stop()
            if not pygame.mixer.get_busy():
                zvonek_1.play()
            if not skolnik.completed:
                postavy_display_grp.update()
                postavy_display_grp.draw(screen)
                player_movable = False
            else:
                hasKlic = False
                inventoryBoots_grp.update("odemknout")
                inventoryKey_grp.update(True)
                current_position = random.choice(mozne_prechody)
                podlaha,dvere = urceni_sprite_group(game_map[current_position[0]][current_position[1]])
                zdi = wall_map[current_position[0]][current_position[1]]
                
                player_movable = True
                skolnik.completed = False
                health = play_minigame()
                current_time = default_time
        
        #prohra
        if health == 0:
            
            while pruhlednost <= 12:
                pruhlednost += 0.1
                pruhlednost_textu += 1.5
                fade_black.set_alpha(pruhlednost)
                lost_font_render.set_alpha(pruhlednost_textu)
                lost_press_enter_font_render.set_alpha(pruhlednost_textu)
                screen.blit(fade_black, (0, 0))
                screen.blit(lost_font_render, lost_font_rect)
                screen.blit(lost_press_enter_font_render, lost_press_enter_font_rect)
                pygame.display.update()
                pygame.time.wait(fade_speed)
            
            health = -1
            inGame = False
            gameLost = True
            hall.stop()
            zvonek_0.stop()
            zvonek_1.stop()
            pruhlednost = 255
            fade_black.set_alpha(pruhlednost)
            lost_font_render.set_alpha(pruhlednost)
            lost_press_enter_font_render.set_alpha(pruhlednost)
            
        #vyhra
        if schoolEscaped:
            i = 0
            while pruhlednost <= 255: #předělal jsem to tu na 255 místo 20 (více v: https://github.com/sps-trutnov/projekt-1ep-shawshank/issues/72)
                pruhlednost += 0.1*i
                pruhlednost_textu += 0.1*i
                i += 1
                fade_white.set_alpha(pruhlednost)
                won_font_render.set_alpha(pruhlednost_textu)
                won_press_enter_font_render.set_alpha(pruhlednost_textu)
                screen.blit(fade_white, (0, 0))
                screen.blit(won_font_render, won_font_rect)
                screen.blit(won_press_enter_font_render, won_press_enter_font_rect)
                pygame.display.update()
                pygame.time.wait(fade_speed*2)
            
            schoolEscaped = False
            inGame = False
            gameWon = True
            hall.stop()
            zvonek_0.stop()
            zvonek_1.stop()
            pruhlednost = 255
            fade_white.set_alpha(pruhlednost)
            won_font_render.set_alpha(pruhlednost)
            won_press_enter_font_render.set_alpha(pruhlednost)
        
        #školník
        if current_time == 0:
            x_hrace = player_instance.prevPosX
            y_hrace = player_instance.prevPosY
            janitor(x_hrace, y_hrace)
    
    if gameLost:
        if not pygame.mixer.get_busy():
            rozmluva.play()
        pruhlednost = 0
        if pressed[pygame.K_RETURN] or pressed[pygame.K_ESCAPE]:
            menuButtonDelay = 50
            gameLost = False
            inMenu = True
            creditsRoll = False
            rozmluva.stop()
            restart()
            current_time = default_time
            health = health_max
    
    if gameWon:
        if pressed[pygame.K_RETURN] or pressed[pygame.K_ESCAPE]:
            menuButtonDelay = 50
            gameWon = False
            inMenu = True
            menu_state = 1
            creditsRoll = True
            delta_y = screen.get_rect().centery + 60
            restart()
            current_time = default_time
            health = health_max
            
    if creditsRoll:
        if not pygame.mixer.get_busy():
            jasot.play()
        text_size = 30
        credits_font = pygame.font.Font(DATA_ROOT + "/data/fonts/ambitsek.ttf",text_size)
        credits_text = \
'''
Projekt vypracován
třídou 1.EP skupina 2

---Generace mapy---

Jakub Polák
Karel Kříž
Jan Štěpánek

---Mechanika hráče---

Vojtěch Nepimach
Karel Kříž
Jakub Polák

---Textury---

Jakub Polák
Karel Kříž
Vojtěch Nepimach

---Zvuky---

Jakub Polák
Anna Poláková

---Minihry---

Marek Langer
Jan Pospíšil
Tadeáš Udatný
Martin Michálek
Tomáš Svoboda
Jakub Polák
Stanislav Lang
Votjtěch Laňka
Jan Serbousek

---Použitý Software---

Thonny
Tiled
Pixel Studio
Aseprite
Ardour

(více naleznete na githubu)
'''
        screen.fill("black")
        delta_y -= 2
        centerx, centery = screen.get_rect().centerx, screen.get_rect().centery
        
        text_list = []
        pos_list = []
        i = 0
        
        for line in credits_text.split('\n'):
            text_line = credits_font.render(line, True, (255,255,255))
            text_list.append(text_line)
            pos = text_line.get_rect(center=(centerx, centery + delta_y + i * text_size))
            pos_list.append(pos)
            i = i + 1
         
        if (centery + delta_y + text_size * (len(credits_text.split('\n'))) < 0):
            creditsRoll = False
            inMenu = True
            jasot.stop()
            delta_y = screen.get_rect().centery + 60
         
        for j in range(i):
            screen.blit(text_list[j], pos_list[j])
            
    if secondChance and timeForSecondChance > 0:
        text(15, "To go to the menu, press escape again.", 23*32/2, 50, (255, 255, 255), "Consolas", "center", True)
        text(15, "You will lose progress.", 23*32/2, 65, (255, 255, 255), "Consolas", "center", True)

    pygame.display.update()
    clock.tick(60)
