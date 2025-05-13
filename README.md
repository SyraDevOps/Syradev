# Linguagem de Programação Syra

Este projeto implementa um interpretador para a linguagem Syra, uma linguagem de programação com sintaxe em português projetada para ser intuitiva e educacional. O interpretador é implementado em Python e oferece um conjunto completo de recursos de programação modernos.

---

## Sumário

1. Introdução
2. Instalação
3. Como Executar Código Syra
   - Modo Script
   - Modo Interativo
   - Debug e Testes
4. Sintaxe Básica
   - Comentários
   - Variáveis e Constantes
   - Tipos de Dados
   - Operadores
5. Entrada e Saída
6. Estruturas de Controle
   - Condicionais
   - Laços
   - Quebrar e Continuar
7. Funções e Procedimentos
   - Definição de Funções
   - Parâmetros e Argumentos
   - Retorno de Valores
   - Funções Anônimas (Lambda)
8. Tratamento de Erros
9. Estruturas de Dados
   - Listas
   - Mapas
   - Métodos de Manipulação
10. Programação Funcional
    - Mapear, Filtrar, Reduzir
    - Funções de Primeira Classe
11. Programação Orientada a Objetos
    - Definindo Classes
    - Criando Instâncias
    - Herança
    - Métodos
12. Sistema de Módulos
    - Importação
    - Namespaces
13. Recursos Avançados
    - Validação de Tipos
    - Privado e Protegido
    - Memoização
    - Concorrência
14. Referência de Funções Nativas
15. Problemas Comuns e Soluções
16. Exemplos de Programas
17. Desenvolvimento e Contribuição

---

## Introdução

Syra é uma linguagem de programação com sintaxe em português, projetada para ser intuitiva e expressiva. Ela combina paradigmas procedurais, orientados a objetos e funcionais em uma linguagem interpretada simples de aprender mas poderosa para implementar algoritmos complexos.

**Características principais:**
- Sintaxe em português clara e legível
- Tipagem dinâmica com verificação de tipos em tempo de execução
- Suporte a múltiplos paradigmas de programação
- Sistema completo de tratamento de erros
- Integração com bibliotecas Python

---

## Instalação

Para usar Syra, clone este repositório ou baixe os arquivos. Você precisará do Python 3.6 ou superior instalado.

```bash
git clone https://github.com/seu-usuario/syra-language.git
cd syra-language
```

---

## Como Executar Código Syra

### Modo Script

Para executar um arquivo Syra (extensão `.syra`):

```bash
python syra_runner.py seu_programa.syra
```

### Modo Interativo

Para iniciar o terminal interativo Syra:

```bash
python syra_terminal.py
```

No terminal interativo você pode digitar comandos e ver os resultados imediatamente. Digite `sair` para encerrar a sessão.

### Debug e Testes

Para testar execução e verificar resultados:

```bash
python rules.py  # Executa um teste interno simples
```

---

## Sintaxe Básica

### Comentários

Linhas que começam com `#` são tratadas como comentários e ignoradas pelo interpretador.

```syra
# Este é um comentário em Syra
mostrar("Isto será executado")  # Comentário ao final da linha
```

### Variáveis e Constantes

#### Variáveis

Para definir uma variável, use a palavra-chave `definir`:

```syra
definir idade como 25
definir nome como "Maria"
definir ativo como verdadeiro
```

Reatribuição de valores:

```syra
definir contador como 1
contador = contador + 1  # Agora contador é 2
```

#### Constantes

Constantes são valores que não podem ser alterados após definidos:

```syra
constante PI como 3.14159
constante DIAS_SEMANA como 7
```

Tentativas de alterar constantes geram erro:

```syra
constante MAX como 100
MAX = 200  # Erro: "Não pode atribuir um novo valor à constante 'MAX'"
```

### Tipos de Dados

Syra oferece os seguintes tipos de dados básicos:

#### Número

Inteiros e decimais são representados como `número`:

```syra
definir inteiro como 42
definir decimal como 3.14
```

#### Texto

Strings delimitadas por aspas duplas ou simples:

```syra
definir mensagem como "Olá, mundo!"
definir nome como 'Maria'
```

