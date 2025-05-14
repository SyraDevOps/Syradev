import re
import uuid

syra_functions = {}  # Armazenamento global para funções Syra definidas

class SyraExecutionError(Exception):
    """Exceção customizada para erros durante a execução de funções Syra."""
    pass

def parse_single_parameter(param_str):
    """
    Analisa uma string de parâmetro individual.
    Exemplos: 'x', 'x:int', 'x = 10', 'x:int = 10', '*args', '*args:list'
    Retorna um dicionário com name, type_hint, default_value_str, is_vararg.
    (is_keyword_only é definido em parse_parameters_string)
    """
    param_str = param_str.strip()
    
    is_vararg = False
    if param_str.startswith('*'):
        is_vararg = True
        param_str = param_str[1:].strip() # Remove o '*' inicial para pegar o nome

    name_part = param_str
    type_hint = None
    default_value_str = None

    if '=' in param_str:
        parts = param_str.split('=', 1)
        name_part = parts[0].strip()
        default_value_str = parts[1].strip()

    if ':' in name_part:
        parts = name_part.split(':', 1)
        name = parts[0].strip()
        type_hint = parts[1].strip()
    else:
        name = name_part.strip()

    if not name and is_vararg: # Caso de `*` sozinho, que não é um vararg nomeado
        raise SyntaxError("Nome de parâmetro variádico ausente após '*'. Para keyword-only marker, use '*' sozinho entre vírgulas.")
    if name and not re.match(r"^\w+$", name):
        raise SyntaxError(f"Nome de parâmetro inválido: '{name}'")
    
    return {
        'name': name,
        'type_hint': type_hint,
        'default_value_str': default_value_str,
        'is_vararg': is_vararg,
        'is_keyword_only': False # Será definido por parse_parameters_string
    }

def parse_parameters_string(params_str):
    """Analisa a string de parâmetros completa (ex: "x, y:int=0, *, z=1, *args")."""
    if not params_str.strip():
        return []
    
    param_parts = params_str.split(',')
    
    parsed_params = []
    has_vararg_been_seen = False # Tracks if *args has been encountered
    keyword_only_marker_found = False

    for part_str in param_parts:
        part_str = part_str.strip()
        if not part_str:
            continue

        if part_str == '*':
            if has_vararg_been_seen:
                raise SyntaxError("Marcador de keyword-only '*' não pode aparecer após um parâmetro variádico (*args).")
            if keyword_only_marker_found:
                raise SyntaxError("Múltiplos marcadores de keyword-only '*' não são permitidos.")
            keyword_only_marker_found = True
            continue # Don't add the marker itself to parsed_params
        
        p_info = parse_single_parameter(part_str)
        
        if p_info['is_vararg']:
            if has_vararg_been_seen:
                raise SyntaxError("Múltiplos parâmetros variádicos (*args) não são permitidos.")
            # A vararg parameter cannot be keyword-only in the same way other params are.
            # It also cannot appear after the keyword-only marker '*'.
            if keyword_only_marker_found:
                raise SyntaxError("Parâmetro variádico (*args) não pode seguir o marcador keyword-only '*'.")
            has_vararg_been_seen = True
        else: # Not a vararg parameter
            if keyword_only_marker_found: # Parameter is after '*'
                p_info['is_keyword_only'] = True
            elif has_vararg_been_seen: # Parameter is after *args (and not *args itself)
                p_info['is_keyword_only'] = True
        
        parsed_params.append(p_info)
    
    return parsed_params

def parse_syra_function_header(header_line):
    """
    Analisa a linha de cabeçalho da função Syra.
    Retorna: func_name, parsed_params_list, expr_body_candidate, return_type_hint
    """
    # Regex para capturar: nome_funcao ( parametros ) is [-> tipo_retorno] [: ou expressao]
    m = re.match(r"(\w+)\s*\((.*?)\)\s+is\s*(?:->\s*([\w.]+)\s*)?(?::)?\s*(.*)", header_line)
    if not m:
        raise SyntaxError(f"Sintaxe de definição de função Syra inválida no cabeçalho: '{header_line}'")
    
    func_name, params_str, return_type_hint, expr_body_candidate = m.groups()
    
    parsed_params = parse_parameters_string(params_str)
    
    return func_name, parsed_params, expr_body_candidate.strip(), return_type_hint.strip() if return_type_hint else None

def syra_env(base_vars=None):
    """Cria um ambiente de execução seguro e controlado para código Syra."""
    env = {
        "str": str, "int": int, "float": float, "len": len, "print": print,
        "True": True, "False": False, "None": None,
    }
    if base_vars:
        env.update(base_vars)
    
    for fname, func_obj in syra_functions.items():
        if fname not in env:
            env[fname] = func_obj
            
    return env

