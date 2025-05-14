import importlib.util
import os
import cv2
import re
import obj
import imp  # Adicionar esta importação
import deff as syra_def

variables = {}
syra_modules = {}  # Armazenar módulos Syra importados

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
    arg = args.strip()
    if arg.startswith("(") and arg.endswith(")"):
        arg = arg[1:-1].strip()
    
    # Verifica se é uma chamada de método $obj.method()
    if re.match(r"\$\w+\.\w+\(.*\)", arg):
        result = cmd_call(arg)
        print(result)
        return
        
    try:
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

def cmd_expor(args):
    """Processa comando 'expor module_name'"""
    args = args.strip()
    # Verifica se tem 'as' para alias
    if " as " in args:
        module_name, alias = args.split(" as ")
        imp.syra_expor(module_name.strip(), variables, alias=alias.strip())
    else:
        # Carrega módulo Syra ou Python
        module_name = args.strip()
        if os.path.exists(f"{module_name}.syra"):
            # É um módulo Syra
            load_syra_module(module_name)
        else:
            # Tenta como módulo Python
            imp.syra_expor(module_name, variables)

commands["expor"] = cmd_expor

def cmd_from_expor(args):
    """Processa comando 'from module_name expor name [as alias]'"""
    if " expor " not in args:
        print("Sintaxe: from module_name expor name1, name2, ... [as alias1, alias2, ...]")
        return
    
    module_part, names_part = args.split(" expor ", 1)
    module_name = module_part.strip()
    
    # Verifica se existe 'as' para aliases
    names = []
    aliases = []
    
    if " as " in names_part:
        name_section, alias_section = names_part.split(" as ", 1)
        names = [n.strip() for n in name_section.split(",")]
        aliases = [a.strip() for a in alias_section.split(",")]
    else:
        names = [n.strip() for n in names_part.split(",")]
    
    if os.path.exists(f"{module_name}.syra"):
        # Módulo Syra
        load_syra_module(module_name, names, aliases)
    else:
        # Módulo Python
        imp.syra_expor(module_name, variables, names=names, aliases=aliases)

commands["from"] = cmd_from_expor

def load_syra_module(module_name, names=None, aliases=None):
    """Carrega um módulo Syra (.syra)"""
    global variables
    
    if module_name in syra_modules:
        module_vars = syra_modules[module_name]
    else:
        # Executa o módulo Syra em um escopo isolado
        module_vars = {}
        old_vars = variables.copy()
        old_classes = obj.syra_classes.copy()
        
        variables = module_vars
        
        try:
            run_syra_file(f"{module_name}.syra")
            
            # Copiar classes definidas para o módulo
            for class_name, class_def in obj.syra_classes.items():
                if class_name not in old_classes:
                    module_vars[class_name] = class_name  # Referência à classe
                    
                    # Adicionar métodos estáticos como funções no namespace do módulo
                    for method_name, method_code in class_def["methods"].items():
                        if method_code.strip().startswith("static "):
                            # Criar wrapper para o método estático
                            def method_wrapper(*args, cls=class_name, m=method_name):
                                return obj.static_call(cls, m, *args)
                            module_vars[method_name] = method_wrapper
                            
        finally:
            # Restaurar escopo global
            syra_modules[module_name] = module_vars
            variables = old_vars

    # Importa todos ou nomes específicos
    if names is None:
        variables[module_name] = module_vars
    else:
        for i, name in enumerate(names):
            alias = aliases[i] if aliases and i < len(aliases) else name
            if name in module_vars:
                variables[alias] = module_vars[name]
            elif '.' in name:
                # Tenta resolver nomes compostos como Classe.método
                parts = name.split('.')
                if parts[0] in module_vars:
                    class_name = parts[0]
                    method_name = parts[1]
                    if class_name in obj.syra_classes and method_name in obj.syra_classes[class_name]["methods"]:
                        def method_wrapper(*args, cls=class_name, m=method_name):
                            return obj.static_call(cls, m, *args)
                        variables[alias] = method_wrapper
                    else:
                        print(f"[Aviso] '{name}' não encontrado em '{module_name}'")
                else:
                    print(f"[Aviso] '{name}' não encontrado em '{module_name}'")
            else:
                print(f"[Aviso] '{name}' não encontrado em '{module_name}'")

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
    # Detecta definição de função Syra (com ou sem decorador)
    if re.match(r"(@\w+\s*)*\w+\s*\(.*\)\s+is(\s|:|->)", line):
        func_lines = [line]
        # Coleta linhas do bloco, se terminar com ':'
        if line.strip().endswith(":"):
            while True:
                next_line = input("... ")
                if not next_line or not next_line.strip():
                    break
                func_lines.append(next_line)
        syra_def.define_syra_function("\n".join(func_lines))
        return
    # Função lambda atribuída a variável
    if re.match(r"\$\w+\s*=\s*\(.*\)\s+is\s+.+", line):
        var_name, lambda_expr = line.split("=", 1)
        var_name = var_name.strip()
        lambda_obj = syra_def.define_syra_lambda(lambda_expr.strip())
        variables[var_name] = lambda_obj
        return
    # Detecta definição de função Syra
    if re.match(r"\w+\s*\(.*\)\s+is(\s|:|->)", line):
        # Bloco de função
        if line.strip().endswith(":"):
            func_block = [line]
            while True:
                try:
                    next_line = input("... ")
                    if not next_line.strip():
                        break
                    func_block.append(next_line)
                except EOFError:
                    break
            syra_def.define_syra_function("\n".join(func_block))
        else:
            # Função de expressão única
            syra_def.define_syra_function(line)
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
    # Comandos de importação
    if line.startswith("expor "):
        cmd_expor(line[6:])
        return
    if line.startswith("from ") and " expor " in line:
        cmd_from_expor(line[5:])
        return
    # Chamada de método estático (só se não for comando Syra)
    if re.match(r"\w+\.\w+\(.*\)", line):
        cmd_static(line)
        return
    # Variáveis e comandos normais
    if line.startswith("$"):
        execute_dollar_declaration(line)
        return

    # Chamada de função Syra
    m = re.match(r"(\w+)\((.*)\)", line)
    if m and m.group(1) in syra_def.syra_functions:
        func_name = m.group(1)
        params_str = m.group(2)
        
        # Transformar parâmetros
        args = []
        kwargs = {}
        
        if params_str.strip():
            param_parts = params_str.split(',')
            for part in param_parts:
                part = part.strip()
                if '=' in part:
                    key, value = part.split('=', 1)
                    kwargs[key.strip()] = safe_eval(value.strip())
                else:
                    args.append(safe_eval(part))
        
        result = syra_def.call_syra_function(func_name, *args, **kwargs)
        if result is not None:
            print(result)
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

