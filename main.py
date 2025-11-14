import pygame
import math
from physics.ball import Ball
from physics.table import TABLE_WIDTH, TABLE_HEIGHT, TABLE_RECT
from physics.collision import handle_cushion_collision, handle_ball_collision

pygame.init()

WIDTH, HEIGHT = TABLE_WIDTH, TABLE_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Cushion Prototype v0.1")
clock = pygame.time.Clock()

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
    dt = clock.tick(60) / 1000.0  # delta time (초 단위)

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

            # 힘 = 드래그 거리의 0.03배
            sx, sy = start_pos
            ex, ey = end_pos
            dx, dy = (sx - ex), (sy - ey)
            balls[0].vx = dx * 0.03
            balls[0].vy = dy * 0.03

    # 공 업데이트 + 충돌 처리
    for i, b in enumerate(balls):
        b.update(dt)
        handle_cushion_collision(b)

        # 공-공 충돌
        for j in range(i + 1, len(balls)):
            handle_ball_collision(b, balls[j])

    # 화면 그리기
    screen.fill((8, 100, 28))  # 당구대 초록색

    # 쿠션 경계
    pygame.draw.rect(screen, (50, 30, 10), TABLE_RECT, 20)

    # 공 렌더링
    for b in balls:
        pygame.draw.circle(screen, b.color, (int(b.x), int(b.y)), b.radius)

    # 드래그 중 샷 표시선
    if shooting and start_pos:
        pygame.draw.line(screen, (255, 255, 255), start_pos,
                         pygame.mouse.get_pos(), 2)

    pygame.display.flip()

pygame.quit()
