import math
from physics.table import (
    INNER_LEFT,
    INNER_RIGHT,
    INNER_TOP,
    INNER_BOTTOM,
)


def _realistic_cushion_response(ball, nx, ny):
    vx, vy = ball.vx, ball.vy
    speed = math.hypot(vx, vy)
    if speed == 0:
        return

    # 속도 벡터를 법선/접선 성분으로 분해
    vn_scalar = vx * nx + vy * ny
    vn_x = vn_scalar * nx
    vn_y = vn_scalar * ny
    vt_x = vx - vn_x
    vt_y = vy - vn_y

    # 입사각에 따른 보정
    cos_theta = abs(vn_scalar) / (speed + 1e-8)

    base_e = 0.93       # 반발계수
    base_tangent = 0.97 # 접선 감쇠

    e = base_e - 0.05 * (1.0 - cos_theta)
    tangent_scale = base_tangent - 0.05 * cos_theta

    e = max(0.7, min(0.98, e))
    tangent_scale = max(0.85, min(0.99, tangent_scale))

    vn_after_x = -e * vn_x
    vn_after_y = -e * vn_y
    vt_after_x = tangent_scale * vt_x
    vt_after_y = tangent_scale * vt_y

    ball.vx = vn_after_x + vt_after_x
    ball.vy = vn_after_y + vt_after_y


def handle_cushion_collision(ball):
    """
    INNER_* (플레이 영역 안쪽 경계)를 기준으로 쿠션 판정.
    """
    hit = False

    # 왼쪽 쿠션
    if ball.x - ball.radius < INNER_LEFT:
        ball.x = INNER_LEFT + ball.radius
        _realistic_cushion_response(ball, nx=1.0, ny=0.0)
        hit = True

    # 오른쪽 쿠션
    if ball.x + ball.radius > INNER_RIGHT:
        ball.x = INNER_RIGHT - ball.radius
        _realistic_cushion_response(ball, nx=-1.0, ny=0.0)
        hit = True

    # 위쪽 쿠션
    if ball.y - ball.radius < INNER_TOP:
        ball.y = INNER_TOP + ball.radius
        _realistic_cushion_response(ball, nx=0.0, ny=1.0)
        hit = True

    # 아래쪽 쿠션
    if ball.y + ball.radius > INNER_BOTTOM:
        ball.y = INNER_BOTTOM - ball.radius
        _realistic_cushion_response(ball, nx=0.0, ny=-1.0)
        hit = True

    return hit


def handle_ball_collision(a, b):
    """
    공-공 충돌 (질량 동일, 약간 비탄성).
    """
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius

    if dist == 0 or dist >= min_dist:
        return False

    nx = dx / dist
    ny = dy / dist

    # 겹침 해소
    overlap = min_dist - dist
    a.x -= nx * overlap * 0.5
    a.y -= ny * overlap * 0.5
    b.x += nx * overlap * 0.5
    b.y += ny * overlap * 0.5

    rvx = b.vx - a.vx
    rvy = b.vy - a.vy
    vel_along_normal = rvx * nx + rvy * ny

    if vel_along_normal > 0:
        return False

    restitution = 0.92
    j = -(1 + restitution) * vel_along_normal
    j /= 2.0

    impulse_x = j * nx
    impulse_y = j * ny

    a.vx -= impulse_x
    a.vy -= impulse_y
    b.vx += impulse_x
    b.vy += impulse_y

    return True
