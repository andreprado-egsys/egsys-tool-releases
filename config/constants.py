"""Constantes e configurações do sistema."""
import os

# Versão do sistema
VERSION = "2.1.2"

# Cores ANSI
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
MAGENTA = "\033[95m"
GRAY = "\033[90m"

# Ícones contextuais
ICONS = {
    'success': '✓',
    'error': '✗',
    'warning': '⚠',
    'info': 'ℹ',
    'loading': '⟳',
    'server': '🖥️',
    'docker': '🐳',
    'vpn': '🔐',
    'ssh': '🔑',
    'monitor': '📊',
    'log': '📝',
    'time': '⏱️',
    'user': '👤',
    'network': '🌐',
    'database': '🗄️',
    'mobile': '📱',
    'api': '🔌',
    'home': '🏠',
    'arrow': '➤'
}

# Configurações de VPN
VPN_CONFIGS = {
    'SC': {
        'address': '200.19.221.254:10443',
        'command': 'snx -r -s 200.19.221.254:10443 -u',
        'nmcli_name': 'VPN PMSC',
        'server_cert_pin': 'pin-sha256:PLACEHOLDER_PIN_SC',
        'ssh_key': '~/.ssh/id_rsa_sc'
    },
    'TO': {
        'address': 'vpn.to.gov.br',
        'command': 'snx -r -s vpn.to.gov.br -u',
        'nmcli_name': 'VPN PMTO',
        'server_cert_pin': 'pin-sha256:Finj/GYZJz1mKotveubenfv8S+Xzn1mcctHTPfOW5nY=',
        'ssh_key': '~/.ssh/id_rsa_to'
    },
    'PR': {'address': 'acessoremoto.pr.gov.br', 'command': 'snx -r -s acessoremoto.pr.gov.br -u /ldap -r yes', 'ssh_key': '~/.ssh/id_rsa_pr'},
    'RO': {'address': '131.72.155.42', 'command': 'snx -r -s 131.72.155.42 -u', 'ssh_key': '~/.ssh/id_rsa_ro'},
    'MT': {'address': 'remoto.mti.mt.gov.br', 'command': 'snx -r -s remoto.mti.mt.gov.br -u', 'ssh_key': '~/.ssh/id_rsa_mt'}
}

# Chaves SSH por estado (para estados sem VPN)
SSH_KEYS = {
    'AM': '~/.ssh/id_rsa_am',
    'GM': '~/.ssh/id_rsa_gm',
    # Adicione outros estados conforme necessário
}

