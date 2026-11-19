from core.settings import load_settings, save_settings
from core.session_log import SessionLog
from core.module_manager import create_default_manager
from core.diagnostics import get_system_diagnostics

print("\n===== NEXUS CORE TEST =====")

settings = load_settings()
print("[OK] Configurações:", settings)

log = SessionLog()
log.add("Teste do núcleo concluído.")
print("[OK] Registro:", log.get_entries())

manager = create_default_manager()
print("[OK] Módulos:", manager.list_modules())

diagnostics = get_system_diagnostics()
print("[OK] Diagnóstico:", diagnostics)

print("\nNEXUS CORE: TODOS OS TESTES PASSARAM!")
