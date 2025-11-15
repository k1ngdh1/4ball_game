import math
from physics.table import TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT

# ... (여기에 네가 이미 만든 _realistic_cushion_response, handle_cushion_collision 그대로 두기)

def handle_ball_collision(b1, b2):
    """
    두 공(b1, b2) 사이의 2D 탄성 충돌 처리.
    - python-billiards처럼 '단단한 원(디스크)의 탄성충돌' 모델을 사용.
    - 접선 성분은 유지, 법선 성분만 서로 교환(질량/반발계수 고려).
    """

    # 1) 거리 / 충돌 여부 판정
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist_sq = dx * dx + dy * dy

    min_dist = (b1.radius + b2.radius)
    if dist_sq == 0:
        # 완전히 같은 위치 → 살짝 밀어내기만 하고 종료
        sep = min_dist or 1.0
        b2.x += sep * 0.5
        b2.y += sep * 0.5
        return

    if dist_sq >= min_dist * min_dist:
        # 아직 겹치지 않았으면 충돌 아님
        return

    dist = math.sqrt(dist_sq)
    nx = dx / dist
    ny = dy / dist  # 두 공 중심을 잇는 단위 법선 벡터 (b1->b2 방향)

    # 2) 상대 속도의 법선 성분 계산
    dvx = b1.vx - b2.vx
    dvy = b1.vy - b2.vy
    rel_normal = dvx * nx + dvy * ny

    # 이미 서로 멀어지는 중이면(법선 방향 상대속도가 0보다 크면) 스킵
    if rel_normal > 0:
        return

    # 3) 질량 / 반발계수
    m1 = getattr(b1, "mass", 1.0)
    m2 = getattr(b2, "mass", 1.0)

    # python-billiards는 에너지 보존(완전 탄성, e=1)을 쓰지만
    # 살짝 현실감 주려고 e를 0.98 정도로 둔다.
    restitution = 0.98

    # 충격량 스칼라(j) 계산 (일반적인 2D impulse 공식)
    # j = -(1+e) * (v_rel·n) / (1/m1 + 1/m2)
    j = -(1.0 + restitution) * rel_normal / (1.0 / m1 + 1.0 / m2)

    impulse_x = j * nx
    impulse_y = j * ny

    # 4) 속도 갱신 (운동량 보존)
    b1.vx += impulse_x / m1
    b1.vy += impulse_y / m1
    b2.vx -= impulse_x / m2
    b2.vy -= impulse_y / m2

    # 5) 겹침(position) 보정
    #    - python-billiards는 '충돌 순간으로 시간을 되감아서' 겹침을 원천 차단하지만
    #      우리는 프레임 기반이라 약간 겹칠 수 있어서 여기서 분리.
    overlap = min_dist - dist
    if overlap > 0:
        # 두 공을 질량 비율에 따라 반반씩 밀어내기
        inv_mass_sum = (1.0 / m1 + 1.0 / m2)
        corr1 = overlap * (1.0 / m1) / inv_mass_sum
        corr2 = overlap * (1.0 / m2) / inv_mass_sum

        b1.x -= corr1 * nx
        b1.y -= corr1 * ny
        b2.x += corr2 * nx
        b2.y += corr2 * ny
