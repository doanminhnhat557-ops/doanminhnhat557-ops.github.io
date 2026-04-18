import pygame, sys, random, math

pygame.init()
screen = pygame.display.set_mode((600,700))
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# ===== LOAD =====
img_back = pygame.transform.scale(pygame.image.load("cata.png"),(400,500))
img_turn = pygame.transform.scale(pygame.image.load("catb.png"),(400,500))
img_bite = pygame.transform.scale(pygame.image.load("catc.png"),(400,500))
img_win  = pygame.transform.scale(pygame.image.load("catwin.png"),(400,500))
img_comb = pygame.transform.scale(pygame.image.load("luoc.png"),(80,80))

# ===== SOUND (nếu có file) =====
try:
    heartbeat = pygame.mixer.Sound("heartbeat.wav")
    bite_sound = pygame.mixer.Sound("bite.wav")
except:
    heartbeat = None
    bite_sound = None

# ===== RESET =====
def reset():
    return {
        "progress":0,
        "status":"back",
        "game_over":False,
        "win":False,
        "is_brushing":False,
        "danger":0,
        "rage":0,
        "combo":1,
        "last_mouse":None,
        "dir":0,
        "slow":1
    }

state = reset()
particles = []

zoom = 1
shake = 0
flash = 0

btn = pygame.Rect(200,620,200,50)

# ===== LOOP =====
while True:
    screen.fill((0,0,0))
    mouse = pygame.mouse.get_pos()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if e.type == pygame.MOUSEBUTTONDOWN:
            if (state["game_over"] or state["win"]) and btn.collidepoint(mouse):
                state = reset()
                particles.clear()
                zoom=1; shake=0; flash=0
                continue
            state["is_brushing"]=True

        if e.type == pygame.MOUSEBUTTONUP:
            state["is_brushing"]=False
            state["combo"]=1

    # ===== CHẢI =====
    if state["is_brushing"] and not state["game_over"] and not state["win"]:
        if state["last_mouse"]:
            dx = mouse[0]-state["last_mouse"][0]

            if dx>5 and state["dir"]==-1:
                state["combo"]=min(5,state["combo"]+1)
                state["progress"] += state["combo"]
                state["rage"] += 0.7

            if dx<-5 and state["dir"]==1:
                state["combo"]=min(5,state["combo"]+1)
                state["progress"] += state["combo"]
                state["rage"] += 0.7

            state["dir"]=1 if dx>0 else -1

        # lông
        for _ in range(5):
            particles.append([mouse[0],mouse[1],
                              random.uniform(-3,3),
                              random.uniform(-6,-2)])

    state["last_mouse"]=mouse

    # ===== WIN =====
    if state["progress"]>=100 and not state["game_over"]:
        state["win"]=True

    # ===== AI =====
    if not state["game_over"] and not state["win"]:
        if state["is_brushing"]:
            chance = 0.01 + state["progress"]/3000 + state["rage"]/300
            if random.random()<chance:
                state["status"]="turn"
                state["danger"]=0

    # ===== TURN =====
    if state["status"]=="turn":
        state["danger"]+=1

        # slow motion
        if 20 < state["danger"] < 45:
            state["slow"]=0.4
            flash = 20
        else:
            state["slow"]=1

        # cắn
        if state["danger"]>45 and state["is_brushing"]:
            state["status"]="bite"
            state["game_over"]=True
            zoom=1
            shake=50
            flash = 30
            if bite_sound: bite_sound.play()

        if state["danger"]>90:
            state["status"]="back"

    # ===== HEARTBEAT =====
    if heartbeat and not state["game_over"]:
        vol = min(1.0, state["rage"]/50)
        heartbeat.set_volume(vol)
        if not pygame.mixer.get_busy():
            heartbeat.play()

    # ===== SHAKE + ZOOM =====
    ox=oy=0
    if shake>0:
        shake-=1
        ox=int(math.sin(pygame.time.get_ticks()*0.3)*20)
        oy=int(math.cos(pygame.time.get_ticks()*0.3)*20)
        zoom += (3-zoom)*0.2
    else:
        zoom += (1-zoom)*0.1

    # ===== IMAGE =====
    if state["win"]: img=img_win
    elif state["status"]=="back": img=img_back
    elif state["status"]=="turn": img=img_turn
    else: img=img_bite

    w=int(400*zoom); h=int(500*zoom)
    img2=pygame.transform.scale(img,(w,h))
    screen.blit(img2,(100-(w-400)//2+ox,150-(h-500)//2+oy))

    # ===== FLASH =====
    if flash>0:
        flash-=1
        overlay = pygame.Surface((600,700))
        overlay.set_alpha(120)
        overlay.fill((255,0,0))
        screen.blit(overlay,(0,0))

    # ===== VIGNETTE =====
    vig = pygame.Surface((600,700), pygame.SRCALPHA)
    pygame.draw.rect(vig,(0,0,0,150),(0,0,600,700), border_radius=200)
    screen.blit(vig,(0,0))

    # ===== PARTICLES =====
    new=[]
    for p in particles:
        p[0]+=p[2]*state["slow"]
        p[1]+=p[3]*state["slow"]
        p[3]+=0.3

        pygame.draw.line(screen,(220,220,220),
                         (p[0],p[1]),(p[0]+4,p[1]+8),2)

        if p[1]<700: new.append(p)
    particles=new

    # ===== COMB =====
    if not state["game_over"] and not state["win"]:
        screen.blit(img_comb,(mouse[0]-40,mouse[1]-40))
        pygame.mouse.set_visible(False)
    else:
        pygame.mouse.set_visible(True)

    # ===== UI =====
    pygame.draw.rect(screen,(80,80,80),(50,50,500,12))
    pygame.draw.rect(screen,(0,255,0),(50,50,int(state["progress"]*5),12))

    pygame.draw.rect(screen,(80,0,0),(50,70,500,10))
    pygame.draw.rect(screen,(255,0,0),(50,70,int(state["rage"]*3),10))

    txt=font.render(f"{int(state['progress'])}% x{state['combo']}",True,(255,255,255))
    screen.blit(txt,(220,90))

    if state["game_over"]:
        t=font.render("YOU DIED 💀",True,(255,0,0))
        screen.blit(t,(200,120))
    elif state["win"]:
        t=font.render("ESCAPED...?",True,(0,255,0))
        screen.blit(t,(190,120))
    else:
        t=font.render("DON'T LOOK BACK...",True,(200,200,200))
        screen.blit(t,(160,120))

    # ===== BUTTON =====
    if state["game_over"] or state["win"]:
        pygame.draw.rect(screen,(255,255,255),btn, border_radius=10)
        t=font.render("RETRY",True,(0,0,0))
        screen.blit(t,(btn.x+60,btn.y+10))

    pygame.display.update()
    clock.tick(int(60*state["slow"]))
