"""Gerenciamento de serviços (Docker, SO, Mobile)."""
import subprocess
import os
from config.constants import SERVICE_LIST, MOBILE_SERVICE_PATHS, GREEN, RED, YELLOW, BOLD, RESET
from core.logger import log_auditoria, dprint

class ServiceManager:
    def __init__(self):
        self.selected_state_prefix = None
    
    def run_remote_command(self, host, command, verbose=True):
        """Executa comando remoto via SSH."""
        if verbose:
            print(f"\n[INFO] Executando em '{host}': {command}")
        
        dprint(f"Comando remoto em '{host}': {command}")
        
        timeout_value = 90 if self.selected_state_prefix == 'PR' else 30
        ssh_command = ["ssh", "-o", "StrictHostKeyChecking=no", host, command]
        
        try:
            result = subprocess.run(ssh_command, capture_output=True, text=True, 
                                  timeout=timeout_value, env=os.environ)
            
            if result.returncode == 0:
                if verbose:
                    print(f"[{GREEN}SUCESSO{RESET}] Comando executado.")
                log_auditoria("REMOTE_EXEC", "SUCCESS", host, f"cmd='{command}'")
                return result.stdout, True
            else:
                error_msg = result.stderr.strip() or f"Código {result.returncode}"
                if verbose:
                    print(f"[{RED}ERRO{RESET}] {error_msg}")
                log_auditoria("REMOTE_EXEC", "FAILURE", host, f"cmd='{command}', error='{error_msg}'")
                return result.stderr, False
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"[{RED}ERRO{RESET}] Timeout em '{host}'")
            return "", False
        except Exception as e:
            if verbose:
                print(f"[{RED}ERRO{RESET}] {e}")
            return "", False
    
    def get_privileged_command(self, command):
        """Adiciona sudo se necessário."""
        cmd_name = os.path.basename(command.split()[0])
        privileged = ["docker", "systemctl", "du", "df", "find", "mkdir", "chmod"]
        
        if "service.in" in cmd_name or any(c in cmd_name for c in privileged):
            return f"sudo {command}"
        return command
    
    def check_disk_space(self, hosts):
        """Verifica espaço em disco."""
        for host in hosts:
            print(f"\n--- {host} ---")
            output, _ = self.run_remote_command(host, "df -h")
            if output:
                print(output)
    
    def get_systemctl_status(self, host, service_name):
        """Verifica status de serviço systemctl."""
        command = f"systemctl is-active {service_name}"
        _, success = self.run_remote_command(host, self.get_privileged_command(command), verbose=False)
        
        if success:
            return f"{GREEN}{BOLD}ATIVO{RESET}"
        else:
            return f"{RED}{BOLD}INATIVO{RESET}"
    
    def manage_systemctl_service(self, hosts, service_name, action):
        """Gerencia serviço systemctl."""
        for host in hosts:
            command = f"systemctl {action} {service_name}"
            self.run_remote_command(host, self.get_privileged_command(command))
    
    def list_docker_containers(self, host):
        """Lista containers Docker."""
        command = "docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}'"
        output, success = self.run_remote_command(host, self.get_privileged_command(command), verbose=False)
        
        if not success:
            return []
        
        containers = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) == 3:
                    containers.append({
                        'id': parts[0],
                        'name': parts[1],
                        'status': parts[2]
                    })
        return containers
    
    def manage_docker_container(self, host, container_id, action):
        """Gerencia container Docker."""
        command = f"docker {action} {container_id}"
        return self.run_remote_command(host, self.get_privileged_command(command))
    
    def find_mobile_services(self, host):
        """Busca serviços mobile Java."""
        host_key = host.lower()
        if host_key not in MOBILE_SERVICE_PATHS:
            return []
        
        services = []
        for service_dir in MOBILE_SERVICE_PATHS[host_key]:
            base_path = os.path.join("/var/servicos", service_dir)
            command = f"find {base_path} -type f -name 'service.in' 2>/dev/null"
            output, success = self.run_remote_command(host, self.get_privileged_command(command), verbose=False)
            
            if success and output.strip():
                for path in output.strip().split('\n'):
                    services.append({
                        'name': os.path.basename(os.path.dirname(path)),
                        'path': path,
                        'host': host
                    })
        return services
    
    def manage_mobile_service(self, service_info, action):
        """Gerencia serviço mobile."""
        command = f"{service_info['path']} {action}"
        return self.run_remote_command(service_info['host'], self.get_privileged_command(command))
