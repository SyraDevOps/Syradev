import func # Importa func.py, que deve popular func.commands e gerenciar func.variables
import os
import sys

def repl():
    print("Syra REPL - Digite comandos Syra. Ctrl+C para sair.")
    buffer = []
    while True:
        try:
            line = input("syra> ")
            if not line.strip():
                continue
            # Suporte a blocos: se linha termina com ':', leia mais linhas
            if line.strip().endswith(":"):
                buffer = [line]
                while True:
                    sub = input("... ")
                    if not sub.strip():
                        break
                    buffer.append(sub)
                code = "\n".join(buffer)
                func.run_syra_code(code)
            else:
                func.run_syra_code(line)
        except (KeyboardInterrupt, EOFError):
            print("\nSaindo do Syra REPL.")
            break

if __name__ == "__main__":
    if len(sys.argv) == 2:
        file_to_run = sys.argv[1]
        if not os.path.exists(file_to_run):
            print(f"Erro: Arquivo '{file_to_run}' não encontrado.")
            sys.exit(1)
        func.run_syra_file(file_to_run)
    else:
        repl()