#### Lógico

Valores booleanos:

```syra
definir ativo como verdadeiro
definir finalizado como falso
```

#### Nulo

Representa a ausência de valor:

```syra
definir resultado como nulo
```

#### Lista

Coleção ordenada de valores:

```syra
definir numeros como [1, 2, 3, 4, 5]
definir nomes como ["Ana", "Carlos", "Maria"]
definir mista como [1, "dois", verdadeiro, [4, 5]]
```

#### Mapa

Coleção de pares chave-valor:

```syra
definir pessoa como {"nome": "João", "idade": 30}
definir config como mapa {"debug": verdadeiro, "max_itens": 100}
```

### Operadores

#### Operadores Aritméticos

```syra
definir a como 10
definir b como 3

mostrar(a + b)    # 13 (adição)
mostrar(a - b)    # 7 (subtração)
mostrar(a * b)    # 30 (multiplicação)
mostrar(a / b)    # 3.3333... (divisão)
mostrar(a % b)    # 1 (módulo/resto)
mostrar(potencia(a, b))  # 1000 (potência)
```

#### Operadores de Comparação

```syra
mostrar(a == b)   # falso (igualdade)
mostrar(a != b)   # verdadeiro (diferença)
mostrar(a > b)    # verdadeiro (maior que)
mostrar(a < b)    # falso (menor que)
mostrar(a >= b)   # verdadeiro (maior ou igual)
mostrar(a <= b)   # falso (menor ou igual)
```

Operadores de comparação também podem ser escritos por extenso:

```syra
mostrar(a é igual a b)          # falso
mostrar(a é diferente de b)     # verdadeiro
mostrar(a é maior que b)        # verdadeiro
mostrar(a é menor que b)        # falso
mostrar(a é maior ou igual a b) # verdadeiro
mostrar(a é menor ou igual a b) # falso
```

#### Operadores Lógicos

```syra
definir x como verdadeiro
definir y como falso

mostrar(x e y)   # falso (AND lógico)
mostrar(x ou y)  # verdadeiro (OR lógico)
mostrar(não x)   # falso (NOT lógico)
```

---

## Entrada e Saída

### Saída de Dados

A função `mostrar()` imprime valores na tela:

```syra
mostrar("Olá, mundo!")
definir idade como 25
mostrar("A idade é:", idade)  # Aceita múltiplos argumentos
```

### Entrada de Dados

A função `perguntar()` obtém entrada do usuário:

```syra
definir nome como perguntar("Qual é o seu nome? ")
mostrar("Olá,", nome)

definir idade como inteiro(perguntar("Qual é sua idade? "))
mostrar("Daqui a 10 anos você terá", idade + 10, "anos")
```

---

## Estruturas de Controle

### Condicionais

#### Instrução `quando` (equivalente ao if)

```syra
definir idade como 18

quando (idade >= 18) {
    mostrar("Maior de idade")
}

quando (idade < 13) {
    mostrar("Criança")
} senão se (idade < 18) {
    mostrar("Adolescente")
} senão {
    mostrar("Adulto")
}
```

### Laços

#### Laço `enquanto` (equivalente ao while)

```syra
definir contador como 1

enquanto (contador <= 5) {
    mostrar("Contagem:", contador)
    contador = contador + 1
}
```

#### Laço `para cada` (equivalente ao for-each)

```syra
definir nomes como ["Ana", "Bruno", "Carla"]

para cada nome em nomes {
    mostrar("Olá,", nome)
}
```

### Quebrar e Continuar

Use `quebrar` para sair de um laço e `continuar` para pular para a próxima iteração:

```syra
definir numeros como [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

para cada num em numeros {
    quando (num == 5) {
        quebrar  # Interrompe o laço ao encontrar o número 5
    }
    mostrar(num)
}

para cada num em numeros {
    quando (num % 2 == 0) {
        continuar  # Pula números pares
    }
    mostrar("Número ímpar:", num)
}
```

---

## Funções e Procedimentos

### Definição de Funções

Em Syra, existem funções (que retornam valor) e procedimentos (que não retornam):

#### Função (com retorno)

