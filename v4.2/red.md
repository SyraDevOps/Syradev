# Syra Interpreter

Um interpretador simples para a linguagem **Syra**, feito em Python, com suporte a variáveis, comandos customizados, blocos `match`, funções, lambdas, decoradores, parâmetros avançados e modo interativo (REPL).

---

## 🚀 Como usar

### Executar um arquivo `.syra`
```sh
python syra_interpreter.py arquivo.syra
```

### Modo Interativo (REPL)
```sh
python syra_interpreter.py
```
Digite comandos Syra diretamente no terminal. As variáveis são mantidas durante a sessão.

---

## 📚 Funcionalidades e Sintaxe

### 1. **Indentação Obrigatória**

A linguagem **Syra** exige **indentação clara e consistente** para blocos de código, como funções, classes, `match`, `each`, etc. Isso significa que todas as linhas que fazem parte de um bloco devem estar **mais indentadas** do que a linha que define o início do bloco.

#### **Regras de Indentação**
- **Blocos de código** devem ser indentados com **espaços** ou **tabulação**, mas a indentação deve ser consistente em todo o arquivo.
- Linhas não indentadas ou com indentação menor do que a linha inicial do bloco **finalizam o bloco**.
- Linhas vazias dentro de um bloco são permitidas, mas devem manter a indentação correta.

#### **Exemplo de Indentação Correta**
```syra
saudacao(nome, saudacao_txt="Olá") is -> str:
    "Retorna uma saudação personalizada."
    return saudacao_txt + ", " + nome

info(nome, *detalhes, idade=99, cidade="N/A") is:
    return "Nome: " + nome + " | Idade: " + str(idade) + " | Cidade: " + cidade + " | Detalhes: " + str(detalhes)

triplica(func) is:
    return (a, b) is func(a, b) * 3

@triplica
soma_tripla(a, b) is -> int:
    return a + b
```

#### **Exemplo de Indentação Incorreta**
```syra
saudacao(nome, saudacao_txt="Olá") is -> str:
"Retorna uma saudação personalizada."  // Não está indentado
return saudacao_txt + ", " + nome      // Não está indentado
```

#### **Blocos Suportados**
- **Funções:** O corpo da função deve ser indentado.
- **Classes:** O corpo da classe e seus métodos devem ser indentados.
- **Blocos `match`:** Cada `case` deve ser indentado em relação ao cabeçalho `match`.
- **Blocos `each`:** O corpo do loop deve ser indentado.

#### **Exemplo com `match`**
```syra
resultado = match $idade:
    case 0          => "Recém-nascido"
    case 1..12      => "Criança"
    case 13..17     => "Adolescente"
    case 18..59     => "Adulto"
    case 60..200    => "Idoso"
    case _          => print("Idade inválida")
shw($resultado)
```

#### **Exemplo com `each`**
```syra
each $item in [1, 2, 3, 4]:
    shw($item)
```

---

### 2. **Variáveis**
- Sempre começam com `$`.
- Atribuição:  
  ```syra
  $nome = "Syra"
  $idade = 25
  ```
- Só é possível acessar variáveis usando o `$`:
  ```syra
  shw($nome)
  ```

### 3. **Funções Syra**
- Definição:
  ```syra
  soma(a, b) is a + b
  ```
  ou bloco:
  ```syra
  saudacao(nome, saudacao_txt="Olá") is -> str:
      "Retorna uma saudação personalizada."
      return saudacao_txt + ", " + nome
  ```
- Suporta:
  - Parâmetros padrão: `x=10`
  - Parâmetros variádicos: `*args`
  - Parâmetros keyword-only: `*, y=2`
  - Anotação de tipo de retorno: `is -> int:`
  - Docstring (primeira linha entre aspas no corpo)
  - Corpo de bloco com `return ...`
- Chamada:
  ```syra
  shw(soma(2, 3))
  ```

### 4. **Funções Lambda Syra**
- Sintaxe:
  ```syra
  $minha_lambda = (x, y=5) is x + y
  shw($minha_lambda(10))      // 15
  shw($minha_lambda(10, 20))  // 30
  ```
- Lambdas podem ser passadas como argumentos para outras funções.

### 5. **Decoradores Syra**
- Defina decoradores como funções que recebem outra função e retornam uma nova função Syra.
- Exemplo:
  ```syra
  triplica(func) is:
      return (a, b) is func(a, b) * 3

  @triplica
  soma_tripla(a, b) is -> int:
      return a + b

  shw(soma_tripla(2, 3))  // 15
  ```
- Decoradores podem ser empilhados.

### 6. **Parâmetros Avançados**
- **Variádicos:** `*args`
- **Keyword-only:** `*, x=1, y=2`
- **Padrão:** `x=10`
- **Tipo:** `x:int`
- Exemplo:
  ```syra
  info(nome, *detalhes, idade=99, cidade="N/A") is:
      return "Nome: " + nome + " | Idade: " + str(idade) + " | Cidade: " + cidade + " | Detalhes: " + str(detalhes)"
  ```

