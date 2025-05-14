import importlib.util
import os
import cv2
import re
import obj

variables = {}

# Dicionário de comandos
commands = {}

def cmd_syra_vd(args):
    try:
        cam_index = int(args.strip("()").strip())
    except ValueError:
        cam_index = 0
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Não foi possível abrir a webcam.")
        return
    print("Pressione 'q' para sair.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar o vídeo.")
            break
        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

commands["syra.vd"] = cmd_syra_vd

def cmd_shw(args):
    # Remove apenas o par de parênteses mais externo, não todos
    arg = args.strip()
    if arg.startswith("(") and arg.endswith(")"):
        arg = arg[1:-1].strip()
    try:
        # Avalia a expressão
        value = safe_eval(arg)
        print(value)
    except Exception as e:
        print(f"Erro ao avaliar expressão '{arg}': {e}")

commands["shw"] = cmd_shw

def load_external_commands(module_path):
    spec = importlib.util.spec_from_file_location("func", module_path)
    func_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(func_module)
    for attr in dir(func_module):
        if attr.startswith("cmd_"):
            cmd_name = attr[4:]
            commands[cmd_name] = getattr(func_module, attr)

def execute_line(line):
    line = line.strip()
    if not line:
        return
    # Bloco de classe
    if line.startswith("class "):
        class_block = [line]
        while True:
            try:
                next_line = input("... ")
                if not next_line.strip():
                    break
                class_block.append(next_line)
            except EOFError:
                break
        cmd_class("\n".join(class_block))
        return
    # Instanciação OO
    if re.match(r"\$\w+\s*=\s*\w+\(.*\)", line):
        cmd_new(line)
        return
    # Chamada de método OO
    if re.match(r"\$\w+\.\w+\(.*\)", line):
        cmd_call(line)
        return
    # Executa comandos (prioritário!)
    for cmd in commands:
        if line.startswith(cmd + "(") and line.endswith(")"):
            args = line[len(cmd):].strip()
            commands[cmd](args)
            return
        elif line.startswith(cmd + " "):
            args = line[len(cmd):].strip()
            commands[cmd](args)
            return
        elif line == cmd:
            commands[cmd]("")
            return
    # Chamada de método estático (só se não for comando Syra)
    if re.match(r"\w+\.\w+\(.*\)", line):
        cmd_static(line)
        return
    # Variáveis e comandos normais
    if line.startswith("$"):
        execute_dollar_declaration(line)
        return
    print(f"Comando desconhecido: {line}")

