4ball_game/
│
├─ main.py               # 실행 파일 (게임 루프)
│
├─ physics/
│   ├─ __init__.py
│   ├─ ball.py           # 공 클래스 (위치, 속도, 업데이트)
│   ├─ collision.py      # 공-공, 공-쿠션 충돌 처리
│   └─ table.py          # 당구대 경계 정의
│
└─ game/
    ├─ state.py          # 공들 상태 관리
    └─ input.py          # 샷 입력(마우스 드래그)
