import pygame
from physics.ball import Ball
from physics.table import (
    TABLE_WIDTH,
    TABLE_HEIGHT,
    TABLE_RECT,        # 플레이 영역 (안쪽 초록)
    CUSHION_RECT,      # 쿠션 영역
    CUSHION_THICKNESS, # 지금은 안 써도 되지만 일단 둬도 됨
)
from physics.collision import handle_cushion_collision, handle_ball_collision

pygame.init()

WIDTH, HEIGHT = TABLE_WIDTH, TABLE_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Cushion Prototype v0.1")
clock = pygame.time.Clock()

# 색상 설정
BACKGROUND_COLOR = (4, 40, 12)     # 바깥 배경(짙은 초록)
CLOTH_COLOR      = (8, 100, 28)    # 테이블 천(안쪽)
CUSHION_COLOR    = (196, 160, 112) # 연한 갈색 쿠션
AIM_LINE_COLOR   = (255, 255, 255) # 조준선

# 공 생성
balls = [
    Ball(300, 200, (255, 255, 255)),  # 흰공
    Ball(600, 250, (255, 255, 0)),    # 노랑
    Ball(400, 350, (255, 0, 0)),      # 빨강
]

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
            balls[0].vx = dx * 0.04
            balls[0].vy = dy * 0.04

    # 공 업데이트 + 충돌 처리
    for i, b in enumerate(balls):
        b.update(dt)
        handle_cushion_collision(b)
        for j in range(i + 1, len(balls)):
            handle_ball_collision(b, balls[j])

    # ===== 화면 그리기 =====
    # 1) 바깥 배경
    screen.fill(BACKGROUND_COLOR)

    # 2) 쿠션(연한 갈색) 전체를 먼저 채우기
    pygame.draw.rect(
        screen,
        CUSHION_COLOR,
        pygame.Rect(*CUSHION_RECT),
    )

    # 3) 그 안쪽에 초록 천을 다시 채우기
    pygame.draw.rect(
        screen,
        CLOTH_COLOR,
        pygame.Rect(*TABLE_RECT),
    )

    # 4) 공 렌더링
    for b in balls:
        pygame.draw.circle(screen, b.color, (int(b.x), int(b.y)), b.radius)

    # 5) 드래그 중 샷 표시선
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
