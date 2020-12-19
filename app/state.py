import multiprocessing
import importlib
import sys
import os


class State:
    ''' Handles the Unicorn HAT state'''

    def get_mode(self, mode):
        supported_modes = {
            1: "hd"
            2: "mini"
            3: "phat"
            4: "original"
        }
        return supported_modes.get(mode, "original")

    def __init__(self, mode=4):
        self._process = None
        self.set_model(get_mode(mode))


    def set_model(self, mode):
        self.mode = mode
        if mode is "hd":
            import unicornhathd
            import app.programs.hd
            self._unicornhat = unicornhathd
            self._app_programs = app.programs.hd.list
        elif mode is "original":
            import unicornhat
            import app.programs.original
            self._unicornhat = unicornhat
            self._app_programs = app.programs.original.list
        elif mode is "mini":
            import unicornhathd
            import app.programs.mini
            self._unicornhat = unicornhathd
            self._app_programs = app.programs.mini.list
        elif mode is "phat":
            import unicornhat
            import app.programs.phat
            self._unicornhat = unicornhat
            self._app_programs = app.programs.phat.list
            self._unicornhat.set_layout(self._unicornhat.PHAT)


    def start_program(self, name, params={}):
        program = self._get_program(name)
        self.stop_program()
        self._set_rotation(params)
        self._set_brightness(params)
        self._start_process(program, params)


    def stop_program(self):
        if self._process is not None:
            self._process.terminate()
        self._unicornhat.show()


    def _get_program(self, name):
        try:
            return self._app_programs[name]
        except KeyError:
            raise ProgramNotFound(name)


    def _set_brightness(self, params):
        if params.get("brightness") is not None:
            brightness = float(params["brightness"])
            if 0 <= brightness <= 1:
                self._unicornhat.brightness(brightness)
            else:
                raise ValueError("Brightness must be between 0.0 and 1.0")

    def _set_rotation(self, params):
        if params.get("rotation") is not None:
            rotation = int(params["rotation"])
            if rotation in [0, 90, 180, 270]:
                self._unicornhat.rotation(rotation)
            else:
                raise ValueError("Rotation must be 0, 90, 180 or 270 degrees")

    def _start_process(self, program, params):
        def run_program(self):
            importlib.import_module(program.location).run(params)
        self._process = multiprocessing.Process(target=run_program, args=(params,))
        self._process.start()


state = State()


class ProgramNotFound(Exception):
    pass
