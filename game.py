import pygame, random, math, sys

# ────── 상수 설정 ──────
BLOCK_SIZE, COLS = 48, 6
PLAY_ROWS        = 7                       # 0~6줄 플레이, 7줄째(8칸) 진입 → Game Over
UI_HEIGHT        = 88
WIDTH            = BLOCK_SIZE * COLS
HEIGHT           = PLAY_ROWS * BLOCK_SIZE + UI_HEIGHT
FPS              = 60
BALL_SPEED, R    = 8, 6
LAUNCH_GAP       = 4
A_MIN, A_MAX     = math.radians(-170), math.radians(-10)

# 색상
BEIGE  = (250, 240, 225)
WHITE  = (255, 255, 255)
ORANGE = (255, 165,   0)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BALL_C = (  0, 200, 255)          # 하늘색
TXT    = ( 50,  50,  50)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swipe Brick Breaker")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("malgungothic", 20, bold=True)

# ────── 유틸 ──────

def lerp(a,b,t): return a+(b-a)*t
def grad(hp,mx):
    return (int(lerp(ORANGE[0],RED[0],hp/mx)),
            int(lerp(ORANGE[1],RED[1],hp/mx)),
            int(lerp(ORANGE[2],RED[2],hp/mx)))
def circle_rect_overlap(cx, cy, radius, rect):
    """
    원(중심 cx,cy, 반지름 r)과 사각형 rect가 겹치면 True
    """
    closest_x = max(rect.left,  min(cx, rect.right))
    closest_y = max(rect.top,   min(cy, rect.bottom))
    dist_sq   = (cx - closest_x)**2 + (cy - closest_y)**2
    return dist_sq <= radius**2

# ────── 클래스 ──────
class Ball:
    def __init__(self, p, ang):
        self.x, self.y = p
        self.dx = BALL_SPEED * math.cos(ang)
        self.dy = BALL_SPEED * math.sin(ang)
        self.prev_x, self.prev_y = self.x, self.y   # 이전 위치

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y
        self.x += self.dx
        self.y += self.dy
        if self.x - R <= 0 or self.x + R >= WIDTH:
            self.dx *= -1
        if self.y - R <= 0:
            self.dy *= -1

    def reflect(self, rect):
        """
        충돌 후 반사 + 위치 보정
        """
        # 충돌 전·후 벡터
        vx, vy = self.dx, self.dy

        # 사각형과 원 중심의 최소 거리 벡터 구하기
        closest_x = max(rect.left,  min(self.prev_x, rect.right))
        closest_y = max(rect.top,   min(self.prev_y, rect.bottom))
        diff_x, diff_y = self.prev_x - closest_x, self.prev_y - closest_y

        # 어느 축 침투가 작은지로 반사 결정
        if abs(diff_x) > abs(diff_y):
            self.dx *= -1
        else:
            self.dy *= -1

        # 위치 보정 : 이전 좌표에서 1픽셀씩 반사방향으로 이동
        self.x, self.y = self.prev_x, self.prev_y
        for _ in range(12):
            self.x += self.dx * 0.5
            self.y += self.dy * 0.5
            if not circle_rect_overlap(self.x, self.y, R, rect):
                break


    @property
    def pos(self):                       # ← 빠졌던 부분
        return int(self.x), int(self.y)

    def draw(self):
        pygame.draw.circle(screen, BALL_C, self.pos, R)

class Block:
    def __init__(self, c, r, hp):
        self.rect = pygame.Rect(c*BLOCK_SIZE, r*BLOCK_SIZE, BLOCK_SIZE-2, BLOCK_SIZE-2)
        self.hp   = hp
    def draw(self, mx):
        pygame.draw.rect(screen, grad(self.hp, mx), self.rect)
        t = font.render(str(self.hp), True, WHITE)
        screen.blit(t, t.get_rect(center=self.rect.center))

class Bonus:
    def __init__(self, c):
        self.rect = pygame.Rect(0,0,20,20)
        self.rect.center = (c*BLOCK_SIZE + BLOCK_SIZE//2, BLOCK_SIZE//2)
    def draw(self):
        pygame.draw.circle(screen, GREEN, self.rect.center, 10)

# ────── 게임 상태 ──────
blocks, bonuses = [], []
balls, q        = [], []
balls_tot, turn = 1, 1

y_line  = PLAY_ROWS * BLOCK_SIZE        # 검은 선 (7칸과 8칸 경계)
shoot   = [WIDTH//2, y_line - R]        # 선 바로 위
shooting=False; first_ball=None; game_over=False

# ────── 함수 ──────
def spawn_row():
    global turn
    for blk in blocks:  blk.rect.y += BLOCK_SIZE
    for bon in bonuses: bon.rect.y += BLOCK_SIZE
    b_col = random.randrange(COLS)
    for c in range(COLS):
        if c == b_col:
            bonuses.append(Bonus(c))
        elif random.random() < 0.7:
            blocks.append(Block(c, 0, turn))

def is_over():
    return any(blk.rect.top >= y_line for blk in blocks)

def draw_ui():
    screen.blit(font.render(f"Level:{turn}  Balls:{balls_tot}", True, TXT), (10, y_line+12))

# 첫 행
spawn_row()
frame=0
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if game_over: continue
        if e.type == pygame.MOUSEBUTTONDOWN and not shooting:
            mx,my = pygame.mouse.get_pos()
            ang = max(min(math.atan2(my-shoot[1], mx-shoot[0]), A_MAX), A_MIN)
            q   = [ang]*balls_tot
            shooting = True

    # ── 업데이트 ──
    if not game_over:
        if shooting and q and frame % LAUNCH_GAP == 0:
            balls.append(Ball(shoot, q.pop(0)))

        for b in balls[:]:
            b.update()

            # 블록 충돌
            for blk in blocks[:]:
                if circle_rect_overlap(b.x, b.y, R, blk.rect):
                    blk.hp -= 1
                    b.reflect(blk.rect)
                    if blk.hp == 0:
                        blocks.remove(blk)
                    break

            # 보너스 충돌 (반사 없음)
            for bon in bonuses[:]:
                if circle_rect_overlap(b.x, b.y, R, bon.rect):
                    balls_tot += 1
                    bonuses.remove(bon)
                    break

            # 검은 선 기준 회수
            if b.y + R >= y_line:
                if first_ball is None:
                    first_ball = (b.x, b.y)
                balls.remove(b)

        if shooting and not balls and not q:
            shoot[0] = first_ball[0] if first_ball else shoot[0]
            shooting, first_ball = False, None
            turn += 1
            spawn_row(); game_over = is_over()

    # ── 렌더 ──
    screen.fill(BEIGE)
    pygame.draw.line(screen, TXT, (0,y_line), (WIDTH,y_line), 3)

    mx_hp = max([blk.hp for blk in blocks], default=1)
    for blk in blocks: blk.draw(mx_hp)
    for bon in bonuses: bon.draw()
    for b   in balls:   b.draw()

    pygame.draw.circle(screen, BALL_C, shoot, 7)     # 대기 공
    draw_ui()

    if game_over:
        msg = font.render("GAME  OVER", True, TXT)
        screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))

    pygame.display.flip(); frame += 1
