import pygame
import pymunk
import pymunk.pygame_util

from physics.table import (
    TABLE_WIDTH,
    TABLE_HEIGHT,
    TABLE_RECT,      # 안쪽 초록 천 영역 (x, y, w, h)
    CUSHION_RECT,    # 쿠션 전체 영역
)

pygame.init()

WIDTH, HEIGHT = TABLE_WIDTH, TABLE_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Cushion Pymunk Version")
clock = pygame.time.Clock()

# ===== 색상 설정 =====
BACKGROUND_COLOR = (4, 40, 12)     # 바깥 배경(짙은 초록)
CLOTH_COLOR      = (8, 100, 28)    # 테이블 천(안쪽 초록)
CUSHION_COLOR    = (196, 160, 112) # 연한 갈색 쿠션
AIM_LINE_COLOR   = (255, 255, 255) # 조준선

# ===== Pymunk 설정 =====
space = pymunk.Space()
space.gravity = (0, 0)  # 당구대이므로 중력 없음

# 디버그용 (원하면 space를 직접 그려볼 수 있음)
# draw_options = pymunk.pygame_util.DrawOptions(screen)

# 공 물리 파라미터
BALL_RADIUS = 12
BALL_MASS = 1.0
BALL_INERTIA = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS)

BALL_FRICTION = 0.6
BALL_RESTITUTION = 0.88  # 공-공 / 공-쿠션 튀는 정도

# 쿠션 물리 파라미터
CUSHION_FRICTION = 0.8
CUSHION_RESTITUTION = 0.85


def add_ball(x, y, color):
    """
    Pymunk space에 공 하나 추가.
    (body, shape, color)를 리턴해서 나중에 그릴 때 쓴다.
    """
    body = pymunk.Body(BALL_MASS, BALL_INERTIA)
    body.position = (x, y)
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.friction = BALL_FRICTION
    shape.elasticity = BALL_RESTITUTION
    # pygame 그릴 때 쓰려고 색을 저장해둔다 (pymunk가 쓰는 필드는 아님)
    shape._render_color = color
    space.add(body, shape)
    return body, shape


# === 공 3개 생성 ===
balls = [
    add_ball(300, 200, (255, 255, 255)),  # 흰공
    add_ball(600, 250, (255, 255, 0)),    # 노랑
    add_ball(400, 350, (255,   0, 0)),    # 빨강
]
# balls[i] = (body, shape)

# === 테이블 내부 경계 (벽) 만들기 ===
inner_x, inner_y, inner_w, inner_h = TABLE_RECT
inner_left   = inner_x
inner_right  = inner_x + inner_w
inner_top    = inner_y
inner_bottom = inner_y + inner_h

static_body = space.static_body

# Segment 네 개로 안쪽 경계에 벽을 만든다.
# radius=0.0인 얇은 선이지만, 원형 공과 충돌은 정확히 처리됨.
cushion_segments = [
    # 위쪽 벽
    pymunk.Segment(static_body, (inner_left,  inner_top),
                                  (inner_right, inner_top),    0.0),
    # 오른쪽 벽
    pymunk.Segment(static_body, (inner_right, inner_top),
                                  (inner_right, inner_bottom), 0.0),
    # 아래쪽 벽
    pymunk.Segment(static_body, (inner_right, inner_bottom),
                                  (inner_left,  inner_bottom), 0.0),
    # 왼쪽 벽
    pymunk.Segment(static_body, (inner_left,  inner_bottom),
                                  (inner_left,  inner_top),    0.0),
]

for seg in cushion_segments:
    seg.friction = CUSHION_FRICTION
    seg.elasticity = CUSHION_RESTITUTION
    space.add(seg)

# ===== 입력/루프 상태 =====
shooting = False
start_pos = None
running = True

while running:
    dt = clock.tick(60) / 1000.0  # 초 단위

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

            # 너무 짧게 드래그한 건 샷 취소
            dist = math.hypot(dx, dy)
            if dist < 5:
                continue

            # 방향 단위 벡터
            nx = dx / dist
            ny = dy / dist

            # 드래그 길이 캡
            drag_len = min(dist, MAX_DRAG_PIXELS)

            # 최종 힘 크기
            force_mag = drag_len * SHOT_POWER_PER_PIXEL

            impulse = (nx * force_mag, ny * force_mag)

            cue_body, cue_shape = balls[0]

            # 이전 잔여 속도/회전 초기화 후 샷
            cue_body.velocity = (0, 0)
            cue_body.angular_velocity = 0

            cue_body.apply_impulse_at_local_point(impulse, (0, 0))
    # ===== Pymunk 물리 업데이트 =====
    space.step(dt)
    for body, shape in balls:
        vx, vy = body.velocity

        # 1) 속도를 약간 줄이기 (프레임마다 0.985배)
        damping = 0.985
        vx *= damping
        vy *= damping

        # 2) 아주 느려지면 그냥 멈춘 것으로 처리
        if abs(vx) < 3 and abs(vy) < 3:
            vx, vy = 0.0, 0.0

        body.velocity = (vx, vy)

    # ===== 화면 그리기 =====
    # 바깥 배경
    screen.fill(BACKGROUND_COLOR)

    # 쿠션(연갈색) 먼저 채우기
    pygame.draw.rect(screen, CUSHION_COLOR, pygame.Rect(*CUSHION_RECT))
    # 안쪽 테이블 천(초록) 덮어쓰기
    pygame.draw.rect(screen, CLOTH_COLOR, pygame.Rect(*TABLE_RECT))

    # (원하면 Pymunk 디버그 렌더)
    # space.debug_draw(draw_options)

    # 공 렌더링 (Pymunk body 위치 사용)
    for body, shape in balls:
        x, y = body.position
        color = shape._render_color
        pygame.draw.circle(screen, color, (int(x), int(y)), int(shape.radius))

    # 드래그 중 조준선
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
