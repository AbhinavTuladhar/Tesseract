import pygame
import numpy as np
from math import sin, cos, pi

WIDTH, HEIGHT = 1366, 768
FPS = 60

# -----Defining colours-----
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# --------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH ,HEIGHT))
pygame.display.set_caption("Tesseract")
clock = pygame.time.Clock()

# ----- Points of the tesseract ----- #
points = []
points.append(np.array([-1, -1, 1, 1]))
points.append(np.array([1, -1, 1, 1]))
points.append(np.array([1,  1, 1, 1]))
points.append(np.array([-1, 1, 1, 1]))
points.append(np.array([-1, -1, -1, 1]))
points.append(np.array([1, -1, -1, 1]))
points.append(np.array([1, 1, -1, 1]))
points.append(np.array([-1, 1, -1, 1]))

points.append(np.array([-1, -1, 1, -1]))
points.append(np.array([1, -1, 1, -1]))
points.append(np.array([1,  1, 1, -1]))
points.append(np.array([-1, 1, 1, -1]))
points.append(np.array([-1, -1, -1, -1]))
points.append(np.array([1, -1, -1, -1]))
points.append(np.array([1, 1, -1, -1]))
points.append(np.array([-1, 1, -1, -1]))
# ------------------------------------#

projected_points = [x for x in range(len(points))]      # List to store projected points
flags_3D = [0 for _ in range(3)]                        # Flags to check whether particular
flags_4D = [0 for _ in range(6)]                        # rotation is active or not

