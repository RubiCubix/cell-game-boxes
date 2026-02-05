"""
Boxes game (Python 3) adapted to the Prison Island cell-base framework.

Original legacy game: PI_Game_Boxes.py (Python 2)
Port notes:
- Uses Level structure (Level0-3) like the reference project.
- Level0 and Level1 are identical (Level1 imports Level0).
- GUI uses base application's GUI drawing helpers (no custom GUI class).
- Arduino I/O uses arduino.send_digital_output_values and arduino.send_rgb_values
  with safe fallbacks for older APIs.
"""
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pi_class_game


class Game(pi_class_game.Game):  # pi_class_game provided by base application
    def __init__(self, gui, cell, arduino, sound, game_queue, logger):
        super().__init__(gui, cell, arduino, sound, game_queue, logger)

        # Version of the game. Do not move or change. Used by release scripts.
        self.cell_game_version = "v1.0.0-src"

        # Match reference bundle style
        self._debug_text_on_screen = False

        # A content surface is useful to draw images without touching base GUI layout
        self.content_surface_width = 1280
        self.content_surface_height = 775

    def game_specific_init_game(self):
        # Read config parameter if available
        try:
            self._debug_text_on_screen = bool(self.game_config_parameters.get('debug_text_on_screen', False))
        except Exception:
            self._debug_text_on_screen = False

        # Create a subsurface used by level(s)
        try:
            self._gui.create_subsurface(
                'contentsurface', (582, 255),
                (self.content_surface_width, self.content_surface_height),
                colorkey=(0, 0, 0)
            )
        except Exception:
            # If GUI implementation differs, levels will still try to draw safely.
            pass

        for _, level_instance in self.get_level_instances().items():
            level_instance.level_specific_init_game()
        return

    def game_specific_start_game(self):
        do_only_game_specific = False
        if self.current_level is not None and self.current_level.level_specific_start_game():
            return do_only_game_specific
        return do_only_game_specific

    def game_specific_end_game(self):
        try:
            self._gui.set_text('Info', '')
        except Exception:
            pass

        if self.current_level is not None:
            self.current_level.level_specific_end_game()
        return

    def game_specific_time_counter(self):
        do_only_game_specific = False
        if self.current_level is not None and self.current_level.level_specific_time_counter():
            return do_only_game_specific
        return do_only_game_specific

    def game_specific_sensor_value_changed(self, board_id, value_type, sensor_id, sensor_value):
        do_only_game_specific = False
        if (self.current_level is not None and
                self.current_level.level_specific_sensor_value_changed(
                    board_id, value_type, sensor_id, sensor_value)):
            return do_only_game_specific
        return do_only_game_specific

