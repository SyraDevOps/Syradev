import importlib
import traceback

ALLOWED_MODULES = {"math", "random", "sys", "os", "json"}  # Adapte conforme desejar
_module_cache = {}

def _resolve_attr_chain(obj, chain):
    """Resolve uma cadeia de atributos separada por ponto, ex: der.ccos."""
    for part in chain.split('.'):
        obj = getattr(obj, part)
    return obj

def cached_import(module_name):
    if module_name in _module_cache:
        return _module_cache[module_name]
    mod = importlib.import_module(module_name)
    _module_cache[module_name] = mod
    return mod

def import_plugin_if_available(mod, syra_globals):
    if hasattr(mod, '__syra_entry__'):
        mod.__syra_entry__(syra_globals)
        return True
    return False

def syra_expor(module_name, syra_globals, names=None, aliases=None, alias=None, debug=False):
    """
    Importa módulos ou símbolos específicos no escopo da Syra, com suporte a alias e plugins.
    - module_name: nome do módulo Python
    - syra_globals: dicionário de variáveis globais Syra
    - names: lista de nomes/símbolos a importar (ou None para tudo)
    - aliases: lista de aliases para os nomes (ou None)
    - alias: alias para o módulo inteiro (ou None)
    """
    try:
        if module_name not in ALLOWED_MODULES:
            raise ImportError(f"O módulo '{module_name}' não é permitido.")

        mod = cached_import(module_name)

        # Plugins Syra
        if import_plugin_if_available(mod, syra_globals):
            return

        # Importação direta do módulo com alias (ex: expor math as m)
        if names is None:
            name_key = alias or module_name
            if name_key in syra_globals:
                print(f"[Aviso Syra] '{name_key}' já está definido e será sobrescrito.")
            syra_globals[name_key] = mod
            for attr in dir(mod):
                if not attr.startswith("_"):
                    if attr in syra_globals:
                        print(f"[Aviso Syra] '{attr}' já está definido e será sobrescrito.")
                    syra_globals[attr] = getattr(mod, attr)
        else:
            for idx, name in enumerate(names):
                alias_name = aliases[idx] if aliases and idx < len(aliases) else name.split('.')[-1]
                if alias_name in syra_globals:
                    print(f"[Aviso Syra] '{alias_name}' já está definido e será sobrescrito.")
                value = _resolve_attr_chain(mod, name) if '.' in name else getattr(mod, name, None)
                if value is None:
                    raise AttributeError(f"'{name}' não encontrado em '{module_name}'")
                syra_globals[alias_name] = value
    except Exception as e:
        print(f"[Importação Syra] Erro: {e}")
        if debug:
            traceback.print_exc()