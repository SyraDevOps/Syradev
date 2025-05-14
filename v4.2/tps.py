import os
import subprocess
import re
import json
import glob
from decimal import Decimal, getcontext
import pandas as pd
import csv
import io

# Dicionário global para armazenar os tipos das variáveis
variable_types = {}
open_files = {}  # Rastreia arquivos abertos: {nome: objeto_arquivo}

# Lista de tipos suportados com seus validadores
SYRA_TYPES = {
    'int': lambda val: isinstance(val, int),
    'float': lambda val: isinstance(val, (float, Decimal)),
    'str': lambda val: isinstance(val, str),
    'bool': lambda val: isinstance(val, bool),
    'list': lambda val: isinstance(val, list),
    'dict': lambda val: isinstance(val, dict),
    'tuple': lambda val: isinstance(val, tuple),
    'any': lambda val: True,  # Aceita qualquer valor
}

class SyraTypeError(Exception):
    """Exceção para erros de tipos no Syra."""
    pass

def check_type(value, type_hint):
    """Verifica se um valor corresponde à anotação de tipo."""
    if type_hint is None or type_hint == 'any':
        return True  # Sem restrição de tipo
    
    if type_hint not in SYRA_TYPES:
        raise SyraTypeError(f"Tipo desconhecido: '{type_hint}'")
    
    if not SYRA_TYPES[type_hint](value):
        return False
    
    return True

def validate_param_types(func_obj, args, kwargs):
    """Valida tipos de parâmetros com base nas anotações."""
    for i, param_info in enumerate(func_obj.params_info):
        if param_info['type_hint'] and param_info['name'] in kwargs:
            value = kwargs[param_info['name']]
            if not check_type(value, param_info['type_hint']):
                raise SyraTypeError(
                    f"Argumento '{param_info['name']}' deve ser do tipo '{param_info['type_hint']}', "
                    f"mas recebeu {type(value).__name__}: {value}"
                )
        elif param_info['type_hint'] and i < len(args) and not param_info['is_vararg']:
            value = args[i]
            if not check_type(value, param_info['type_hint']):
                raise SyraTypeError(
                    f"Argumento '{param_info['name']}' deve ser do tipo '{param_info['type_hint']}', "
                    f"mas recebeu {type(value).__name__}: {value}"
                )

def register_variable_type(var_name, value):
    """Registra o tipo inferido de uma variável."""
    if isinstance(value, int):
        variable_types[var_name] = 'int'
    elif isinstance(value, float):
        variable_types[var_name] = 'float'
    elif isinstance(value, str):
        variable_types[var_name] = 'str'
    elif isinstance(value, bool):
        variable_types[var_name] = 'bool'
    elif isinstance(value, list):
        variable_types[var_name] = 'list'
    elif isinstance(value, dict):
        variable_types[var_name] = 'dict'
    elif isinstance(value, tuple):
        variable_types[var_name] = 'tuple'
    else:
        variable_types[var_name] = 'any'

# ===== Conversores de Tipos =====

def to_int(value):
    """Converte um valor para inteiro."""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise SyraTypeError(f"Não foi possível converter '{value}' para inteiro.")

def to_float(value, precision=None):
    """Converte um valor para float com precisão opcional."""
    try:
        if precision is not None:
            getcontext().prec = precision + 10  # Precisão extra para cálculos
            decimal_val = Decimal(str(float(value)))
            format_str = f"{{:.{precision}f}}"
            return float(format_str.format(decimal_val))
        return float(value)
    except (ValueError, TypeError):
        raise SyraTypeError(f"Não foi possível converter '{value}' para float.")

def to_str(value):
    """Converte um valor para string."""
    return str(value)

def to_bool(value):
    """Converte um valor para booleano."""
    if isinstance(value, str):
        value = value.lower()
        if value in ('true', 'sim', 'yes', 's', 'y', '1'):
            return True
        if value in ('false', 'não', 'nao', 'no', 'n', '0'):
            return False
        raise SyraTypeError(f"Não foi possível converter string '{value}' para booleano.")
    return bool(value)