# Em safe_eval no func.py
def safe_eval(expr):
    expr = expr.strip()

    # Priority 1: Check for a direct Syra function call (e.g., func_name(...) or $var_name(...))
    call_match = re.match(r"(\$?\w+)\s*\((.*)\)", expr)
    if call_match:
        func_name_from_call = call_match.group(1)
        params_str = call_match.group(2)
        
        func_object_to_call = None
        
        if func_name_from_call.startswith("$"): # Check if it's a Syra variable (like a stored lambda)
            if func_name_from_call in variables:
                potential_func = variables[func_name_from_call]
                if isinstance(potential_func, syra_def.SyraFunction):
                    func_object_to_call = potential_func
        elif func_name_from_call in syra_def.syra_functions: # Check globally defined Syra functions
            func_object_to_call = syra_def.syra_functions[func_name_from_call]
        
        if func_object_to_call: # If we found a SyraFunction to call
            args = []
            kwargs = {}
            if params_str.strip():
                # This is a simplified parser for args. A more robust one might be needed for complex cases.
                param_parts = params_str.split(',') 
                for part in param_parts:
                    part = part.strip()
                    if '=' in part:
                        key, value_str = part.split('=', 1)
                        kwargs[key.strip()] = safe_eval(value_str.strip()) # Recursively eval param values
                    else:
                        args.append(safe_eval(part.strip())) # Recursively eval param values
            # Use syra_def.call_syra_function, which expects the SyraFunction object directly
            return syra_def.call_syra_function(func_object_to_call, *args, **kwargs)

    # Priority 2: If it's a Syra variable (not a call, just the variable itself)
    if expr.startswith("$"):
        var_value = variables.get(expr)
        # If the variable holds an object_id for a Syra OO object
        if isinstance(var_value, str) and var_value.startswith("obj_"):
            return obj.syra_objects.get(var_value)
        return var_value # Could be a number, string, list, or even a SyraFunction object itself

    # Priority 3: Module attribute access or static class method calls
    # Example: math_utils.pi or Matematica.quadrado(5)
    # This part needs to be robust and might need integration with how modules are stored.
    # For now, let's assume static calls are handled if they look like Class.method(...)
    static_call_match = re.match(r"(\w+)\.(\w+)\((.*)\)", expr)
    if static_call_match:
        class_name, method, params_str_static = static_call_match.groups()
        # Check if class_name is a known Syra class
        if class_name in obj.syra_classes:
            param_list_static = [safe_eval(p.strip()) for p in params_str_static.split(",")] if params_str_static.strip() else []
            return obj.static_call(class_name, method, *param_list_static)
    
    # Fallback to Python's eval for simple literals or expressions not caught above
    try:
        # The environment for eval should be carefully constructed.
        # It should include Syra global variables and defined Syra functions.
        eval_globals = {"__builtins__": {}, "str": str, "int": int, "float": float}
        # Combine Syra variables and Syra function definitions for the eval context
        eval_locals = {**variables, **syra_def.syra_functions} 
        return eval(expr, eval_globals, eval_locals)
    except Exception:
        # If all evaluations fail, return the expression string itself
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
    return obj.call_method(obj_id, method, *param_list)
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
    with open(filename, "r", encoding="utf-8") as f:
        lines_from_file = f.readlines()

    i = 0
    while i < len(lines_from_file):
        # Linha original para acumular em blocos (preserva indentação e conteúdo interno)
        current_line_content_for_block = lines_from_file[i].rstrip('\n') 
        
        # Linha para lógica de decisão (if/elif/else):
        # 1. Tira espaços das pontas.
        # 2. Remove comentário inline.
        # 3. Tira espaços das pontas novamente (caso o comentário deixe espaços).
        line_for_logic = lines_from_file[i].strip()
        if "//" in line_for_logic:
            line_for_logic = line_for_logic.split("//", 1)[0].strip()
        
        if not line_for_logic: # Se a linha ficar vazia após remover comentário e espaços
            i += 1
            continue
        
        # --- Class Definition Block ---
        if line_for_logic.startswith("class "):
            class_block_lines = [current_line_content_for_block]
            # Determine base indent of the class definition line
            base_indent = len(lines_from_file[i]) - len(lines_from_file[i].lstrip())
            processed_idx = i + 1
            while processed_idx < len(lines_from_file):
                next_line_raw = lines_from_file[processed_idx]
                next_line_stripped_for_check = next_line_raw.strip()
                # Indent relative to the class def line, or empty line
                current_indent = len(next_line_raw) - len(next_line_raw.lstrip())
                if not next_line_stripped_for_check or current_indent > base_indent:
                    class_block_lines.append(next_line_raw.rstrip('\n'))
                    processed_idx += 1
                else:
                    break 
            obj.define_class("\n".join(class_block_lines))
            i = processed_idx # Atualiza o índice principal
            continue

        # --- Function Definition Block (handles decorators too) ---
        elif line_for_logic.startswith("@") or re.match(r"^\w+\s*\(.*\)\s+is(\s|:|->)", line_for_logic):
            func_def_block_lines = [current_line_content_for_block]
            
            header_line_raw_for_indent_check = current_line_content_for_block
            idx_after_decorators = i

            # Consome linhas de decoradores
            if line_for_logic.startswith("@"):
                temp_idx = i + 1
                while temp_idx < len(lines_from_file):
                    next_line_check = lines_from_file[temp_idx].strip()
                    if "//" in next_line_check: # Limpa para verificação
                        next_line_check = next_line_check.split("//",1)[0].strip()
                    
                    if next_line_check.startswith("@"):
                        func_def_block_lines.append(lines_from_file[temp_idx].rstrip('\n'))
                        temp_idx +=1
                    elif re.match(r"^\w+\s*\(.*\)\s+is(\s|:|->)", next_line_check): # Achou o header da função
                        func_def_block_lines.append(lines_from_file[temp_idx].rstrip('\n'))
                        header_line_raw_for_indent_check = lines_from_file[temp_idx].rstrip('\n')
                        idx_after_decorators = temp_idx
                        break
                    else: # Linha inesperada após decorador
                        break 
                idx_after_decorators = temp_idx


            base_indent_for_body = len(header_line_raw_for_indent_check) - len(header_line_raw_for_indent_check.lstrip())
            
            processed_idx = idx_after_decorators + 1
            # Verifica se o header da função (última linha em func_def_block_lines) termina com ':'
            if func_def_block_lines[-1].strip().split("//",1)[0].strip().endswith(":"):
                while processed_idx < len(lines_from_file):
                    next_body_line_raw = lines_from_file[processed_idx]
                    current_body_indent = len(next_body_line_raw) - len(next_body_line_raw.lstrip())
                    # Linha vazia ou indentada faz parte do corpo
                    if not next_body_line_raw.strip() or current_body_indent > base_indent_for_body:
                        func_def_block_lines.append(next_body_line_raw.rstrip('\n'))
                        processed_idx += 1
                    else:
                        break 
            
            syra_def.define_syra_function("\n".join(func_def_block_lines))
            i = processed_idx # Atualiza o índice principal
            continue

        # --- Lambda assignment ---
        elif re.match(r"\$\w+\s*=\s*\(.*\)\s+is\s+.+", line_for_logic):
            var_name, lambda_expr_str = line_for_logic.split("=", 1)
            var_name = var_name.strip()
            lambda_expr_str = lambda_expr_str.strip()
            try:
                lambda_obj = syra_def.define_syra_lambda(lambda_expr_str, defining_env=variables.copy())
                variables[var_name] = lambda_obj
            except Exception as e_lambda:
                print(f"Erro ao definir lambda para '{var_name}': {e_lambda}")
            i += 1
            continue
        
        # --- Match Block ---
        elif re.match(r"(\$?\w+)\s*=\s*match\s+([^\:]+)\s*:", line_for_logic):
            match_block_lines = [current_line_content_for_block]
            base_indent = len(lines_from_file[i]) - len(lines_from_file[i].lstrip())
            processed_idx = i + 1
            while processed_idx < len(lines_from_file):
                next_line_raw = lines_from_file[processed_idx]
                next_line_stripped_for_check = next_line_raw.strip().split("//",1)[0].strip()
                current_indent = len(next_line_raw) - len(next_line_raw.lstrip())
                if not next_line_stripped_for_check or next_line_stripped_for_check.lower().startswith("case ") or current_indent > base_indent:
                    match_block_lines.append(next_line_raw.rstrip('\n'))
                    processed_idx += 1
                else:
                    break
            cmd_match("\n".join(match_block_lines))
            i = processed_idx # Atualiza o índice principal
            continue
            
        # --- Each Block ---
        elif re.match(r"each\s+(\([^)]+\)|\$\w+)\s+in\s+.+:", line_for_logic):
            each_block_lines = [current_line_content_for_block]
            base_indent = len(lines_from_file[i]) - len(lines_from_file[i].lstrip())
            processed_idx = i + 1
            while processed_idx < len(lines_from_file):
                next_line_raw = lines_from_file[processed_idx]
                next_line_stripped_for_check = next_line_raw.strip().split("//",1)[0].strip()
                current_indent = len(next_line_raw) - len(next_line_raw.lstrip())
                if not next_line_stripped_for_check or current_indent > base_indent:
                    each_block_lines.append(next_line_raw.rstrip('\n'))
                    processed_idx += 1
                else:
                    break
            cmd_each("\n".join(each_block_lines))
            i = processed_idx # Atualiza o índice principal
            continue
            
        # --- Fallback to execute_line para comandos de uma linha ---
        else:
            execute_line(line_for_logic) # Passa a linha já limpa de comentários e espaços
            i += 1

