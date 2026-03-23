# ui/array_modal.py - Custom array input modal for AlgoFlow
import pygame
import random
from config import Colors, FONT_FAMILY, BOX_MODE_THRESHOLD


class ArrayModal:
    """Centered overlay modal for entering custom arrays or selecting presets."""

    PRESET_LABELS = ["Random", "Sorted", "Reversed", "Nearly", "Few Unique"]

    def __init__(self, screen_width, screen_height):
        self.visible = False
        self.current_size = 10
        self.input_text = ""
        self.error_msg = ""
        self.is_valid = False
        self.parsed_array = []
        self.select_all = False

        # Focus state
        self.array_focused = True
        self.size_focused = False
        self.size_text = str(self.current_size)

        # Cursor blink state
        self.cursor_visible = True
        self.cursor_timer = 0

        # Backspace repeat state
        self.backspace_held = False
        self.backspace_timer = 0
        self.backspace_initial_delay = 400
        self.backspace_repeat_interval = 50
        self.backspace_repeating = False

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

        # Size selector row:  [-]  [__]  [+]
        size_row_y = input_y + input_h + 38
        sq = 28
        size_input_w = 50
        gap_s = 8
        total_size_w = sq + gap_s + size_input_w + gap_s + sq
        size_x = cx + (self.card_w - total_size_w) // 2
        self.minus_rect = pygame.Rect(size_x, size_row_y, sq, sq)
        self.size_input_rect = pygame.Rect(size_x + sq + gap_s, size_row_y, size_input_w, sq)
        self.plus_rect = pygame.Rect(size_x + sq + gap_s + size_input_w + gap_s, size_row_y, sq, sq)

        # Preset row
        preset_y = size_row_y + sq + 14
        preset_h = 36
        preset_gap = 6
        self.preset_rects = []
        total_w = sum(self.font_btn.size(p)[0] + 24 for p in self.PRESET_LABELS) + preset_gap * (len(self.PRESET_LABELS) - 1)
        px = cx + (self.card_w - total_w) // 2
        for label in self.PRESET_LABELS:
            pw = self.font_btn.size(label)[0] + 24
            self.preset_rects.append(pygame.Rect(px, preset_y, pw, preset_h))
            px += pw + preset_gap

        # Bottom row: [Clear] [Cancel] [Apply]
        btn_w = 100
        btn_h = 42
        btn_y = cy + self.card_h - pad - btn_h
        btn_gap = 12
        total_btn_w = btn_w * 3 + btn_gap * 2
        btn_x = cx + self.card_w - pad - total_btn_w
        self.clear_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.cancel_rect = pygame.Rect(btn_x + btn_w + btn_gap, btn_y, btn_w, btn_h)
        self.apply_rect = pygame.Rect(btn_x + (btn_w + btn_gap) * 2, btn_y, btn_w, btn_h)

        # Rebuild overlay
        self._overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 140))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def open(self, current_size=10, current_array=None, is_custom=False):
        self.visible = True
        self.current_size = current_size
        self.size_text = str(current_size)
        if is_custom and current_array:
            self.input_text = ", ".join(map(str, current_array))
        else:
            self.input_text = ""
        self.error_msg = ""
        self.is_valid = False
        self.parsed_array = []
        self.select_all = False
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()
        self.array_focused = True
        self.size_focused = False
        self.backspace_held = False
        self.backspace_repeating = False
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
                self.error_msg = f"Values must be 1\u201399 (got {v})"
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
    # Size text commit
    # ------------------------------------------------------------------

    def _commit_size_text(self):
        """Parse size text, clamp to valid range, update current_size."""
        try:
            val = int(self.size_text) if self.size_text else 2
        except ValueError:
            val = 2
        self.current_size = max(2, min(BOX_MODE_THRESHOLD, val))
        self.size_text = str(self.current_size)

    # ------------------------------------------------------------------
    # Contextual presets
    # ------------------------------------------------------------------

    def _apply_preset(self, preset_name):
        """Apply a preset — transforms existing valid input or generates new."""
        if self.is_valid and self.parsed_array:
            # TRANSFORM mode
            arr = list(self.parsed_array)
            if preset_name == "Random":
                random.shuffle(arr)
            elif preset_name == "Sorted":
                arr.sort()
            elif preset_name == "Reversed":
                arr.sort(reverse=True)
            elif preset_name == "Nearly":
                arr.sort()
                for _ in range(min(2, len(arr) // 3)):
                    idx = random.randint(0, len(arr) - 2)
                    arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
            elif preset_name == "Few Unique":
                n_distinct = random.randint(3, 4)
                distinct = random.sample(range(1, 50), n_distinct)
                arr = [random.choice(distinct) for _ in range(len(arr))]
        elif not self.input_text.strip():
            # GENERATE mode
            self._commit_size_text()
            size = self.current_size
            if preset_name == "Random":
                arr = [random.randint(1, 50) for _ in range(size)]
            elif preset_name == "Sorted":
                arr = [round(1 + (49 * i) / max(1, size - 1)) for i in range(size)]
            elif preset_name == "Reversed":
                arr = [round(1 + (49 * i) / max(1, size - 1)) for i in range(size)]
                arr.reverse()
            elif preset_name == "Nearly":
                arr = [round(1 + (49 * i) / max(1, size - 1)) for i in range(size)]
                for _ in range(min(2, size // 3)):
                    idx = random.randint(0, len(arr) - 2)
                    arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
            elif preset_name == "Few Unique":
                n_distinct = random.randint(3, 4)
                distinct = random.sample(range(1, 50), n_distinct)
                arr = [random.choice(distinct) for _ in range(size)]
            else:
                return
        else:
            # Non-empty but invalid — do nothing
            return

        self.input_text = ", ".join(str(v) for v in arr)
        self._validate()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event):
        """Returns {'action': 'apply', 'array': [...]} or {'action': 'cancel'} or None."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            # Global keys
            if event.key == pygame.K_ESCAPE:
                return {"action": "cancel"}

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.size_focused:
                    self._commit_size_text()
                    self.array_focused = True
                    self.size_focused = False
                elif self.is_valid:
                    return {"action": "apply", "array": list(self.parsed_array)}
                return None

            # Backspace — immediate delete + start hold tracking
            if event.key == pygame.K_BACKSPACE:
                self._handle_backspace_key()
                self.backspace_held = True
                self.backspace_timer = pygame.time.get_ticks()
                self.backspace_repeating = False
                return None

            # Route to focused field
            if self.size_focused:
                if event.unicode.isdigit() and len(self.size_text) < 2:
                    self.size_text += event.unicode
                elif event.key == pygame.K_TAB:
                    self._commit_size_text()
                    self.array_focused = True
                    self.size_focused = False
                return None

            if self.array_focused:
                mods = pygame.key.get_mods()
                ctrl = mods & (pygame.KMOD_CTRL | pygame.KMOD_META)

                if ctrl and event.key == pygame.K_a:
                    self.select_all = True
                    return None

                if ctrl and event.key == pygame.K_v:
                    self._handle_paste()
                    return None

                if event.key == pygame.K_DELETE:
                    if self.select_all:
                        self.input_text = ""
                        self.select_all = False
                        self._validate()
                    return None

                if event.key == pygame.K_TAB:
                    self.size_focused = True
                    self.array_focused = False
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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
                self.backspace_repeating = False
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Focus management — commit size text if leaving size box
            was_size_focused = self.size_focused
            if self.input_rect.collidepoint(pos):
                self.array_focused = True
                self.size_focused = False
            elif self.size_input_rect.collidepoint(pos):
                self.size_focused = True
                self.array_focused = False
            else:
                # Clicking a button — keep current focus but commit size if needed
                if was_size_focused:
                    self._commit_size_text()

            # Cancel button
            if self.cancel_rect.collidepoint(pos):
                return {"action": "cancel"}

            # Apply button
            if self.apply_rect.collidepoint(pos):
                if self.is_valid:
                    return {"action": "apply", "array": list(self.parsed_array)}
                return None

            # Clear button
            if self.clear_rect.collidepoint(pos):
                self.input_text = ""
                self.select_all = False
                self._validate()
                return None

            # Size selector buttons
            if self.minus_rect.collidepoint(pos):
                self._commit_size_text()
                self.current_size = max(2, self.current_size - 1)
                self.size_text = str(self.current_size)
                return None
            if self.plus_rect.collidepoint(pos):
                self._commit_size_text()
                self.current_size = min(BOX_MODE_THRESHOLD, self.current_size + 1)
                self.size_text = str(self.current_size)
                return None

            # Preset buttons
            for i, rect in enumerate(self.preset_rects):
                if rect.collidepoint(pos):
                    self._apply_preset(self.PRESET_LABELS[i])
                    return None

        return None

    def _handle_backspace_key(self):
        """Perform one immediate backspace on the focused field."""
        if self.size_focused:
            self.size_text = self.size_text[:-1]
        elif self.array_focused:
            if self.select_all or (pygame.key.get_mods() & (pygame.KMOD_CTRL | pygame.KMOD_META) and self.input_text):
                self.input_text = ""
                self.select_all = False
            elif self.input_text:
                self.input_text = self.input_text[:-1]
            self._validate()

    def _do_backspace(self):
        """Delete one character from the focused field (for repeat timer)."""
        if self.array_focused and self.input_text:
            self.input_text = self.input_text[:-1]
            self._validate()
        elif self.size_focused and self.size_text:
            self.size_text = self.size_text[:-1]

    def _handle_paste(self):
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if raw:
                text = raw.decode("utf-8", errors="ignore").rstrip("\x00")
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
    # Update (called every frame for backspace repeat)
    # ------------------------------------------------------------------

    def update(self):
        """Handle held-backspace repeat. Call every frame when modal is open."""
        if not self.visible or not self.backspace_held:
            return
        now = pygame.time.get_ticks()
        elapsed = now - self.backspace_timer
        if not self.backspace_repeating:
            if elapsed >= self.backspace_initial_delay:
                self.backspace_repeating = True
                self.backspace_timer = now
                self._do_backspace()
        else:
            if elapsed >= self.backspace_repeat_interval:
                self.backspace_timer = now
                self._do_backspace()

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

        # Array input field
        arr_border = Colors.TEXT_ACCENT if self.array_focused else Colors.CARD_BORDER
        pygame.draw.rect(surface, Colors.BG, self.input_rect, border_radius=8)
        pygame.draw.rect(surface, arr_border, self.input_rect, width=2, border_radius=8)

        input_pad = 12
        clip_rect = pygame.Rect(
            self.input_rect.x + input_pad, self.input_rect.y,
            self.input_rect.width - input_pad * 2, self.input_rect.height
        )

        if self.input_text:
            text_surf = self.font_input.render(self.input_text, True, Colors.TEXT_PRIMARY)
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

            if self.cursor_visible and self.array_focused and not self.select_all:
                cursor_x = min(text_x + text_surf.get_width() + 1, clip_rect.right - 1)
                cy_top = self.input_rect.y + 8
                cy_bot = self.input_rect.y + self.input_rect.height - 8
                pygame.draw.line(surface, Colors.TEXT_PRIMARY, (cursor_x, cy_top), (cursor_x, cy_bot), 2)
        else:
            # Placeholder
            ph = self.font_input.render("e.g. 5, 34, 12, 8, 27", True, Colors.TEXT_SECONDARY)
            ph_y = self.input_rect.centery - ph.get_height() // 2
            surface.blit(ph, (clip_rect.x, ph_y))
            if self.cursor_visible and self.array_focused:
                cy_top = self.input_rect.y + 8
                cy_bot = self.input_rect.y + self.input_rect.height - 8
                pygame.draw.line(surface, Colors.TEXT_PRIMARY, (clip_rect.x, cy_top), (clip_rect.x, cy_bot), 2)

        # Validation feedback
        if self.error_msg:
            color = (50, 200, 100) if self.is_valid else (230, 70, 70)
            valid_surf = self.font_label.render(self.error_msg, True, color)
            surface.blit(valid_surf, self.valid_pos)

        # Size selector row:  [-]  [__]  [+]
        mouse_pos = pygame.mouse.get_pos()

        minus_hov = self.minus_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, Colors.BUTTON_HOVER if minus_hov else Colors.BUTTON_BG,
                         self.minus_rect, border_radius=6)
        m_surf = self.font_btn.render("\u2212", True, Colors.BUTTON_TEXT)
        surface.blit(m_surf, m_surf.get_rect(center=self.minus_rect.center))

        # Size input box
        size_border = Colors.TEXT_ACCENT if self.size_focused else Colors.CARD_BORDER
        pygame.draw.rect(surface, Colors.BG, self.size_input_rect, border_radius=6)
        pygame.draw.rect(surface, size_border, self.size_input_rect, width=2, border_radius=6)
        sz_surf = self.font_btn.render(self.size_text, True, Colors.TEXT_PRIMARY)
        surface.blit(sz_surf, sz_surf.get_rect(center=self.size_input_rect.center))
        if self.cursor_visible and self.size_focused:
            sz_cx = self.size_input_rect.centerx + sz_surf.get_width() // 2 + 2
            sz_cy_top = self.size_input_rect.y + 5
            sz_cy_bot = self.size_input_rect.y + self.size_input_rect.height - 5
            pygame.draw.line(surface, Colors.TEXT_PRIMARY, (sz_cx, sz_cy_top), (sz_cx, sz_cy_bot), 2)

        plus_hov = self.plus_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, Colors.BUTTON_HOVER if plus_hov else Colors.BUTTON_BG,
                         self.plus_rect, border_radius=6)
        p_surf = self.font_btn.render("+", True, Colors.BUTTON_TEXT)
        surface.blit(p_surf, p_surf.get_rect(center=self.plus_rect.center))

        # Preset buttons
        for i, label in enumerate(self.PRESET_LABELS):
            rect = self.preset_rects[i]
            hovered = rect.collidepoint(mouse_pos)
            bg = Colors.BUTTON_HOVER if hovered else Colors.BUTTON_BG
            pygame.draw.rect(surface, bg, rect, border_radius=6)
            lbl_surf = self.font_btn.render(label, True, Colors.BUTTON_TEXT)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=rect.center))

        # Bottom row: [Clear] [Cancel] [Apply]

        clear_hovered = self.clear_rect.collidepoint(mouse_pos)
        clear_bg = Colors.BUTTON_HOVER if clear_hovered else Colors.BUTTON_BG
        pygame.draw.rect(surface, clear_bg, self.clear_rect, border_radius=8)
        clear_surf = self.font_btn.render("Clear", True, Colors.BUTTON_TEXT)
        surface.blit(clear_surf, clear_surf.get_rect(center=self.clear_rect.center))

        cancel_hovered = self.cancel_rect.collidepoint(mouse_pos)
        cancel_bg = Colors.BUTTON_HOVER if cancel_hovered else Colors.BUTTON_BG
        pygame.draw.rect(surface, cancel_bg, self.cancel_rect, border_radius=8)
        cancel_surf = self.font_btn.render("Cancel", True, Colors.BUTTON_TEXT)
        surface.blit(cancel_surf, cancel_surf.get_rect(center=self.cancel_rect.center))

        apply_hovered = self.apply_rect.collidepoint(mouse_pos)
        if self.is_valid:
            apply_bg = Colors.BUTTON_ACTIVE if not apply_hovered else (80, 150, 220)
        else:
            apply_bg = Colors.BUTTON_BG
        pygame.draw.rect(surface, apply_bg, self.apply_rect, border_radius=8)
        apply_surf = self.font_btn.render("Apply", True, Colors.BUTTON_TEXT)
        surface.blit(apply_surf, apply_surf.get_rect(center=self.apply_rect.center))
