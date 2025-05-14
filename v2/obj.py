import re
import func

# Armazenamento global de classes e objetos
syra_classes = {}
syra_objects = {}
syra_object_counter = 0

class SyraObject:
    def __init__(self, data):
        self._data = data
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        print("DEBUG self._data:", self._data)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    def __getitem__(self, key):
        return self._data[key]
    def __setitem__(self, key, value):
        self._data[key] = value

def define_class(class_code):
    """
    Recebe o código da classe Syra como string.
    Exemplo:
    class Pessoa:
        nome
        idade

        init(nome, idade):
            self.nome = nome
            self.idade = idade

        saudacao():
            print("Olá, eu sou " + self.nome)
    """
    lines = [l.rstrip() for l in class_code.strip().splitlines() if l.strip()]
    header = lines[0]
    m = re.match(r"class\s+(\w+)(?:\s*:\s*(\w+))?:", header)
    if not m:
        print("Erro de sintaxe na definição da classe.")
        return
    class_name, base_class = m.groups()
    fields = []
    methods = {}
    current_method = None
    method_lines = []
    for line in lines[1:]:
        if re.match(r"(static\s+)?\w+\(.*\):", line.strip()):
            # Salvando método anterior
            if current_method:
                methods[current_method] = "\n".join(method_lines)
            # Novo método
            current_method = line.strip().split("(")[0].replace("static ", "")
            method_lines = [line]
        elif current_method:
            method_lines.append(line)
        else:
            # Campo simples
            fields.append(line.strip())
    if current_method:
        methods[current_method] = "\n".join(method_lines)
    syra_classes[class_name] = {
        "fields": fields,
        "methods": methods,
        "base": base_class
    }
    print(f"Classe '{class_name}' definida.")

def instantiate(class_name, *args):
    global syra_object_counter
    if class_name not in syra_classes:
        print(f"Classe '{class_name}' não definida.")
        return None
    class_def = syra_classes[class_name]
    obj_id = f"obj_{syra_object_counter}"
    syra_object_counter += 1
    obj = SyraObject({"__class__": class_name})
    # Inicializa campos
    for idx, field in enumerate(class_def["fields"]):
        obj[field] = args[idx] if idx < len(args) else None
    syra_objects[obj_id] = obj
    # Executa init se existir
    if "init" in class_def["methods"]:
        call_method(obj_id, "init", *args)
    return obj_id

def call_method(obj_id, method_name, *args):
    obj = syra_objects.get(obj_id)
    if not obj:
        print(f"Objeto '{obj_id}' não existe.")
        return
    class_name = obj["__class__"]
    class_def = syra_classes[class_name]
    method_code = None
    if method_name in class_def["methods"]:
        method_code = class_def["methods"][method_name]
    elif class_def["base"]:
        base = class_def["base"]
        if base in syra_classes and method_name in syra_classes[base]["methods"]:
            method_code = syra_classes[base]["methods"][method_name]
    if not method_code:
        print(f"Método '{method_name}' não existe na classe '{class_name}'.")
        return
    # Cria escopo local para self e args
    local_vars = {"self": obj if isinstance(obj, SyraObject) else SyraObject(obj)}
    header = method_code.splitlines()[0]
    params = re.findall(r"\((.*?)\)", header)
    param_names = [p.strip() for p in params[0].split(",")] if params and params[0].strip() else []
    # Debug:
    # print("param_names:", param_names)
    # print("args:", args)
    for idx, pname in enumerate(param_names):
        if pname and idx < len(args):
            local_vars[pname] = args[idx]
    body = "\n".join(method_code.splitlines()[1:])
    body_lines = body.splitlines()
    new_body_lines = []
    for line in body_lines:
        stripped = line.strip()
        m = re.match(r"super\((.*)\)", stripped)
        if m and class_def["base"]:
            # Avalia os argumentos de super()
            super_args = [eval(arg.strip(), {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float}) for arg in m.group(1).split(",") if arg.strip()]
            base_class = class_def["base"]
            # Chama o init da base
            call_method_base(obj_id, class_def["base"], "init", *super_args)
            continue  # Não executa a linha super no corpo
        new_body_lines.append(line)
    body = "\n".join(new_body_lines)
    for line in body.splitlines():
        exec_line = line.strip()
        if exec_line.startswith("return "):
            expr = exec_line[7:].strip()
            result = eval(expr, {**local_vars, "str": str, "int": int, "float": float})
            return result
        elif exec_line.startswith("shw(") or exec_line.startswith("print("):
            expr = exec_line[exec_line.find("(")+1:-1]
            print(eval(expr, {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float}))
        elif "=" in exec_line:
            left, right = exec_line.split("=", 1)
            left = left.strip()
            right = right.strip()
            if left.startswith("self."):
                setattr(local_vars["self"], left[5:], eval(right, {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float}))
            else:
                local_vars[left] = eval(right, {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float})