```syra
função somar(a, b) {
    voltar a + b
}

definir resultado como somar(5, 3)
mostrar(resultado)  # 8
```

#### Procedimento (sem retorno)

```syra
procedimento saudação(nome) {
    mostrar("Olá,", nome + "!")
}

saudação("Maria")  # Olá, Maria!
```

### Parâmetros e Argumentos

```syra
função calcular_média(valores) {
    definir soma como 0
    para cada valor em valores {
        soma = soma + valor
    }
    voltar soma / tamanho(valores)
}

mostrar(calcular_média([8, 9, 7, 10, 6]))  # 8.0
```

### Retorno de Valores

O comando `voltar` interrompe a execução e retorna um valor:

```syra
função é_par(numero) {
    quando (numero % 2 == 0) {
        voltar verdadeiro
    }
    voltar falso
}

função classificar_número(n) {
    quando (n < 0) {
        voltar "negativo"
    } senão se (n == 0) {
        voltar "zero"
    } senão {
        voltar "positivo"
    }
}
```

### Funções Anônimas (Lambda)

Funções anônimas são definidas sem nome e geralmente usadas em operações funcionais:

```syra
definir dobrar como função(x) { voltar x * 2 }
mostrar(dobrar(5))  # 10

mostrar(mapear(função(x) { voltar x * x }, [1, 2, 3, 4]))  # [1, 4, 9, 16]
```

---

## Tratamento de Erros

Syra oferece blocos `tentar`/`capturar` para tratamento de exceções:

```syra
tentar {
    definir resultado como 10 / 0  # Gera erro de divisão por zero
    mostrar("Este código não será executado")
} capturar erro {
    mostrar("Ocorreu um erro:", erro)
}

# Exemplo prático
procedimento ler_arquivo(nome_arquivo) {
    tentar {
        # Código para ler arquivo (simulado)
        quando (nome_arquivo != "dados.txt") {
            # Simulando erro
            definir x como 1 / 0
        }
        mostrar("Arquivo lido com sucesso")
    } capturar erro {
        mostrar("Erro ao ler arquivo:", erro)
    }
}

ler_arquivo("dados.txt")
ler_arquivo("inexistente.txt")
```

---

## Estruturas de Dados

### Listas

Listas são coleções ordenadas que podem armazenar qualquer tipo de valor:

```syra
definir frutas como ["maçã", "banana", "laranja"]

# Acessando por índice (começa em 0)
mostrar(frutas[0])  # maçã

# Modificando elementos
frutas[1] = "morango"
mostrar(frutas)  # ["maçã", "morango", "laranja"]

# Adicionando elementos
frutas.adicionar("uva")
mostrar(frutas)  # ["maçã", "morango", "laranja", "uva"]

# Removendo elementos
frutas.remover("morango")
mostrar(frutas)  # ["maçã", "laranja", "uva"]
```

### Mapas

Mapas são coleções de pares chave-valor:

```syra
definir pessoa como {"nome": "João", "idade": 30, "cidade": "São Paulo"}

# Acessando valores
mostrar(pessoa["nome"])  # João
mostrar(pessoa.idade)    # 30 (notação alternativa)

# Modificando valores
pessoa["idade"] = 31
pessoa.cidade = "Rio de Janeiro"

# Adicionando novos pares
pessoa["profissão"] = "Engenheiro"

# Verificando se chave existe
quando (pessoa.contem("email")) {
    mostrar("Email:", pessoa.email)
} senão {
    mostrar("Email não cadastrado")
}
```

### Métodos de Manipulação

#### Métodos de Lista

```syra
definir números como [3, 1, 4, 1, 5, 9]

mostrar(números.tamanho)       # 6
números.adicionar(2)           # Adiciona ao final
números.inserir(0, 0)          # Insere no início (índice 0)
mostrar(números.indice_de(5))  # 5 (índice do valor 5)
mostrar(números.contar(1))     # 2 (ocorrências do valor 1)
números.ordenar()              # Ordena crescente
mostrar(números)               # [0, 1, 1, 2, 3, 4, 5, 9]
números.inverter()             # Inverte a ordem
mostrar(números)               # [9, 5, 4, 3, 2, 1, 1, 0]
```

