import pygame
import random
from math import sin
 
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FOV = 250
FPS = 60
 
frames = 0
camera_x, camera_y, camera_z = 0, 5, 0
 
polygons = {}
 
background_color = (135, 206, 235)
 
x_velocity = 0
cube_size = 20
cubes = []
 
start_speed = 4
current_speed = start_speed
scores_to_speed_up = 3000
speed_up_amount = 1
shown_speed_increase_frames = 0
showing_speed_up = False
next_speed_up = scores_to_speed_up
speed_up_time_factor = 1
 
def add_cube(cx, cy, cz, size, polygons):
 
    hs = size / 2
 
    vertices = [
        (cx - hs, cy - hs, cz - hs),
        (cx + hs, cy - hs, cz - hs),
        (cx + hs, cy + hs, cz - hs),
        (cx - hs, cy + hs, cz - hs),
        (cx - hs, cy - hs, cz + hs),
        (cx + hs, cy - hs, cz + hs),
        (cx + hs, cy + hs, cz + hs),
        (cx - hs, cy + hs, cz + hs)
    ]
 
    cubes.append((cx, cy, cz))
 
    # skipping the bottom face
    faces = [
        (vertices[0], vertices[1], vertices[2], vertices[3]),  # Front
        (vertices[4], vertices[5], vertices[6], vertices[7]),  # Back
        (vertices[3], vertices[2], vertices[6], vertices[7]),  # Top
        (vertices[0], vertices[4], vertices[7], vertices[3]),  # Left
        (vertices[1], vertices[5], vertices[6], vertices[2])   # Right
    ]
 
    color = (random.randint(220, 255), random.randint(0, 255), random.randint(0, 50))
    for face in faces:
        polygons[face] = color
 
 
def clipline(p1, p2, clip_distance):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
 
    if z1 >= clip_distance and z2 >= clip_distance:
        return p1, p2
 
    if z1 < clip_distance and z2 < clip_distance:
        return None
 
    if z1 != z2:
        t = (clip_distance - z1) / (z2 - z1)
    else:
        t = 0
 
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    z = clip_distance
 
    if z1 < clip_distance:
        return (x, y, z), p2
    else:
        return p1, (x, y, z)
 
 
def clippolygon(vertices, clip_distance):
    clipped_vertices = []
 
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
 
        # Clip the edge
        clipped_edge = clipline(p1, p2, clip_distance)
 
        if clipped_edge:
            if not clipped_vertices or clipped_vertices[-1] != clipped_edge[0]:
                clipped_vertices.append(clipped_edge[0])
 
            clipped_vertices.append(clipped_edge[1])
 
    return tuple(clipped_vertices)
 
 
def projected(x, y, z):
    if z <= 0:
        return None
    return x / z * FOV + SCREEN_WIDTH / 2, y / z * FOV + SCREEN_HEIGHT / 2
 
 
offscreen_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
 
running = True
 
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("OVCC 3D Graphics - Cubefield Example - FPS: loading...")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Times New Roman', 30)
largefont = pygame.font.SysFont('Times New Roman', 60)
 
lost = False
lost_score = None
 
while running:
    offscreen_surface.fill(background_color) 
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
 
    if not lost:
 
        score = -camera_z*2
 
        frames += 1
        camera_z -= current_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x_velocity += 0.6
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x_velocity -= 0.6
        if not ((keys[pygame.K_a] or keys[pygame.K_LEFT]) or (keys[pygame.K_d] or keys[pygame.K_RIGHT])):
            x_velocity /= 1.1
            if abs(x_velocity) < 0.5:
                x_velocity = 0
 
        camera_x += x_velocity
 
        x_velocity = max(-10, min(10, x_velocity))
        camera_x = max(-1000000, min(1000000, camera_x))
 
        sorted_polygons = sorted(
            polygons.items(),
            key=lambda item: sum(vertex[2] for vertex in item[0]) / len(item[0]),
            reverse=True
        )
 
        pygame.draw.rect(offscreen_surface, (150, 150, 150), pygame.Rect(0, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT/2))
 
        for polygon, color in sorted_polygons:
            translated_polygon = [(x + camera_x, y + camera_y, z + camera_z) for x, y, z in polygon]
            zs = [coord[2] for coord in translated_polygon]
            if all([not z > camera_z for z in zs]):
                del polygons[polygon]
 
            clipped = clippolygon(translated_polygon, clip_distance=0.1)
            if clipped:
                projections = [projected(*coord) for coord in clipped]
                pygame.draw.polygon(offscreen_surface, color, projections)
 
 
        pygame.draw.polygon(offscreen_surface,
                            (0, 0, 0),
                            [(SCREEN_WIDTH/2-x_velocity*5, SCREEN_HEIGHT*4/5-sin(frames/10)*5),
                            (SCREEN_WIDTH/2-50-x_velocity*5, SCREEN_HEIGHT*4/5+50-sin(frames/10)*5),
                            (SCREEN_WIDTH/2+50-x_velocity*5, SCREEN_HEIGHT*4/5+50-sin(frames/10)*5)])
 
        rotated_surface = pygame.transform.rotate(offscreen_surface, -x_velocity)
        rotated_rect = rotated_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(rotated_surface, rotated_rect)
 
        if frames % 10 == 0:
            add_cube(-camera_x + random.randint(-700, 700), 2, -camera_z + random.randint(200, 800), 40, polygons)
        
        for cube in cubes:
            cx, cy, cz = cube
            if abs(cx + camera_x) < cube_size:
                if abs(cz + camera_z - 10) < cube_size:
                    lost = True
                    lost_score = score
 
            if -camera_z>cz:
                cubes.remove(cube)
 
        
        if score > next_speed_up:
            speed_up_time_factor += 1.2
            next_speed_up += scores_to_speed_up*speed_up_time_factor
            current_speed += speed_up_amount
            shown_speed_increase_frames = 0
            showing_speed_up = True
        
        if showing_speed_up:
            if shown_speed_increase_frames < 2*FPS:
                text_surface = font.render(f"SPEED UP", True, (0, 0, 0))
                text_rect = text_surface.get_rect()
                text_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                screen.blit(text_surface, text_rect)
                shown_speed_increase_frames += 1
            else:
                shown_speed_increase_frames = 0
                showing_speed_up = False
        
 
        text_surface = font.render("Prismmeadow - not associated with cubefield :)", True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)
        screen.blit(text_surface, text_rect)
 
        text_surface = font.render(f"Score: {score}", True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 50)
        screen.blit(text_surface, text_rect)
        
        text_surface = font.render(f"Position: ({-round(camera_x)}, {round(camera_y)}, {-round(camera_z)})", True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 90)
        screen.blit(text_surface, text_rect)
 
        if lost:
            text_surface = largefont.render(f"Game Over! Score: {lost_score}", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(text_surface, text_rect)
 
        
 
    pygame.display.flip()
    clock.tick(FPS)
    pygame.display.set_caption(f"OVCC 3D Graphics - Cubefield - FPS: {clock.get_fps() // 1}")
