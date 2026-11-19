"""Integração segura com Spotify e Spicetify."""

import os
import shutil
import subprocess


def _run_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout.strip(), result.returncode
    except (OSError, subprocess.TimeoutExpired):
        return "", -1


def get_spotify_status():
    """Consulta o estado do Spotify sem modificar configurações."""

    # Detecta o pacote instalado pela Microsoft Store.
    powershell = shutil.which("powershell") or "powershell.exe"

    install_path, _ = _run_command([
        powershell,
        "-NoProfile",
        "-Command",
        "Get-AppxPackage -Name 'SpotifyAB.SpotifyMusic' "
        "| Select-Object -First 1 -ExpandProperty InstallLocation",
    ])

    spotify_installed = bool(install_path)

    # Detecta o Spicetify.
    spicetify_command = shutil.which("spicetify")
    spicetify_version = "Não encontrado"
    marketplace = False

    if spicetify_command:
        version, code = _run_command(
            [spicetify_command, "--version"]
        )
        if code == 0 and version:
            spicetify_version = version

        custom_apps, code = _run_command(
            [spicetify_command, "config", "custom_apps"]
        )
        marketplace = (
            code == 0
            and "marketplace" in custom_apps.lower()
        )

    # Verifica se o Spotify está em execução.
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
        "spotify_path": install_path or "Não encontrado",
        "spotify_running": spotify_running,
        "spicetify_installed": bool(spicetify_command),
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