# Helper function for Syra-aware evaluation, especially for 'retornar'
def _syra_eval_for_return(expr_str, environment):
    expr_str = expr_str.strip()
    
    # Check if the expression string itself IS a Syra lambda definition string
    if expr_str.startswith("(") and ") is " in expr_str:
        try:
            # Attempt to define it as a Syra lambda.
            # define_syra_lambda should return a SyraFunction or raise an error.
            syra_lambda_func = define_syra_lambda(expr_str, defining_env=environment)
            # It's crucial that define_syra_lambda itself is robust and returns SyraFunction
            # or raises a specific error if it can't.
            return syra_lambda_func 
        except SyntaxError as e_lambda_syn:
            # This will catch syntax errors from define_syra_lambda's parsing
            raise SyraExecutionError(f"Erro de sintaxe na definição da lambda de retorno '{expr_str}': {e_lambda_syn}")
        except Exception as e_lambda_other: 
            # This will catch other errors from define_syra_lambda
            raise SyraExecutionError(f"Erro inesperado ao definir lambda de retorno '{expr_str}': {e_lambda_other}")
    else: # Not a Syra lambda string, try Python eval for other expressions
        try:
            # This eval is for Python expressions or Syra variables that resolve to Python types
            return eval(expr_str, environment)
        except NameError as e_name:
            # Check if it's a variable name present in the environment
            if expr_str in environment: # This handles cases where expr_str is just a variable name
                return environment[expr_str]
            # Otherwise, it's a genuine NameError within the Python eval context
            raise SyraExecutionError(f"Nome não definido ao avaliar expressão de retorno Python '{expr_str}': {e_name}")
        except SyntaxError as e_syn_py:
            # Python eval found a syntax error (e.g., if a non-lambda Syra construct was passed)
            raise SyraExecutionError(f"Erro de sintaxe Python ao avaliar expressão de retorno '{expr_str}': {e_syn_py}")
        except Exception as e_eval_other:
            # Other errors during Python eval
            raise SyraExecutionError(f"Erro Python ao avaliar expressão de retorno '{expr_str}': {e_eval_other}")

