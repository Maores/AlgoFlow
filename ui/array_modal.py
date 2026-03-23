# ui/array_modal.py - Custom array input modal for AlgoFlow
import pygame
import random
from config import Colors, FONT_FAMILY, BOX_MODE_THRESHOLD


class ArrayModal:
    """Centered overlay modal for entering custom arrays or selecting presets."""

    def __init__(self, screen_width, screen_height):
        self.visible = False
        self.current_size = 10
        self.original_text = ""
        self.input_text = ""
        self.error_msg = ""
        self.is_valid = False
        self.parsed_array = []
        self.select_all = False

        # Cursor blink state
        self.cursor_visible = True
        self.cursor_timer = 0

        # Fonts
        self.font_title = pygame.font.SysFont(FONT_FAMILY, 30, bold=True)
        self.font_input = pygame.font.SysFont(FONT_FAMILY, 22)
        self.font_label = pygame.font.SysFont(FONT_FAMILY, 19)
        self.font_btn = pygame.font.SysFont(FONT_FAMILY, 20)

        # Overlay surface (cached, rebuilt on resize)
        self._overlay = None

        # Layout — computed in _rebuild_layout
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.card_w = 520
        self.card_h = 400
        self._rebuild_layout()

    # ------------------------------------------------------------------
    # Preset generators
    # ------------------------------------------------------------------

    def _gen_random(self, size):
        return [random.randint(1, 50) for _ in range(size)]

    def _gen_sorted(self, size):
        if size <= 50:
            return [round(1 + (49 * i) / max(1, size - 1)) for i in range(size)]
        return list(range(1, size + 1))

    def _gen_reversed(self, size):
        return list(reversed(self._gen_sorted(size)))

    def _gen_nearly_sorted(self, size):
        arr = self._gen_sorted(size)
        swaps = min(3, size // 3)
        for _ in range(swaps):
            idx = random.randint(0, len(arr) - 2)
            arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
        return arr

    def _gen_few_unique(self, size):
        distinct = random.sample(range(1, 50), min(4, 49))
        return [random.choice(distinct) for _ in range(size)]

    PRESETS = [
        ("Random", "_gen_random"),
        ("Sorted", "_gen_sorted"),
        ("Reversed", "_gen_reversed"),
        ("Nearly", "_gen_nearly_sorted"),
        ("Few Unique", "_gen_few_unique"),
    ]

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _rebuild_layout(self):
        cx = (self.screen_w - self.card_w) // 2
        cy = (self.screen_h - self.card_h) // 2
        self.card_rect = pygame.Rect(cx, cy, self.card_w, self.card_h)

        pad = 28
        inner_w = self.card_w - pad * 2

        # Title
        self.title_pos = (cx + self.card_w // 2, cy + 28)

        # Input field
        input_y = cy + 68
        input_h = 44
        self.input_rect = pygame.Rect(cx + pad, input_y, inner_w, input_h)

        # Validation text
        self.valid_pos = (cx + pad, input_y + input_h + 8)

        # Size selector row:  [-]  Size: 20  [+]
        size_row_y = input_y + input_h + 38
        sq = 28  # square button size
        size_label_w = self.font_btn.size("Size: 30")[0]  # max width estimate
        total_size_w = sq + 10 + size_label_w + 10 + sq
        size_x = cx + (self.card_w - total_size_w) // 2
        self.minus_rect = pygame.Rect(size_x, size_row_y, sq, sq)
        self.size_label_pos = (size_x + sq + 10 + size_label_w // 2, size_row_y + sq // 2)
        self.plus_rect = pygame.Rect(size_x + sq + 10 + size_label_w + 10, size_row_y, sq, sq)

        # Preset row
        preset_y = size_row_y + sq + 14
        preset_h = 36
        preset_gap = 6
        self.preset_rects = []
        total_w = sum(self.font_btn.size(p[0])[0] + 24 for p in self.PRESETS) + preset_gap * (len(self.PRESETS) - 1)
        px = cx + (self.card_w - total_w) // 2
        for label, _ in self.PRESETS:
            pw = self.font_btn.size(label)[0] + 24
            self.preset_rects.append(pygame.Rect(px, preset_y, pw, preset_h))
            px += pw + preset_gap

        # Bottom row: [Reset] [Cancel] [Apply]
        btn_w = 100
        btn_h = 42
        btn_y = cy + self.card_h - pad - btn_h
        btn_gap = 12
        total_btn_w = btn_w * 3 + btn_gap * 2
        btn_x = cx + self.card_w - pad - total_btn_w
        self.reset_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.cancel_rect = pygame.Rect(btn_x + btn_w + btn_gap, btn_y, btn_w, btn_h)
        self.apply_rect = pygame.Rect(btn_x + (btn_w + btn_gap) * 2, btn_y, btn_w, btn_h)

        # Rebuild overlay
        self._overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 140))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def open(self, current_size=10, current_array=None):
        self.visible = True
        self.current_size = current_size
        if current_array:
            self.original_text = ", ".join(map(str, current_array))
        else:
            self.original_text = ""
        self.input_text = self.original_text
        self.error_msg = ""
        self.is_valid = False
        self.parsed_array = []
        self.select_all = False
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()
        self._validate()

    def close(self):
        self.visible = False

    def is_open(self):
        return self.visible

    def resize(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self._rebuild_layout()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self):
        text = self.input_text.strip()
        if not text:
            self.error_msg = ""
            self.is_valid = False
            self.parsed_array = []
            return

        parts = text.split(",")
        values = []
        for part in parts:
            s = part.strip()
            if not s:
                continue
            try:
                v = int(s)
            except ValueError:
                self.error_msg = f"'{s}' is not a valid integer"
                self.is_valid = False
                self.parsed_array = []
                return
            if v < 1 or v > 99:
                self.error_msg = f"Values must be 1–99 (got {v})"
                self.is_valid = False
                self.parsed_array = []
                return
            values.append(v)

        if len(values) < 2:
            self.error_msg = "Need at least 2 values"
            self.is_valid = False
            self.parsed_array = []
            return
        if len(values) > 30:
            self.error_msg = f"Max 30 values (got {len(values)})"
            self.is_valid = False
            self.parsed_array = []
            return

        self.parsed_array = values
        self.is_valid = True
        self.error_msg = f"{len(values)} values \u2014 ready"

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event):
        """Returns {'action': 'apply', 'array': [...]} or {'action': 'cancel'} or None."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            ctrl = mods & (pygame.KMOD_CTRL | pygame.KMOD_META)

            if event.key == pygame.K_ESCAPE:
                return {"action": "cancel"}

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.is_valid:
                    return {"action": "apply", "array": list(self.parsed_array)}
                return None

            if ctrl and event.key == pygame.K_a:
                self.select_all = True
                return None

            if ctrl and event.key == pygame.K_v:
                self._handle_paste()
                return None

            if event.key == pygame.K_BACKSPACE:
                if self.select_all or (ctrl and self.input_text):
                    self.input_text = ""
                    self.select_all = False
                elif self.input_text:
                    self.input_text = self.input_text[:-1]
                self._validate()
                return None

            if event.key == pygame.K_DELETE:
                if self.select_all:
                    self.input_text = ""
                    self.select_all = False
                    self._validate()
                return None

            # Printable character
            ch = event.unicode
            if ch and ch in "0123456789, ":
                if self.select_all:
                    self.input_text = ""
                    self.select_all = False
                if len(self.input_text) < 200:
                    self.input_text += ch
                self._validate()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Cancel button
            if self.cancel_rect.collidepoint(pos):
                return {"action": "cancel"}

            # Apply button
            if self.apply_rect.collidepoint(pos):
                if self.is_valid:
                    return {"action": "apply", "array": list(self.parsed_array)}
                return None

            # Reset button — restore original array text
            if self.reset_rect.collidepoint(pos):
                self.input_text = self.original_text
                self.select_all = False
                self._validate()
                return None

            # Size selector buttons
            if self.minus_rect.collidepoint(pos):
                self.current_size = max(2, self.current_size - 5)
                return None
            if self.plus_rect.collidepoint(pos):
                self.current_size = min(BOX_MODE_THRESHOLD, self.current_size + 5)
                return None

            # Preset buttons
            for i, rect in enumerate(self.preset_rects):
                if rect.collidepoint(pos):
                    gen_name = self.PRESETS[i][1]
                    gen_func = getattr(self, gen_name)
                    arr = gen_func(self.current_size)
                    self.input_text = ", ".join(str(v) for v in arr)
                    self._validate()
                    return None

        return None

    def _handle_paste(self):
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if raw:
                text = raw.decode("utf-8", errors="ignore").rstrip("\x00")
                # Filter to allowed chars
                filtered = "".join(c for c in text if c in "0123456789, ")
                if self.select_all:
                    self.input_text = ""
                    self.select_all = False
                space = 200 - len(self.input_text)
                if space > 0:
                    self.input_text += filtered[:space]
                self._validate()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface):
        if not self.visible:
            return

        # Update cursor blink
        now = pygame.time.get_ticks()
        if now - self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now

        # Overlay
        surface.blit(self._overlay, (0, 0))

        # Card background
        pygame.draw.rect(surface, Colors.PANEL_BG, self.card_rect, border_radius=12)
        pygame.draw.rect(surface, Colors.CARD_BORDER, self.card_rect, width=1, border_radius=12)

        # Title
        title_surf = self.font_title.render("Custom Array", True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(centerx=self.title_pos[0], top=self.title_pos[1])
        surface.blit(title_surf, title_rect)

        # Input field
        border_color = Colors.TEXT_ACCENT if not self.select_all else (100, 180, 230)
        pygame.draw.rect(surface, Colors.BG, self.input_rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.input_rect, width=2, border_radius=8)

        input_pad = 12
        clip_rect = pygame.Rect(
            self.input_rect.x + input_pad, self.input_rect.y,
            self.input_rect.width - input_pad * 2, self.input_rect.height
        )

        if self.input_text:
            text_surf = self.font_input.render(self.input_text, True, Colors.TEXT_PRIMARY)
            # If text is wider than clip area, show the rightmost portion
            text_x = clip_rect.x
            if text_surf.get_width() > clip_rect.width:
                text_x = clip_rect.right - text_surf.get_width()
            text_y = self.input_rect.centery - text_surf.get_height() // 2
            surface.set_clip(clip_rect)
            if self.select_all:
                sel_rect = pygame.Rect(text_x, text_y, text_surf.get_width(), text_surf.get_height())
                pygame.draw.rect(surface, (60, 130, 200), sel_rect)
            surface.blit(text_surf, (text_x, text_y))
            surface.set_clip(None)

            # Cursor
            if self.cursor_visible and not self.select_all:
                cursor_x = min(text_x + text_surf.get_width() + 1, clip_rect.right - 1)
                cy_top = self.input_rect.y + 8
                cy_bot = self.input_rect.y + self.input_rect.height - 8
                pygame.draw.line(surface, Colors.TEXT_PRIMARY, (cursor_x, cy_top), (cursor_x, cy_bot), 2)
        else:
            # Placeholder
            ph = self.font_input.render("e.g. 5, 34, 12, 8, 27", True, Colors.TEXT_SECONDARY)
            ph_y = self.input_rect.centery - ph.get_height() // 2
            surface.blit(ph, (clip_rect.x, ph_y))
            # Cursor at start
            if self.cursor_visible:
                cy_top = self.input_rect.y + 8
                cy_bot = self.input_rect.y + self.input_rect.height - 8
                pygame.draw.line(surface, Colors.TEXT_PRIMARY, (clip_rect.x, cy_top), (clip_rect.x, cy_bot), 2)

        # Validation feedback
        if self.error_msg:
            color = (50, 200, 100) if self.is_valid else (230, 70, 70)
            valid_surf = self.font_label.render(self.error_msg, True, color)
            surface.blit(valid_surf, self.valid_pos)

        # Size selector row:  [-]  Size: 20  [+]
        mouse_pos = pygame.mouse.get_pos()

        minus_hov = self.minus_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, Colors.BUTTON_HOVER if minus_hov else Colors.BUTTON_BG,
                         self.minus_rect, border_radius=6)
        m_surf = self.font_btn.render("\u2212", True, Colors.BUTTON_TEXT)
        surface.blit(m_surf, m_surf.get_rect(center=self.minus_rect.center))

        size_text = f"Size: {self.current_size}"
        sz_surf = self.font_btn.render(size_text, True, Colors.TEXT_PRIMARY)
        surface.blit(sz_surf, sz_surf.get_rect(center=self.size_label_pos))

        plus_hov = self.plus_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, Colors.BUTTON_HOVER if plus_hov else Colors.BUTTON_BG,
                         self.plus_rect, border_radius=6)
        p_surf = self.font_btn.render("+", True, Colors.BUTTON_TEXT)
        surface.blit(p_surf, p_surf.get_rect(center=self.plus_rect.center))

        # Preset buttons
        for i, (label, _) in enumerate(self.PRESETS):
            rect = self.preset_rects[i]
            hovered = rect.collidepoint(mouse_pos)
            bg = Colors.BUTTON_HOVER if hovered else Colors.BUTTON_BG
            pygame.draw.rect(surface, bg, rect, border_radius=6)
            lbl_surf = self.font_btn.render(label, True, Colors.BUTTON_TEXT)
            lbl_rect = lbl_surf.get_rect(center=rect.center)
            surface.blit(lbl_surf, lbl_rect)

        # Bottom row: [Reset] [Cancel] [Apply]

        # Reset button
        reset_hovered = self.reset_rect.collidepoint(mouse_pos)
        reset_bg = Colors.BUTTON_HOVER if reset_hovered else Colors.BUTTON_BG
        pygame.draw.rect(surface, reset_bg, self.reset_rect, border_radius=8)
        reset_surf = self.font_btn.render("Reset", True, Colors.BUTTON_TEXT)
        surface.blit(reset_surf, reset_surf.get_rect(center=self.reset_rect.center))

        # Cancel button
        cancel_hovered = self.cancel_rect.collidepoint(mouse_pos)
        cancel_bg = Colors.BUTTON_HOVER if cancel_hovered else Colors.BUTTON_BG
        pygame.draw.rect(surface, cancel_bg, self.cancel_rect, border_radius=8)
        cancel_surf = self.font_btn.render("Cancel", True, Colors.BUTTON_TEXT)
        surface.blit(cancel_surf, cancel_surf.get_rect(center=self.cancel_rect.center))

        # Apply button
        apply_hovered = self.apply_rect.collidepoint(mouse_pos)
        if self.is_valid:
            apply_bg = Colors.BUTTON_ACTIVE if not apply_hovered else (80, 150, 220)
        else:
            apply_bg = Colors.BUTTON_BG
        pygame.draw.rect(surface, apply_bg, self.apply_rect, border_radius=8)
        apply_surf = self.font_btn.render("Apply", True, Colors.BUTTON_TEXT)
        surface.blit(apply_surf, apply_surf.get_rect(center=self.apply_rect.center))
