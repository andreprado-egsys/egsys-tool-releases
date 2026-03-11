"""Sistema de logging e auditoria."""
import os
from datetime import datetime
from config.constants import DEBUG_LOG_ENABLED, DEBUG_LOG_FILE, BLUE, RESET

class Logger:
    def __init__(self):
        self.audit_log_file = ''
        self.current_user = ''
        self.debug_enabled = DEBUG_LOG_ENABLED
        self._ensure_audit_dir()
    
    def _ensure_audit_dir(self):
        """Garante que o diretório de auditoria existe."""
        try:
            audit_dir = os.path.expanduser("~/logs_scriptN1")
            if not os.path.exists(audit_dir):
                os.makedirs(audit_dir, exist_ok=True)
                os.chmod(audit_dir, 0o777)
            self.audit_log_file = os.path.join(audit_dir, "egsys_audit.log")
        except Exception:
            pass
    
    def _ensure_debug_dir(self):
        """Garante que o diretório de debug existe."""
        try:
            d = os.path.dirname(DEBUG_LOG_FILE)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                os.chmod(d, 0o777)
        except Exception:
            pass
    
    def set_user(self, username):
        """Define usuário atual para auditoria."""
        self.current_user = username
    
    def dprint(self, message):
        """Log de debug."""
        if not self.debug_enabled:
            return
        
        message = str(message) if not isinstance(message, str) else message
        print(f"{BLUE}[DEBUG]{RESET} {message}")
        
        try:
            self._ensure_debug_dir()
            with open(DEBUG_LOG_FILE, "a") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {message}\n")
        except Exception:
            pass
    
    def log_action(self, action_description, host='local', status='success', details=''):
        """Registra ação no log de auditoria."""
        if not self.audit_log_file:
            self._ensure_audit_dir()
        
        try:
            with open(self.audit_log_file, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = (
                    f"[{timestamp}] | "
                    f"user={self.current_user} | "
                    f"host={host} | "
                    f"action={action_description} | "
                    f"status={status}"
                )
                if details:
                    log_entry += f" | details={details}"
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Aviso: Falha ao escrever no log. Erro: {e}")
    
    def log_command(self, host, command, status='executed'):
        """Log específico para comandos SSH."""
        self.log_action(f"SSH_COMMAND: {command}", host=host, status=status)
    
    def log_vpn(self, state, action, status='success'):
        """Log específico para VPN."""
        self.log_action(f"VPN_{action.upper()}: {state}", status=status)
    
    def log_service(self, host, service, action, status='success'):
        """Log específico para serviços."""
        self.log_action(f"SERVICE_{action.upper()}: {service}", host=host, status=status)
    
    def log_docker(self, host, container, action, status='success'):
        """Log específico para Docker."""
        self.log_action(f"DOCKER_{action.upper()}: {container}", host=host, status=status)
    
    def log_auditoria(self, acao, status, host='local', detalhes='N/A'):
        """Log de auditoria (compatibilidade)."""
        self.log_action(acao, host=host, status=status, details=detalhes)

# Instância global
_logger = Logger()

def set_user(username):
    """Define usuário para auditoria."""
    _logger.set_user(username)

def log_action(action, host='local', status='success', details=''):
    """Função helper para log de ação."""
    _logger.log_action(action, host, status, details)

def log_command(host, command, status='executed'):
    """Função helper para log de comando."""
    _logger.log_command(host, command, status)

def log_vpn(state, action, status='success'):
    """Função helper para log VPN."""
    _logger.log_vpn(state, action, status)

def log_service(host, service, action, status='success'):
    """Função helper para log de serviço."""
    _logger.log_service(host, service, action, status)

def log_docker(host, container, action, status='success'):
    """Função helper para log Docker."""
    _logger.log_docker(host, container, action, status)

def dprint(message):
    """Função helper para debug print."""
    _logger.dprint(message)

def log_auditoria(acao, status, host='local', detalhes='N/A'):
    """Função helper para log de auditoria."""
    _logger.log_auditoria(acao, status, host, detalhes)