#### Métodos de Mapa

```syra
definir config como {"debug": verdadeiro, "max_itens": 100}

mostrar(config.tamanho)    # 2
mostrar(config.chaves)     # ["debug", "max_itens"]
mostrar(config.valores)    # [verdadeiro, 100]
mostrar(config.contem("debug"))  # verdadeiro
```

#### Métodos de Texto

```syra
definir texto como "Olá, Mundo!"

mostrar(texto.tamanho)           # 11
mostrar(texto.maiusculo())       # OLÁ, MUNDO!
mostrar(texto.minusculo())       # olá, mundo!
mostrar(texto.substituir(",", "")) # Olá Mundo!
mostrar(texto.contem_texto("Mundo"))  # verdadeiro
mostrar(texto.inicia_com("Olá"))     # verdadeiro
mostrar(texto.termina_com("!"))      # verdadeiro
mostrar(texto.dividir_texto(","))    # ["Olá", " Mundo!"]
mostrar(texto.subtexto(0, 3))        # Olá
```

---

## Programação Funcional

Syra suporta o paradigma funcional com funções de primeira classe e operações funcionais.

### Mapear, Filtrar, Reduzir

```syra
definir números como [1, 2, 3, 4, 5]

# Mapear: aplica uma função a cada elemento
definir quadrados como mapear(função(x) { voltar x * x }, números)
mostrar(quadrados)  # [1, 4, 9, 16, 25]

# Filtrar: seleciona elementos que satisfazem uma condição
definir pares como filtrar(função(x) { voltar x % 2 == 0 }, números)
mostrar(pares)  # [2, 4]

# Reduzir: combina elementos com uma função acumuladora
definir soma como reduzir(função(acc, val) { voltar acc + val }, números)
mostrar(soma)  # 15

# Encontrar: retorna o primeiro elemento que satisfaz uma condição
definir maior_que_três como encontrar(função(x) { voltar x > 3 }, números)
mostrar(maior_que_três)  # 4

# Todos/Algum: verificam condições para todos ou algum elemento
mostrar(todos(função(x) { voltar x > 0 }, números))  # verdadeiro
mostrar(algum(função(x) { voltar x > 4 }, números))  # verdadeiro
```

### Funções de Primeira Classe

Em Syra, funções são valores de primeira classe, podendo ser armazenadas em variáveis, passadas como argumento e retornadas por outras funções:

```syra
# Armazenando função em variável
definir duplicar como função(x) { voltar x * 2 }

# Função que recebe outra função como argumento
função aplicar(f, valor) {
    voltar f(valor)
}

mostrar(aplicar(duplicar, 10))  # 20

# Função que retorna outra função
função criar_multiplicador(fator) {
    voltar função(x) { voltar x * fator }
}

definir triplicar como criar_multiplicador(3)
mostrar(triplicar(5))  # 15
```

---

## Programação Orientada a Objetos

Syra suporta conceitos básicos de POO através de classes, instâncias, herança e encapsulamento.

### Definindo Classes

```syra
classe Pessoa {
    procedimento inicializar(nome, idade) {
        self.nome = nome
        self.idade = idade
    }
    
    função apresentar() {
        voltar "Olá, meu nome é " + self.nome + " e tenho " + texto(self.idade) + " anos."
    }
    
    função fazer_aniversario() {
        self.idade = self.idade + 1
        voltar self.idade
    }
}
```

### Criando Instâncias

```syra
definir p1 como novo Pessoa("João", 30)
definir p2 como novo Pessoa("Maria", 25)

mostrar(p1.nome)             # João
mostrar(p1.apresentar())     # Olá, meu nome é João e tenho 30 anos.
mostrar(p1.fazer_aniversario())  # 31
```

### Herança

```syra
classe Estudante : Pessoa {
    procedimento inicializar(nome, idade, curso) {
        # Chama construtor da classe pai
        super.inicializar(nome, idade)
        self.curso = curso
    }
    
    função apresentar() {
        voltar super.apresentar() + " Estou cursando " + self.curso + "."
    }
}

definir e1 como novo Estudante("Pedro", 20, "Engenharia")
mostrar(e1.apresentar())  # Olá, meu nome é Pedro e tenho 20 anos. Estou cursando Engenharia.
```

