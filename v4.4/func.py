import importlib.util
import os
import cv2
import re
import obj
import imp  # Adicionar esta importação
import deff as syra_def
import tps as syra_types
import tps  # Importa o arquivo tps.py

variables = {}
syra_modules = {}  # Armazenar módulos Syra importados
commands = {}
# Inicializa o sistema de tipos e registra os comandos
tps.initialize_types()
tps.register_type_commands(commands)

# No início da execução:
syra_types.initialize_types()
syra_types.register_type_commands(commands)
tps.register_type_commands(commands)

def initialize():
    # ... código existente ...
    syra_types.initialize_types()
    syra_types.register_type_commands(commands)

initialize()

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
        
    value = safe_eval(arg)
    print(value)

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

def process_ampersand_command(line):
    """Process commands that start with '&' like &Syope, &Sywr, etc."""
    m = re.match(r"&(\w+)\s*\((.*)\)", line)
    if not m:
        return False
    
    cmd_name = m.group(1)
    args_str = m.group(2)
    
    cmd_key = f"&{cmd_name}"
    if cmd_key in commands:
        result = commands[cmd_key](args_str)
        return True
    
    cmd_key_lower = f"&{cmd_name.lower()}"
    if cmd_key_lower in commands:
        result = commands[cmd_key_lower](args_str)
        return True
        
    print(f"Comando desconhecido: {line}")
    return True

def execute_line(line):
    line = line.strip()
    if not line:
        return
        
    # Novo handler para comandos com &
    if line.startswith("&"):
        if process_ampersand_command(line):
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
        parts = line.split("=", 1)
        if len(parts) < 2:
            print(f"Erro de sintaxe na atribuição: {line}")
            return False
            
        var_name = parts[0].strip()
        expr_str = parts[1].strip()
        
        # Trata comandos com & de forma especial
        command_call_match = re.match(r"&(\w+)\s*\((.*)\)", expr_str)
        if command_call_match:
            command_name = command_call_match.group(1)
            command_args = command_call_match.group(2)
            cmd_key = f"&{command_name}"
            
            if cmd_key in commands:
                variables[var_name] = commands[cmd_key](command_args)
                return True
                
            cmd_key_lower = f"&{command_name.lower()}"
            if cmd_key_lower in commands:
                variables[var_name] = commands[cmd_key_lower](command_args)
                return True
        
        # Se não for um comando com &, avalie normalmente
        variables[var_name] = safe_eval(expr_str)
        return True
    return False

# Em safe_eval no func.py
def safe_eval(expr):
    expr = expr.strip()

    # Special handling for &run ... orv ... expressions
    # This part should be robust. If `operacao()` is not defined, safe_eval(operacao()) will raise an error.
    run_orv_match = re.match(r"&run\s+(.*?)\s+orv\s+(.*)", expr, re.IGNORECASE)
    if run_orv_match:
        try_expr = run_orv_match.group(1).strip()
        fallback_expr = run_orv_match.group(2).strip()
        try:
            return safe_eval(try_expr)  # Evaluate the expression to try
        except Exception:
            return safe_eval(fallback_expr) # Evaluate the fallback expression

    # Handle other & commands like &Syope(args), &Syread(args)
    # This assumes commands like &Syope return a value that safe_eval should return.
    command_match = re.match(r"&(\w+)\s*\((.*)\)", expr)
    if command_match:
        cmd_name = command_match.group(1)
        cmd_args = command_match.group(2).strip() # Arguments string
        
        # Check for registered command (case-sensitive and then case-insensitive for the key)
        cmd_key_exact = f"&{cmd_name}"
        cmd_key_lower = f"&{cmd_name.lower()}" # Assuming commands might be registered lowercase

        if cmd_key_exact in commands:
            return commands[cmd_key_exact](cmd_args)
        elif cmd_key_lower in commands:
            return commands[cmd_key_lower](cmd_args)
        # If command not found but matched pattern, it could be an error or unhandled case
        # For now, let it fall through, but ideally, this might raise an "unknown &command" error.

    # Substitute Syra variables ($nome) with their Python literal representations
    def syra_var_replacer(match):
        var_syra_name = match.group(0) # e.g., $e
        if var_syra_name in variables: # `variables` is your global Syra variables dictionary
            val = variables[var_syra_name]
            if isinstance(val, str):
                # Create a valid Python string literal, correctly escaping internal quotes
                return '"' + val.replace('\\', '\\\\').replace('"', '\\"') + '"'
            elif isinstance(val, bool):
                return str(val) # "True" or "False"
            elif isinstance(val, (int, float)):
                return str(val) # Numbers as strings
            elif val is None:
                return "None"
            else:
                # For other types (lists, dicts), converting to string might not be directly evaluatable
                # in a simple Python expression unless they are already in Python literal format.
                # For this specific case ("Erro: " + $e), $e is a string.
                return str(val) # Fallback, might need refinement for complex types
        else:
            # This should ideally raise a Syra-specific runtime error
            raise NameError(f"Variável Syra '{var_syra_name}' não definida.")

    # Apply the replacer to the expression string
    # This will turn ' "Erro: " + $e ' into ' "Erro: " + "division by zero" '
    expr_after_syra_vars = re.sub(r"\$\w+", syra_var_replacer, expr)

    # Python eval for the final expression string
    try:
        # The expression is now a Python-compatible string, e.g., '"Erro: " + "division by zero"'
        # or a simple literal like '"falha"' or a number like '123'
        
        safe_globals = {
            "__builtins__": {
                "True": True, "False": False, "None": None,
                "int": int, "float": float, "str": str, "len": len
                # Add any other Python built-ins you want to expose safely
            }
        }
        
        # The `locals` for eval. Since Syra variables are substituted into the expression string
        # as literals, we don't need to pass Syra's `variables` dict here for $var resolution.
        # Passing an empty dict or a controlled context is safer.
        python_eval_locals = {} 

        # eval() will compute '"Erro: " + "division by zero"' to the string "Erro: division by zero"
        # eval('"falha"') will result in the string "falha"
        # eval('1/0') will raise ZeroDivisionError
        return eval(expr_after_syra_vars, safe_globals, python_eval_locals)
        
    except Exception as e:
        # Propagate the exception (e.g., ZeroDivisionError from '1/0', or NameError if 'operacao()' is undefined)
        # This allows &attempt/&rescue and &run/orv to catch it.
        raise e

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
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            i += 1
            continue
            
        # Check for attempt/rescue blocks
        if line.lower().startswith('&attempt:'):
            # Collect the block
            attempt_block = []
            attempt_block.append(lines[i])  # Add &attempt: line
            
            i += 1  # Move to next line
            # Collect attempt body until &rescue or end of indented block
            while i < len(lines):
                current = lines[i].strip()
                if current.lower().startswith('&rescue'):
                    break
                if not current:  # Empty line
                    i += 1
                    continue
                attempt_block.append(lines[i])
                i += 1
                
            # Now collect the rescue part
            if i < len(lines) and lines[i].strip().lower().startswith('&rescue'):
                attempt_block.append(lines[i])  # Add &rescue line
                i += 1
                # Collect rescue body
                while i < len(lines):
                    if not lines[i].strip():  # Empty line
                        i += 1
                        continue
                    # Check if we're still in the indented block
                    indentation = len(lines[i]) - len(lines[i].lstrip())
                    if indentation == 0 and lines[i].strip():
                        break  # No longer in the rescue block
                    attempt_block.append(lines[i])
                    i += 1
            
            # Process the entire block
            tps.cmd_attempt_block(attempt_block)
        else:
            # Process normal line
            execute_line(line)
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
