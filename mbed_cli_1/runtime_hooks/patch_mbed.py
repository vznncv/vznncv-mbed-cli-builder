import importlib
import os
import runpy
from contextlib import contextmanager
from functools import wraps

import sys


def _get_cwd():
    return os.environ.get('PWD', os.getcwd())


@contextmanager
def _update_context(env=None, cwd=None, argv=None):
    env = env or {}
    argv = argv or sys.argv
    original_env = os.environ.copy()
    original_cwd = _get_cwd()
    original_argv = sys.argv.copy()
    try:
        os.environ.update(env)
        if cwd:
            os.chdir(cwd)
        sys.argv[:] = argv
        yield
    finally:
        os.environ.clear()
        os.environ.update(original_env)
        os.chdir(original_cwd)
        sys.argv[:] = original_argv


def _dummy_check_requirements(self, *args, **kwargs):
    return True


def _patch_run_cmd(mbed_cli_module, fun_name):
    original_run = getattr(mbed_cli_module, fun_name)
    python_cmd = mbed_cli_module.python_cmd
    ProcessException = mbed_cli_module.ProcessException

    def run_python(command, **kwargs):
        patched_argv = []
        script_pos = next((i for i, arg in enumerate(command[1:], start=1) if arg.endswith('.py')), None)
        if not script_pos:
            raise ValueError(f"Cannot find script in the {command}")
        patched_argv.extend(command[script_pos:])

        with _update_context(env=kwargs.get('env'), cwd=kwargs.get('cwd'), argv=patched_argv):
            try:
                runpy.run_path(
                    path_name=patched_argv[0],
                    run_name='__main__',
                    init_globals={'exit': sys.exit}
                )
            except BaseException as e:
                if isinstance(e, SystemExit):
                    ret_code = e.code
                else:
                    ret_code = 1
                if ret_code:
                    raise ProcessException(ret_code, patched_argv[0], ' '.join(patched_argv), _get_cwd()) from e

    @wraps(original_run)
    def run_cmd_patched(command, **kwargs):
        if command[0] != python_cmd:
            return original_run(command, **kwargs)
        else:
            return run_python(command, **kwargs)

    setattr(mbed_cli_module, fun_name, run_cmd_patched)


def patch_mbed():
    mbed_cli_module = importlib.import_module('mbed.mbed')

    # patch current directory
    mbed_cli_module._cwd = os.environ.get('PWD', os.getcwd())

    # patch requirements validation
    mbed_cli_module.Program.check_requirements = _dummy_check_requirements

    # patch mbed tools usage
    _patch_run_cmd(mbed_cli_module, 'popen')
    _patch_run_cmd(mbed_cli_module, 'pquery')


patch_mbed()
