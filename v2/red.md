# Syra Interpreter

Um interpretador simples para a linguagem **Syra**, feito em Python, com suporte a variáveis, comandos customizados, blocos `match` e modo interativo (REPL).

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

### 1. **Variáveis**
- Sempre começam com `$`.
- Atribuição:  
  ```
  $nome = "Syra"
  $idade = 25
  ```
- Só é possível acessar variáveis usando o `$`:
  ```
  shw($nome)
  ```

### 2. **Comando `shw`**
- Mostra o valor de uma variável Syra.
- Exemplo:
  ```
  shw($idade)
  ```
- Se a variável não existir, mostra uma mensagem de erro.

### 3. **Comando `syra.vd`**
- Abre a webcam (usando OpenCV).
- Exemplo:
  ```
  syra.vd(0)
  ```

### 4. **Bloco `match`**
- Estrutura de decisão semelhante ao `match`/`switch` de outras linguagens.
- Sintaxe:
  ```
  resultado = match $idade:
      case 0          => "Recém-nascido"
      case 1..12      => "Criança"
      case 13..17     => "Adolescente"
      case 18..59     => "Adulto"
      case 60..200    => "Idoso"
      case _          => print("Idade inválida")
  shw($resultado)
  ```
- **Regras:**
  - O valor pode ser uma variável Syra ou expressão.
  - `case` aceita valores exatos, intervalos (`1..12`) e coringa (`_`).
  - O resultado pode ser uma string, expressão ou comando `print(...)`.
  - Se nenhum padrão combinar, mostra mensagem de erro.

### 5. **Expressões**
- O lado direito da atribuição pode ser:
  - Um valor literal (`"texto"`, `123`)
  - Outra variável Syra (`$outra`)
  - Uma expressão simples (ex: `$idade + 1` se suportado pelo Python `eval`)

### 6. **Comentários**
- Linhas iniciadas com `//` são ignoradas.

### 7. **Classes e Orientação a Objetos**

O Syra suporta **classes**, **herança**, **métodos de instância**, **métodos estáticos** e **super()**.

### **Definição de Classes**

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

### **Herança**

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

### **Instanciação e Métodos**

- Instancie objetos com `Classe(args)` e atribua a uma variável.
- Chame métodos com `$obj.metodo()`.

Exemplo:
```syra
$p = Pessoa("João", 30)
$p.saudacao()

$f = Funcionario("Ana", 25, "Dev")
$f.saudacao()
```

### **Métodos Estáticos**

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

### **Resumo**

- **Classes** permitem organizar código e reutilizar lógica.
- **Herança** facilita a extensão de funcionalidades.
- **Métodos estáticos** são úteis para lógica independente de instâncias.
- **super()** permite acessar a lógica da classe base.

Agora, o Syra suporta programação orientada a objetos de forma simples e poderosa!

---

## 🛠️ Regras Gerais

- **Todas as variáveis** devem começar com `$`.
- **Comandos** são registrados no dicionário `commands` e podem ser expandidos facilmente.
- **Blocos `match`** são detectados automaticamente no arquivo `.syra` e no REPL.
- **Modo REPL** mantém o estado das variáveis enquanto a sessão estiver aberta.
- **Atribuição de listas**:  
  ```
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