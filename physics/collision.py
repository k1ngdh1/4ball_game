import math
from physics.table import (
    INNER_LEFT,
    INNER_RIGHT,
    INNER_TOP,
    INNER_BOTTOM,
)


def _realistic_cushion_response(ball, nx, ny):
    """
    쿠션 반사 응답.
    nx, ny: 쿠션 안쪽을 향하는 단위 법선 벡터
      - 왼쪽 벽:  ( 1, 0)
      - 오른쪽 벽: (-1, 0)
      - 위쪽 벽:  ( 0, 1)
      - 아래쪽 벽: ( 0,-1)
    """
    vx, vy = ball.vx, ball.vy
    speed = math.hypot(vx, vy)
    if speed == 0:
        return

    # 속도 벡터를 법선/접선 성분으로 분해
    vn_scalar = vx * nx + vy * ny      # v·n
    vn_x = vn_scalar * nx
    vn_y = vn_scalar * ny
    vt_x = vx - vn_x
    vt_y = vy - vn_y

    # 입사각에 따른 보정
    cos_theta = abs(vn_scalar) / (speed + 1e-8)

    base_e = 0.93        # 기본 반발계수
    base_tangent = 0.97  # 기본 접선 감쇠

    # 정면에 가까울수록(e.g. cosθ≈1) 반발 조금 더 강하게,
    # 비스듬할수록 살짝 약하게
    e = base_e - 0.05 * (1.0 - cos_theta)
    # 접선 마찰: 정면일수록 마찰 좀 더 크게
    tangent_scale = base_tangent - 0.05 * cos_theta

    # 안정 범위 클램프
    e = max(0.7, min(0.98, e))
    tangent_scale = max(0.85, min(0.99, tangent_scale))

    # 반사 후 법선/접선 성분
    vn_after_x = -e * vn_x
    vn_after_y = -e * vn_y
    vt_after_x = tangent_scale * vt_x
    vt_after_y = tangent_scale * vt_y

    # 최종 속도
    ball.vx = vn_after_x + vt_after_x
    ball.vy = vn_after_y + vt_after_y


def handle_cushion_collision(ball):
    """
    INNER_* (플레이 영역 안쪽 경계)를 기준으로
    쿠션 충돌 판정을 한다.
    충돌이 발생하면 True, 아니면 False를 반환.
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


def handle_ball_collision(b1, b2):
    """
    두 공(b1, b2) 사이의 2D 탄성 충돌 처리.
    - python-billiards에서 쓰는 '단단한 원(디스크)의 탄성충돌' 모델과 같은 원리.
    - 접선 성분은 유지하고, 법선 성분만 운동량/에너지 보존을 만족하도록 갱신.
    """
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist_sq = dx * dx + dy * dy

    min_dist = b1.radius + b2.radius
    min_dist_sq = min_dist * min_dist

    # 너무 멀거나 완전히 같은 위치
    if dist_sq == 0:
        # 완전 겹친 특수 케이스: 살짝 벌려주기만 하고 종료
        sep = min_dist or 1.0
        b2.x += sep * 0.5
        b2.y += sep * 0.5
        return

    if dist_sq >= min_dist_sq:
        return  # 아직 안 겹침 → 충돌 아님

    dist = math.sqrt(dist_sq)
    nx = dx / dist
    ny = dy / dist  # b1 → b2 방향 단위 법선

    # 상대 속도를 법선 방향으로 투영
    dvx = b1.vx - b2.vx
    dvy = b1.vy - b2.vy
    rel_normal = dvx * nx + dvy * ny

    # 이미 서로 멀어지는 중이면 스킵
    if rel_normal > 0:
        return

    # 질량 (없으면 1.0으로 가정)
    m1 = getattr(b1, "mass", 1.0)
    m2 = getattr(b2, "mass", 1.0)

    # 거의 탄성 충돌 (e=1이면 완전 탄성, 살짝 줄여서 0.98)
    restitution = 0.95

    # 충격량 스칼라 j
    # j = -(1+e) * (v_rel·n) / (1/m1 + 1/m2)
    inv_m1 = 1.0 / m1
    inv_m2 = 1.0 / m2
    j = -(1.0 + restitution) * rel_normal / (inv_m1 + inv_m2)

    impulse_x = j * nx
    impulse_y = j * ny

    # 속도 갱신 (운동량 보존)
    b1.vx += impulse_x * inv_m1
    b1.vy += impulse_y * inv_m1
    b2.vx -= impulse_x * inv_m2
    b2.vy -= impulse_y * inv_m2

    # 위치 겹침 보정 (프레임 기반이라 약간 겹칠 수 있어서 분리)
    overlap = min_dist - dist
    if overlap > 0:
        inv_mass_sum = inv_m1 + inv_m2
        corr1 = overlap * inv_m1 / inv_mass_sum
        corr2 = overlap * inv_m2 / inv_mass_sum

        b1.x -= corr1 * nx
        b1.y -= corr1 * ny
        b2.x += corr2 * nx
        b2.y += corr2 * ny
