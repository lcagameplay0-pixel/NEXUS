
import os
import shutil
import subprocess
import winreg
from pathlib import Path


def _run_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt" else 0
            ),
        )
        return result.stdout.strip(), result.returncode
    except (OSError, subprocess.TimeoutExpired):
        return "", -1


def _find_spotify():
    """Procura o Spotify em diferentes fontes do Windows."""

    if os.name != "nt":
        return None

    powershell = shutil.which("powershell") or "powershell.exe"

    output, _ = _run_command([
        powershell,
        "-NoProfile",
        "-Command",
        "Get-AppxPackage -Name 'SpotifyAB.SpotifyMusic' "
        "| Select-Object -First 1 -ExpandProperty InstallLocation",
    ])

    if output and Path(output).exists():
        return output

    candidates = [
        Path(os.environ.get("APPDATA", "")) / "Spotify" / "Spotify.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
        / "Spotify" / "Spotify.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Spotify"
        / "Spotify.exe",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    registry_paths = [
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for root, key_path in registry_paths:
        try:
            with winreg.OpenKey(root, key_path) as key:
                count = winreg.QueryInfoKey(key)[0]

                for index in range(count):
                    try:
                        subkey_name = winreg.EnumKey(key, index)

                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name, _ = winreg.QueryValueEx(
                                    subkey, "DisplayName"
                                )
                            except OSError:
                                continue

                            if "spotify" not in name.lower():
                                continue

                            for value_name in (
                                "InstallLocation", "DisplayIcon"
                            ):
                                try:
                                    value, _ = winreg.QueryValueEx(
                                        subkey, value_name
                                    )
                                    path = Path(
                                        str(value).strip('"')
                                    )

                                    if path.is_file() and path.name.lower() == "spotify.exe":
                                        return str(path)

                                    if path.is_dir():
                                        executable = path / "Spotify.exe"
                                        if executable.is_file():
                                            return str(executable)

                                except (OSError, ValueError):
                                    continue

                    except OSError:
                        continue

        except OSError:
            continue

    return None


def _find_spicetify():
    """Localiza o executável do Spicetify."""

    command = shutil.which("spicetify")

    if command:
        return command

    local_app_data = Path(
        os.environ.get("LOCALAPPDATA", "")
    )

    candidates = [
        local_app_data / "spicetify" / "spicetify.exe",
        Path.home() / ".spicetify" / "spicetify.exe",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return None


def get_spotify_status():
    """Consulta o estado do Spotify e do Spicetify."""

    spotify_path = _find_spotify()
    spotify_installed = bool(spotify_path)

    spicetify_command = _find_spicetify()
    spicetify_installed = bool(spicetify_command)

    spicetify_version = "Não encontrado"
    marketplace = False

    if spicetify_command:
        version, code = _run_command(
            [spicetify_command, "--version"]
        )

        if code == 0 and version:
            spicetify_version = version

        custom_apps, code = _run_command([
            spicetify_command, "config", "custom_apps"
        ])

        marketplace = (
            code == 0
            and "marketplace" in custom_apps.lower()
        )

    tasklist = shutil.which("tasklist") or "tasklist.exe"

    processes, _ = _run_command([
        tasklist,
        "/FI", "IMAGENAME eq Spotify.exe",
        "/FO", "CSV",
        "/NH",
    ])

    spotify_running = "spotify.exe" in processes.lower()

    return {
        "spotify_installed": spotify_installed,
        "spotify_path": spotify_path or "Não encontrado",
        "spotify_running": spotify_running,
        "spicetify_installed": spicetify_installed,
        "spicetify_version": spicetify_version,
        "marketplace_configured": marketplace,
    }


def open_spotify():
    """Abre o Spotify pelo protocolo registrado no Windows."""

    if os.name != "nt":
        return {
            "success": False,
            "message": "Esta função está disponível apenas no Windows.",
        }

    try:
        os.startfile("spotify:")
        return {
            "success": True,
            "message": "Solicitação de abertura do Spotify enviada.",
        }
    except OSError as error:
        return {
            "success": False,
            "message": f"Não foi possível abrir o Spotify: {error}",
        }