def to_list(value):
    """Converte um valor para lista."""
    if isinstance(value, str):
        # Tenta interpretar como JSON se for string
        try:
            if value.startswith('[') and value.endswith(']'):
                return json.loads(value)
        except json.JSONDecodeError:
            pass
        # Se não for JSON válido, divide a string
        return value.split(',')
    elif hasattr(value, '__iter__') and not isinstance(value, (str, dict)):
        return list(value)
    else:
        return [value]

# ===== Funções de Sistema de Arquivos =====

def SyraOS(command):
    """Executa um comando no terminal e retorna a saída."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[ERRO] {result.stderr}"
        return output
    except Exception as e:
        return f"[ERRO AO EXECUTAR] {str(e)}"

def Syope(filename, extension=None):
    """Abre ou cria um arquivo. Retorna o nome do arquivo para operações futuras."""
    if extension and not filename.endswith(extension):
        full_filename = f"{filename}{extension}"
    else:
        full_filename = filename
    
    try:
        # Fechar o arquivo se já estiver aberto
        if full_filename in open_files:
            open_files[full_filename].close()
        
        # Abrir para leitura e escrita (criando se não existir)
        file = open(full_filename, 'a+')
        file.seek(0)  # Posicionar no início para leitura
        open_files[full_filename] = file
        return full_filename
    except Exception as e:
        return f"[ERRO AO ABRIR] {str(e)}"

def Sywr(filename, content):
    """Escreve conteúdo em um arquivo, em uma nova linha."""
    if filename not in open_files:
        return f"[ERRO] Arquivo '{filename}' não está aberto. Use Syope() primeiro."
    
    try:
        file = open_files[filename]
        # Verificar se o arquivo está vazio ou se já tem conteúdo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        
        if file_size > 0:
            # Se o arquivo não estiver vazio, adiciona uma nova linha
            file.write(f"\n{content}")
        else:
            # Se estiver vazio, apenas escreve o conteúdo
            file.write(f"{content}")
        
        file.flush()  # Garantir que o conteúdo seja escrito imediatamente
        return f"Conteúdo escrito em '{filename}'"
    except Exception as e:
        return f"[ERRO AO ESCREVER] {str(e)}"

def Sycls(filename):
    """Fecha um arquivo aberto."""
    if filename in open_files:
        try:
            open_files[filename].close()
            del open_files[filename]
            return f"Arquivo '{filename}' fechado com sucesso"
        except Exception as e:
            return f"[ERRO AO FECHAR] {str(e)}"
    else:
        return f"[AVISO] Arquivo '{filename}' não estava aberto"

def Syread(filename):
    """Lê e exibe o conteúdo de um arquivo."""
    # Se o arquivo já está aberto, use a referência
    if filename in open_files:
        try:
            file = open_files[filename]
            file.seek(0)  # Voltar ao início do arquivo
            content = file.read()
            return content
        except Exception as e:
            return f"[ERRO AO LER ARQUIVO ABERTO] {str(e)}"
    
    # Se não está aberto, tente abrir temporariamente
    try:
        # Detectar tipo de arquivo baseado na extensão
        if filename.endswith(('.csv', '.tsv')):
            return _read_tabular(filename)
        elif filename.endswith('.json'):
            return _read_json(filename)
        elif filename.endswith(('.xlsx', '.xls')):
            return _read_excel(filename)
        else:
            # Arquivo texto comum
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"[ERRO AO LER] {str(e)}"

def _read_tabular(filename):
    """Lê arquivos tabulares (CSV, TSV)."""
    try:
        delimiter = '\t' if filename.endswith('.tsv') else ','
        df = pd.read_csv(filename, delimiter=delimiter)
        return df.to_string()
    except Exception as e:
        return f"[ERRO AO LER CSV/TSV] {str(e)}"

def _read_json(filename):
    """Lê arquivos JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"[ERRO AO LER JSON] {str(e)}"

def _read_excel(filename):
    """Lê arquivos Excel."""
    try:
        df = pd.read_excel(filename)
        return df.to_string()
    except Exception as e:
        return f"[ERRO AO LER EXCEL] {str(e)}"

# ===== Operadores Syra =====

