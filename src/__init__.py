"""OFX Normalizer - Pacote Principal
Normalizador de arquivos OFX para compatibilidade com Microsoft Money

Author: Brendown Ferreira (Br3n0k) - NokTech
Email: brendown@noktech.com
Version: 2.0.0
"""

from .normalizer import Normalizer
from .helpers import Helper
from .config import Config
# Removido import automático do win para evitar execução da GUI

__all__ = ['Normalizer', 'Helper', 'Config']

__version__ = "2.0.0"
__author__ = "Brendown Ferreira (Br3n0k)"
__email__ = "brendown@noktech.com"