### Métodos

Classes podem ter métodos estáticos, além dos métodos de instância:

```syra
classe Matemática {
    estatico função quadrado(x) {
        voltar x * x
    }
    
    estatico função cubo(x) {
        voltar x * x * x
    }
}

mostrar(Matemática.quadrado(4))  # 16
mostrar(Matemática.cubo(3))      # 27
```

---

## Sistema de Módulos

Syra permite organizar código em módulos reutilizáveis.

### Importação

Há dois tipos de importação:

1. Importação de módulos Syra (arquivos `.syra`):

```syra
importar "utilitarios"
mostrar(utilitarios.formatar_data("2023-01-15"))
```

2. Importação de módulos Python:

```syra
importar "math"
mostrar(sqrt(16))  # 4.0
mostrar(sin(0))    # 0.0
```

### Namespaces

Syra permite criar namespaces para evitar conflitos de nomes:

```syra
definir matematica como criar_namespace()
matematica["PI"] = 3.14159
matematica["dobrar"] = função(x) { voltar x * 2 }

mostrar(matematica["PI"])  # 3.14159
mostrar(matematica["dobrar"](5))  # 10

mostrar(namespace_membros(matematica))  # ["PI", "dobrar"]
mostrar(namespace_contem(matematica, "PI"))  # verdadeiro
```

---

## Recursos Avançados

### Validação de Tipos

Syra permite verificação de tipos em tempo de execução:

```syra
função somar_numeros(a, b) {
    validar_tipos([a, b], ["número", "número"])
    voltar a + b
}

# Usando anotações de tipo (exclusivo para funções)
função multiplicar(a: número, b: número) {
    voltar a * b
}
```

### Privado e Protegido

Syra oferece mecanismos para encapsular dados:

```syra
definir conta como {
    "saldo": privado(1000),
    "limite": protegido(500),
    "sacar": função(self, valor) {
        quando (valor <= self.saldo.valor) {
            self.saldo.valor = self.saldo.valor - valor
            voltar verdadeiro
        }
        voltar falso
    }
}

mostrar(conta.saldo.valor)   # 1000
mostrar(conta.sacar(200))    # verdadeiro
mostrar(conta.saldo.valor)   # 800
```

### Memoização

Syra suporta memoização para otimizar funções recursivas ou custosas:

```syra
definir fibonacci como função(n) {
    quando (n <= 1) {
        voltar n
    }
    voltar fibonacci(n-1) + fibonacci(n-2)
}

definir fibonacci_rapido como memoizar(fibonacci)

mostrar(fibonacci_rapido(30))  # Muito mais rápido que fibonacci(30)
```

### Concorrência

Syra permite executar funções em threads separadas:

```syra
procedimento tarefa_longa() {
    mostrar("Iniciando tarefa...")
    # Simulando operação longa
    definir contador como 0
    enquanto (contador < 1000000) {
        contador = contador + 1
    }
    mostrar("Tarefa concluída!")
}

mostrar("Iniciando programa")
# Executa em uma nova thread
em_thread(tarefa_longa)
mostrar("Continuando execução principal")
```

---

## Referência de Funções Nativas

### Conversões e Tipos

- `inteiro(valor)`: Converte para número inteiro
- `decimal(valor)`: Converte para número decimal
- `texto(valor)`: Converte para texto
- `logico(valor)`: Converte para valor lógico
- `tipo(valor)`: Retorna o tipo do valor como texto

### Matemática

- `abs(x)`: Valor absoluto
- `raiz_quadrada(x)`: Raiz quadrada
- `potencia(x, y)`: x elevado a y
- `arredondar(x, casas=0)`: Arredonda com número de casas definido
- `piso(x)`: Arredonda para baixo
- `teto(x)`: Arredonda para cima
- `seno(x)`, `cosseno(x)`, `tangente(x)`: Funções trigonométricas
- `log(x)`, `log10(x)`: Logaritmos

### Coleções e Estruturas