### 7. **Comando `shw`**
- Mostra o valor de uma expressão, variável ou chamada de função Syra.
- Exemplo:
  ```syra
  shw($idade)
  shw(soma(2, 3))
  ```

### 8. **Comando `syra.vd`**
- Abre a webcam (usando OpenCV).
- Exemplo:
  ```syra
  syra.vd(0)
  ```

### 9. **Bloco `match`**
- Estrutura de decisão semelhante ao `match`/`switch` de outras linguagens.
- Sintaxe:
  ```syra
  resultado = match $idade:
      case 0          => "Recém-nascido"
      case 1..12      => "Criança"
      case 13..17     => "Adolescente"
      case 18..59     => "Adulto"
      case 60..200    => "Idoso"
      case _          => print("Idade inválida")
  shw($resultado)
  ```

### 10. **Expressões**
- O lado direito da atribuição pode ser:
  - Um valor literal (`"texto"`, `123`)
  - Outra variável Syra (`$outra`)
  - Uma expressão simples (ex: `$idade + 1` se suportado pelo Python `eval`)

### 11. **Comentários**
- Linhas iniciadas com `//` são ignoradas.
- Comentários inline também são suportados:
  ```syra
  shw(soma(2, 3))  // Mostra 5
  ```

### 12. **Classes e Orientação a Objetos**

O Syra suporta **classes**, **herança**, **métodos de instância**, **métodos estáticos** e **super()**.

#### **Definição de Classes**

- Use `class NomeDaClasse:` para definir uma classe.
- Campos são declarados diretamente no corpo da classe.
- Métodos são definidos com `nome_do_metodo():`.
- O método `init` é o construtor da classe.

Exemplo:
```syra
class Pessoa:
    nome
    idade

    init(nome, idade):
        self.nome = nome
        self.idade = idade

    saudacao():
        shw("Olá, eu sou " + self.nome)
```

#### **Herança**

- Use `class NomeDaClasse : ClasseBase:` para herdar de outra classe.
- Use `super(...)` para chamar o construtor da classe base.

Exemplo:
```syra
class Funcionario : Pessoa:
    cargo

    init(nome, idade, cargo):
        super(nome, idade)
        self.cargo = cargo

    saudacao():
        shw("Olá, sou " + self.nome + " e sou " + self.cargo)
```

#### **Instanciação e Métodos**

- Instancie objetos com `Classe(args)` e atribua a uma variável.
- Chame métodos com `$obj.metodo()`.

Exemplo:
```syra
$p = Pessoa("João", 30)
$p.saudacao()

$f = Funcionario("Ana", 25, "Dev")
$f.saudacao()
```

#### **Métodos Estáticos**

- Use `static` antes do nome do método para definir métodos estáticos.
- Chame métodos estáticos diretamente pela classe.

Exemplo:
```syra
class Matematica:
    static quadrado(x):
        return x * x

shw(Matematica.quadrado(5))  # Saída: 25
```

---

### **Sistema de Importação de Módulos**

O Syra suporta um sistema de importação robusto, permitindo reutilizar código entre arquivos `.syra` e importar funcionalidades de módulos Python.

#### **Sintaxe de Importação**

- **Importar módulo inteiro**  
  ```syra
  expor math_utils
  ```
  Importa todo o módulo e seus símbolos. Você acessa símbolos via `math_utils.nome`.

- **Importar símbolos específicos**  
  ```syra
  from math_utils expor quadrado, pi
  ```
  Importa apenas os símbolos desejados diretamente no escopo.

- **Importar com alias**  
  ```syra
  from math_utils expor cubo as elevar3
  ```
  Importa o símbolo com um novo nome.

- **Importar classes e usá-las**  
  ```syra
  from math_utils expor Angulo
  $a = Angulo(180)
  shw($a.radianos())
  ```

#### **Tipos de Importação**

- **Módulos Syra** (`.syra`):  
  Arquivos Syra com funções, classes e variáveis reutilizáveis.  
  Mantêm escopo isolado para evitar conflitos de nomes.

- **Módulos Python**:  
  Acesso a módulos padrão do Python (ex: `math`, `random`).  
  Lista controlada de módulos permitidos por segurança.

#### **Exemplo de Módulo Syra**

Arquivo `math_utils.syra`:
```syra
class Matematica:
    static quadrado(x):
        return x * x

    static cubo(x):
        return x * x * x

pi = 3.14159

class Angulo:
    init(graus):
        self.graus = graus
    radianos():
        return self.graus * pi / 180
```

Usando o módulo em outro arquivo:
```syra
expor math_utils
shw(math_utils.pi)
shw(math_utils.Matematica.quadrado(4))

from math_utils expor quadrado, pi
shw(quadrado(5))
shw(pi)

from math_utils expor cubo as elevar3
shw(elevar3(2))

from math_utils expor Angulo
$a = Angulo(180)
shw($a.radianos())
```

#### **Benefícios**

- **Organização**: Divide código em módulos temáticos.
- **Reutilização**: Compartilha código entre arquivos.
- **Namespaces**: Evita conflitos de nomes.
- **Extensibilidade**: Integração com bibliotecas Python existentes.

