
"""Inicializador principal do NEXUS."""

import os
import webview

from pathlib import Path
from urllib.parse import unquote, urlsplit

from core.settings import (
    APP_NAME,
    APP_VERSION,
    load_settings,
    save_settings,
)
from core.session_log import session_log
from core.module_manager import module_manager
from core.diagnostics import get_system_diagnostics

from modules.spotify import (
    get_spotify_status,
    open_spotify,
)


def _is_allowed_navigation(uri, allowed_page):
    """Permite somente a página principal local do NEXUS."""

    try:
        parsed = urlsplit(uri)

        if parsed.scheme.lower() != "file":
            return False

        if parsed.netloc not in ("", "localhost"):
            return False

        requested_path = unquote(parsed.path)

        # Remove a barra inicial de caminhos Windows como /C:/...
        if (
            os.name == "nt"
            and len(requested_path) >= 3
            and requested_path[0] == "/"
            and requested_path[2] == ":"
        ):
            requested_path = requested_path[1:]

        return Path(requested_path).resolve() == allowed_page.resolve()

    except (OSError, ValueError):
        return False


def _install_navigation_protection(window, html_file):
    """Registra proteção complementar no evento NavigationStarting."""

    native = window.native
    webview_control = getattr(native, "webview", None)

    if webview_control is None:
        session_log.add(
            "AVISO: não foi possível ativar a proteção de navegação."
        )
        return

    allowed_page = html_file.resolve()

    def on_navigation_start(sender, args):
        try:
            requested_url = str(args.Uri)

            if not _is_allowed_navigation(requested_url, allowed_page):
                args.Cancel = True
                session_log.add("Navegação externa bloqueada.")

        except Exception:
            args.Cancel = True
            session_log.add(
                "Navegação bloqueada por falha na verificação."
            )

    # Adiciona um manipulador sem substituir o original do pywebview.
    webview_control.NavigationStarting += on_navigation_start

    session_log.add("Proteção de navegação ativada.")


class NexusAPI:
    """Ponte controlada entre a interface e o Python."""

    def get_dashboard_data(self):
        return {
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "settings": load_settings(),
            "diagnostics": get_system_diagnostics(),
            "logs": session_log.get_entries(),
            "modules": module_manager.list_modules(),
        }

    def set_theme(self, theme):
        if theme not in ("cyan", "violet"):
            return {"success": False, "message": "Tema inválido."}

        settings = load_settings()
        settings["theme"] = theme
        save_settings(settings)

        session_log.add(f"Tema alterado para {theme}.")
        return {"success": True, "theme": theme}

    def clear_log(self):
        session_log.clear()
        session_log.add("Registro da sessão limpo.")
        return {"success": True}

    def refresh_diagnostics(self):
        session_log.add("Diagnóstico do sistema atualizado.")
        return get_system_diagnostics()

    def get_spotify_status(self):
        status = get_spotify_status()
        session_log.add("Diagnóstico do Spotify atualizado.")
        return status

    def launch_spotify(self):
        result = open_spotify()

        if result["success"]:
            session_log.add("Solicitação de abertura do Spotify enviada.")
        else:
            session_log.add(
                f"Falha ao abrir Spotify: {result['message']}"
            )

        return result


def main():
    session_log.add("NEXUS iniciado.")

    api = NexusAPI()
    html_file = Path(__file__).parent / "ui" / "index.html"

    window = webview.create_window(
        title=f"NEXUS {APP_VERSION}",
        url=str(html_file.resolve()),
        js_api=api,
        width=1180,
        height=800,
        min_size=(900, 620),
        resizable=True,
        background_color="#070B12",
    )

    def on_window_before_show(window):
        session_log.add(
            "Janela nativa criada. Ativando proteção de navegação."
        )
        _install_navigation_protection(window, html_file)

    # window.events.before_show += on_window_before_show

    webview.start(debug=False)


if __name__ == "__main__":
    main()
