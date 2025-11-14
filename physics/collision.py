import math
from physics.table import TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT


def _realistic_cushion_response(ball, nx, ny):
    """
    nx, ny: 쿠션의 '안쪽을 향하는' 법선 벡터
      - 왼쪽 벽:  (1, 0)
      - 오른쪽 벽: (-1, 0)
      - 위쪽 벽:  (0, 1)
      - 아래쪽 벽:(0,-1)
    """
    vx, vy = ball.vx, ball.vy

    # 속도 벡터 크기
    speed = math.hypot(vx, vy)
    if speed == 0:
        return

    # v 를 법선/접선 성분으로 분해
    # v·n
    vn_scalar = vx * nx + vy * ny
    # 법선 성분 벡터
    vn_x = vn_scalar * nx
    vn_y = vn_scalar * ny
    # 접선 성분 벡터
    vt_x = vx - vn_x
    vt_y = vy - vn_y

    # 입사각에 따른 반발계수/마찰계수 보정
    # cos(theta) = |vn| / |v|
    cos_theta = abs(vn_scalar) / (speed + 1e-8)

    # 기본 반발계수/마찰계수
    base_e = 0.93       # 쿠션의 반발계수(대략 0.9~0.95 정도)
    base_tangent = 0.97 # 접선 감쇠(1에 가까울수록 미끄러짐, 낮을수록 더 감속)

    # 입사각이 정면(법선에 가깝)일수록 반발계수 더 높이고,
    # 비스듬히 스칠수록 살짝 낮추는 정도
    # e(θ) = e0 - a * (1 - cosθ)
    e = base_e - 0.05 * (1.0 - cos_theta)
    # 접선 마찰: 정면에 가까울수록 마찰 조금 더 큼
    tangent_scale = base_tangent - 0.05 * cos_theta

    # 안정 범위 클램프
    e = max(0.7, min(0.98, e))
    tangent_scale = max(0.85, min(0.99, tangent_scale))

    # 반사 후 법선/접선 성분
    # 법선은 방향 뒤집고 크기는 e 배
    vn_after_x = -e * vn_x
    vn_after_y = -e * vn_y

    # 접선은 마찰로 크기를 줄여줌
    vt_after_x = tangent_scale * vt_x
    vt_after_y = tangent_scale * vt_y

    # 최종 속도 = 법선 + 접선
    ball.vx = vn_after_x + vt_after_x
    ball.vy = vn_after_y + vt_after_y


def handle_cushion_collision(ball):
    """
    테이블 사각형에 대한 쿠션 충돌 처리.
    위치 보정 + 현실적인 반사 응답.
    """
    # 왼쪽 쿠션
    if ball.x - ball.radius < TABLE_MARGIN:
        ball.x = TABLE_MARGIN + ball.radius
        _realistic_cushion_response(ball, nx=1.0, ny=0.0)

    # 오른쪽 쿠션
    if ball.x + ball.radius > TABLE_WIDTH - TABLE_MARGIN:
        ball.x = TABLE_WIDTH - TABLE_MARGIN - ball.radius
        _realistic_cushion_response(ball, nx=-1.0, ny=0.0)

    # 위쪽 쿠션
    if ball.y - ball.radius < TABLE_MARGIN:
        ball.y = TABLE_MARGIN + ball.radius
        _realistic_cushion_response(ball, nx=0.0, ny=1.0)

    # 아래쪽 쿠션
    if ball.y + ball.radius > TABLE_HEIGHT - TABLE_MARGIN:
        ball.y = TABLE_HEIGHT - TABLE_MARGIN - ball.radius
        _realistic_cushion_response(ball, nx=0.0, ny=-1.0)


def handle_ball_collision(a, b):
    """
    공-공 충돌 처리 (질량 같은 두 공, 약간 비탄성).
    """
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius

    # 충돌하지 않은 경우
    if dist == 0 or dist >= min_dist:
        return

    # 정규화된 충돌 법선
    nx = dx / dist
    ny = dy / dist

    # 겹침 해소 (penetration correction)
    overlap = min_dist - dist
    a.x -= nx * overlap * 0.5
    a.y -= ny * overlap * 0.5
    b.x += nx * overlap * 0.5
    b.y += ny * overlap * 0.5

    # 상대 속도
    rvx = b.vx - a.vx
    rvy = b.vy - a.vy

    # 법선 방향 상대 속도
    vel_along_normal = rvx * nx + rvy * ny

    # 이미 서로 멀어지는 중이면 패스
    if vel_along_normal > 0:
        return

    # 반발계수 (당구는 0.85~0.95 정도가 자연스러움)
    restitution = 0.92

    # 충격량 스칼라 (질량 동일 가정)
    j = -(1 + restitution) * vel_along_normal
    j /= 2.0

    # 충격량 벡터
    impulse_x = j * nx
    impulse_y = j * ny

    # 속도 업데이트
    a.vx -= impulse_x
    a.vy -= impulse_y
    b.vx += impulse_x
    b.vy += impulse_y
