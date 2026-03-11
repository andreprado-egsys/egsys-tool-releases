#!/usr/bin/env python3
"""
egSYS Tool - Sistema de Gerenciamento Multi-Servidor
Versão Refatorada 2.0

Criado por: André Antônio Prado da Silva
Data: 28/07/2025
"""
import sys
import os

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.cli import CLIInterface
from config.logo import VERSION

def check_dependencies():
    """Verifica dependências necessárias."""
    try:
        import pexpect
        import pwinput
    except ImportError as e:
        print(f"\nErro: Biblioteca necessária não encontrada: {e}")
        print("Instale as dependências com: pip install pexpect pwinput")
        sys.exit(1)

def show_version():
    """Mostra versão do sistema."""
    print(f"egSYS SAPA Tool v{VERSION}")
    print("Sistema de Avaliação e Performance de Ambientes")
    print("\nCriado por: André Antônio Prado da Silva")
    print("Licença: Proprietary - egSYS © 2026")

def main():
    """Função principal."""
    # Verifica argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v', 'version']:
            show_version()
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h', 'help']:
            print("egSYS SAPA Tool - Sistema de Gerenciamento Multi-Servidor")
            print("\nUso: egsys [opção]")
            print("\nOpções:")
            print("  --version, -v    Mostra versão do sistema")
            print("  --help, -h       Mostra esta ajuda")
            print("\nSem argumentos: Inicia o sistema interativo")
            sys.exit(0)
    
    check_dependencies()
    
    try:
        cli = CLIInterface()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário. Saindo...")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
