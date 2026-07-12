import pygame
import sys
import time
import random
import math

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Configuration & Screen Setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("To the One Who Holds My Heart ❤️")
clock = pygame.time.Clock()

# Colors (Romantic Cinematic Palette)
BG_DARK = (12, 8, 20)
BG_DARK2 = (20, 10, 28)
TEXT_PINK = (255, 133, 190)
TEXT_WHITE = (245, 240, 250)
NEON_CYAN = (120, 230, 255)
GOLD = (255, 215, 130)
CAKE_COLOR = (244, 179, 194)
ICING_COLOR = (255, 250, 250)
CANDLE_COLOR = (255, 215, 0)
PETAL_PINK = (255, 150, 195)
PETAL_PINK_LIGHT = (255, 200, 220)
STEM_GREEN = (90, 150, 90)

# Fonts
font_small = pygame.font.SysFont("georgia", 24)
font_medium = pygame.font.SysFont("georgia", 38, bold=True)
font_large = pygame.font.SysFont("georgia", 56, bold=True)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ---------- Background gradient ----------
def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_DARK[0] + (BG_DARK2[0] - BG_DARK[0]) * t)
        g = int(BG_DARK[1] + (BG_DARK2[1] - BG_DARK[1]) * t)
        b = int(BG_DARK[2] + (BG_DARK2[2] - BG_DARK[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


# ---------- Particle Classes ----------
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(100, 255)
        self.speed = random.choice([0.5, 1, 1.5])

    def draw(self, surface):
        # Twinkle effect, clamped so alpha never leaves the valid 0-255 range
        self.alpha += self.speed
        if self.alpha >= 255:
            self.alpha = 255
            self.speed = -abs(self.speed)
        elif self.alpha <= 100:
            self.alpha = 100
            self.speed = abs(self.speed)

        safe_alpha = int(clamp(self.alpha, 0, 255))
        star_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (255, 255, 255, safe_alpha), (self.size, self.size), self.size)
        surface.blit(star_surf, (self.x, self.y))


class FloatingPetal:
    """A gently drifting flower petal, replacing the plain heart shapes."""

    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(HEIGHT, HEIGHT + 150) if not initial else random.randint(-150, HEIGHT)
        self.size = random.randint(8, 16)
        self.speed = random.uniform(0.6, 1.8)
        self.sway_speed = random.uniform(0.01, 0.03)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.2, 1.2)
        self.color = random.choice([PETAL_PINK, PETAL_PINK_LIGHT, TEXT_PINK])

    def move(self):
        self.y -= self.speed
        self.x += math.sin(self.sway_offset) * 0.8
        self.sway_offset += self.sway_speed
        self.rotation += self.rot_speed
        if self.y < -40:
            self.reset()

    def draw(self, surface):
        s = self.size * 2
        petal_surf = pygame.Surface((s, s), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.ellipse(petal_surf, (r, g, b, 200), (0, 0, s, s // 2 + 4))
        rotated = pygame.transform.rotate(petal_surf, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)


class Firefly:
    """Small glowing dot that drifts near the flower, echoing the reference image sparkle."""

    def __init__(self, cx, cy, radius):
        self.cx, self.cy, self.radius = cx, cy, radius
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.005, 0.015)
        self.dist = random.uniform(radius * 0.3, radius)
        self.pulse = random.uniform(0, math.pi * 2)

    def draw(self, surface):
        self.angle += self.speed
        self.pulse += 0.08
        x = self.cx + math.cos(self.angle) * self.dist
        y = self.cy + math.sin(self.angle * 0.7) * self.dist * 0.5
        alpha = int(150 + 100 * math.sin(self.pulse))
        alpha = int(clamp(alpha, 0, 255))
        glow = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 220, alpha), (5, 5), 3)
        surface.blit(glow, (x - 5, y - 5))


# ---------- Vector Flower (inspired by the reference bouquet look) ----------
def draw_flower_bouquet(surface, cx, base_y, sway=0.0, scale=1.0):
    """Draws a small stylized bouquet: a few stems with layered petals and leaves."""
    stem_h = 160 * scale
    stems = [
        (cx - 55 * scale, 0.85, -0.10),
        (cx - 20 * scale, 1.0, -0.04),
        (cx + 15 * scale, 1.08, 0.03),
        (cx + 50 * scale, 0.9, 0.10),
    ]

    for sx, height_mult, tilt in stems:
        top_x = sx + math.sin(sway + tilt * 4) * 10 * scale
        top_y = base_y - stem_h * height_mult
        # stem (slight curve via 2 segments)
        mid_x = (sx + top_x) / 2 + math.sin(sway) * 4 * scale
        mid_y = (base_y + top_y) / 2
        pygame.draw.line(surface, STEM_GREEN, (sx, base_y), (mid_x, mid_y), max(2, int(3 * scale)))
        pygame.draw.line(surface, STEM_GREEN, (mid_x, mid_y), (top_x, top_y), max(2, int(3 * scale)))

        # a leaf
        leaf_surf = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, STEM_GREEN, (0, 0, 40, 20))
        leaf_surf = pygame.transform.rotate(leaf_surf, 30 + tilt * 60)
        surface.blit(leaf_surf, (mid_x - 20, mid_y - 5))

        # petals around the top point
        petal_r = 16 * scale
        for i in range(6):
            ang = (math.pi * 2 / 6) * i + sway * 0.5
            px = top_x + math.cos(ang) * petal_r
            py = top_y + math.sin(ang) * petal_r * 0.8 - petal_r * 0.3
            petal_surf = pygame.Surface((int(petal_r * 1.6), int(petal_r * 1.1)), pygame.SRCALPHA)
            pygame.draw.ellipse(petal_surf, (*PETAL_PINK, 235), petal_surf.get_rect())
            petal_surf = pygame.transform.rotate(petal_surf, math.degrees(ang))
            rect = petal_surf.get_rect(center=(px, py))
            surface.blit(petal_surf, rect.topleft)
        # flower center
        pygame.draw.circle(surface, GOLD, (int(top_x), int(top_y - petal_r * 0.3)), max(3, int(5 * scale)))

    # base foliage cluster (like the fluffy greenery in the reference photo)
    for i in range(10):
        fx = cx + random.uniform(-70, 70) * scale
        fy = base_y - random.uniform(0, 15) * scale
        pygame.draw.circle(surface, (200, 195, 180), (int(fx), int(fy)), int(random.uniform(6, 11) * scale))


