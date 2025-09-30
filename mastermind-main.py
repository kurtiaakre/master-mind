import pygame
from pygame.locals import *

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    has_opengl = True
except ImportError:
    has_opengl = False

# Import the second module (to be created later)
# import logic  # For player/AI guesses and judgements

# Constants
BASE_W = 1920
BASE_H = 1080
MIN_W = 128
MIN_H = 64
IMAGE_PATH = './resources/MasterMind.jpg'
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_EMPTY_GRAY = (132, 132, 132)
COLOR_BROWN = (128, 64, 0)
COLOR_BAR = COLOR_DARK_GRAY

# Initialize Pygame
pygame.init()

# Get display info for initial window setup
info = pygame.display.Info()
if info.current_w <= BASE_W and info.current_h <= BASE_H:
    initial_size = (info.current_w, info.current_h)
    initial_flags = FULLSCREEN
else:
    initial_size = (BASE_W, BASE_H)
    initial_flags = RESIZABLE

screen = pygame.display.set_mode(initial_size, initial_flags)
pygame.display.set_caption("Master Mind")

# Load image
image_surf = pygame.image.load(IMAGE_PATH)

# Game variables
running = True
is_fullscreen = initial_flags == FULLSCREEN
scroll_x = 0
scroll_y = 0
dragging_horiz = False
dragging_vert = False
drag_start_mouse = (0, 0)
drag_start_scroll = (0, 0)
mode_3d = False  # Switch with key press (e.g., '3' for 3D, '2' for 2D)
game_mode = None  # To be chosen: 'Human/Human', 'AI/Human', 'Human/AI', 'AI/AI'
game_started = False
wait_for_key = True  # Wait for keypress after GUI display
current_text = "Press any key to continue...\nThen choose game mode by pressing 1-4."
guesses = []  # List of guesses (each a list of 4 colors, placeholder as strings)
judgements = []  # List of judgements (each a tuple (black, white))

# Placeholder colors for board
colors = {
    'R': (255, 0, 0),
    'G': (0, 255, 0),
    'B': (0, 0, 255),
    'Y': (255, 255, 0),
    'O': (255, 165, 0),
    'P': (128, 0, 128)
}

# For 3D textures
texture_image = None
texture_text = None