class SyraFunction:
    def __init__(self, name, params_info_list, body_lines, is_expr_body, docstring=None, return_type_hint=None, closure_env=None):
        self.name = name
        self.params_info = params_info_list
        self.body_lines = body_lines
        self.is_expr_body = is_expr_body
        self.docstring = docstring
        self.return_type_hint = return_type_hint
        self.closure_env = closure_env

        self.param_names = [p['name'] for p in self.params_info if p['name']] # Exclui o '*' anônimo
        self.vararg_param_name = next((p['name'] for p in self.params_info if p['is_vararg']), None)

    def __call__(self, *args, **kwargs):
        local_vars = {}
        args_iter = iter(args)
        
        # 1. Mapear argumentos posicionais
        for p_info in self.params_info:
            if p_info['is_vararg']:
                local_vars[p_info['name']] = tuple(args_iter)
                break 
            if p_info['is_keyword_only']: 
                break
            try:
                val = next(args_iter)
                if p_info['name'] in kwargs:
                    raise SyraExecutionError(
                        f"Função '{self.name}' recebeu múltiplos valores para o argumento '{p_info['name']}'"
                    )
                local_vars[p_info['name']] = val
            except StopIteration:
                pass 
        
        remaining_pos_args = list(args_iter)
        if remaining_pos_args:
            if not self.vararg_param_name:
                 raise SyraExecutionError(
                    f"Função '{self.name}' esperava menos argumentos posicionais, mas recebeu {len(args)}"
                )

        # 2. Mapear argumentos nomeados (keywords)
        for kw_name, kw_val in kwargs.items():
            if kw_name not in self.param_names:
                raise SyraExecutionError(
                    f"Função '{self.name}' recebeu um argumento nomeado inesperado '{kw_name}'"
                )
            if kw_name in local_vars and local_vars[kw_name] is not kwargs[kw_name]: 
                 raise SyraExecutionError(
                    f"Função '{self.name}' recebeu múltiplos valores para o argumento '{kw_name}'"
                )
            local_vars[kw_name] = kw_val

        # 3. Aplicar valores padrão e verificar argumentos obrigatórios ausentes
        env_for_defaults = syra_env(self.closure_env if hasattr(self, 'closure_env') else None) 

        for p_info in self.params_info:
            if p_info['is_vararg']:
                if p_info['name'] not in local_vars:
                     local_vars[p_info['name']] = tuple()
                continue

            if p_info['name'] not in local_vars:
                if p_info['default_value_str'] is not None:
                    try:
                        default_val = eval(p_info['default_value_str'], env_for_defaults)
                        local_vars[p_info['name']] = default_val
                    except Exception as e_def:
                        raise SyraExecutionError(
                            f"Erro ao avaliar valor padrão para '{p_info['name']}' na função '{self.name}': {e_def}"
                        )
                elif not p_info['is_keyword_only'] or (p_info['is_keyword_only'] and p_info['name'] in kwargs):
                     raise SyraExecutionError(
                        f"Função '{self.name}' não recebeu o argumento obrigatório: '{p_info['name']}'"
                    )
        
        # Build execution environment, incorporating closure if it exists
        current_closure = self.closure_env if hasattr(self, 'closure_env') and self.closure_env else {}
        effective_env_vars = {**current_closure, **local_vars}
        exec_env = syra_env(effective_env_vars)

        try:
            if self.is_expr_body:
                return _syra_eval_for_return(self.body_lines[0], exec_env)
            else: 
                result = None 
                for line_content in self.body_lines:
                    stripped_line = line_content.strip()
                    if not stripped_line or stripped_line.startswith("//"):
                        continue
                    
                    if stripped_line.startswith("return "): # Changed from "retornar "
                        expr_to_return = stripped_line[len("return "):].strip() # Changed from "retornar "
                        result = _syra_eval_for_return(expr_to_return, exec_env)
                        return result 
                    else:
                        exec(stripped_line, exec_env) 
                return result
        except Exception as e_exec:
            error_message = f"Erro durante a execução da função Syra '{self.name}': {type(e_exec).__name__}: {e_exec}"
            raise SyraExecutionError(error_message)

    def __repr__(self):
        params_repr = []
        kw_only_marker_added = False
        for i, p in enumerate(self.params_info):
            if p['is_keyword_only'] and not kw_only_marker_added and not (i > 0 and self.params_info[i-1]['is_vararg']):
                if params_repr: params_repr.append('*')
                kw_only_marker_added = True
            
            s = "*" if p['is_vararg'] else ""
            s += p['name']
            if p['type_hint']: s += f":{p['type_hint']}"
            if p['default_value_str']: s += f"={p['default_value_str']}"
            params_repr.append(s)
        
        ret_hint_repr = f" -> {self.return_type_hint}" if self.return_type_hint else ""
        return f"<SyraFunction {self.name}({', '.join(params_repr)}){ret_hint_repr}>"

