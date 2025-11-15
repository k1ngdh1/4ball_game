# physics/table.py

# 전체 창 크기
TABLE_WIDTH = 900
TABLE_HEIGHT = 500

# 창 가장자리 여백 (바깥 배경용)
TABLE_MARGIN = 40

# 쿠션 두께 (픽셀) – pygame rect width로도 사용
CUSHION_THICKNESS = 30

# 쿠션을 그릴 사각형 (테두리 중심 기준)
# 여기 기준으로 width=CUSHION_THICKNESS 테두리를 그리면
# 안/밖으로 절반씩 쿠션이 생김
CUSHION_RECT = (
    TABLE_MARGIN,
    TABLE_MARGIN,
    TABLE_WIDTH - 2 * TABLE_MARGIN,
    TABLE_HEIGHT - 2 * TABLE_MARGIN,
)

# === 물리적으로 공이 움직일 수 있는 "안쪽 경계" ===
# 테두리의 안쪽 라인이 이 좌표가 되도록 맞춤
INNER_LEFT   = TABLE_MARGIN + CUSHION_THICKNESS / 2
INNER_TOP    = TABLE_MARGIN + CUSHION_THICKNESS / 2
INNER_RIGHT  = TABLE_WIDTH  - TABLE_MARGIN - CUSHION_THICKNESS / 2
INNER_BOTTOM = TABLE_HEIGHT - TABLE_MARGIN - CUSHION_THICKNESS / 2

# 플레이 영역(Rect) – 안쪽 초록색 영역
TABLE_RECT = (
    INNER_LEFT,
    INNER_TOP,
    INNER_RIGHT - INNER_LEFT,
    INNER_BOTTOM - INNER_TOP,
)
