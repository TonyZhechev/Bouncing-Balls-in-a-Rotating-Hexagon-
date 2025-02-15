import pygame

import math

import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
HEX_RADIUS = 250
BALL_RADIUS = 15
GRAVITY = 0.5
FRICTION = 0.99
WALL_FRICTION = 0.1
COR = 0.8  # Coefficient of restitution
ANGULAR_VELOCITY = 0.03
BALL_COLORS = [(255, 0, 0), (0, 255, 0)]  # Red and Green balls

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class Ball:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.color = color

class Hexagon:
    def __init__(self, radius, center):
        self.radius = radius
        self.center = center
        self.angle = 0.0

    def get_vertices(self):
        return [(self.center[0] + self.radius * math.cos(self.angle + i * math.pi/3),
                 self.center[1] + self.radius * math.sin(self.angle + i * math.pi/3))
                for i in range(6)]

def closest_point_on_segment(A, B, C):
    ax, ay = A
    bx, by = B
    cx, cy = C
    abx, aby = bx - ax, by - ay
    t = ((cx - ax) * abx + (cy - ay) * aby) / (abx**2 + aby**2 + 1e-8)
    t = max(0, min(1, t))
    return (ax + t * abx, ay + t * aby)

def resolve_ball_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.hypot(dx, dy)

    if distance < 2 * BALL_RADIUS:
        overlap = 2 * BALL_RADIUS - distance
        angle = math.atan2(dy, dx)
        sin = math.sin(angle)
        cos = math.cos(angle)

        # Separate balls to avoid overlap
        ball1.x -= overlap * cos / 2
        ball1.y -= overlap * sin / 2
        ball2.x += overlap * cos / 2
        ball2.y += overlap * sin / 2

        # Calculate relative velocity
        v1x = ball1.vx
        v1y = ball1.vy
        v2x = ball2.vx
        v2y = ball2.vy

        # Normal and tangential components
        nx = dx / distance
        ny = dy / distance
        tx = -ny
        ty = nx

        # Dot products
        dp_tan1 = v1x * tx + v1y * ty
        dp_tan2 = v2x * tx + v2y * ty
        dp_norm1 = v1x * nx + v1y * ny
        dp_norm2 = v2x * nx + v2y * ny

        # Conservation of momentum and energy
        m1 = (dp_norm1 * (1 - COR) + dp_norm2 * (1 + COR)) / 2
        m2 = (dp_norm2 * (1 - COR) + dp_norm1 * (1 + COR)) / 2

        # Update velocities
        ball1.vx = tx * dp_tan1 + nx * m1
        ball1.vy = ty * dp_tan1 + ny * m1
        ball2.vx = tx * dp_tan2 + nx * m2
        ball2.vy = ty * dp_tan2 + ny * m2

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Spinning Hexagon with Two Balls")
clock = pygame.time.Clock()

# Initialize balls
ball1 = Ball(CENTER[0] - 50, CENTER[1] - HEX_RADIUS + BALL_RADIUS + 5, BALL_COLORS[0])
ball2 = Ball(CENTER[0] + 50, CENTER[1] - HEX_RADIUS + BALL_RADIUS + 5, BALL_COLORS[1])
balls = [ball1, ball2]

# Initialize hexagon
hexagon = Hexagon(HEX_RADIUS, CENTER)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    hexagon.angle = (hexagon.angle + ANGULAR_VELOCITY) % (2 * math.pi)

    # Update ball physics
    for ball in balls:
        ball.vy += GRAVITY
        ball.vx *= FRICTION
        ball.vy *= FRICTION
        ball.x += ball.vx
        ball.y += ball.vy

    # Check for ball collisions with hexagon walls
    vertices = hexagon.get_vertices()
    for ball in balls:
        for i in range(6):
            A, B = vertices[i], vertices[(i+1)%6]
            P = closest_point_on_segment(A, B, (ball.x, ball.y))
            dx, dy = ball.x - P[0], ball.y - P[1]
            distance = math.hypot(dx, dy)

            if distance < BALL_RADIUS:
                midpoint = ((A[0]+B[0])/2, (A[1]+B[1])/2)
                normal_x, normal_y = hexagon.center[0]-midpoint[0], hexagon.center[1]-midpoint[1]
                length = math.hypot(normal_x, normal_y)
                if length == 0:
                    continue
                normal_x, normal_y = normal_x/length, normal_y/length

                # Wall velocity at collision point
                vw_x = -ANGULAR_VELOCITY * (P[1]-hexagon.center[1])
                vw_y = ANGULAR_VELOCITY * (P[0]-hexagon.center[0])

                # Relative velocity
                rel_vx = ball.vx - vw_x
                rel_vy = ball.vy - vw_y

                dp = rel_vx * normal_x + rel_vy * normal_y
                if dp < 0:
                    # Collision response
                    nc_x = dp * normal_x
                    nc_y = dp * normal_y
                    tc_x = rel_vx - nc_x
                    tc_y = rel_vy - nc_y

                    new_nc_x = -COR * nc_x
                    new_nc_y = -COR * nc_y
                    new_tc_x = tc_x * (1 - WALL_FRICTION)
                    new_tc_y = tc_y * (1 - WALL_FRICTION)

                    ball.vx = vw_x + new_nc_x + new_tc_x
                    ball.vy = vw_y + new_nc_y + new_tc_y

                    # Reposition ball
                    penetration = BALL_RADIUS - distance
                    ball.x += normal_x * penetration
                    ball.y += normal_y * penetration

    # Check for collisions between balls
    resolve_ball_collision(ball1, ball2)

    # Render
    screen.fill(BLACK)
    pygame.draw.polygon(screen, BLUE, vertices, 2)
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), BALL_RADIUS)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()