# Helper: Smooth Text Renderer with soft glow
def render_text_center(text, font, color, y_pos, glow=False):
    if glow:
        glow_surf = font.render(text, True, color)
        glow_surf.set_alpha(70)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            rect = glow_surf.get_rect(center=(WIDTH // 2 + dx, y_pos + dy))
            screen.blit(glow_surf, rect)
    txt_surface = font.render(text, True, color)
    txt_rect = txt_surface.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(txt_surface, txt_rect)


# Act I: Cinematic Intro Typing (Handles Music & Lyrics Sync)
def play_intro():
    try:
        pygame.mixer.music.load("romantic_song.mp3")
        pygame.mixer.music.play()
    except Exception:
        print("Audio file not found, playing without audio.")

    lyrics = [
        "Na Samjho Ajnabee Sadiyon Se...",
        "Hum To Bas Tumhare Hain.",
        "In a universe full of stars...",
        "My eyes will always look for you.",
    ]

    for line in lyrics:
        current_text = ""
        for char in line:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            draw_gradient_bg(screen)
            current_text += char
            render_text_center(current_text, font_medium, TEXT_PINK, HEIGHT // 2, glow=True)
            pygame.display.flip()
            time.sleep(0.08)

        time.sleep(1.5)


# Act III: Vector Birthday Cake Draw Functions
def draw_cake(y_offset):
    pygame.draw.rect(screen, CAKE_COLOR, (WIDTH // 2 - 150, y_offset, 300, 120), border_radius=10)
    pygame.draw.rect(screen, ICING_COLOR, (WIDTH // 2 - 150, y_offset, 300, 30), border_radius=5)
    for i in range(6):
        pygame.draw.circle(screen, ICING_COLOR, (WIDTH // 2 - 125 + (i * 50), y_offset + 30), 15)
    pygame.draw.rect(screen, TEXT_WHITE, (WIDTH // 2 - 10, y_offset - 40, 20, 40))
    flame_size = random.choice([10, 12, 14])
    pygame.draw.circle(screen, CANDLE_COLOR, (WIDTH // 2, y_offset - 45), flame_size)


# Main App Loop
def main():
    play_intro()

    stars = [Star() for _ in range(80)]
    petals = [FloatingPetal() for _ in range(18)]
    fireflies = [Firefly(WIDTH // 2, HEIGHT // 2 + 60, 140) for _ in range(14)]

    photos = []
    photo_files = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
    for file in photo_files:
        try:
            img = pygame.image.load(file)
            img = pygame.transform.scale(img, (500, 380))
            photos.append(img)
        except Exception:
            pass

    start_ticks = pygame.time.get_ticks()
    running = True

    while running:
        draw_gradient_bg(screen)
        current_time_ms = pygame.time.get_ticks() - start_ticks
        sway = math.sin(current_time_ms / 800.0) * 0.15

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        for star in stars:
            star.draw(screen)

        for petal in petals:
            petal.move()
            petal.draw(screen)

        if current_time_ms < 6000:
            render_text_center("Happy Birthday, My Gorgeous! ✨", font_large, NEON_CYAN, 110, glow=True)
            draw_flower_bouquet(screen, WIDTH // 2, HEIGHT // 2 + 150, sway=sway, scale=1.1)
            for fly in fireflies:
                fly.draw(screen)
            draw_cake(HEIGHT // 2 - 20)
            render_text_center("You make my world infinitely brighter.", font_small, TEXT_WHITE, HEIGHT - 90)

        elif current_time_ms < 18000:
            render_text_center("Looking Back At Our Beautiful Moments...", font_medium, TEXT_PINK, 70, glow=True)

            if photos:
                photo_index = int((current_time_ms - 6000) // 4000) % len(photos)
                current_photo = photos[photo_index]
                photo_rect = current_photo.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                pygame.draw.rect(screen, ICING_COLOR, photo_rect.inflate(20, 20), border_radius=10)
                screen.blit(current_photo, photo_rect)
            else:
                draw_flower_bouquet(screen, WIDTH // 2, HEIGHT // 2 + 130, sway=sway, scale=1.3)
                for fly in fireflies:
                    fly.draw(screen)
                render_text_center("[ Insert Your Beautiful Photos Here ]", font_small, TEXT_WHITE, HEIGHT - 90)

        else:
            render_text_center("Forever & Always,", font_medium, TEXT_WHITE, HEIGHT // 2 - 110, glow=True)
            render_text_center("I LOVE YOU ❤️", font_large, TEXT_PINK, HEIGHT // 2 - 20, glow=True)
            draw_flower_bouquet(screen, WIDTH // 2, HEIGHT - 60, sway=sway, scale=0.9)
            render_text_center("Press Esc to close anytime.", font_small, (170, 160, 190), HEIGHT - 30)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()