class SyraOperators:
    """Implementação de todos os operadores Syra."""
    
    @staticmethod
    def add(a, b):
        """Implementa o operador +"""
        return a + b
    
    @staticmethod
    def subtract(a, b):
        """Implementa o operador -"""
        return a - b
    
    @staticmethod
    def multiply(a, b):
        """Implementa o operador *"""
        return a * b
    
    @staticmethod
    def divide(a, b):
        """Implementa o operador /"""
        if b == 0:
            raise ZeroDivisionError("Divisão por zero não permitida")
        return a / b
    
    @staticmethod
    def integer_divide(a, b):
        """Implementa o operador //"""
        if b == 0:
            raise ZeroDivisionError("Divisão por zero não permitida")
        return a // b
    
    @staticmethod
    def modulo(a, b):
        """Implementa o operador %"""
        if b == 0:
            raise ZeroDivisionError("Módulo por zero não permitido")
        return a % b
    
    @staticmethod
    def power(a, b):
        """Implementa o operador **"""
        return a ** b
    
    @staticmethod
    def equals(a, b):
        """Implementa o operador =="""
        return a == b
    
    @staticmethod
    def not_equals(a, b):
        """Implementa o operador !="""
        return a != b
    
    @staticmethod
    def greater_than(a, b):
        """Implementa o operador >"""
        return a > b
    
    @staticmethod
    def less_than(a, b):
        """Implementa o operador <"""
        return a < b
    
    @staticmethod
    def greater_equal(a, b):
        """Implementa o operador >="""
        return a >= b
    
    @staticmethod
    def less_equal(a, b):
        """Implementa o operador <="""
        return a <= b
    
    @staticmethod
    def logical_and(a, b):
        """Implementa o operador and"""
        return a and b
    
    @staticmethod
    def logical_or(a, b):
        """Implementa o operador or"""
        return a or b
    
    @staticmethod
    def logical_not(a):
        """Implementa o operador not"""
        return not a
    
    @staticmethod
    def bitwise_and(a, b):
        """Implementa o operador &"""
        return a & b
    
    @staticmethod
    def bitwise_or(a, b):
        """Implementa o operador |"""
        return a | b
    
    @staticmethod
    def bitwise_xor(a, b):
        """Implementa o operador ^"""
        return a ^ b
    
    @staticmethod
    def bitwise_not(a):
        """Implementa o operador ~"""
        return ~a
    
    @staticmethod
    def left_shift(a, b):
        """Implementa o operador <<"""
        return a << b
    
    @staticmethod
    def right_shift(a, b):
        """Implementa o operador >>"""
        return a >> b
    
    @staticmethod
    def increment(a):
        """Implementa o operador ++"""
        return a + 1
    
    @staticmethod
    def decrement(a):
        """Implementa o operador --"""
        return a - 1
    
    @staticmethod
    def in_operator(a, b):
        """Implementa o operador 'in'"""
        return a in b
    
    @staticmethod
    def not_in_operator(a, b):
        """Implementa o operador 'not in'"""
        return a not in b
    
    @staticmethod
    def is_operator(a, b):
        """Implementa o operador 'is'"""
        return a is b
    
    @staticmethod
    def is_not_operator(a, b):
        """Implementa o operador 'is not'"""
        return a is not b
    
    @staticmethod
    def concat(a, b):
        """Implementa o operador '+!' (concatenação especial Syra)"""
        return str(a) + str(b)

# ===== Sistema de Conversão Type Properties =====

def apply_type_property(var_name, prop_name, args=None):
    """
    Aplica propriedades de tipo às variáveis Syra.
    Ex: $var.int, $var.float(2), etc.
    """
    from func import variables  # Importação tardia para evitar circular
    
    if var_name not in variables:
        raise SyraTypeError(f"Variável '{var_name}' não encontrada")
    
    value = variables[var_name]
    
    # Propriedades simples de tipo
    if prop_name == 'int':
        result = to_int(value)
    elif prop_name == 'float':
        precision = int(args[0]) if args else None
        result = to_float(value, precision)
    elif prop_name == 'string' or prop_name == 'str':
        result = to_str(value)
    elif prop_name == 'bool':
        result = to_bool(value)
    elif prop_name == 'list':
        result = to_list(value)
    
    # Atualiza o tipo registrado
    register_variable_type(var_name, result)
    
    # Atualiza o valor na tabela de variáveis
    variables[var_name] = result
    return result