# Mapeamento de hosts mobile
MOBILE_SERVICE_PATHS = {
    "ro-mobile-prd": ["ServicoPMRORun/", "ServicosPMROGestaoRun2/", "ServicoSYSAit/", "SYSAitIntegrationRun_OLD/", "SystemGlobalProviderRun/"],
    "ro-mobile-hml": ["ServicoPMRORun/", "ServicosPMROGestaoRun2/", "ServicoSYSAit/", "SYSAitIntegrationRun/", "SystemGlobalProviderRun/"],
    "pr-mobile-prd": ["ServicoPMRun/", "ServicoSYSAIT/", "SystemGlobalProviderRun/"],
    "pr-mobile-hml": ["ServicoGestao/", "ServicoPMRun/", "ServicoSYSAIT/", "SystemGlobalProviderRun/"],
    "pr-mobile3-hml": ["ServicoGestao/", "ServicoPMRun/", "ServicoSYSAIT/", "SystemGlobalProviderRun/"],
    "mt-mobile-prd": ["ServicoPMGestaoRun/", "ServicoPMRun/", "ServicoSYSAit/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "mt-mobile-hml": ["ServicoPMGestaoRun/", "ServicoPMRun/", "ServicoSYSAit/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "am-mobile-prd": ["ServicoPMRun/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "am-mobile-hml": ["ServicoPMRun/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "am-mobile-hml-dc": ["ServicoPMRun/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "gm-cloud-mobile-prd": ["siseg-gm/", "system-email-sender/", "system-global-provider/"],
    "gm-cloud-mobile-hml": ["siseg-gm/", "system-email-sender/", "system-global-provider/"],
    "sc-mobile-prd": ["ServicosPMSCRun/", "SystemEmailSenderPMSCRun/", "SystemGlobalProviderRun/"],
    "sc-mobile-hml": ["ServicosPMSCGestaoRun/", "ServicosPMSCRun/", "syspm-integracao-eproc-build/", "SystemEmailSenderPMSCRun/", "SystemGlobalProviderRun/"],
    "to-mobile-prd": ["ServicoPMGestaoRun/", "ServicoPMRun/", "ServicoSYSAit/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"],
    "to-mobile-hml": ["ServicoPMGestaoRun/", "ServicoPMRun/", "ServicoSYSAit/", "SystemEmailSenderRun/", "SystemGlobalProviderRun/"]
}

# Serviços do SO
SERVICE_LIST = [
    ("nginx", "Servidor Web Nginx"),
    ("apache2", "Servidor Web Apache"),
    ("mysql", "Banco de dados MySQL/MariaDB"),
    ("postgresql", "Banco de dados PostgreSQL"),
    ("php7.4-fpm", "Processador PHP 7.4"),
    ("docker", "Serviço de Container Docker")
]

# Configurações de log
DEBUG_LOG_ENABLED = False
DEBUG_LOG_FILE = os.path.expanduser("~/logs_scriptN1/egsys_debug.log")
LOG_PATTERNS_FILE = 'egsys_log_patterns.json'

# Senha de administrador
PASSWORD_SAFEGUARD = "egsys_salvaguarda_123"
ADMIN_PASSWORD_HASH = "8ee58327417ff1edeb9257f6e90f0cda367c9bf7050a86ec324437d8dc0594f9"
ADMIN_USER = "egsys_admin"

# Chave SSH padrão
DEFAULT_SSH_KEY = "~/.ssh/id_rsa"

# Tipos de servidor e padrões de identificação
SERVER_TYPES = {
    'mobile': {
        'patterns': ['mobile', '-app'],
        'name': 'Servidor Mobile',
        'icon': '📱'
    },
    'web': {
        'patterns': ['web', '-web', 'nginx', 'apache'],
        'name': 'Servidor Web',
        'icon': '🌐'
    },
    'bd': {
        'patterns': ['bd', 'db', 'database', 'postgres', 'mysql', 'mariadb'],
        'name': 'Servidor Banco de Dados',
        'icon': '🗄️'
    },
    'api': {
        'patterns': ['api', '-api', 'rest', 'backend'],
        'name': 'Servidor API',
        'icon': '🔌'
    }
}

# Comandos disponíveis por tipo de servidor
SERVER_COMMANDS = {
    'mobile': [
        ('disk', 'Checar espaço em disco', 'df -h'),
        ('services', 'Gerenciar serviços do SO', None),
        ('docker', 'Gerenciar containers Docker', None),
        ('mobile_services', 'Gerenciar serviços Mobile', None),
        ('logs', 'Buscar nos logs', None),
        ('monitor', 'Monitoramento (top/htop)', None),
        ('memory', 'Uso de memória', 'free -h'),
        ('uptime', 'Tempo de atividade', 'uptime')
    ],
    'web': [
        ('disk', 'Checar espaço em disco', 'df -h'),
        ('services', 'Gerenciar serviços do SO', None),
        ('docker', 'Gerenciar containers Docker', None),
        ('logs', 'Buscar nos logs', None),
        ('monitor', 'Monitoramento (top/htop)', None),
        ('connections', 'Conexões ativas (detalhadas)', 'ss -tunap | grep ESTAB'),
        ('memory', 'Uso de memória', 'free -h'),
        ('uptime', 'Tempo de atividade', 'uptime')
    ],
    'bd': [
        ('disk', 'Checar espaço em disco', 'df -h'),
        ('services', 'Gerenciar serviços do SO', None),
        ('docker', 'Gerenciar containers Docker', None),
        ('logs', 'Buscar nos logs', None),
        ('monitor', 'Monitoramento (top/htop)', None),
        ('backup', 'Verificar backups', 'ls -lh /backup/'),
        ('memory', 'Uso de memória', 'free -h'),
        ('uptime', 'Tempo de atividade', 'uptime')
    ],
    'api': [
        ('disk', 'Checar espaço em disco', 'df -h'),
        ('services', 'Gerenciar serviços do SO', None),
        ('docker', 'Gerenciar containers Docker', None),
        ('logs', 'Buscar nos logs', None),
        ('monitor', 'Monitoramento (top/htop)', None),
        ('processes', 'Listar processos', 'ps aux | grep -E "node|python|java"'),
        ('endpoints', 'Testar endpoints', 'curl -I http://localhost/health'),
        ('memory', 'Uso de memória', 'free -h'),
        ('connections', 'Conexões ativas (detalhadas)', 'ss -tunap | grep ESTAB'),
        ('uptime', 'Tempo de atividade', 'uptime')
    ],
    'default': [
        ('disk', 'Checar espaço em disco', 'df -h'),
        ('services', 'Gerenciar serviços do SO', None),
        ('docker', 'Gerenciar Docker', None),
        ('logs', 'Buscar nos logs', None),
        ('monitor', 'Monitoramento (top/htop)', None),
        ('memory', 'Uso de memória', 'free -h'),
        ('processes', 'Processos ativos', 'top -bn1 | head -20'),
        ('uptime', 'Tempo de atividade', 'uptime')
    ]
}
