"""Funções auxiliares e utilitárias."""
import os
import re
from datetime import datetime
from config.constants import GREEN, BOLD, RESET, SERVER_TYPES, CYAN
from config.logo import print_logo_compact

def detect_server_type(hostname):
    """Detecta o tipo de servidor baseado no hostname."""
    hostname_lower = hostname.lower()
    
    for server_type, config in SERVER_TYPES.items():
        for pattern in config['patterns']:
            if pattern in hostname_lower:
                return server_type
    
    return 'default'

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width():
    """Retorna largura do terminal."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def print_banner(title):
    """Imprime banner com título e logo discreto."""
    width = get_terminal_width()
    
    # Logo compacto com SAPA
    logo_text = f"{GREEN}{BOLD}egSYS{RESET} {CYAN}SAPA{RESET}"
    logo_len = 10  # "egSYS SAPA" sem cores
    
    # Título
    title_display = f"{BOLD}{title.upper()}{RESET}"
    title_len = len(title.upper())
    
    # Calcula espaçamento
    total_content = title_len + logo_len + 4  # +4 para espaços
    padding_left = (width - total_content) // 2
    padding_right = width - total_content - padding_left
    
    print("═" * width)
    print(f"{' ' * padding_left}{title_display}    {logo_text}{' ' * padding_right}")
    print("═" * width + "\n")

def print_menu_header(title, show_breadcrumb=True):
    """Imprime cabeçalho de menu com logo e breadcrumb."""
    from config.constants import VERSION
    clear_screen()
    print_banner(title)
    
    # Breadcrumb
    if show_breadcrumb:
        breadcrumb = get_breadcrumb()
        if breadcrumb:
            print(f"{breadcrumb}\n")
    
    # Informações do sistema (data/hora e versão)
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    width = get_terminal_width()
    
    # Linha de informações
    info_line = f"{CYAN}Horário: {current_time}{RESET}  |  {GREEN}Versão: {VERSION}{RESET}"
    print(info_line)
    print("─" * width)

def press_enter_to_continue():
    """Aguarda Enter."""
    input(f"\n{BOLD}Pressione Enter para continuar...{RESET}")

def parse_selection_input(input_string, max_value):
    """Analisa entrada de seleção múltipla (ex: 1 3 5-7)."""
    selected = set()
    parts = input_string.replace(' ', ',').split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if start > end:
                    start, end = end, start
                for i in range(start, end + 1):
                    if 1 <= i <= max_value:
                        selected.add(str(i))
            except ValueError:
                continue
        else:
            try:
                num = int(part)
                if 1 <= num <= max_value:
                    selected.add(str(num))
            except ValueError:
                continue
    
    return sorted(list(selected), key=int)

def get_ssh_config_hosts(config_path):
    """Lê hosts do arquivo SSH config."""
    hosts_by_state = {}
    standalone_hosts = []
    all_hosts = []
    
    if not os.path.exists(config_path):
        return None, None, None
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Host '):
                host_alias = line.split()[1]
                if '*' not in host_alias:
                    all_hosts.append(host_alias)
                    match = re.match(r'^([a-zA-Z0-9]+)-', host_alias)
                    if match:
                        prefix = match.group(1).upper()
                        if prefix not in hosts_by_state:
                            hosts_by_state[prefix] = []
                        hosts_by_state[prefix].append(host_alias)
                    else:
                        standalone_hosts.append(host_alias)
    
    # Move hosts únicos para standalone
    prefixes_to_remove = []
    for prefix, hosts in hosts_by_state.items():
        if len(hosts) == 1:
            standalone_hosts.append(hosts[0])
            prefixes_to_remove.append(prefix)
    
    for prefix in prefixes_to_remove:
        del hosts_by_state[prefix]
    
    standalone_hosts.sort()
    
    return hosts_by_state, standalone_hosts, all_hosts


def print_footer():
    """Imprime rodapé padronizado."""
    width = get_terminal_width()
    print("─" * width)
    footer_text = f"{CYAN}egSYS SAPA{RESET} - Sistema de Avaliação e Performance de Ambientes"
    print(f"{footer_text:^{width}}")

def print_separator(char="─"):
    """Imprime linha separadora."""
    print(char * get_terminal_width())


# Breadcrumb navigation
_breadcrumb_stack = []

def push_breadcrumb(item):
    """Adiciona item ao breadcrumb."""
    _breadcrumb_stack.append(item)

def pop_breadcrumb():
    """Remove último item do breadcrumb."""
    if _breadcrumb_stack:
        _breadcrumb_stack.pop()

def clear_breadcrumb():
    """Limpa breadcrumb."""
    _breadcrumb_stack.clear()

def get_breadcrumb():
    """Retorna breadcrumb formatado."""
    from config.constants import CYAN, GRAY, RESET, ICONS
    if not _breadcrumb_stack:
        return ""
    
    icon = ICONS.get('home', '🏠')
    arrow = ICONS.get('arrow', '→')
    
    parts = [f"{CYAN}{icon} Home{RESET}"]
    for item in _breadcrumb_stack:
        parts.append(f"{GRAY}{arrow}{RESET} {item}")
    
    return " ".join(parts)

def icon(name, fallback=""):
    """Retorna ícone por nome com fallback."""
    from config.constants import ICONS
    return ICONS.get(name, fallback)