# execute_dollar_declaration
def execute_dollar_declaration(line):
    line = line.strip()
    if line.startswith("$"):
        var_part, expr = line[1:].split("=", 1)
        var = "$" + var_part.strip() if not var_part.strip().startswith("$") else var_part.strip()
        expr = expr.strip()
        if expr == "[]":
            variables[var] = []
        elif (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            variables[var] = expr[1:-1]
        elif expr.isdigit():
            variables[var] = int(expr)
        elif re.match(r"\w+\.\w+\(.*\)", expr):
            m = re.match(r"(\w+)\.(\w+)\((.*)\)", expr)
            if m:
                class_name, method, params = m.groups()
                param_list = [safe_eval(p.strip()) for p in params.split(",")] if params.strip() else []
                variables[var] = obj.static_call(class_name, method, *param_list)
        else:
            variables[var] = safe_eval(expr)  # <-- aqui!
        return True
    return False

def safe_eval(expr):
    expr = expr.strip()
    if expr.startswith("$"):
        # Retorna o valor da variável ou o próprio nome se não existir
        return variables.get(expr, expr)
    # Suporte a chamada estática: Matematica.quadrado(5)
    m = re.match(r"(\w+)\.(\w+)\((.*)\)", expr)
    if m:
        class_name, method, params = m.groups()
        param_list = [safe_eval(p.strip()) for p in params.split(",")] if params.strip() else []
        return obj.static_call(class_name, method, *param_list)
    try:
        # Avalia expressões simples (números, strings, etc.)
        return eval(expr, {"__builtins__": {}, "str": str, "int": int, "float": float}, variables)
    except Exception:
        # Retorna a expressão literal se não puder ser avaliada
        return expr

def parse_match_cases(lines):
    cases = []
    for line in lines:
        line = line.strip()
        if not line or not line.lower().startswith("case "):
            continue
        m = re.match(r"case\s+(.+?)\s*=>\s*(.+)", line, re.IGNORECASE)
        if not m:
            continue
        pattern, result = m.groups()
        cases.append((pattern.strip(), result.strip()))
    return cases

def eval_match_pattern(value, pattern):
    pattern = pattern.strip()
    if pattern == "_":
        return True
    m = re.match(r"(\d+)\.\.(\d+)", pattern)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
        try:
            return start <= int(value) <= end
        except Exception:
            return False
    try:
        return int(pattern) == int(value)
    except Exception:
        return str(value) == pattern

# cmd_match
def cmd_match(args):
    m = re.match(r"(\$?\w+)\s*=\s*match\s+([^\:]+)\s*:(.*)", args, re.DOTALL | re.IGNORECASE)
    if not m:
        print("Erro de sintaxe em match.")
        return
    var_name, value_expr, rest = m.groups()
    value = safe_eval(value_expr.strip())
    case_lines = rest.strip().splitlines()
    cases = parse_match_cases(case_lines)
    result = None
    for pattern, expr in cases:
        if eval_match_pattern(value, pattern):
            expr = expr.strip()
            if expr.startswith(("\"", "'")) and expr.endswith(("\"", "'")):
                result = expr[1:-1]
            elif expr.startswith("print("):
                eval(expr, {"__builtins__": {}, "print": print}, variables)
            else:
                result = safe_eval(expr)
            break
    if result is not None:
        variables["$" + var_name.strip().lstrip("$")] = result  # <-- aqui!
    else:
        print(f"Nenhum padrão correspondeu ao valor '{value}' em match.")

commands["match"] = cmd_match

def cmd_each(args):
    header, *block_lines = args.split('\n')
    header = header.strip()
    block = [line for line in block_lines if line.strip()]
    if not header.endswith(":") or not block:
        print("Erro de sintaxe em each.")
        return

    header = header[:-1].strip()
    m = re.match(r"each\s+(\([^)]+\)|\$\w+)\s+in\s+(.+)", header)
    if not m:
        print("Erro de sintaxe em each.")
        return
    var_part, iterable_expr = m.groups()
    iterable_expr = iterable_expr.strip()

    range_match = re.match(r"(\d+)\.\.(\d+)", iterable_expr)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        iterable = range(start, end + 1)
    else:
        if iterable_expr.startswith("$"):
            iterable = variables.get(iterable_expr, [])
        else:
            iterable = safe_eval(iterable_expr)
        if not hasattr(iterable, "__iter__"):
            print(f"'{iterable_expr}' não é iterável.")
            return

    if var_part.startswith("(") and var_part.endswith(")"):
        var_names = [v.strip() for v in var_part[1:-1].split(",")]
        use_index = True
    else:
        var_names = [var_part.strip()]
        use_index = False

    for idx, item in enumerate(iterable):
        local_vars = {}
        if use_index:
            if len(var_names) == 2:
                local_vars[var_names[0].lstrip("$")] = idx
                local_vars[var_names[1].lstrip("$")] = item
            else:
                print("Erro: use ($i, $item) para índice e valor.")
                return
        else:
            local_vars[var_names[0].lstrip("$")] = item

        old_vars = {k: variables.get(k) for k in local_vars}
        variables.update(local_vars)
        for code_line in block:
            execute_line(code_line)
        for k in local_vars:
            if old_vars[k] is not None:
                variables[k] = old_vars[k]
            else:
                variables.pop(k, None)

commands["each"] = cmd_each

def cmd_class(args):
    # Recebe bloco de classe como string
    obj.define_class(args)
commands["class"] = cmd_class

def cmd_new(args):
    # Exemplo: $p = Pessoa("João", 30)
    m = re.match(r"(\$\w+)\s*=\s*(\w+)\((.*)\)", args)
    if not m:
        print("Sintaxe: $var = Classe(arg1, arg2)")
        return
    var, class_name, params = m.groups()
    param_list = [safe_eval(p.strip()) for p in params.split(",")] if params.strip() else []
    obj_id = obj.instantiate(class_name, *param_list)
    if obj_id:
        variables[var] = obj_id
commands["new"] = cmd_new

def cmd_call(args):
    # Exemplo: $p.saudacao()
    m = re.match(r"(\$\w+)\.(\w+)\((.*)\)", args)
    if not m:
        print("Sintaxe: $obj.metodo(arg1, ...)")
        return
    var, method, params = m.groups()
    obj_id = variables.get(var)
    if not obj_id:
        print(f"Objeto '{var}' não encontrado.")
        return
    param_list = [safe_eval(p.strip()) for p in params.split(",")] if params.strip() else []
    obj.call_method(obj_id, method, *param_list)
commands["call"] = cmd_call

def cmd_static(args):
    # Exemplo: Matematica.quadrado(5)
    m = re.match(r"(\w+)\.(\w+)\((.*)\)", args)
    if not m:
        print("Sintaxe: Classe.metodo(arg1, ...)")
        return
    class_name, method, params = m.groups()
    param_list = [safe_eval(p.strip()) for p in params.split(",")] if params.strip() else []
    obj.static_call(class_name, method, *param_list)
commands["static"] = cmd_static

def run_syra_file(filename):
    with open(filename, "r") as f:
        lines = list(f)
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            i += 1
            continue
        # Detecta início de bloco class
        if line.startswith("class "):
            class_block = [lines[i].rstrip('\n')]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Considera parte do bloco se for indentado (espaço ou tab no início)
                if next_line.startswith(" ") or next_line.startswith("\t"):
                    class_block.append(next_line.rstrip('\n'))
                    i += 1
                elif not next_line.strip():
                    i += 1  # pula linha em branco dentro do bloco
                else:
                    break
            cmd_class("\n".join(class_block))
        # Detecta início de bloco match
        elif re.match(r"(\$?\w+)\s*=\s*match\s+([^\:]+)\s*:", line):
            match_block = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip().startswith("case ") or not next_line.strip():
                    match_block.append(next_line.rstrip("\n"))
                    i += 1
                else:
                    break
            cmd_match("\n".join(match_block))
        # Detecta início de bloco each
        elif re.match(r"each\s+(\([^)]+\)|\$\w+)\s+in\s+.+:", line):
            each_block = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Considera parte do bloco se for indentado (espaço ou tab no início)
                if next_line.startswith(" ") or next_line.startswith("\t"):
                    each_block.append(next_line.rstrip("\n"))
                    i += 1
                elif not next_line.strip():
                    i += 1  # pula linha em branco dentro do bloco
                else:
                    break
            cmd_each("\n".join(each_block))
        else:
            execute_line(line)
            i += 1

def run_syra_code(code):
    lines = code.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("//"):
            i += 1
            continue
        if re.match(r"(\$?\w+)\s*=\s*match\s+([^\:]+)\s*:", line):
            match_block = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip().startswith("case ") or not next_line.strip():
                    match_block.append(next_line.rstrip("\n"))
                    i += 1
                else:
                    break
            cmd_match("\n".join(match_block))
        elif re.match(r"each\s+(\([^)]+\)|\$\w+)\s+in\s+.+:", line):
            each_block = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith(" ") or next_line.startswith("\t"):
                    each_block.append(next_line.rstrip("\n"))
                    i += 1
                elif not next_line.strip():
                    i += 1
                else:
                    break
            cmd_each("\n".join(each_block))
        else:
            execute_line(line)
            i += 1