# ===== Documentação sobre Escopos =====

SCOPE_DOCUMENTATION = """
# Escopos de Variáveis em Syra

Syra utiliza um sistema de escopos claro e consistente:

## Variáveis Globais
- Variáveis com `$` são **variáveis globais** acessíveis em todo o código
- Podem ser acessadas e modificadas em qualquer função ou bloco
- Exemplo: `$nome = "Syra"` define uma variável global

## Variáveis Locais
- Parâmetros de função são **variáveis locais** dentro do escopo da função
- Visíveis apenas dentro da função onde foram declaradas
- Exemplo: `soma(a, b) is a + b` onde `a` e `b` são variáveis locais

## Regras de Resolução
1. Syra procura primeiro por uma variável local no escopo atual
2. Se não encontrar, procura por uma variável global (com `$`)
3. Erro é gerado se a variável não for encontrada em nenhum escopo

## Closures
- Funções lambda capturam variáveis do escopo onde foram definidas
- O escopo capturado é preservado no `closure_env` da função

## Boas Práticas
- Use `$` para variáveis compartilhadas entre múltiplas funções
- Evite modificar variáveis globais dentro de funções (efeitos colaterais)
- Prefira passar valores como parâmetros e retornar resultados
"""

# ===== Inicialização =====

def initialize_types():
    """Inicializa o sistema de tipos do Syra."""
    # Limpe arquivos que possam ter ficado abertos em execuções anteriores
    for filename in list(open_files.keys()):
        Sycls(filename)

# Registrar comandos no sistema Syra
def register_type_commands(commands_dict):
    """Registra os comandos do sistema de tipos no dicionário de comandos Syra."""
    commands_dict["&Syope"] = cmd_syope
    commands_dict["&syope"] = cmd_syope  # Version with lowercase
    commands_dict["&Sywr"] = cmd_sywr
    commands_dict["&sywr"] = cmd_sywr    # Version with lowercase
    commands_dict["&Sycls"] = cmd_sycls
    commands_dict["&sycls"] = cmd_sycls  # Version with lowercase
    commands_dict["&Syread"] = cmd_syread
    commands_dict["&syread"] = cmd_syread  # Version with lowercase

# Funções de comando que lidam corretamente com variáveis Syra
def cmd_syraos(args):
    """Comando para executar comandos no sistema operacional."""
    from func import safe_eval
    command = safe_eval(args)
    return SyraOS(command)

def cmd_syope(args):
    """Comando para abrir ou criar arquivos."""
    from func import safe_eval
    args_parts = args.split(",", 1)
    filename = safe_eval(args_parts[0].strip())
    extension = safe_eval(args_parts[1].strip()) if len(args_parts) > 1 else None
    return Syope(filename, extension)

def cmd_sywr(args):
    """Comando para escrever em arquivos."""
    from func import safe_eval
    args_parts = args.split(",", 1)
    if len(args_parts) < 2:
        return "[ERRO] Sywr requer dois argumentos: nome_arquivo, conteúdo"
    filename = safe_eval(args_parts[0].strip())
    content = safe_eval(args_parts[1].strip())
    return Sywr(filename, content)

def cmd_sycls(args):
    """Comando para fechar arquivos."""
    from func import safe_eval
    filename = safe_eval(args)
    return Sycls(filename)

def cmd_syread(args):
    """Comando para ler arquivos."""
    from func import safe_eval
    filename = safe_eval(args)
    return Syread(filename)

# Cria um parser para propriedades de tipo (como $var.int)
def parse_type_property(expr):
    """
    Analisa expressões de propriedades de tipo como $var.int ou $var.float(2)
    Retorna: (var_name, property, args) ou None se não for uma propriedade.
    """
    match = re.match(r"(\$\w+)\.(\w+)(?:\(([^)]+)\))?", expr)
    if match:
        var_name, prop, args_str = match.groups()
        args = [a.strip() for a in args_str.split(",")] if args_str else None
        return (var_name, prop, args)
    return None