- `tamanho(colecao)`: Retorna o tamanho de uma lista, mapa ou texto
- `clonar(valor)`: Cria uma cópia profunda
- `nova_lista()`: Cria uma lista vazia
- `novo_mapa()`: Cria um mapa vazio
- `nova_fila()`: Cria uma fila vazia
- `nova_pilha()`: Cria uma pilha vazia
- `unir(lista1, lista2)`: Concatena duas listas

### Programação Funcional

- `mapear(função, coleção)`: Aplica função a cada elemento
- `filtrar(função, coleção)`: Filtra elementos por condição
- `reduzir(função, coleção, inicial=null)`: Reduz coleção a um valor
- `encontrar(função, coleção)`: Encontra primeiro elemento que satisfaz condição
- `todos(função, coleção)`: Verifica se todos os elementos satisfazem condição
- `algum(função, coleção)`: Verifica se algum elemento satisfaz condição

### Sistema e I/O

- `mostrar(...)`: Imprime na saída padrão
- `perguntar(prompt)`: Lê entrada do usuário
- `limpar()`: Limpa a tela do terminal
- `sessao_id()`: Retorna identificador único da sessão
- `logar(...)`: Registra mensagens de log
- `coletar_lixo()`: Força coleta de lixo

### Tipagem e Reflexão

- `validar_tipos(args, tipos)`: Valida tipos dos argumentos
- `atributos(objeto)`: Lista atributos do objeto
- `metodos(objeto)`: Lista métodos do objeto
- `instancia_de(objeto, classe)`: Verifica se objeto é instância da classe

---

## Problemas Comuns e Soluções

### Erros de Sintaxe

**Problema:** `SyraSyntaxError: Sintaxe inválida na expressão`  
**Solução:** Verifique parênteses, chaves, colchetes e aspas que podem estar desbalanceados.

```syra
# Errado
mostrar("Olá mundo)

# Correto
mostrar("Olá mundo")
```

### Variáveis não Definidas

**Problema:** `SyraNameError: Nome 'x' não definido`  
**Solução:** Certifique-se de definir a variável antes de usá-la.

```syra
# Errado
contador = contador + 1

# Correto
definir contador como 0
contador = contador + 1
```

### Problemas de Escopo

**Problema:** Variáveis definidas em blocos não estão acessíveis fora deles.  
**Solução:** Defina variáveis no escopo apropriado.

```syra
# Problema
função calcular() {
    definir resultado como 42
}
calcular()
mostrar(resultado)  # Erro: resultado não definido

# Solução
função calcular() {
    voltar 42
}
definir resultado como calcular()
mostrar(resultado)
```

### Nomes Reservados

**Problema:** Erro ao usar palavras-chave como nomes de variáveis.  
**Solução:** Evite usar nomes como `mostrar`, `quando`, `definir`, etc.

```syra
# Errado
definir mostrar como "texto"  # Conflita com a função mostrar()

# Correto
definir exibir como "texto"
```

### Recursão Infinita

**Problema:** `SyraRecursionError: Limite máximo de recursão (500) atingido`  
**Solução:** Certifique-se de que sua função recursiva tem um caso base adequado.

```syra
# Problema (recursão infinita)
função fatorial(n) {
    voltar n * fatorial(n - 1)
}

# Correto
função fatorial(n) {
    quando (n <= 1) {
        voltar 1
    }
    voltar n * fatorial(n - 1)
}
```

### Conversão de Tipos

**Problema:** Operações entre tipos incompatíveis.  
**Solução:** Converta explicitamente os tipos.

```syra
# Problema
definir idade como perguntar("Idade: ")
mostrar(idade + 10)  # Erro: tentando somar texto e número

# Solução
definir idade como inteiro(perguntar("Idade: "))
mostrar(idade + 10)
```

### Divisão por Zero

**Problema:** `SyraZeroDivisionError: Tentativa de divisão por zero`  
**Solução:** Verifique divisores antes de usar.

```syra
# Problema
definir x como 10 / 0

# Solução
definir divisor como 0
quando (divisor != 0) {
    definir x como 10 / divisor
} senão {
    mostrar("Divisão por zero não permitida")
}
```

---

## Exemplos de Programas

### Calculadora Simples