angle = 0                                               # initial angle
scale = 600                                             # For scaling purposes
cube_position = [WIDTH // 2, HEIGHT // 2]               # For translation
speed = 0.01                                            # For change in angle
z_change = 0.025                                        # Used when zooming
z_offset = 0
font = pygame.font.SysFont("helvetica", 20, bold = True)

# Dictionaries for output purposes
line_rotation_dict = {
    0 : 'x', 1 : 'y', 2 : 'z'
}
plane_rotation_dict = {
    0 : 'xy', 1 : 'xz',
    2 : 'xw', 3 : 'yz',
    4 : 'yw', 5 : 'zw',
}

def connect_point(i, j, k, offset):
    a = k[i + offset]
    b = k[j + offset]
    pygame.draw.line(screen, WHITE, (a[0], a[1]), (b[0], b[1]), 3)

# For output purposes
numbers = [x for x in range(1, 7)]
numbers = list(map(str, numbers))

running = True
while running:
    screen.fill(BLACK)
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_UP:
                z_offset += z_change
            if event.key == pygame.K_DOWN:
                z_offset -= z_change

            # For 4D rotations
            key_name = pygame.key.name(event.key)
            if key_name in numbers:
                num = int(key_name) - 1
                flags_4D[num] = (flags_4D[num] + 1) % 2

            # For 3D rotations
            if event.key == pygame.K_x:
                flags_3D[0] = (flags_3D[0] + 1) % 2
            if event.key == pygame.K_y:
                flags_3D[1] = (flags_3D[1] + 1) % 2
            if event.key == pygame.K_z:
                flags_3D[2] = (flags_3D[2] + 1) % 2

    # List to store all 3D rotation matrices
    rotate_matrices_3D = []
    rotation_x = np.array([
        [1, 0, 0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle), cos(angle)]
    ])
    rotation_y = np.array([
        [cos(angle), 0, -sin(angle)],
        [0, 1, 0],
        [sin(angle), 0, cos(angle)]
    ])
    rotation_z = np.array([
        [cos(angle), -sin(angle), 0],
        [sin(angle), cos(angle), 0],
        [0, 0, 1]
    ])
    rotate_matrices_3D.extend([rotation_x, rotation_y, rotation_z])

    #4d matrix rotations
    rotate_matrices_4D = []
    rotation_xy= [[cos(angle), -sin(angle), 0, 0],
                  [sin(angle), cos(angle), 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]]
    rotation_xz = [[cos(angle), 0, -sin(angle), 0],
                     [0, 1, 0, 0],
                     [sin(angle), 0, cos(angle), 0],
                     [0, 0, 0, 1]]
    rotation_xw = [[cos(angle), 0, 0, -sin(angle)],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [sin(angle), 0, 0, cos(angle)]]
    rotation_yz = [[1, 0, 0, 0],
                     [0, cos(angle), -sin(angle), 0],
                     [0, sin(angle), cos(angle), 0],
                     [0, 0, 0, 1]]
    rotation_yw = [[1, 0, 0, 0],
                     [0, cos(angle), 0, -sin(angle)],
                     [0, 0, 1, 0],
                     [0, sin(angle), 0, cos(angle)]]
    rotation_zw = [[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, cos(angle), -sin(angle)],
                     [0, 0, sin(angle), cos(angle)]]
    rotate_matrices_4D.extend([
        rotation_xy, rotation_xz,
        rotation_xw, rotation_yz,
        rotation_yw, rotation_zw
    ])

    index = 0
    for point in points:
        # First, perform necessary 4D rotation
        # Then project it onto 3D space.
        rotated_3d = np.dot(np.identity(4), point.reshape(4, 1))
        for flag, matrix in zip(flags_4D, rotate_matrices_4D):
            # If flag is set, multiply with corresponding rotation matrix
            if flag:
                rotated_3d = np.dot(matrix, rotated_3d)

        distance = 3.2
        w = 1 / (distance - rotated_3d[3][0]) + z_offset
        projection_4D = np.array([
            [w, 0, 0, 0],
            [0, w, 0, 0],
            [0, 0, w, 0]
        ])

        # Obtain projected 3D points
        projected_3D = np.dot(projection_4D, rotated_3d)

        # Now, perform necessary 3D rotation and project it onto 2D space
        rotated_2D = np.dot(np.identity(3), projected_3D)
        for flag, matrix in zip(flags_3D, rotate_matrices_3D):
            if flag:
                rotated_2D = np.dot(matrix, rotated_2D)
        
        z = 1 / (distance - (rotated_3d[3][0] + rotated_2D[2][0])) + z_offset
        projection_3D = np.array([
            [z, 0, 0],
            [0, z, 0],
        ])
        projected_2D = np.dot(projection_3D, rotated_2D)

        x = int(projected_2D[0][0] * scale) + cube_position[0]
        y = int(projected_2D[1][0] * scale) + cube_position[1]

        projected_points[index] = [x, y]
        index += 1

        # Draw a circle with radius 5 at the projected point
        pygame.draw.circle(screen, WHITE, (x, y), 5)

    # Copied
    for m in range(4):
        connect_point(m, (m + 1) % 4, projected_points, 8)
        connect_point(m + 4, (m + 1) %4 + 4, projected_points, 8)
        connect_point(m, m + 4, projected_points, 8)

    for m in range(4):
        connect_point(m, (m + 1) % 4, projected_points, 0)
        connect_point(m + 4, (m + 1) % 4 + 4, projected_points, 0)
        connect_point(m, m + 4, projected_points, 0)

    for m in range(8):
        connect_point(m,  m + 8, projected_points, 0)

    # Reset angle to zero if all flags are reset
    if all(flag == 0 for flag in flags_4D) and all(flag == 0 for flag in flags_3D):
        angle = 0
    else:
        angle += speed
    
    # For text purposes
    expression1 = "Active 4D rotation matrices: "
    for count, flag in enumerate(flags_4D):
        if flag:
            expression1 += plane_rotation_dict[count] + " "
    label1 = font.render(expression1, 2, WHITE)
    screen.blit(label1, (0, 0))

    expression2 = "Active 3D rotation matrices: "
    for count, flag in enumerate(flags_3D):
        if flag:
            expression2 += line_rotation_dict[count] + " "
    label2 = font.render(expression2, 2, WHITE)
    screen.blit(label2, (0, 20))

    pygame.display.update()
pygame.quit()