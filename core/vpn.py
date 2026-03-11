"""Gerenciamento de conexões VPN."""
import subprocess
import sys
import time
import os
import pexpect
import pwinput
from config.constants import VPN_CONFIGS, GREEN, RED, YELLOW, CYAN, BOLD, RESET
from core.logger import dprint

class VPNManager:
    def __init__(self):
        self.connected_state = None
    
    def get_os_type(self):
        """Detecta o tipo de sistema operacional."""
        try:
            release_info = subprocess.run(['lsb_release', '-i'], capture_output=True, text=True, timeout=5)
            if 'Ubuntu' in release_info.stdout or 'Debian' in release_info.stdout:
                return 'ubuntu_debian'
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        if os.path.exists('/etc/arch-release'):
            return 'arch'
        
        return 'unknown'
    
    def get_vpn_gateway(self, state_prefix):
        """Obtém o IP do gateway da VPN conectada."""
        vpn_info = VPN_CONFIGS.get(state_prefix)
        if not vpn_info:
            return None
        
        # Para VPNs via nmcli
        if state_prefix in ['SC', 'TO']:
            try:
                vpn_name = vpn_info.get('nmcli_name', '')
                result = subprocess.run(["nmcli", "-t", "-f", "IP4.GATEWAY", "connection", "show", vpn_name],
                                      capture_output=True, text=True, timeout=5)
                gateway = result.stdout.strip().replace('IP4.GATEWAY:', '').strip()
                if gateway and gateway != '--':
                    return gateway
            except:
                pass
        
        # Para VPNs via SNX - tenta pegar gateway da interface tunsnx
        try:
            result = subprocess.run(['ip', 'route', 'show', 'dev', 'tunsnx'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'via' in line:
                    parts = line.split()
                    idx = parts.index('via')
                    if idx + 1 < len(parts):
                        return parts[idx + 1]
        except:
            pass
        
        return None
    
    def verificar_conexao_vpn(self, state_prefix):
        """Verifica se a VPN está realmente conectada usando ping no gateway."""
        vpn_info = VPN_CONFIGS.get(state_prefix)
        if not vpn_info:
            return True  # Sem VPN configurada
        
        # Para VPNs via nmcli
        if state_prefix in ['SC', 'TO']:
            try:
                result = subprocess.run(["nmcli", "-t", "-f", "STATE,NAME", "connection", "show", "--active"],
                                      capture_output=True, text=True, timeout=5)
                vpn_name = vpn_info.get('nmcli_name', '')
                if vpn_name and ":activated" in result.stdout and vpn_name in result.stdout:
                    # Tenta validar com ping no gateway
                    gateway = self.get_vpn_gateway(state_prefix)
                    if gateway:
                        print(f"{CYAN}Validando conectividade com gateway {gateway}...{RESET}")
                        ping_result = subprocess.run(['ping', '-c', '2', '-W', '2', gateway],
                                                   capture_output=True, timeout=5)
                        if ping_result.returncode == 0:
                            print(f"{GREEN}Gateway acessível!{RESET}")
                            return True
                        else:
                            print(f"{YELLOW}Gateway não responde ao ping{RESET}")
                    return True  # Considera conectado mesmo sem ping
            except:
                pass
            return False
        
        # Para VPNs via SNX - múltiplas verificações
        try:
            # Verifica processo snx
            result = subprocess.run(['pgrep', '-f', 'snx'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                # Tenta validar com ping
                gateway = self.get_vpn_gateway(state_prefix)
                if gateway:
                    print(f"{CYAN}Validando conectividade com gateway {gateway}...{RESET}")
                    ping_result = subprocess.run(['ping', '-c', '2', '-W', '2', gateway],
                                               capture_output=True, timeout=5)
                    if ping_result.returncode == 0:
                        print(f"{GREEN}Gateway acessível!{RESET}")
                        return True
                return True
            
            # Verifica interface tunsnx
            result = subprocess.run(['ip', 'link', 'show', 'tunsnx'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
        except:
            pass
        
        return False
    
    def desconectar_todas_vpns(self):
        """Desconecta todas as VPNs ativas para evitar conflitos de IP."""
        print(f"{YELLOW}Desconectando VPNs ativas...{RESET}")
        
        # Desconecta SNX
        try:
            subprocess.run(['snx', '-d'], capture_output=True, timeout=5)
        except:
            pass
        
        # Desconecta VPNs do NetworkManager
        try:
            result = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active"],
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'vpn' in line.lower():
                    vpn_name = line.split(':')[0]
                    subprocess.run(["nmcli", "connection", "down", vpn_name], 
                                 capture_output=True, timeout=5)
        except:
            pass
        
        time.sleep(2)
        print(f"{GREEN}VPNs desconectadas{RESET}")
    
    def conectar_nmcli(self, state_prefix):
        """Conecta VPN via NetworkManager."""
        vpn_info = VPN_CONFIGS.get(state_prefix)
        if not vpn_info or 'nmcli_name' not in vpn_info:
            return False
        
        vpn_name = vpn_info['nmcli_name']
        
        # Verifica se já está conectado
        try:
            check = subprocess.run(["nmcli", "-t", "-f", "STATE,NAME", "connection", "show", "--active"], 
                                 capture_output=True, text=True, timeout=5)
            if vpn_name in check.stdout and ":activated" in check.stdout:
                print(f"[{YELLOW}INFO{RESET}] VPN '{vpn_name}' já está ativa.")
                return True
        except:
            pass
        
        # Verifica se a conexão existe, senão busca por nome similar
        try:
            all_conns = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                                      capture_output=True, text=True, timeout=5)
            
            vpn_found = None
            for line in all_conns.stdout.split('\n'):
                if ':vpn' in line.lower():
                    conn_name = line.split(':')[0]
                    # Busca exata
                    if conn_name == vpn_name:
                        vpn_found = conn_name
                        break
                    # Busca por estado no nome (fallback)
                    if state_prefix.upper() in conn_name.upper():
                        vpn_found = conn_name
            
            if vpn_found:
                vpn_name = vpn_found
                print(f"[{CYAN}INFO{RESET}] Usando conexão VPN: '{vpn_name}'")
            else:
                print(f"[{RED}ERRO{RESET}] Conexão VPN não encontrada para {state_prefix}.")
                print(f"[{YELLOW}DICA{RESET}] Verifique: nmcli connection show | grep vpn")
                return False
        except Exception as e:
            print(f"[{RED}ERRO{RESET}] Falha ao listar conexões: {e}")
            return False
        
        print(f"[{CYAN}INFO{RESET}] Ativando VPN '{vpn_name}'...")
        print(f"[{YELLOW}ATENÇÃO{RESET}] Uma janela do NetworkManager será aberta para solicitar suas credenciais.")
        print(f"[{YELLOW}INFO{RESET}] Por favor, insira seu usuário e senha na janela que abrir.")
        
        try:
            # Usa Popen para não bloquear e permitir janela gráfica, suprimindo saída
            subprocess.Popen(["nmcli", "connection", "up", vpn_name],
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[{RED}ERRO{RESET}] Falha ao ativar VPN: {e}")
            return False
        
        # Aguarda conexão com feedback
        print(f"\n{CYAN}Aguardando conexão VPN...{RESET}")
        start_time = time.time()
        dots = 0
        
        while time.time() - start_time < 30:  # Reduzido de 90 para 30 segundos
            try:
                result = subprocess.run(["nmcli", "-t", "-f", "STATE,NAME", "connection", "show", "--active"],
                                      capture_output=True, text=True, timeout=5)
                
                # Verifica múltiplos formatos de saída
                if vpn_name in result.stdout:
                    # Verifica se está ativada (formato: "activated:VPN PMTO" ou "VPN PMTO:activated")
                    if "activated" in result.stdout.lower() or "ativad" in result.stdout.lower():
                        print(f"\n[{GREEN}SUCESSO{RESET}] VPN '{vpn_name}' ativada!")
                        
                        # Validação rápida com ping no gateway
                        time.sleep(2)  # Aguarda 2s para estabilizar
                        gateway = self.get_vpn_gateway(state_prefix)
                        if gateway:
                            print(f"{CYAN}Validando conectividade com {gateway}...{RESET}")
                            ping_result = subprocess.run(['ping', '-c', '2', '-W', '2', gateway],
                                                       capture_output=True, timeout=5)
                            if ping_result.returncode == 0:
                                print(f"{GREEN}✓ VPN conectada e acessível!{RESET}")
                                return True
                            else:
                                print(f"{YELLOW}⚠ VPN ativa mas gateway não responde{RESET}")
                        return True
            except:
                pass
            
            # Feedback visual
            dots = (dots + 1) % 4
            print(f"\rVerificando conexão{'.' * dots}   ", end='', flush=True)
            time.sleep(2)  # Reduzido de 3 para 2 segundos
        
        print(f"\n[{RED}ERRO{RESET}] Timeout na conexão VPN. A conexão não foi estabelecida a tempo.")
        return False
    
    def conectar_snx(self, state_prefix):
        """Conecta VPN via SNX."""
        vpn_info = VPN_CONFIGS.get(state_prefix)
        if not vpn_info:
            return False
        
        # Desconecta VPNs ativas
        try:
            subprocess.run(['snx', '-d'], check=True, capture_output=True, timeout=5)
        except:
            pass
        
        username = input(f"{BOLD}Usuário VPN: {RESET}")
        
        if state_prefix == 'PR':
            command = f"snx -r -s {vpn_info['address']} -u {username} /ldap -r yes"
        else:
            command = f"{vpn_info['command']}{username}"
        
        try:
            child = pexpect.spawn(command, timeout=30, encoding='utf-8')
            child.logfile_read = sys.stdout
            
            index = child.expect([r'Please enter your password:', r'SNX: Authentication failed', 
                                r'SNX: Connection was successful', pexpect.EOF], timeout=60)
            
            if index == 0:
                password = pwinput.pwinput(prompt="Senha VPN: ", mask='*')
                child.sendline(password)
                
                final = child.expect([r'SNX: Connection was successful', r'SNX: Authentication failed', pexpect.EOF], timeout=60)
                
                if final == 0 or (final == 2 and "connected" in child.before):
                    print(f"\n{GREEN}VPN conectada!{RESET}")
                    child.close()
                    return True
            
            child.close()
            return False
        except Exception as e:
            print(f"{RED}Erro na conexão VPN: {e}{RESET}")
            return False
    
    def conectar(self, state_prefix):
        """Conecta à VPN do estado especificado."""
        if state_prefix not in VPN_CONFIGS:
            return True
        
        # Desconecta outras VPNs antes de conectar
        self.desconectar_todas_vpns()
        
        if state_prefix in ['SC', 'TO']:
            success = self.conectar_nmcli(state_prefix)
            if success:
                self.connected_state = state_prefix
        else:
            success = self.conectar_snx(state_prefix)
            if success:
                self.connected_state = state_prefix
                print(f"{GREEN}VPN {state_prefix} conectada e verificada{RESET}")
        
        return success
