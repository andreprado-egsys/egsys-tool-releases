"""Logo ASCII do egSYS - SAPA."""
from config.constants import GREEN, CYAN, BOLD, RESET, YELLOW

# Versão do sistema
VERSION = "2.0.0"

# Logo principal do egSYS
LOGO_EGSYS = f"""{GREEN}{BOLD}
    ███████╗ ██████╗ ███████╗██╗   ██╗███████╗
    ██╔════╝██╔════╝ ██╔════╝╚██╗ ██╔╝██╔════╝
    █████╗  ██║  ███╗███████╗ ╚████╔╝ ███████╗
    ██╔══╝  ██║   ██║╚════██║  ╚██╔╝  ╚════██║
    ███████╗╚██████╔╝███████║   ██║   ███████║
    ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝{RESET}
"""

# Subtítulo SAPA
SUBTITLE_SAPA = f"""{CYAN}
         ╔═══════════════════════════════════════════════╗
         ║  {BOLD}S{RESET}{CYAN}istema de {BOLD}A{RESET}{CYAN}valiação e {BOLD}P{RESET}{CYAN}erformance de {BOLD}A{RESET}{CYAN}mbientes  ║
         ╚═══════════════════════════════════════════════╝{RESET}
"""

# Logo compacto para cabeçalhos
LOGO_COMPACT = f"{GREEN}{BOLD}egSYS{RESET}"

# Logo completo (logo + subtítulo)
LOGO_FULL = LOGO_EGSYS + SUBTITLE_SAPA

# Versão alternativa - mais compacta
LOGO_EGSYS_ALT = f"""{GREEN}{BOLD}
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║     ███████  ██████  ███████ ██   ██ ║
    ║     ██      ██       ██       ██ ██  ║
    ║     █████   ██   ███ ███████   ███   ║
    ║     ██      ██    ██      ██    ██   ║
    ║     ███████  ██████  ███████    ██   ║
    ║                                       ║
    ╚═══════════════════════════════════════╝{RESET}
{CYAN}        Sistema de Avaliação e Performance
              de Ambientes (SAPA){RESET}
"""

# Banner de boas-vindas
WELCOME_BANNER = f"""
{GREEN}{BOLD}╔════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                        ║
║     ███████╗ ██████╗ ███████╗██╗   ██╗███████╗   ███████╗ █████╗ ██████╗  █████╗     ║
║     ██╔════╝██╔════╝ ██╔════╝╚██╗ ██╔╝██╔════╝   ██╔════╝██╔══██╗██╔══██╗██╔══██╗    ║
║     █████╗  ██║  ███╗███████╗ ╚████╔╝ ███████╗   ███████╗███████║██████╔╝███████║    ║
║     ██╔══╝  ██║   ██║╚════██║  ╚██╔╝  ╚════██║   ╚════██║██╔══██║██╔═══╝ ██╔══██║    ║
║     ███████╗╚██████╔╝███████║   ██║   ███████║   ███████║██║  ██║██║     ██║  ██║    ║
║     ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ║
║                                                                                        ║{RESET}
{CYAN}║              Sistema de Avaliação e Performance de Ambientes                      ║
║                    Gerenciamento Multi-Servidor Inteligente                           ║
║                                                                                        ║{RESET}
{YELLOW}║                                  Versão {VERSION}                                      ║{RESET}
{GREEN}{BOLD}║                                                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════╝{RESET}
"""

def print_logo_full():
    """Imprime o logo completo."""
    print(LOGO_FULL)

def print_logo_compact():
    """Imprime o logo compacto."""
    return LOGO_COMPACT

def print_welcome_banner():
    """Imprime o banner de boas-vindas."""
    print(WELCOME_BANNER)

def print_logo_alt():
    """Imprime o logo alternativo."""
    print(LOGO_EGSYS_ALT)
