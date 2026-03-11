"""Gerenciamento do agente SSH."""
import subprocess
import os
import pexpect
import pwinput
from config.constants import GREEN, RED, YELLOW, RESET, BOLD, VPN_CONFIGS, SSH_KEYS, DEFAULT_SSH_KEY

class SSHAgent:
    def __init__(self):
        self.agent_pid = None
        self.agent_sock = None
        self.loaded_keys = set()
    
    def is_agent_running(self):
        """Verifica se o agente SSH está rodando."""
        return 'SSH_AUTH_SOCK' in os.environ and 'SSH_AGENT_PID' in os.environ
    
    def start_agent(self):
        """Inicia o agente SSH se não estiver rodando."""
        if self.is_agent_running():
            return True
        
        try:
            result = subprocess.run(['ssh-agent', '-s'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'SSH_AUTH_SOCK' in line:
                        sock = line.split('=')[1].split(';')[0]
                        os.environ['SSH_AUTH_SOCK'] = sock
                        self.agent_sock = sock
                    elif 'SSH_AGENT_PID' in line:
                        pid = line.split('=')[1].split(';')[0]
                        os.environ['SSH_AGENT_PID'] = pid
                        self.agent_pid = pid
                return True
        except Exception as e:
            print(f"{RED}Erro ao iniciar agente SSH: {e}{RESET}")
        return False
    
    def list_available_keys(self):
        """Lista todas as chaves SSH disponíveis no diretório ~/.ssh."""
        ssh_dir = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh_dir):
            return []
        
        keys = []
        for file in os.listdir(ssh_dir):
            file_path = os.path.join(ssh_dir, file)
            # Ignora arquivos .pub, known_hosts, config, etc
            if (os.path.isfile(file_path) and 
                not file.endswith('.pub') and 
                not file in ['known_hosts', 'known_hosts.old', 'config', 'config.bkp', 'agent'] and
                not file.endswith('.txt')):
                keys.append(file_path)
        return sorted(keys)
    
    def select_ssh_key(self, state_prefix):
        """Permite ao usuário selecionar uma chave SSH."""
        print(f"\n{BOLD}Selecione a chave SSH para {state_prefix}:{RESET}")
        
        available_keys = self.list_available_keys()
        
        if not available_keys:
            print(f"{RED}Nenhuma chave SSH encontrada em ~/.ssh{RESET}")
            return None
        
        # Mostra opções
        for idx, key in enumerate(available_keys, 1):
            key_name = os.path.basename(key)
            print(f"{YELLOW}{idx}.{RESET} {key_name}")
        
        print(f"{YELLOW}0.{RESET} Cancelar")
        
        while True:
            try:
                choice = input(f"\n{BOLD}Escolha (0-{len(available_keys)}): {RESET}").strip()
                
                if choice == '0':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(available_keys):
                    return available_keys[idx]
                else:
                    print(f"{RED}Opção inválida{RESET}")
            except (ValueError, KeyboardInterrupt):
                print(f"{RED}\nOpção inválida{RESET}")
    
    def get_key_for_state(self, state_prefix):
        """Retorna o caminho da chave SSH para o estado."""
        # SEMPRE mostra menu de seleção para o usuário escolher
        return self.select_ssh_key(state_prefix)
    
    def is_key_loaded(self, key_path):
        """Verifica se a chave já está carregada no agente."""
        try:
            result = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True, timeout=5)
            key_name = os.path.basename(key_path)
            return key_name in result.stdout or key_path in self.loaded_keys
        except:
            return False
    
    def add_key_for_state(self, state_prefix):
        """Adiciona chave SSH do estado ao agente."""
        if not self.is_agent_running():
            if not self.start_agent():
                return False
        
        key_path = self.get_key_for_state(state_prefix)
        
        if not key_path or not os.path.exists(key_path):
            print(f"{RED}Nenhuma chave SSH selecionada ou encontrada{RESET}")
            return False
        
        # Verifica se já está carregada
        if self.is_key_loaded(key_path):
            print(f"{GREEN}Chave SSH do estado {state_prefix} já carregada{RESET}")
            return True
        
        print(f"\n{BOLD}Carregando chave SSH para {state_prefix}...{RESET}")
        print(f"Chave: {key_path}")
        
        try:
            child = pexpect.spawn(f'ssh-add {key_path}', timeout=30, encoding='utf-8')
            
            index = child.expect([r'Enter passphrase.*:', r'Identity added:', pexpect.EOF], timeout=10)
            
            if index == 0:
                passphrase = pwinput.pwinput(prompt="Senha da chave SSH: ", mask='*')
                child.sendline(passphrase)
                
                result = child.expect([r'Identity added:', r'Bad passphrase', pexpect.EOF], timeout=10)
                
                if result == 0:
                    print(f"{GREEN}Chave SSH adicionada com sucesso!{RESET}")
                    self.loaded_keys.add(key_path)
                    child.close()
                    return True
                else:
                    print(f"{RED}Senha incorreta{RESET}")
                    child.close()
                    return False
            elif index == 1:
                print(f"{GREEN}Chave SSH adicionada!{RESET}")
                self.loaded_keys.add(key_path)
                child.close()
                return True
            
            child.close()
            return False
        except Exception as e:
            print(f"{RED}Erro ao adicionar chave SSH: {e}{RESET}")
            return False
    
    def stop_agent(self):
        """Para o agente SSH."""
        if self.agent_pid:
            try:
                subprocess.run(['kill', self.agent_pid], timeout=5)
            except:
                pass