def call_method_base(obj_id, base_class, method_name, *args):
    obj = syra_objects.get(obj_id)
    if not obj:
        print(f"Objeto '{obj_id}' não existe.")
        return
    class_def = syra_classes[base_class]
    method_code = class_def["methods"].get(method_name)
    if not method_code:
        print(f"Método '{method_name}' não existe na classe base '{base_class}'.")
        return
    local_vars = {"self": obj if isinstance(obj, SyraObject) else SyraObject(obj)}
    header = method_code.splitlines()[0]
    params = re.findall(r"\((.*?)\)", header)
    param_names = [p.strip() for p in params[0].split(",")] if params and params[0].strip() else []
    for idx, pname in enumerate(param_names):
        if pname and idx < len(args):
            local_vars[pname] = args[idx]
    body = "\n".join(method_code.splitlines()[1:])
    body_lines = body.splitlines()
    new_body_lines = []
    for line in body_lines:
        stripped = line.strip()
        m = re.match(r"super\((.*)\)", stripped)
        if m and class_def["base"]:
            super_args = [eval(arg.strip(), {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float}) for arg in m.group(1).split(",") if arg.strip()]
            call_method_base(obj_id, class_def["base"], "init", *super_args)
            continue
        new_body_lines.append(line)
    body = "\n".join(new_body_lines)
    for line in body.splitlines():
        exec_line = line.strip()
        if exec_line.startswith("return "):
            expr = exec_line[7:].strip()
            result = eval(expr, {**local_vars, "str": str, "int": int, "float": float})
            return result
        elif exec_line.startswith("shw(") or exec_line.startswith("print("):
            expr = exec_line[exec_line.find("(")+1:-1]
            print(eval(expr, {**local_vars, "str": str, "int": int, "float": float}))
        elif "=" in exec_line:
            left, right = exec_line.split("=", 1)
            left = left.strip()
            right = right.strip()
            if left.startswith("self."):
                setattr(local_vars["self"], left[5:], eval(right, {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float}))
            else:
                local_vars[left] = eval(right, {"self": local_vars["self"], **local_vars, "str": str, "int": int, "float": float})

def static_call(class_name, method_name, *args):
    if class_name not in syra_classes:
        print(f"Classe '{class_name}' não definida.")
        return
    class_def = syra_classes[class_name]
    if method_name not in class_def["methods"]:
        print(f"Método estático '{method_name}' não existe na classe '{class_name}'.")
        return
    method_code = class_def["methods"][method_name]
    header = method_code.splitlines()[0]
    params = re.findall(r"\((.*?)\)", header)
    param_names = [p.strip() for p in params[0].split(",")] if params and params[0].strip() else []
    local_vars = {}
    for idx, pname in enumerate(param_names):
        if pname and idx < len(args):
            local_vars[pname] = args[idx]
    body = "\n".join(method_code.splitlines()[1:])
    for line in body.splitlines():
        exec_line = line.strip()
        if exec_line.startswith("return "):
            expr = exec_line[7:].strip()
            result = eval(expr, {**local_vars, "str": str, "int": int, "float": float})
            return result
        elif exec_line.startswith("shw(") or exec_line.startswith("print("):
            expr = exec_line[exec_line.find("(")+1:-1]
            print(eval(expr, {**local_vars, "str": str, "int": int, "float": float}))
        elif "=" in exec_line:
            left, right = exec_line.split("=", 1)
            local_vars[left.strip()] = eval(right.strip(), {**local_vars, "str": str, "int": int, "float": float})
    # Se não houver return explícito, retorna None
    return None

# Exemplo de uso (para testes):
if __name__ == "__main__":
    define_class("""
class Pessoa:
    nome
    idade

    init(nome, idade):
        self.nome = nome
        self.idade = idade

    saudacao():
        print("Olá, eu sou " + self.nome)
""")
    obj_id = instantiate("Pessoa", "João", 30)
    call_method(obj_id, "saudacao")