```syra
procedimento calculadora() {
    mostrar("Calculadora Syra")
    mostrar("Operações: +, -, *, /")
    
    enquanto (verdadeiro) {
        definir expr como perguntar("> ")
        quando (expr == "sair") {
            quebrar
        }
        
        tentar {
            mostrar("=", eval(expr))
        } capturar erro {
            mostrar("Erro:", erro)
        }
    }
}

calculadora()
```

### Jogo de Adivinhação

```syra
importar "math"

procedimento jogo_adivinhacao() {
    mostrar("Bem-vindo ao Jogo de Adivinhação!")
    definir secreto como inteiro(random() * 100) + 1
    definir tentativas como 0
    definir max_tentativas como 7
    
    enquanto (tentativas < max_tentativas) {
        tentativas = tentativas + 1
        definir palpite como inteiro(perguntar("Tentativa " + texto(tentativas) + "/" + texto(max_tentativas) + ": "))
        
        quando (palpite < secreto) {
            mostrar("Muito baixo!")
        } senão se (palpite > secreto) {
            mostrar("Muito alto!")
        } senão {
            mostrar("Parabéns! Você acertou em", tentativas, "tentativas!")
            voltar
        }
    }
    
    mostrar("Acabaram as tentativas. O número era", secreto)
}

jogo_adivinhacao()
```

### Lista de Tarefas

```syra
definir tarefas como []

procedimento adicionar_tarefa() {
    definir titulo como perguntar("Título da tarefa: ")
    tarefas.adicionar({
        "titulo": titulo,
        "concluida": falso,
        "data": data_atual()
    })
    mostrar("Tarefa adicionada!")
}

procedimento listar_tarefas() {
    mostrar("\n=== TAREFAS ===")
    quando (tarefas.tamanho == 0) {
        mostrar("Nenhuma tarefa cadastrada.")
        voltar
    }
    
    para cada idx em range(0, tarefas.tamanho) {
        definir tarefa como tarefas[idx]
        definir status como tarefa.concluida ? "[✓]" : "[ ]"
        mostrar(idx + 1, "-", status, tarefa.titulo, "(" + tarefa.data + ")")
    }
}

procedimento marcar_concluida() {
    listar_tarefas()
    quando (tarefas.tamanho == 0) { voltar }
    
    definir idx como inteiro(perguntar("Número da tarefa a concluir: ")) - 1
    quando (idx >= 0 e idx < tarefas.tamanho) {
        tarefas[idx].concluida = verdadeiro
        mostrar("Tarefa marcada como concluída!")
    } senão {
        mostrar("Número inválido!")
    }
}

função data_atual() {
    # Simulação simplificada
    voltar "2023-05-10"
}

procedimento menu_tarefas() {
    enquanto (verdadeiro) {
        mostrar("\n=== MENU ===")
        mostrar("1. Adicionar tarefa")
        mostrar("2. Listar tarefas")
        mostrar("3. Marcar como concluída")
        mostrar("4. Sair")
        
        definir opcao como perguntar("> ")
        
        quando (opcao == "1") {
            adicionar_tarefa()
        } senão se (opcao == "2") {
            listar_tarefas()
        } senão se (opcao == "3") {
            marcar_concluida()
        } senão se (opcao == "4") {
            mostrar("Até logo!")
            quebrar
        } senão {
            mostrar("Opção inválida!")
        }
    }
}

menu_tarefas()
```

---

## Desenvolvimento e Contribuição

Syra é um projeto em desenvolvimento e contribuições são bem-vindas. Você pode melhorar:

- Implementação de novos recursos de linguagem
- Otimizações de desempenho do interpretador
- Documentação e tutoriais
- Exemplos de programas e bibliotecas
- Testes e correção de bugs

Para contribuir:

1. Fork este repositório
2. Crie sua branch de recurso (`git checkout -b meu-novo-recurso`)
3. Commit suas mudanças (`git commit -am 'Adiciona novo recurso'`)
4. Push para a branch (`git push origin meu-novo-recurso`)
5. Crie um novo Pull Request

### Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

---

**Desenvolvido por:**  
Equipe Syra Team #2025  
v1.0.0.2

---
