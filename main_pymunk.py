import pygame
import pymunk
import pymunk.pygame_util

from physics.table import (
    TABLE_WIDTH,
    TABLE_HEIGHT,
    TABLE_RECT,
    CUSHION_RECT,
)
# 기존 Ball, collision은 잠시 안 쓴다.


pygame.init()

WIDTH, HEIGHT = TABLE_WIDTH, TABLE_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Cushion Pymunk Prototype")
clock = pygame.time.Clock()

# 색상
BACKGROUND_COLOR = (4, 40, 12)
CLOTH_COLOR      = (8, 100, 28)
CUSHION_COLOR    = (196, 160, 112)
AIM_LINE_COLOR   = (255, 255, 255)

# ===== Pymunk 설정 =====
space = pymunk.Space()
space.gravity = (0, 0)  # 중력 없음 (당구니까)

draw_options = pymunk.pygame_util.DrawOptions(screen)

# 마찰/반발 기본값
BALL_FRICTION = 0.2
BALL_RESTITUTION = 0.95
CUSHION_FRICTION = 0.3
CUSHION_RESTITUTION = 0.9

BALL_RADIUS = 12
BALL_MASS = 1.0
BALL_INERTIA = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS)


def add_ball(x, y, color):
    """Pymunk Space에 공 하나 추가하고, (body, shape, color)를 리턴."""
    body = pymunk.Body(BALL_MASS, BALL_INERTIA)
    body.position = (x, y)
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.friction = BALL_FRICTION
    shape.elasticity = BALL_RESTITUTION
    shape.color = color  # pygame 그릴 때 쓰기 위한 커스텀 필드
    space.add(body, shape)
    return body, shape


# 공 3개
balls = [
    add_ball(300, 200, (255, 255, 255)),  # 흰공
    add_ball(600, 250, (255, 255, 0)),    # 노랑
    add_ball(400, 350, (255,   0, 0)),    # 빨강
]
# balls[i] = (body, shape)


# ===== 테이블 쿠션을 Pymunk static shape로 만들기 =====
# TABLE_RECT는 (x, y, w, h) 형태의 플레이 영역
inner_x, inner_y, inner_w, inner_h = TABLE_RECT
inner_left   = inner_x
inner_right  = inner_x + inner_w
inner_top    = inner_y
inner_bottom = inner_y + inner_h

static_body = space.static_body

# 네 변을 Segment로 만든다 (반지름=0인 선)
# 살짝 안쪽으로 radius 주고 싶으면 Segment의 radius를 BALL_RADIUS 정도로 줄 수도 있음.
cushion_segments = [
    pymunk.Segment(static_body, (inner_left,  inner_top),    (inner_right, inner_top),    1.0),
    pymunk.Segment(static_body, (inner_right, inner_top),    (inner_right, inner_bottom), 1.0),
    pymunk.Segment(static_body, (inner_right, inner_bottom), (inner_left,  inner_bottom),1.0),
    pymunk.Segment(static_body, (inner_left,  inner_bottom), (inner_left,  inner_top),   1.0),
]

for seg in cushion_segments:
    seg.friction = CUSHION_FRICTION
    seg.elasticity = CUSHION_RESTITUTION
    space.add(seg)


shooting = False
start_pos = None
running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 마우스 드래그 → 샷
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = pygame.mouse.get_pos()
            shooting = True

        if event.type == pygame.MOUSEBUTTONUP and shooting:
            end_pos = pygame.mouse.get_pos()
            shooting = False

            sx, sy = start_pos
            ex, ey = end_pos
            dx, dy = (sx - ex), (sy - ey)

            cue_body, cue_shape = balls[0]
            # 기존에는 vx, vy를 직접 세팅했지만,
            # 이제는 impulse를 줘서 튕기게 하자.
            # 힘 스케일은 필요에 따라 조절 (여기선 8.0 정도)
            power = 8.0
            cue_body.apply_impulse_at_local_point((dx * power, dy * power))


    # ===== Pymunk 물리 한 스텝 =====
    space.step(dt)

    # ===== 그리기 =====
    screen.fill(BACKGROUND_COLOR)

    # 쿠션 영역
    pygame.draw.rect(screen, CUSHION_COLOR, pygame.Rect(*CUSHION_RECT))
    # 안쪽 테이블 천
    pygame.draw.rect(screen, CLOTH_COLOR, pygame.Rect(*TABLE_RECT))

    # 공 렌더링 (Pymunk body 위치 사용)
    for body, shape in balls:
        x, y = body.position
        pygame.draw.circle(
            screen,
            shape.color,
            (int(x), int(y)),
            int(shape.radius),
        )

    # 조준선
    if shooting and start_pos:
        pygame.draw.line(
            screen,
            AIM_LINE_COLOR,
            start_pos,
            pygame.mouse.get_pos(),
            2,
        )

    pygame.display.flip()

pygame.quit()
