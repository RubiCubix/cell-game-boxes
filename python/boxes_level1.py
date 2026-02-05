# -------------------------------------------------------------------------------------------------
# Program: Boxes Level0
# Copyright: Prison Island AB
# Description:
#   Port of legacy "PI_Game_Boxes.py" to cell-base level structure.
#   The team must press the correct button on the big box and the small box.
#   Correct choice is shown as an image (symbol / color / mixed) depending on score.
# -------------------------------------------------------------------------------------------------

import random

class _Button:
    def __init__(self, sensor_id: int, symbol_image: str, color_image: str):
        self.sensor_id = sensor_id
        self.symbol_image = symbol_image
        self.color_image = color_image

class _Box:
    def __init__(self, buttons, box_size: str):
        self.buttons = buttons
        self.box_size = box_size
        self.correct_button_sensor_id = -1


class Level:
    def __init__(self, game):
        self._game = game
        self._gui = game._gui
        self._arduinos = game._arduinos
        self._sound = game._sound
        self._logger = game._logger
        self._debug_level = getattr(game, "_debug_level", 0)

        # --- Legacy constants / mappings (kept as in the uploaded Python2 game) ---
        self.time_between_buttons = 6  # not used directly (base loop), kept for future parity
        # --- Constants / mappings (single NEW STANDARD variant) ---
        self.time_between_buttons = 6  # kept for parity (not currently used directly)

        # All image filenames are lowercase
        self.button_colors_images = [
            "pi_cube_red.png",
            "pi_cube_green.png",
            "pi_cube_blue.png",
            "pi_cube_yellow.png",
            "pi_cube_orange.png",
        ]

        self.button_symbols_images = [
            "pi_cube_circle.png",
            "pi_cube_triangle.png",
            "pi_cube_square.png",
            "pi_cube_pentagon.png",
            "pi_cube_hexagon.png",
        ]

        # NEW STANDARD sensor wiring
        self.small_box_sensors = [1, 2, 3, 4, 5]
        self.large_box_sensors = [6, 7, 8, 9, 10]

        # NEW STANDARD mapping
        self.large_box_color_map = [0, 1, 2, 3, 4]
        self.large_box_symbol_map = [1, 2, 3, 4, 0]

        self.small_box_color_map = [0, 1, 2, 3, 4]
        self.small_box_symbol_map = [4, 1, 2, 3, 0]
# NEW STANDARD, JKP (legacy comment)

                # Digital output indices for button LEDs (per boxes_main.json)
        # DO1 is DoorLock, DO2-DO11 are SB1-SB10 LEDs
        self.small_box_led_outputs = [2, 3, 4, 5, 6]
        self.large_box_led_outputs = [7, 8, 9, 10, 11]

