
#!/usr/bin/env python3
"""
OFX Normalizer - Main Entry Point
Cross-platform OFX file normalizer for Microsoft Money compatibility

Author: Brendown Ferreira (Br3n0k) - NokTech
"""

import sys
import os

# Adicionar o diretório src ao path para imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.helpers.helper import Helper

def main():
    """
    Ponto de entrada principal da aplicação
    Detecta automaticamente o sistema operacional e executa a interface apropriada
    """
    try:
        helper = Helper()
        exit_code = helper.run_appropriate_interface()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
