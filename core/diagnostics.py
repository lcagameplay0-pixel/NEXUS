"""Diagnósticos básicos e somente de leitura."""

import platform
import shutil
import sys
from pathlib import Path


def get_system_diagnostics():
    try:
        disk = shutil.disk_usage(Path.home())
        free_space_gb = round(disk.free / (1024 ** 3), 2)
    except OSError:
        free_space_gb = None

    return {
        "app_status": "running",
        "operating_system": platform.system(),
        "windows_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "disk_free_gb": free_space_gb,
        "python_executable": sys.executable,
        "diagnostic_mode": "read_only",
    }