def define_syra_function(code_block_str):
    # As linhas já vêm com rstrip('\n') de run_syra_file, mas splitlines() é seguro.
    all_lines_from_block = code_block_str.splitlines() 

    decorator_names = []
    header_line_of_func_raw = None # Linha original do cabeçalho da função
    source_body_lines_for_func = [] # Linhas originais do corpo
    
    line_idx = 0

    # 1. Consumir linhas de decoradores
    while line_idx < len(all_lines_from_block):
        current_line_raw = all_lines_from_block[line_idx]
        current_line_cleaned_for_logic = current_line_raw.strip()
        if "//" in current_line_cleaned_for_logic:
            current_line_cleaned_for_logic = current_line_cleaned_for_logic.split("//",1)[0].strip()

        if not current_line_cleaned_for_logic: # Pular linhas completamente vazias
            line_idx += 1
            continue

        if current_line_cleaned_for_logic.startswith('@'):
            deco_name = current_line_cleaned_for_logic[1:].strip() # Nome do decorador
            # Validação simples do nome do decorador
            if not re.match(r"^\w+$", deco_name) or deco_name in ["is", "return"]: # Evitar palavras-chave
                print(f"[Syra Def] Erro: Nome de decorador inválido '{deco_name}'.")
                return
            decorator_names.append(deco_name)
            line_idx += 1
        else:
            # Não é um decorador, deve ser o cabeçalho da função ou o início do corpo (se não houver cabeçalho aqui)
            break 
            
    # 2. Encontrar o cabeçalho da função
    if line_idx < len(all_lines_from_block):
        # A linha atual (all_lines_from_block[line_idx]) é a candidata a cabeçalho
        header_candidate_raw = all_lines_from_block[line_idx]
        header_candidate_cleaned_for_logic = header_candidate_raw.strip()
        if "//" in header_candidate_cleaned_for_logic:
             header_candidate_cleaned_for_logic = header_candidate_cleaned_for_logic.split("//",1)[0].strip()
        
        # Verifica se é um cabeçalho de função válido
        if re.match(r"^\w+\s*\(.*\)\s+is(\s|:|->)", header_candidate_cleaned_for_logic):
            header_line_of_func_raw = header_candidate_raw 
            line_idx += 1 # Avança para o corpo
        else:
            # Se tínhamos decoradores, mas a linha seguinte não é um cabeçalho de função
            if decorator_names:
                print(f"[Syra Def] Aviso: Nenhuma linha de definição de função válida encontrada após decorador(es). Linha encontrada: '{header_candidate_cleaned_for_logic[:50]}...'")
            else:
                # Se não havia decoradores e a primeira linha significativa não é um cabeçalho
                print(f"[Syra Def] Erro: Bloco de código não inicia com uma definição de função válida: '{header_candidate_cleaned_for_logic[:50]}...'")
            return # Não prosseguir se não houver cabeçalho válido
    else:
        # O bloco terminou antes de encontrar um cabeçalho de função (ex: só decoradores ou bloco vazio)
        if decorator_names:
             print("[Syra Def] Aviso: Bloco de definição de função está incompleto após decorador(es).")
        else:
             print("[Syra Def] Aviso: Bloco de definição de função está vazio ou incompleto.")
        return

    # 3. O restante das linhas (se houver) é o corpo da função
    source_body_lines_for_func = all_lines_from_block[line_idx:]

    try:
        # Passar a linha de cabeçalho limpa para parse_syra_function_header
        func_name, parsed_params, expr_body_candidate, return_type_hint = \
            parse_syra_function_header(header_line_of_func_raw.strip()) # .strip() é crucial aqui
    except SyntaxError as e_syn:
        potential_func_name_for_error = header_line_of_func_raw.strip().split('(')[0].strip()
        print(f"[Syra Def] Erro de sintaxe no cabeçalho da função '{potential_func_name_for_error}': {e_syn}")
        return
    except TypeError: # Se header_line_of_func_raw for None
        print("[Syra Def] Erro interno: Cabeçalho da função não foi encontrado corretamente.")
        return


    docstring = None
    is_expr_body = False
    actual_executable_body_lines = []

    if expr_body_candidate: 
        is_expr_body = True
        actual_executable_body_lines = [expr_body_candidate]
    else: 
        is_expr_body = False
        # Processar source_body_lines_for_func para docstring e corpo executável
        # A indentação já foi validada por run_syra_file.
        # As linhas em source_body_lines_for_func são as linhas originais do corpo.
        
        first_real_code_line_idx_in_body = 0
        processed_body_lines = [] # Linhas limpas para execução

        if source_body_lines_for_func:
            # Tenta extrair docstring da primeira linha significativa do corpo
            temp_line_raw = source_body_lines_for_func[0]
            temp_line_cleaned = temp_line_raw.strip()
            if "//" in temp_line_cleaned:
                temp_line_cleaned = temp_line_cleaned.split("//",1)[0].strip()

            if temp_line_cleaned and \
               ((temp_line_cleaned.startswith('"') and temp_line_cleaned.endswith('"')) or \
                (temp_line_cleaned.startswith("'") and temp_line_cleaned.endswith("'"))):
                try:
                    docstring = eval(temp_line_cleaned, syra_env()) # syra_env() para segurança
                    first_real_code_line_idx_in_body = 1 # Próxima linha é código
                except: 
                    docstring = None # Não é uma string válida, trata como código
                    # first_real_code_line_idx_in_body permanece 0
            
            # Coleta as linhas de corpo executáveis (já indentadas corretamente por run_syra_file)
            # Para SyraFunction.__call__, as linhas do corpo devem ser passadas com sua indentação relativa
            # se exec() for usado em todo o bloco. Se cada linha for processada individualmente,
            # o strip() pode ser feito mais tarde. Por agora, vamos manter a indentação original do corpo.
            actual_executable_body_lines = [l for l in source_body_lines_for_func[first_real_code_line_idx_in_body:]]


    func_obj = SyraFunction(func_name, parsed_params, actual_executable_body_lines, 
                            is_expr_body, docstring, return_type_hint)
    
    final_func_obj = func_obj
    if decorator_names:
        for deco_name in reversed(decorator_names):
            decorator_syra_func = syra_functions.get(deco_name)
            if not decorator_syra_func or not isinstance(decorator_syra_func, SyraFunction):
                print(f"[Syra Def] Erro: Decorador Syra '{deco_name}' não encontrado ou não é uma função Syra válida.")
                return 
            try:
                final_func_obj = decorator_syra_func(final_func_obj) 
                if not isinstance(final_func_obj, SyraFunction): 
                    print(f"[Syra Def] Erro: Decorador Syra '{deco_name}' não retornou uma função Syra válida.")
                    return 
                final_func_obj.name = func_name 
            except Exception as e_deco_call:
                print(f"[Syra Def] Erro ao aplicar decorador Syra '{deco_name}' à função '{func_name}': {e_deco_call}")
                return
    
    syra_functions[func_name] = final_func_obj

