"""Gerenciador seguro de módulos do NEXUS."""


class ModuleManager:
    def __init__(self):
        self.modules = {}

    def register(self, module_id, name, description, enabled=False):
        if not module_id or module_id in self.modules:
            raise ValueError("Identificador inválido ou duplicado.")

        self.modules[module_id] = {
            "id": module_id,
            "name": name,
            "description": description,
            "enabled": bool(enabled),
            "status": "available",
        }

    def set_enabled(self, module_id, enabled):
        if module_id not in self.modules:
            raise KeyError("Módulo não encontrado.")

        self.modules[module_id]["enabled"] = bool(enabled)

    def list_modules(self):
        return [module.copy() for module in self.modules.values()]

    def get_module(self, module_id):
        module = self.modules.get(module_id)
        return module.copy() if module else None


def create_default_manager():
    manager = ModuleManager()

    manager.register(
        "spotify",
        "Spotify",
        "Integração com Spotify e Marketplace.",
        enabled=False,
    )

    return manager


module_manager = create_default_manager()