# Game loop
while running:
    w, h = screen.get_size()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if wait_for_key:
                wait_for_key = False
                current_text = "Choose game mode:\n1: Human/Human\n2: AI/Human\n3: Human/AI\n4: AI/AI"
            elif game_mode is None:
                if event.key == K_1:
                    game_mode = 'Human/Human'
                    current_text = f"Mode: {game_mode}\nGame starting..."
                    game_started = True
                elif event.key == K_2:
                    game_mode = 'AI/Human'
                    current_text = f"Mode: {game_mode}\nGame starting..."
                    game_started = True
                elif event.key == K_3:
                    game_mode = 'Human/AI'
                    current_text = f"Mode: {game_mode}\nGame starting..."
                    game_started = True
                elif event.key == K_4:
                    game_mode = 'AI/AI'
                    current_text = f"Mode: {game_mode}\nGame starting..."
                    game_started = True
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_f:
                is_fullscreen = not is_fullscreen
                flags = FULLSCREEN if is_fullscreen else RESIZABLE
                if mode_3d and has_opengl:
                    flags |= DOUBLEBUF | OPENGL
                new_size = (info.current_w, info.current_h) if is_fullscreen else (BASE_W, BASE_H)
                screen = pygame.display.set_mode(new_size, flags)
            elif event.key == K_2:
                if mode_3d:
                    mode_3d = False
                    flags = FULLSCREEN if is_fullscreen else RESIZABLE
                    screen = pygame.display.set_mode((w, h), flags)
            elif event.key == K_3:
                if not mode_3d and has_opengl:
                    mode_3d = True
                    flags = (FULLSCREEN if is_fullscreen else RESIZABLE) | DOUBLEBUF | OPENGL
                    screen = pygame.display.set_mode((w, h), flags)
            # Placeholder for interaction (e.g., enter guess or judgement)
            # If game_started, use keys or input for guesses/judgements
            # For now, skip detailed input; add later with second module
        elif event.type == VIDEORESIZE:
            new_size = event.size
            new_w = max(new_size[0], MIN_W)
            new_h = max(new_size[1], MIN_H)
            flags = RESIZABLE
            if mode_3d and has_opengl:
                flags |= DOUBLEBUF | OPENGL
            if new_w != new_size[0] or new_h != new_size[1]:
                screen = pygame.display.set_mode((new_w, new_h), flags)
            w, h = screen.get_size()
        elif event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            scroll_bar_width = 20
            # Check vertical scroll bar
            if max_scroll_y > 0 and w - scroll_bar_width <= mouse_x <= w:
                bar_h = h * (h / v_h)
                bar_y = (scroll_y / max_scroll_y) * (h - bar_h)
                if bar_y <= mouse_y <= bar_y + bar_h:
                    dragging_vert = True
                    drag_start_mouse = (mouse_x, mouse_y)
                    drag_start_scroll = (scroll_x, scroll_y)
            # Check horizontal scroll bar
            if max_scroll_x > 0 and h - scroll_bar_width <= mouse_y <= h:
                bar_w = w * (w / v_w)
                bar_x = (scroll_x / max_scroll_x) * (w - bar_w)
                if bar_x <= mouse_x <= bar_x + bar_w:
                    dragging_horiz = True
                    drag_start_mouse = (mouse_x, mouse_y)
                    drag_start_scroll = (scroll_x, scroll_y)
        elif event.type == MOUSEBUTTONUP:
            dragging_vert = False
            dragging_horiz = False
        elif event.type == MOUSEMOTION:
            if dragging_vert:
                _, mouse_y = event.pos
                delta_y = mouse_y - drag_start_mouse[1]
                scroll_factor = max_scroll_y / (h - bar_h) if (h - bar_h) > 0 else 0
                scroll_y = drag_start_scroll[1] + delta_y * scroll_factor
                scroll_y = max(0, min(scroll_y, max_scroll_y))
            if dragging_horiz:
                mouse_x, _ = event.pos
                delta_x = mouse_x - drag_start_mouse[0]
                scroll_factor = max_scroll_x / (w - bar_w) if (w - bar_w) > 0 else 0
                scroll_x = drag_start_scroll[0] + delta_x * scroll_factor
                scroll_x = max(0, min(scroll_x, max_scroll_x))
        elif event.type == MOUSEWHEEL:
            if max_scroll_y > 0:
                scroll_y = max(0, min(scroll_y - event.y * 30, max_scroll_y))

    if wait_for_key:
        # Display GUI and wait
        pass
    else:
        # Normal game flow
        # Placeholder for game logic: update guesses, judgements, check win/loss
        # If game_started, call logic functions based on game_mode
        # For example:
        # if 'Human' in guesser:
        #     guess = logic.player_make_guess()
        # else:
        #     guess = logic.ai_make_guess(guesses, judgements)
        # Then update GUI with results
        # For now, placeholder: add a dummy guess after mode select
        if game_started and len(guesses) < 1:
            guesses.append(['R', 'G', 'B', 'Y'])
            judgements.append((2, 1))  # Dummy judgement (black, white)

    # Calculate scaling and virtual size
    fit_scale = min(w / BASE_W, h / BASE_H)
    scale = max(min(fit_scale, 2), 0.5)
    v_w = BASE_W * scale
    v_h = BASE_H * scale
    need_scroll = scale > fit_scale  # Only when clamped to min and window too small
    max_scroll_x = max(0, v_w - w)
    max_scroll_y = max(0, v_h - h)
    scroll_x = max(0, min(scroll_x, max_scroll_x))
    scroll_y = max(0, min(scroll_y, max_scroll_y))

    if mode_3d and has_opengl:
        # 3D mode drawing - simplify scaling for 3D, use full window
        glViewport(0, 0, w, h)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)  # For simple colors
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -20)  # Adjust camera

        # Draw image as textured quad
        if texture_image is None:
            texture_image = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_image)
            image_data = pygame.image.tostring(image_surf, "RGB", 1)
            img_w, img_h = image_surf.get_size()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_w, img_h, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_image)
        glPushMatrix()
        glTranslatef(-8, 5, 0)  # Upper left position
        glScale(4, 4, 1)  # Scale to fit
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-1, -1, 0)
        glTexCoord2f(1, 0); glVertex3f(1, -1, 0)
        glTexCoord2f(1, 1); glVertex3f(1, 1, 0)
        glTexCoord2f(0, 1); glVertex3f(-1, 1, 0)
        glEnd()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Draw text area as textured quad (regenerate since text may change)
        font_size = int(24 * fit_scale)
        font = pygame.font.SysFont(None, font_size)
        lines = current_text.split('\n')
        line_height = font.get_linesize()
        text_height = len(lines) * line_height + 20
        text_width = max([font.render(line, True, COLOR_WHITE).get_width() for line in lines]) + 20
        text_surface = pygame.Surface((text_width, text_height))
        text_surface.fill(COLOR_GRAY)
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, COLOR_WHITE)
            text_surface.blit(text_surf, (10, 10 + i * line_height))

        if texture_text is None:
            texture_text = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_text)
        text_data = pygame.image.tostring(text_surface, "RGB", 1)
        t_w, t_h = text_surface.get_size()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, t_w, t_h, 0, GL_RGB, GL_UNSIGNED_BYTE, text_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_text)
        glPushMatrix()
        glTranslatef(-8, -5, 0)  # Lower left position
        glScale(4, 4, 1)  # Scale to fit
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-1, -1, 0)
        glTexCoord2f(1, 0); glVertex3f(1, -1, 0)
        glTexCoord2f(1, 1); glVertex3f(1, 1, 0)
        glTexCoord2f(0, 1); glVertex3f(-1, 1, 0)
        glEnd()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Draw board background as quad
        glPushMatrix()
        glTranslatef(0, 0, -0.1)
        glColor3f(128/255.0, 64/255.0, 0)
        glBegin(GL_QUADS)
        glVertex3f(-5, -5, 0)
        glVertex3f(10, -5, 0)
        glVertex3f(10, 5, 0)
        glVertex3f(-5, 5, 0)
        glEnd()
        glPopMatrix()

        # Draw solution pegs as spheres
        for peg_row in range(4):
            glPushMatrix()
            glTranslatef(-10, -peg_row * 1.2 + 2, 0)
            glColor3f(64/255.0, 64/255.0, 64/255.0)
            quad = gluNewQuadric()
            gluSphere(quad, 0.8, 32, 32)
            glPopMatrix()

        # Draw vertical bar as quad
        glPushMatrix()
        glTranslatef(-9, 0, 0)
        glColor3f(64/255.0, 64/255.0, 64/255.0)
        pegs_height = 3.6
        margin = 0.1 * pegs_height
        glBegin(GL_QUADS)
        glVertex3f(-0.2, -pegs_height / 2 - margin, 0)
        glVertex3f(0.2, -pegs_height / 2 - margin, 0)
        glVertex3f(0.2, pegs_height / 2 + margin, 0)
        glVertex3f(-0.2, pegs_height / 2 + margin, 0)
        glEnd()
        glPopMatrix()

        # Draw board pegs as spheres
        for col in range(12):
            for peg_row in range(4):
                glPushMatrix()
                glTranslatef(col * 1.2 - 8, -peg_row * 1.2 + 2, 0)
                if col < len(guesses):
                    color = colors.get(guesses[col][peg_row], COLOR_WHITE)
                    glColor3f(color[0]/255.0, color[1]/255.0, color[2]/255.0)
                else:
                    glColor3f(132/255.0, 132/255.0, 132/255.0)
                quad = gluNewQuadric()
                gluSphere(quad, 0.8, 32, 32)
                glPopMatrix()

        # Draw judgement pegs as smaller spheres, always 4, below
        for col in range(12):
            if col < len(judgements):
                black, white = judgements[col]
            else:
                black, white = 0, 0
            base_x = col * 1.2 - 8 
            base_y = -1.6 - 1.2  # Increased distance
            for p in range(4):
                j_row = p // 2
                j_col = p % 2
                glPushMatrix()
                glTranslatef(base_x + j_col * 0.8, base_y - j_row * 0.8, 0)  # Removed -0.4 offset for alignment adjustment
                if p < black:
                    glColor3f(0, 0, 0)
                elif p < black + white:
                    glColor3f(1, 1, 1)
                else:
                    glColor3f(132/255.0, 132/255.0, 132/255.0)
                quad = gluNewQuadric()
                gluSphere(quad, 0.4, 32, 32)
                glPopMatrix()

    else:
        # 2D mode drawing
        if not need_scroll:
            offset_x = (w - v_w) / 2
            offset_y = (h - v_h) / 2
            draw_surface = screen
            draw_offset_x = offset_x
            draw_offset_y = offset_y
            clip_rect = None
        else:
            virtual = pygame.Surface((int(v_w), int(v_h)))
            draw_surface = virtual
            draw_offset_x = 0
            draw_offset_y = 0
            clip_rect = (scroll_x, scroll_y, w, h)

        # Clear draw surface
        draw_surface.fill(COLOR_BLACK)

        # Calculate layout on draw_surface (scaled)
        left_margin = 0.05 * v_w
        gap = 0.05 * v_w
        right_margin = 0.05 * v_w
        top_margin = 0.1 * v_h
        bottom_margin = 0.1 * v_h
        content_h = v_h - top_margin - bottom_margin
        available_w = v_w - left_margin - gap - right_margin
        left_width = available_w / 4
        board_width = available_w * 3 / 4
        left_height = content_h / 2

        # Draw picture (upper left)
        picture_x = left_margin + draw_offset_x
        picture_y = top_margin + draw_offset_y
        scaled_image = pygame.transform.smoothscale(image_surf, (int(left_width), int(left_height)))
        draw_surface.blit(scaled_image, (picture_x, picture_y))

        # Draw text area (lower left)
        text_x = left_margin + draw_offset_x
        text_y = top_margin + left_height + draw_offset_y
        pygame.draw.rect(draw_surface, COLOR_GRAY, (text_x, text_y, left_width, left_height))
        font_size = int(24 * scale)
        font = pygame.font.SysFont(None, font_size)
        lines = current_text.split('\n')
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, COLOR_WHITE)
            draw_surface.blit(text_surf, (text_x + 10, text_y + 10 + i * line_height))

        # Draw board (right)
        board_x = left_margin + left_width + gap + draw_offset_x
        board_y = top_margin + draw_offset_y
        # Draw board background and frame
        pygame.draw.rect(draw_surface, COLOR_BROWN, (board_x, board_y, board_width, content_h))
        pygame.draw.rect(draw_surface, COLOR_BLACK, (board_x, board_y, board_width, content_h), 2)

        # Placeholder for board: grid of 12 columns horizontal + solution column + bar
        left_padding = 0.05 * board_width
        right_padding = left_padding
        content_width = board_width - left_padding - right_padding
        effective_columns = 14  # 1 sol + 1 sep + 12 guesses
        column_width = content_width / effective_columns
        solution_width = column_width
        sep_width = column_width
        bar_width = 0.2 * column_width
        gap_left = (sep_width - bar_width) / 2
        gap_right = gap_left
        peg_size = min(column_width / 2.5, content_h / 5) * 0.8
        judgement_size = peg_size / 2
        border_width = max(1, int(peg_size / 20))
        pegs_span = 3 * peg_size * 1.2 + peg_size
        j_span = 2.2 * judgement_size
        space = 0.4 * peg_size
        total_height = pegs_span + space + j_span
        peg_start_y = board_y + (content_h - total_height) / 2
        judgement_start_y = peg_start_y + pegs_span + space

        # Draw solution column
        solution_x = board_x + left_padding
        for peg_row in range(4):
            peg_y = peg_start_y + peg_row * peg_size * 1.2
            peg_center = (int(solution_x + peg_size / 2), int(peg_y + peg_size / 2))
            color = COLOR_DARK_GRAY
            pygame.draw.circle(draw_surface, color, peg_center, int(peg_size / 2))
            pygame.draw.circle(draw_surface, COLOR_BLACK, peg_center, int(peg_size / 2), border_width)

        # Draw vertical bar
        bar_x = solution_x + solution_width + gap_left
        pegs_height = 4 * peg_size * 1.2
        bar_margin = 0.1 * pegs_span
        bar_y = peg_start_y - bar_margin
        bar_height = pegs_span + 2 * bar_margin
        pygame.draw.rect(draw_surface, COLOR_BAR, (bar_x, bar_y, bar_width, bar_height))

        # Draw guessing columns
        first_guess_x = bar_x + bar_width + gap_right
        for col in range(12):
            guess_x = first_guess_x + col * column_width
            # Draw guess pegs
            for peg_row in range(4):
                peg_y = peg_start_y + peg_row * peg_size * 1.2
                peg_center = (int(guess_x + peg_size / 2), int(peg_y + peg_size / 2))
                if col < len(guesses):
                    color = colors.get(guesses[col][peg_row], COLOR_WHITE)
                else:
                    color = COLOR_EMPTY_GRAY
                pygame.draw.circle(draw_surface, color, peg_center, int(peg_size / 2))
                pygame.draw.circle(draw_surface, COLOR_BLACK, peg_center, int(peg_size / 2), border_width)
            # Draw judgement pegs (2x2 grid, always 4, below)
            judgement_x = guess_x
            if col < len(judgements):
                black, white = judgements[col]
            else:
                black, white = 0, 0
            for p in range(4):
                j_row = p // 2
                j_col = p % 2
                j_y = judgement_start_y + j_row * judgement_size * 1.2
                j_center = (int(judgement_x + j_col * judgement_size * 1.2 + judgement_size / 2), int(j_y + judgement_size / 2))
                if p < black:
                    color = COLOR_BLACK
                elif p < black + white:
                    color = COLOR_WHITE
                else:
                    color = COLOR_EMPTY_GRAY
                pygame.draw.circle(draw_surface, color, j_center, int(judgement_size / 2))
                pygame.draw.circle(draw_surface, COLOR_BLACK, j_center, int(judgement_size / 2), border_width)

        if need_scroll:
            screen.blit(virtual, (0, 0), clip_rect)
            # Draw scroll bars
            scroll_bar_width = 20
            # Vertical
            if max_scroll_y > 0:
                bar_h = h * (h / v_h)
                bar_y = (scroll_y / max_scroll_y) * (h - bar_h)
                pygame.draw.rect(screen, COLOR_GRAY, (w - scroll_bar_width, 0, scroll_bar_width, h))
                pygame.draw.rect(screen, COLOR_LIGHT_GRAY, (w - scroll_bar_width, bar_y, scroll_bar_width, bar_h))
            # Horizontal
            if max_scroll_x > 0:
                bar_w = w * (w / v_w)
                bar_x = (scroll_x / max_scroll_x) * (w - bar_w)
                pygame.draw.rect(screen, COLOR_GRAY, (0, h - scroll_bar_width, w, scroll_bar_width))
                pygame.draw.rect(screen, COLOR_LIGHT_GRAY, (bar_x, h - scroll_bar_width, bar_w, scroll_bar_width))

    pygame.display.flip()

# Exit
pygame.quit()

# Placeholder for win/loss validation and concluding (add in loop when game logic implemented)
# E.g., if len(guesses) == 12 without 4 black: loss
# If last judgement has 4 black: win