# --- Runtime state ---
        self.large_box = None
        self.small_box = None

        self.flag_sensor = []  # debounce/lock until new symbols generated
        self.generate_at_elapsed_s = 2

        self.start_image = "pi_cube.png"  # placeholder image shown when "cleared"
        self.big_image_current = self.start_image
        self.small_image_current = self.start_image

        self._start_timestamp_ms = 0
        self._close_door_sent = False

    # ---------------- Framework hooks ----------------

    def level_specific_init_game(self):
        # Build boxes + internal sensor flags
        self._init_boxes()

        sensor_flags = int(self._safe_get_param("sensorFlags", 10))
        self.flag_sensor = [False for _ in range(sensor_flags)]

        # Prepare drawing area
        self._safe_gui_prepare()

        return

    def level_specific_start_game(self):
        do_only_level_specific = False

        # Reset game values (legacy reset_game_specific ran on start)
        self._set_points_absolute(0)

        self._start_timestamp_ms = self._game.current_time_ms()
        self._close_door_sent = False
        self.generate_at_elapsed_s = 2

        self.big_image_current = self.start_image
        self.small_image_current = self.start_image

        self._safe_gui_prepare()
        self._draw_images()

        # Light up buttons + clear sensor flags
        self._set_all_sensor_flags(False)
        self._light_all_buttons()

        return do_only_level_specific

    def level_specific_end_game(self):
        # Cleanup hook (stop threads etc). We do not spawn threads here.
        return

    def level_specific_time_counter(self):
        do_only_level_specific = False
        # Emulate legacy timed events using elapsed time
        if (not self._game.has_game_ended()) and self._game.get_state() == "GAME":
            elapsed_s = (self._game.current_time_ms() - self._start_timestamp_ms) // 1000

            # Fire when we've reached/passed the target, exactly once
            if elapsed_s >= self.generate_at_elapsed_s:
                self.generate_symbols()

                # Schedule next generation (example: every 6 seconds)
                self.generate_at_elapsed_s = elapsed_s + self.time_between_buttons


                return do_only_level_specific

    def level_specific_sensor_value_changed(self, board_id, value_type, sensor_id, sensor_value):
        do_only_level_specific = False

        # Treat any positive value as "pressed"
        try:
            pressed = int(sensor_value) > 0
        except Exception:
            pressed = bool(sensor_value)

        if not pressed:
            return do_only_level_specific

        # Legacy uses a sensorFlags range check
        try:
            sensor_id_int = int(sensor_id)
        except Exception:
            return do_only_level_specific

        sensor_index = sensor_id_int - 1

        if sensor_id_int < 0 or sensor_id_int >= len(self.flag_sensor):
            return do_only_level_specific

        if self.flag_sensor[sensor_index]:
            # already pressed / locked until next generation
            return do_only_level_specific

        self.flag_sensor[sensor_index] = True

        # Handle correct/incorrect presses
        if sensor_id_int == self.large_box.correct_button_sensor_id:
            self._safe_play("PI_Positive01")
            self._set_points_relative(+2)
            self.big_image_current = self.start_image
            self.large_box.correct_button_sensor_id = -1
            self._draw_images()

        elif sensor_id_int == self.small_box.correct_button_sensor_id:
            self._safe_play("PI_Positive01")
            self._set_points_relative(+2)
            self.small_image_current = self.start_image
            self.small_box.correct_button_sensor_id = -1
            self._draw_images()

        else:
            self._safe_play("PI_Error")
            if int(self._game.get_attributes('points')) > 1:
                self._set_points_relative(-2)

        # If both solved, schedule next symbol generation soon (legacy: +1s)
        if self.small_box.correct_button_sensor_id == -1 and self.large_box.correct_button_sensor_id == -1:
            elapsed_s = int((self._game.current_time_ms() - self._start_timestamp_ms) / 1000)
            self.generate_at_elapsed_s = elapsed_s + 1

        # Win condition
        if int(self._game.get_attributes('points')) >= int(self._safe_get_param('maxPoints', 100)):
            self._game.initiate_end_game("Max points reached")

        # Clamp points >= 0
        if int(self._game.get_attributes('points')) < 0:
            self._set_points_absolute(0)

        return do_only_level_specific

    # ---------------- Game logic (ported) ----------------

    def _init_boxes(self):
        large_buttons = []
        for i, sensor in enumerate(self.large_box_sensors):
            large_buttons.append(
                _Button(
                    sensor_id=sensor,
                    symbol_image=self.button_symbols_images[self.large_box_symbol_map[i]],
                    color_image=self.button_colors_images[self.large_box_color_map[i]],
                )
            )
        self.large_box = _Box(large_buttons, "big")

        small_buttons = []
        for i, sensor in enumerate(self.small_box_sensors):
            small_buttons.append(
                _Button(
                    sensor_id=sensor,
                    symbol_image=self.button_symbols_images[self.small_box_symbol_map[i]],
                    color_image=self.button_colors_images[self.small_box_color_map[i]],
                )
            )
        self.small_box = _Box(small_buttons, "small")

    def generate_random_button_sensor(self, box: _Box) -> int:
        random_index = random.randint(0, len(box.buttons) - 1)
        return box.buttons[random_index].sensor_id

    def generate_symbols(self):
        self.large_box.correct_button_sensor_id = self.generate_random_button_sensor(self.large_box)
        self.small_box.correct_button_sensor_id = self.generate_random_button_sensor(self.small_box)

        points = int(self._game.get_attributes('points'))

        # First level (<25): symbols
        if points < 25:
            self.big_image_current = self._button_by_sensor(self.large_box, self.large_box.correct_button_sensor_id).symbol_image
            self.small_image_current = self._button_by_sensor(self.small_box, self.small_box.correct_button_sensor_id).symbol_image

        # Second level (<50): colors
        elif points < 50:
            self.big_image_current = self._button_by_sensor(self.large_box, self.large_box.correct_button_sensor_id).color_image
            self.small_image_current = self._button_by_sensor(self.small_box, self.small_box.correct_button_sensor_id).color_image

        # Third level (>=50): mixed random
        else:
            if random.randint(0, 1) == 0:
                self.big_image_current = self._button_by_sensor(self.large_box, self.large_box.correct_button_sensor_id).symbol_image
            else:
                self.big_image_current = self._button_by_sensor(self.large_box, self.large_box.correct_button_sensor_id).color_image

            if random.randint(0, 1) == 0:
                self.small_image_current = self._button_by_sensor(self.small_box, self.small_box.correct_button_sensor_id).symbol_image
            else:
                self.small_image_current = self._button_by_sensor(self.small_box, self.small_box.correct_button_sensor_id).color_image

        self._draw_images()
        self._set_all_sensor_flags(False)
        self._light_all_buttons()

        self._update_debug_text()

    def _button_by_sensor(self, box: _Box, sensor_id: int) -> _Button:
        for b in box.buttons:
            if b.sensor_id == sensor_id:
                return b
        return box.buttons[0]

    # ---------------- GUI helpers (base GUI) ----------------

    def _safe_gui_prepare(self):
        try:
            self._gui.fill_subsurface('contentsurface', (0, 0, 0))
            self._gui.set_subsurface_visibility('contentsurface', True)
            self._gui.set_other_gui_objects_zindex('contentsurface', 21)
        except Exception:
            pass

    def _draw_images(self):
        # Draw big + small images onto the shared subsurface.
        # Uses the same base GUI helper as the reference project.
        try:
            self._gui.fill_subsurface('contentsurface', (0, 0, 0))

            big_key = self._strip_ext(self.big_image_current)
            small_key = self._strip_ext(self.small_image_current)

            # Big image
            self._gui.draw_image_on_subsurface(
                big_key, 'contentsurface',
                (self._game.content_surface_width / 2, 220),
                center_aligned=True
            )

            # Small image (scaled down)
            self._gui.draw_image_on_subsurface(
                small_key, 'contentsurface',
                (260, 520),
                center_aligned=True,
                scale=0.5
            )
        except Exception:
            # If GUI differs, at least keep Info text updated.
            pass

    @staticmethod
    def _strip_ext(filename: str) -> str:
        return filename.rsplit('.', 1)[0] if '.' in filename else filename

    # ---------------- Points helpers ----------------

    def _set_points_relative(self, delta: int):
        try:
            self._game.change_points(delta, True)
        except Exception:
            # Fallback: try absolute style
            cur = int(self._game.get_attributes('points'))
            self._set_points_absolute(cur + delta)

    def _set_points_absolute(self, value: int):
        try:
            self._game.change_points(value, False)
        except Exception:
            cur = int(self._game.get_attributes('points'))
            self._game.change_points(value - cur, True)

    # ---------------- Arduino helpers ----------------

    def _send_close_door(self):
        """
        Legacy game sent: dataToMainProgram("A:CLOSE")
        New base instruction: use arduino.send_digital_output_values / send_rgb_values.
        This implementation is best-effort; adapt mapping in your base if needed.
        """
        if not self._arduinos:
            return
        a = self._arduinos[0]

        # Try common calling styles
        for args, kwargs in [
            (({1: 0},), {}),
            (([(1, 0)],), {}),
            ((), {"output_id": 1, "value": 0}),
        ]:
            try:
                if hasattr(a, "send_digital_output_values"):
                    a.send_digital_output_values(*args, **kwargs)
                    return
            except Exception:
                continue

    def _set_all_sensor_flags(self, value: bool):
        # Legacy: send "F" to Arduino to clear flags, then reset local list.
        # Here we only reset local flags (and optionally can send a clear packet).
        for i in range(len(self.flag_sensor)):
            self.flag_sensor[i] = value

        # Optional best-effort clear on Arduino (no-op if unsupported)
        if not self._arduinos:
            return
        a = self._arduinos[0]
        try:
            if hasattr(a, "send_digital_output_values"):
                a.send_digital_output_values({})
        except Exception:
            pass

    def _light_all_buttons(self):
        """Turn on all 10 button LEDs (SB1-SB10).

        Hardware mapping (boxes_main.json):
        - DO1: DoorLock (pin 10)
        - DO2-DO6: Small box button LEDs (SB1-SB5)
        - DO7-DO11: Large box button LEDs (SB6-SB10)
        """
        if not self._arduinos:
            return
        a = self._arduinos[0]

        output_ids = self.small_box_led_outputs + self.large_box_led_outputs
        payload_dict = {oid: 1 for oid in output_ids}

        # Try common signatures
        for args, kwargs in [
            ((payload_dict,), {}),
            ((), {"values": payload_dict}),
            (([(k, v) for k, v in payload_dict.items()],), {}),
        ]:
            try:
                if hasattr(a, "send_digital_output_values"):
                    a.send_digital_output_values(*args, **kwargs)
                    return
            except Exception:
                continue


    # ---------------- Misc helpers ----------------

    def _safe_play(self, sound_name: str, loop: int = 0):
        try:
            self._sound.play_sound_file(sound_name, loop=loop)
        except Exception:
            try:
                self._sound.play_soundfile(sound_name, loop=loop)  # legacy naming
            except Exception:
                pass

    def _safe_get_param(self, key: str, default):
        # Prefer new config parameters, fall back to attributes (base) if present
        try:
            return self._game.game_config_parameters.get(key, default)
        except Exception:
            pass
        try:
            return self._game.get_attributes(key)
        except Exception:
            return default


    def _update_debug_text(self):
        if not self._game.debug_text_on_screen:
            return

        small = self.small_box.correct_button_sensor_id
        large = self.large_box.correct_button_sensor_id

        if small == -1 and large == -1:
            text = "No active target"
        else:
            text = f"Correct sensors → Small: {small}, Large: {large}"

        self._gui.set_text("Info", text)