def run_syra_code(code_block_str): # code_block_str pode ser uma ou múltiplas linhas
    lines = code_block_str.splitlines()
    
    # Tenta identificar se o bloco inteiro é uma definição única (classe, função, match, each)
    # Esta lógica é para quando o REPL envia um bloco coletado.
    if lines:
        first_line_cleaned = lines[0].strip()
        if "//" in first_line_cleaned:
            first_line_cleaned = first_line_cleaned.split("//", 1)[0].strip()

        if first_line_cleaned: # Procede apenas se a primeira linha limpa não for vazia
            if first_line_cleaned.startswith("class "):
                obj.define_class(code_block_str) # Passa o bloco original
                return
            elif first_line_cleaned.startswith("@") or re.match(r"^\w+\s*\(.*\)\s+is(\s|:|->)", first_line_cleaned):
                syra_def.define_syra_function(code_block_str) # Passa o bloco original
                return
            elif re.match(r"(\$?\w+)\s*=\s*match\s+([^\:]+)\s*:", first_line_cleaned):
                cmd_match(code_block_str) # Passa o bloco original
                return
            elif re.match(r"each\s+(\([^)]+\)|\$\w+)\s+in\s+.+:", first_line_cleaned):
                cmd_each(code_block_str) # Passa o bloco original
                return
    
    # Se não for um bloco único reconhecido acima, processa linha por linha
    # (útil se run_syra_code for chamado com múltiplas linhas que não formam um único bloco Syra)
    i = 0
    while i < len(lines):
        line_for_logic = lines[i].strip()
        if "//" in line_for_logic:
            line_for_logic = line_for_logic.split("//", 1)[0].strip()
        
        if not line_for_logic:
            i += 1
            continue
        
        # Definição de lambda em uma linha (não precisa de tratamento de bloco especial aqui)
        if re.match(r"\$\w+\s*=\s*\(.*\)\s+is\s+.+", line_for_logic):
            var_name, lambda_expr_str = line_for_logic.split("=", 1)
            var_name = var_name.strip()
            lambda_expr_str = lambda_expr_str.strip()
            try:
                lambda_obj = syra_def.define_syra_lambda(lambda_expr_str, defining_env=variables.copy())
                variables[var_name] = lambda_obj
            except Exception as e_lambda:
                print(f"Erro ao definir lambda para '{var_name}': {e_lambda}")
        else:
            execute_line(line_for_logic) # Passa a linha limpa
        i += 1