---

### 13. **Comandos Especiais de Arquivo e Sistema (`&`)**

A linguagem Syra agora suporta comandos especiais para manipulação de arquivos e executar comandos do sistema operacional, todos identificados pelo prefixo `&`.  
Esses comandos são diferenciados de funções e classes, tornando o código mais claro e seguro.

#### **Comandos disponíveis:**

- `&Syope(nome, extensão)` — Cria ou abre um arquivo para escrita/leitura.
- `&Sywr(arquivo, conteúdo)` — Escreve uma linha no arquivo aberto.
- `&Syread(arquivo)` — Lê e retorna o conteúdo do arquivo (suporta `.txt`, `.csv`, `.json`, `.xlsx`).
- `&Sycls(arquivo)` — Fecha o arquivo aberto.
- `&SyraOS(comando)` — Executa um comando no terminal e retorna a saída.

#### **Exemplo de uso:**
```syra
$arquivo = &Syope("exemplo", ".txt")
&Sywr($arquivo, "Olá, mundo!")
&Sywr($arquivo, "Segunda linha")
$conteudo = &Syread($arquivo)
shw($conteudo)
&Sycls($arquivo)
```

#### **Leitura de arquivos CSV, JSON e Excel**
```syra
$dados = &Syread("planilha.xlsx")
shw($dados)
```

#### **Execução de comandos do sistema**
```syra
$resultado = &SyraOS("dir")  // Windows
shw($resultado)
```

---

### 14. **Diferenciação clara de comandos (`&`)**

- **Comandos especiais** sempre começam com `&` (ex: `&Sywr`, `&Syread`), evitando conflito com nomes de funções ou classes.
- O interpretador reconhece e executa esses comandos de forma otimizada, inclusive em atribuições (`$var = &Syread(...)`).

---

### 15. **Case-insensitive para comandos especiais**

- Os comandos com `&` funcionam tanto em maiúsculas quanto minúsculas (`&Sywr` ou `&sywr`).

---

### 16. **Sistema de tipos e conversão**

- Variáveis Syra reconhecem tipos básicos (`int`, `float`, `str`, `bool`, `list`, etc.).
- Conversão fácil:  
  ```syra
  $idade = "25"
  $idade.int
  $valor = "3.14159"
  $valor.float(2)  // 3.14
  ```

---

### 17. **Resumo das novidades**

- **Comandos de arquivo e sistema** com `&` (Syope, Sywr, Syread, Sycls, SyraOS).
- **Leitura de arquivos**: `.txt`, `.csv`, `.json`, `.xlsx`.
- **Execução de comandos do SO** via SyraOS.
- **Conversão de tipos** com `.int`, `.float(n)`, `.string`, etc.
- **Case-insensitive** para comandos especiais.
- **Diferenciação clara** entre comandos, funções e classes.

---

### **Resumo**

- **Funções Syra**: Suporte completo a funções, lambdas, decoradores e parâmetros avançados.
- **Classes**: Organize código e reutilize lógica.
- **Herança**: Extensão de funcionalidades.
- **Métodos estáticos**: Lógica independente de instâncias.
- **super()**: Acesse lógica da classe base.
- **Blocos `match`**: Decisão poderosa e expressiva.
- **Importação de módulos**: Modularize e reutilize código facilmente.
- **Comentários inline**: Suporte a `//` em qualquer parte da linha.
- **Comandos especiais**: Manipulação de arquivos e sistema com `&`.

---

## 🛠️ Regras Gerais

- **Todas as variáveis** devem começar com `$`.
- **Comandos** são registrados no dicionário `commands` e podem ser expandidos facilmente.
- **Blocos `match`** são detectados automaticamente no arquivo `.syra` e no REPL.
- **Modo REPL** mantém o estado das variáveis enquanto a sessão estiver aberta.
- **Atribuição de listas**:  
  ```syra
  $lista = []
  ```
- **Strings** podem ser com aspas simples ou duplas.

---

## 🧩 Como adicionar novos comandos

No arquivo `func.py`, crie uma função `cmd_nome` e registre no dicionário `commands`:
```python
def cmd_hello(args):
    print("Olá,", args)
commands["hello"] = cmd_hello
```
No Syra:
```
hello Syra!
```

---

## 📄 Exemplo Completo

```syra
$idade = 25
resultado = match $idade:
    case 0          => "Recém-nascido"
    case 1..12      => "Criança"
    case 13..17     => "Adolescente"
    case 18..59     => "Adulto"
    case 60..200    => "Idoso"
    case _          => print("Idade inválida")
shw($resultado)
```

---

## 📝 Observações

- O interpretador não depende de indentação, mas sim do início das linhas (`case ...`) para blocos.
- O REPL aceita blocos: digite a linha com `:` e depois as linhas do bloco, finalizando com uma linha em branco.
- O sistema é facilmente expansível para novos comandos e estruturas.

---

**Contribua ou sugira melhorias!**