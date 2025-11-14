import math

class Ball:
    def __init__(self, x, y, color, radius=12, friction=0.992):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color

        self.vx = 0.0  # 픽셀/프레임
        self.vy = 0.0
        self.friction = friction  # 1프레임마다 몇 배 남기는지 (0~1)

    def update(self, dt):
        # 1) 마찰 적용 (프레임 기반)
        self.vx *= self.friction
        self.vy *= self.friction

        if abs(self.vx) < 0.02:
            self.vx = 0.0
        if abs(self.vy) < 0.02:
            self.vy = 0.0

        # 2) 위치 업데이트 (dt 안 쓰고 px/frame 기준)
        self.x += self.vx
        self.y += self.vy
import math

class Ball:
    def __init__(self, x, y, color, radius=12, friction=0.992):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color

        self.vx = 0.0  # 픽셀/프레임
        self.vy = 0.0
        self.friction = friction  # 1프레임마다 몇 배 남기는지 (0~1)

    def update(self, dt):
        # 1) 마찰 적용 (프레임 기반)
        self.vx *= self.friction
        self.vy *= self.friction

        if abs(self.vx) < 0.02:
            self.vx = 0.0
        if abs(self.vy) < 0.02:
            self.vy = 0.0

        # 2) 위치 업데이트 (dt 안 쓰고 px/frame 기준)
        self.x += self.vx
        self.y += self.vy