def define_syra_lambda(lambda_expr_str, defining_env=None):
    lambda_expr_str = lambda_expr_str.strip()
    if lambda_expr_str.startswith("lambda "):
        lambda_expr_str = lambda_expr_str[len("lambda "):].strip()
    # Aceita *args no início dos parâmetros
    m = re.match(r"^\((.*?)\)\s+is\s+(.*)", lambda_expr_str)
    if not m:
        raise SyntaxError(f"Sintaxe de lambda Syra inválida: '{lambda_expr_str}'. Use o formato '(params) is expressao'.")
    params_str, expr_body = m.groups()
    # Aqui, parse_parameters_string já suporta *args
    parsed_params = parse_parameters_string(params_str)
    lambda_name = f"<lambda_{str(uuid.uuid4())[:8]}>"
    return SyraFunction(lambda_name, parsed_params, [expr_body.strip()], True, None, None, closure_env=defining_env)

def call_syra_function(func_name_or_obj, *args, **kwargs):
    """Chama uma função Syra definida (por nome ou objeto SyraFunction)."""
    func_to_call = None
    if isinstance(func_name_or_obj, str):
        if func_name_or_obj not in syra_functions:
            raise NameError(f"Função Syra '{func_name_or_obj}' não está definida.")
        func_to_call = syra_functions[func_name_or_obj]
    elif isinstance(func_name_or_obj, SyraFunction):
        func_to_call = func_name_or_obj
    else:
        raise TypeError("call_syra_function espera um nome de função ou um objeto SyraFunction.")

    try:
        return func_to_call(*args, **kwargs)
    except SyraExecutionError as e_syra: 
        print(f"[Chamada Syra] {e_syra}")
        return None 
    except Exception as e_py: 
        func_display_name = func_to_call.name if func_to_call else "desconhecida"
        print(f"[Chamada Syra] Erro Python inesperado ao chamar '{func_display_name}': {type(e_py).__name__}: {e_py}")
        return None

# --- Exemplos de Uso ---
if __name__ == "__main__":
    print("--- Testando Definições de Funções Syra Avançadas ---")
    syra_functions.clear()

    # 1. Teste com return type e keyword-only args
    define_syra_function("""
    config(drive, *, modo:str="normal", velocidade:int=100) is -> str:
        "Configura o drive."
        retornar "Drive " + drive + " configurado para modo " + modo + " a " + str(velocidade) + "rpm."
    """)
    print("\nConfig 1:", call_syra_function("config", "C", modo="rapido"))
    print("Config 2:", call_syra_function("config", "D", velocidade=150, modo="lento"))
    print("Config 3 (erro esperado):")
    try:
        call_syra_function("config", "E", "super", 200)
    except Exception as e:
        print(f"  {e}")

    if 'config' in syra_functions:
        print(f"  Repr de 'config': {syra_functions['config']}")

    # 2. Teste de Decoradores
    define_syra_function("""
    duplica_retorno(func_original: SyraFunction) is -> SyraFunction:
        "Decorador que duplica o retorno numérico da função original."
        print("Decorador 'duplica_retorno' aplicado a: " + func_original.name)
        retornar func_original
    """)

    define_syra_function("""
    @duplica_retorno
    soma_simples(a:int, b:int) is -> int:
        "Soma dois números."
        retornar a + b
    """)
    print("\nSoma Simples Decorada:", call_syra_function("soma_simples", 10, 5))

    # 3. Teste de Lambdas
    print("\n--- Testando Lambdas Syra ---")
    try:
        lambda_add = define_syra_lambda("(a, b=5) is a + b")
        print("Lambda Add 1:", call_syra_function(lambda_add, 10))       # 10 + 5 = 15
        print("Lambda Add 2:", call_syra_function(lambda_add, 10, 20))   # 10 + 20 = 30
        print(f"  Repr da Lambda Add: {lambda_add}")

        lambda_greet = define_syra_lambda('(nome="Mundo") is "Olá, " + nome')
        print("Lambda Greet 1:", call_syra_function(lambda_greet))
        print("Lambda Greet 2:", call_syra_function(lambda_greet, nome="Syra Lambda"))

    except SyntaxError as e_lambda_syn:
        print(f"Erro ao definir lambda: {e_lambda_syn}")
    except Exception as e_lambda_call:
        print(f"Erro ao chamar lambda: {e_lambda_call}")

    print("\n--- Fim dos Testes Avançados ---")