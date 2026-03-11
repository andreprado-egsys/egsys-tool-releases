"""Interface CLI do egSYS Tool."""
import sys
import re
from datetime import datetime
from config.constants import *
from config.constants import VERSION
from core.auth import AuthManager
from core.vpn import VPNManager
from core.ssh_agent import SSHAgent
from core.services import ServiceManager
from core.monitoring import MonitoringManager
from core.admin import AdminManager
from core.help import HelpManager
from core.logger import log_action, set_user, log_command, log_vpn, log_service, log_docker
from utils.helpers import *

class CLIInterface:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.vpn_manager = VPNManager()
        self.ssh_agent = SSHAgent()
        self.service_manager = ServiceManager()
        self.monitoring_manager = MonitoringManager()
        self.admin_manager = AdminManager()
        self.help_manager = HelpManager()
        self.selected_hosts = []
        self.selected_state = None
        self.state_hosts = []
    
    def run(self):
        """Executa a interface CLI."""
        from config.logo import print_welcome_banner
        from utils.helpers import clear_screen, press_enter_to_continue
        
        # Banner de boas-vindas
        clear_screen()
        print_welcome_banner()
        press_enter_to_continue()
        
        # Login
        print_menu_header("AUTENTICAÇÃO")
        user = self.auth_manager.realizar_login()
        if not user:
            print(f"\n{RED}Falha na autenticação. Encerrando.{RESET}")
            sys.exit(1)
        
        # Configura usuário no logger para auditoria
        set_user(user)
        log_action("LOGIN", status="success")
        
        print(f"\n{GREEN}Bem-vindo, {user}!{RESET}")
        press_enter_to_continue()
        
        # Loop principal
        while True:
            if not self.selected_state:
                # Seleciona estado
                if not self.show_state_selection():
                    break
            elif not self.selected_hosts:
                # Seleciona hosts dentro do estado
                if self.selected_state == 'AVULSO':
                    # Host avulso já foi selecionado, vai direto para menu
                    pass
                elif not self.show_host_selection_in_state():
                    # Voltar = sair do estado
                    self.selected_state = None
                    continue
            
            if self.selected_hosts:
                # Menu de ações
                if not self.show_main_menu():
                    # Voltar = limpa hosts e estado se for avulso
                    self.selected_hosts = []
                    if self.selected_state == 'AVULSO':
                        self.selected_state = None
    
    def show_state_selection(self):
        """Mostra menu de seleção de estados."""
        from utils.helpers import clear_breadcrumb, push_breadcrumb
        
        clear_breadcrumb()  # Limpa breadcrumb ao voltar ao início
        
        ssh_config = os.path.expanduser("~/.ssh/config")
        hosts_by_state, standalone, all_hosts = get_ssh_config_hosts(ssh_config)
        
        if hosts_by_state is None:
            print(f"{RED}Erro ao ler configuração SSH{RESET}")
            return False
        
        print_menu_header("SELEÇÃO DE ESTADO")
        
        # Mostra grupos de estado
        print(f"{BOLD}GRUPOS DE ESTADO:{RESET}")
        numbered = {}
        num = 1
        
        for state in sorted(hosts_by_state.keys()):
            vpn_tag = " [VPN]" if state in VPN_CONFIGS else ""
            print(f"  {num}) {state} ({len(hosts_by_state[state])} servidores){vpn_tag}")
            numbered[str(num)] = {'type': 'state', 'data': state, 'hosts': hosts_by_state[state]}
            num += 1
        
        # Mostra hosts avulsos
        print(f"\n{BOLD}HOSTS AVULSOS:{RESET}")
        for host in standalone:
            print(f"  {num}) {host}")
            numbered[str(num)] = {'type': 'host', 'data': host}
            num += 1
        
        print(f"\n{RED}Q{RESET} - Sair")
        print(f"{MAGENTA}A{RESET} - Menu Administrativo")
        print(f"{YELLOW}H{RESET} - Ajuda")
        
        choice = input("\nSua escolha: ")
        
        if choice.upper() == 'Q':
            log_action("LOGOUT", status="success")
            return False
        
        if choice.upper() == 'A':
            if self.admin_manager.validate_admin():
                log_action("ADMIN_ACCESS", status="granted")
                self.admin_manager.show_admin_menu()
            else:
                log_action("ADMIN_ACCESS", status="denied")
            return True
        
        if choice.upper() == 'H':
            log_action("HELP_ACCESS")
            self.help_manager.show_help_menu()
            return True
        
        if choice in numbered:
            item = numbered[choice]
            if item['type'] == 'state':
                self.selected_state = item['data']
                self.state_hosts = item['hosts']
                
                # Adiciona ao breadcrumb
                push_breadcrumb(self.selected_state)
                
                # Configura agente SSH para o estado
                print(f"\n{CYAN}Configurando acesso ao estado {self.selected_state}...{RESET}")
                if not self.ssh_agent.add_key_for_state(self.selected_state):
                    print(f"{RED}Falha ao carregar chave SSH{RESET}")
                    press_enter_to_continue()
                    self.selected_state = None
                    return True
                
                # Conecta VPN se necessário (apenas se não estiver conectado)
                if self.selected_state in VPN_CONFIGS:
                    if self.vpn_manager.connected_state != self.selected_state:
                        log_vpn(self.selected_state, 'connect_attempt')
                        if not self.vpn_manager.conectar(self.selected_state):
                            log_vpn(self.selected_state, 'connect', status='failed')
                            print(f"{RED}Falha na conexão VPN{RESET}")
                            press_enter_to_continue()
                            self.selected_state = None
                            return True
                        log_vpn(self.selected_state, 'connect', status='success')
                    else:
                        print(f"{GREEN}VPN {self.selected_state} já conectada{RESET}")
            else:
                # Host avulso - usa chave padrão e vai direto para menu
                if not self.ssh_agent.add_key_for_state('DEFAULT'):
                    print(f"{YELLOW}Aviso: Chave SSH não carregada{RESET}")
                self.selected_hosts = [item['data']]
                self.selected_state = 'AVULSO'  # Define estado para não voltar ao menu de estados
        
        return True
    
    def show_host_selection_in_state(self):
        """Mostra menu de seleção de hosts dentro do estado."""
        from utils.helpers import push_breadcrumb, pop_breadcrumb
        
        print_menu_header(f"SELEÇÃO DE SERVIDORES - {self.selected_state}")
        
        print(f"{BOLD}Estado: {self.selected_state}{RESET}")
        if self.selected_state in VPN_CONFIGS:
            print(f"{GREEN}VPN: Conectada{RESET}")
        print(f"{GREEN}Chave SSH: Carregada{RESET}\n")
        
        for i, host in enumerate(self.state_hosts, 1):
            print(f"  {i}) {host}")
        
        print(f"\n{YELLOW}V{RESET} - Voltar (sair do estado)")
        choice = input("\nDigite os números (ex: 1 3 5): ")
        
        if choice.upper() == 'V':
            return False
        
        selected = []
        for num in choice.split():
            if num.isdigit() and 1 <= int(num) <= len(self.state_hosts):
                selected.append(self.state_hosts[int(num) - 1])
        
        if selected:
            self.selected_hosts = selected
        
        return True
    
    def show_main_menu(self):
        """Mostra menu principal."""
        from config.constants import SERVER_COMMANDS, SERVER_TYPES
        from utils.helpers import detect_server_type
        
        # Detecta tipo do primeiro servidor
        server_type = detect_server_type(self.selected_hosts[0])
        commands = SERVER_COMMANDS.get(server_type, SERVER_COMMANDS['default'])
        
        print_menu_header("MENU PRINCIPAL")
        
        print(f"{BOLD}Estado: {self.selected_state}{RESET}")
        
        # Mostra tipo de servidor
        if server_type != 'default':
            type_info = SERVER_TYPES[server_type]
            print(f"{BOLD}Tipo: {type_info['icon']} {type_info['name']}{RESET}")
        
        print(f"{BOLD}Servidores selecionados:{RESET}")
        for h in self.selected_hosts:
            print(f" - {h}")
        
        print(f"\n{BOLD}COMANDOS DISPONÍVEIS:{RESET}")
        
        menu_map = {}
        for i, (cmd_id, cmd_desc, cmd_exec) in enumerate(commands, 1):
            print(f"  {i}) {cmd_desc}")
            menu_map[str(i)] = (cmd_id, cmd_exec)
        
        print(f"\n{YELLOW}V{RESET} - Voltar (selecionar outros servidores)")
        print(f"{RED}Q{RESET} - Sair")
        
        choice = input("\nSua escolha: ")
        
        if choice.upper() == 'Q':
            sys.exit(0)
        elif choice.upper() == 'V':
            return False
        elif choice in menu_map:
            cmd_id, cmd_exec = menu_map[choice]
            self.execute_command(cmd_id, cmd_exec, server_type)
        
        return True
    
    def execute_command(self, cmd_id, cmd_exec, server_type):
        """Executa comando específico."""
        if cmd_exec is None:
            # Comandos especiais
            if cmd_id == 'mobile_services' or cmd_id == 'processes':
                log_action(f"MANAGE_MOBILE_SERVICES", host=','.join(self.selected_hosts))
                self.manage_mobile_services()
            elif cmd_id == 'services':
                log_action(f"MANAGE_OS_SERVICES", host=','.join(self.selected_hosts))
                self.manage_os_services()
            elif cmd_id == 'docker':
                log_action(f"MANAGE_DOCKER", host=','.join(self.selected_hosts))
                self.manage_docker()
            elif cmd_id == 'logs':
                log_action(f"SEARCH_LOGS", host=','.join(self.selected_hosts))
                self.search_logs()
            elif cmd_id == 'monitor':
                log_action(f"MONITORING_MENU", host=','.join(self.selected_hosts))
                self.show_monitoring_menu()
        else:
            # Executa comando SSH
            print(f"\n{CYAN}Executando comando...{RESET}\n")
            for host in self.selected_hosts:
                print(f"{BOLD}=== {host} ==={RESET}")
                log_command(host, cmd_exec)
                import subprocess
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', host, cmd_exec],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.stdout.strip():
                        # Formatação especial para conexões
                        if cmd_id == 'connections' and 'ss -tunap' in cmd_exec:
                            lines = result.stdout.strip().split('\n')
                            if lines:
                                print(f"{BOLD}Total de conexões estabelecidas: {len(lines)}{RESET}\n")
                                print(f"{BOLD}{'PROTOCOLO':<10} {'LOCAL':<25} {'REMOTO':<25} {'PROCESSO'}{RESET}")
                                print("-" * 90)
                                for line in lines[:20]:  # Mostra primeiras 20
                                    parts = line.split()
                                    if len(parts) >= 5:
                                        proto = parts[0]
                                        local = parts[4] if len(parts) > 4 else 'N/A'
                                        remote = parts[5] if len(parts) > 5 else 'N/A'
                                        process = parts[-1] if 'users:' in line else 'N/A'
                                        print(f"{proto:<10} {local:<25} {remote:<25} {process}")
                                if len(lines) > 20:
                                    print(f"\n{YELLOW}... e mais {len(lines) - 20} conexões{RESET}")
                        else:
                            print(result.stdout)
                    else:
                        print(f"{YELLOW}Sem saída{RESET}")
                    
                    if result.stderr:
                        print(f"{RED}{result.stderr}{RESET}")
                except Exception as e:
                    print(f"{RED}Erro: {e}{RESET}")
                print()
            
            press_enter_to_continue()
    
    def search_logs(self):
        """Busca nos logs com filtros."""
        import subprocess
        
        print_menu_header("BUSCAR NOS LOGS")
        
        print(f"{BOLD}Opções de busca:{RESET}")
        print("1 - Últimas linhas (tail)")
        print("2 - Buscar por texto/padrão")
        print("3 - Buscar por data/hora")
        print("4 - Buscar erro específico")
        print(f"\n{YELLOW}V{RESET} - Voltar")
        
        choice = input("\nEscolha: ")
        
        if choice.upper() == 'V':
            return
        
        if choice == '1':
            lines = input("Quantas linhas? (padrão 50): ") or "50"
            
            # Descobre logs disponíveis
            log_path = self.select_log_file()
            if not log_path:
                return
            
            cmd = f"tail -n {lines} {log_path}"
        
        elif choice == '2':
            pattern = input("Digite o texto/padrão para buscar: ")
            if not pattern:
                print(f"{RED}Padrão não pode ser vazio{RESET}")
                press_enter_to_continue()
                return
            
            log_path = self.select_log_file()
            if not log_path:
                return
            
            case_sensitive = input("Case sensitive? (s/N): ").lower() == 's'
            
            if case_sensitive:
                cmd = f"grep '{pattern}' {log_path} | tail -n 100"
            else:
                cmd = f"grep -i '{pattern}' {log_path} | tail -n 100"
        
        elif choice == '3':
            date_pattern = input("Digite a data/hora (ex: 2026-03-09 ou Mar 09): ")
            if not date_pattern:
                print(f"{RED}Data não pode ser vazia{RESET}")
                press_enter_to_continue()
                return
            
            log_path = self.select_log_file()
            if not log_path:
                return
            
            cmd = f"grep '{date_pattern}' {log_path} | tail -n 100"
        
        elif choice == '4':
            print(f"\n{BOLD}Tipos de erro comuns:{RESET}")
            print("1 - ERROR")
            print("2 - Exception")
            print("3 - FATAL")
            print("4 - WARNING")
            print("5 - Personalizado")
            
            error_choice = input("\nEscolha: ")
            error_patterns = {
                '1': 'ERROR',
                '2': 'Exception',
                '3': 'FATAL',
                '4': 'WARNING'
            }
            
            if error_choice == '5':
                error_pattern = input("Digite o padrão de erro: ")
            else:
                error_pattern = error_patterns.get(error_choice, 'ERROR')
            
            log_path = self.select_log_file()
            if not log_path:
                return
            
            cmd = f"grep -i '{error_pattern}' {log_path} | tail -n 100"
        
        else:
            print(f"{RED}Opção inválida{RESET}")
            press_enter_to_continue()
            return
        
        # Executa busca
        print(f"\n{CYAN}Buscando...{RESET}\n")
        for host in self.selected_hosts:
            print(f"{BOLD}=== {host} ==={RESET}")
            try:
                result = subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', host, cmd],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    print(f"{GREEN}Encontradas {len(lines)} linhas:{RESET}\n")
                    print(result.stdout)
                else:
                    print(f"{YELLOW}Nenhum resultado encontrado{RESET}")
                
                if result.stderr:
                    print(f"{RED}{result.stderr}{RESET}")
            except Exception as e:
                print(f"{RED}Erro: {e}{RESET}")
            print()
        
        press_enter_to_continue()
    
    def manage_os_services(self):
        """Gerencia serviços do SO."""
        import subprocess
        
        while True:
            print_menu_header("SERVIÇOS DO SO")
            
            # Lista serviços com status
            services_status = []
            for i, (name, desc) in enumerate(SERVICE_LIST, 1):
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', self.selected_hosts[0], 
                         f'systemctl is-active {name} 2>/dev/null || echo "not-found"'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    status = result.stdout.strip().replace('\n', ' ')
                    
                    if status == 'active':
                        status_display = f"{GREEN}[ATIVO]{RESET}"
                    elif status == 'inactive':
                        status_display = f"{YELLOW}[INATIVO]{RESET}"
                    elif 'not-found' in status:
                        status_display = f"{RED}[NÃO INSTALADO]{RESET}"
                    else:
                        status_display = f"{RED}[{status.upper()}]{RESET}"
                    
                    services_status.append((name, desc, status))
                    print(f"  {i}) {name.upper():<20} {status_display:<30} {desc}")
                except Exception as e:
                    services_status.append((name, desc, 'error'))
                    print(f"  {i}) {name.upper():<20} {RED}[ERRO]{RESET:<30} {desc}")
            
            print(f"\n{YELLOW}V{RESET} - Voltar")
            choice = input("\nSelecione um serviço: ")
            
            if choice.upper() == 'V':
                break
            
            if choice.isdigit() and 1 <= int(choice) <= len(SERVICE_LIST):
                service_name, service_desc, status = services_status[int(choice) - 1]
                if status != 'not-found':
                    self.manage_single_service(service_name)
                else:
                    print(f"\n{RED}Serviço {service_name} não está instalado{RESET}")
                    press_enter_to_continue()
    
    def manage_single_service(self, service_name):
        """Gerencia um serviço específico."""
        import subprocess
        
        while True:
            print_menu_header(f"GERENCIAR {service_name.upper()}")
            
            # Obtém status detalhado
            try:
                result = subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', self.selected_hosts[0], 
                     f'systemctl status {service_name}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                print(f"{BOLD}Status:{RESET}")
                print(result.stdout[:500])  # Primeiras linhas
            except Exception as e:
                print(f"{RED}Erro ao obter status: {e}{RESET}")
            
            print(f"\n{BOLD}AÇÕES:{RESET}")
            print("1 - Start")
            print("2 - Stop")
            print("3 - Restart")
            print("4 - Enable (iniciar com o sistema)")
            print("5 - Disable (não iniciar com o sistema)")
            print("6 - Status completo")
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nAção: ")
            
            if choice.upper() == 'V':
                break
            
            actions = {
                '1': 'start',
                '2': 'stop',
                '3': 'restart',
                '4': 'enable',
                '5': 'disable',
                '6': 'status'
            }
            
            if choice in actions:
                action = actions[choice]
                print(f"\n{CYAN}Executando: systemctl {action} {service_name}{RESET}\n")
                
                for host in self.selected_hosts:
                    print(f"{BOLD}=== {host} ==={RESET}")
                    log_service(host, service_name, action)
                    try:
                        result = subprocess.run(
                            ['ssh', '-o', 'LogLevel=ERROR', host, 
                             f'sudo systemctl {action} {service_name}'],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode == 0:
                            print(f"{GREEN}Sucesso!{RESET}")
                            if result.stdout:
                                print(result.stdout)
                        else:
                            print(f"{RED}Erro:{RESET}")
                            print(result.stderr if result.stderr else result.stdout)
                    except Exception as e:
                        print(f"{RED}Erro: {e}{RESET}")
                    print()
                
                press_enter_to_continue()
                if choice != '6':
                    break
    
    def manage_docker(self):
        """Gerencia containers Docker."""
        import subprocess
        
        while True:
            print_menu_header("GERENCIAR DOCKER")
            
            containers = []
            for host in self.selected_hosts:
                print(f"\n{BOLD}{host}{RESET}")
                print(f"  {'#':<3} {'ID':<14} | {'NOME':<40} | {'STATUS':<30}")
                print(f"  {'-'*3} {'-'*14} | {'-'*40} | {'-'*30}")
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', host, 'docker ps -a --format "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}"'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        for line in result.stdout.strip().split('\n'):
                            parts = line.split('|')
                            if len(parts) >= 3:
                                container_id, name, status, image = parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else 'N/A'
                                containers.append({
                                    'host': host,
                                    'id': container_id,
                                    'name': name,
                                    'status': status,
                                    'image': image
                                })
                                status_color = GREEN if 'Up' in status else RED
                                # Formatação com colunas alinhadas
                                print(f"  {len(containers):>2}) {container_id[:12]:<14} | {name:<40} | {status_color}{status:<30}{RESET}")
                    else:
                        print(f"  {YELLOW}Nenhum container encontrado{RESET}")
                except Exception as e:
                    print(f"  {RED}Erro: {e}{RESET}")
            
            if not containers:
                print(f"\n{YELLOW}Nenhum container encontrado em nenhum host{RESET}")
                press_enter_to_continue()
                return
            
            print(f"\n{BOLD}OPÇÕES:{RESET}")
            print("-" * 50)
            print("  - Digite o(s) número(s) do(s) container(s) (ex: 1 3 5-7)")
            print(f"  - Digite '{YELLOW}V{RESET}' para {YELLOW}VOLTAR{RESET}")
            print("-" * 50)
            
            choice = input("\nSua escolha: ")
            
            if choice.upper() == 'V':
                break
            
            # Parse seleção múltipla
            from utils.helpers import parse_selection_input
            selected_nums = parse_selection_input(choice, len(containers))
            
            if not selected_nums:
                print(f"{RED}Nenhuma seleção válida{RESET}")
                press_enter_to_continue()
                continue
            
            # Obtém containers selecionados
            selected_containers = [containers[int(num) - 1] for num in selected_nums]
            
            # Se apenas 1 container, usa o fluxo antigo
            if len(selected_containers) == 1:
                self.manage_single_container(selected_containers[0])
            else:
                # Múltiplos containers - novo fluxo
                self.manage_multiple_containers(selected_containers)
    
    def manage_single_container(self, container):
        """Gerencia um container Docker específico."""
        import subprocess
        
        while True:
            print_menu_header(f"GERENCIAR CONTAINER - {container['name']}")
            
            print(f"{BOLD}Host:{RESET} {container['host']}")
            print(f"{BOLD}ID:{RESET} {container['id'][:12]}")
            print(f"{BOLD}Nome:{RESET} {container['name']}")
            print(f"{BOLD}Status:{RESET} {container['status']}")
            print(f"{BOLD}Imagem:{RESET} {container['image']}\n")
            
            print("1 - Start")
            print("2 - Stop")
            print("3 - Restart")
            print("4 - Logs (tail)")
            print("5 - Buscar nos logs")
            print("6 - Inspecionar")
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nAção: ")
            
            if choice.upper() == 'V':
                break
            
            actions = {
                '1': f"docker start {container['id']}",
                '2': f"docker stop {container['id']}",
                '3': f"docker restart {container['id']}",
                '4': f"docker logs --tail 50 {container['id']}",
                '5': 'search_logs',
                '6': f"docker inspect {container['id']}"
            }
            
            if choice in actions:
                if choice == '5':
                    self.search_container_logs(container)
                    continue
                
                cmd = actions[choice]
                action_name = {'1': 'start', '2': 'stop', '3': 'restart', '4': 'logs', '6': 'inspect'}.get(choice, 'unknown')
                log_docker(container['host'], container['name'], action_name)
                
                print(f"\n{CYAN}Executando: {cmd}{RESET}\n")
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', container['host'], cmd],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.stdout.strip():
                        print(result.stdout)
                    else:
                        print(f"{YELLOW}Sem saída{RESET}")
                    if result.stderr:
                        print(f"{RED}{result.stderr}{RESET}")
                except Exception as e:
                    print(f"{RED}Erro: {e}{RESET}")
                
                press_enter_to_continue()
    
    def search_container_logs(self, container):
        """Busca nos logs de um container Docker."""
        import subprocess
        
        print_menu_header(f"BUSCAR LOGS - {container['name']}")
        
        print(f"{BOLD}Opções:{RESET}")
        print("1 - Últimas linhas")
        print("2 - Buscar texto/padrão")
        print("3 - Buscar erro")
        print(f"\n{YELLOW}V{RESET} - Voltar")
        
        choice = input("\nEscolha: ")
        
        if choice.upper() == 'V':
            return
        
        if choice == '1':
            lines = input("Quantas linhas? (padrão 100): ") or "100"
            cmd = f"docker logs --tail {lines} {container['id']}"
        elif choice == '2':
            pattern = input("Digite o texto para buscar: ")
            if not pattern:
                return
            cmd = f"docker logs --tail 500 {container['id']} 2>&1 | grep -i '{pattern}'"
        elif choice == '3':
            cmd = f"docker logs --tail 500 {container['id']} 2>&1 | grep -iE 'error|exception|fatal'"
        else:
            return
        
        print(f"\n{CYAN}Buscando...{RESET}\n")
        try:
            result = subprocess.run(
                ['ssh', '-o', 'LogLevel=ERROR', container['host'], cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                print(f"{GREEN}Encontradas {len(lines)} linhas:{RESET}\n")
                print(result.stdout)
            else:
                print(f"{YELLOW}Nenhum resultado encontrado{RESET}")
        except Exception as e:
            print(f"{RED}Erro: {e}{RESET}")
        
        press_enter_to_continue()
    
    def manage_mobile_services(self):
        """Gerencia serviços mobile via /var/servicos/."""
        import subprocess
        import re
        
        print_menu_header("GERENCIAMENTO DE SERVIÇOS MOBILE (JAVA)")
        
        print(f"[{CYAN}INFO{RESET}] Buscando serviços mobile nos hosts selecionados...\n")
        
        # Descobre serviços em /var/servicos/
        all_services = []
        for host in self.selected_hosts:
            try:
                # Lista pastas em /var/servicos/
                result = subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', host,
                     'find /var/servicos/*/bin/* -maxdepth 0 -type d 2>/dev/null | grep -v "^/var/servicos/[^/]*$"'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout.strip():
                    for service_path in result.stdout.strip().split('\n'):
                        service_name = service_path.split('/')[-1]
                        
                        # Verifica se tem service.in
                        check = subprocess.run(
                            ['ssh', '-o', 'LogLevel=ERROR', host,
                             f'test -f {service_path}/service.in && echo "exists"'],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if 'exists' in check.stdout:
                            # Verifica status
                            status_result = subprocess.run(
                                ['ssh', '-o', 'LogLevel=ERROR', host,
                                 f'cd {service_path} && ./service.in status 2>&1 | head -1'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            status = 'ATIVO' if 'running' in status_result.stdout.lower() else 'INATIVO'
                            
                            all_services.append({
                                'name': service_name,
                                'host': host,
                                'path': service_path,
                                'status': status
                            })
            except Exception as e:
                print(f"{RED}Erro ao buscar serviços em {host}: {e}{RESET}")
        
        if not all_services:
            print(f"{YELLOW}Nenhum serviço mobile encontrado{RESET}")
            press_enter_to_continue()
            return
        
        print(f"{BOLD}SERVIÇOS ENCONTRADOS:{RESET}")
        for i, svc in enumerate(all_services, 1):
            status_color = GREEN if svc['status'] == 'ATIVO' else RED
            print(f"  {i}) {svc['name']} ({svc['host']}): {status_color}{svc['status']}{RESET}")
        
        print(f"\n{BOLD}OPÇÕES:{RESET}")
        print("-" * 50)
        print("  - Digite o(s) número(s) do(s) serviço(s) para gerenciar (ex: 1 3 5-7)")
        print("  - Digite 'V' para VOLTAR")
        print("-" * 50)
        
        choice = input("\nSua escolha: ")
        
        if choice.upper() == 'V':
            return
        
        # Parse seleção
        selected_nums = parse_selection_input(choice, len(all_services))
        if not selected_nums:
            return
        
        selected_services = [all_services[int(num) - 1] for num in selected_nums]
        
        print(f"\n{BOLD}Você selecionou os seguintes serviços:{RESET}")
        for svc in selected_services:
            print(f" - {svc['name']} ({svc['host']})")
        
        print(f"\n{BOLD}AÇÕES DISPONÍVEIS:{RESET}")
        print("1) START")
        print("2) STOP")
        print("3) RESTART")
        print("4) CONDRESTART")
        print("5) STATUS")
        print("V) CANCELAR")
        
        action_choice = input("\nEscolha uma ação para aplicar a TODOS os serviços selecionados: ")
        
        if action_choice.upper() == 'V':
            return
        
        actions = {'1': 'start', '2': 'stop', '3': 'restart', '4': 'condrestart', '5': 'status'}
        
        if action_choice in actions:
            action = actions[action_choice]
            print(f"\n{CYAN}Executando {action.upper()} nos serviços selecionados...{RESET}\n")
            
            for svc in selected_services:
                print(f"{BOLD}=== {svc['name']} ({svc['host']}) ==={RESET}")
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', svc['host'],
                         f"cd {svc['path']} && sudo ./service.in {action}"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.stdout.strip():
                        print(result.stdout)
                    else:
                        print(f"{GREEN}Comando executado com sucesso{RESET}")
                    
                    if result.stderr:
                        print(f"{RED}{result.stderr}{RESET}")
                except Exception as e:
                    print(f"{RED}Erro: {e}{RESET}")
                print()
        
        press_enter_to_continue()
    
    def select_log_file(self):
        """Seleciona arquivo de log dinamicamente."""
        import subprocess
        import re
        
        print(f"\n{BOLD}Selecionar arquivo de log:{RESET}")
        print("1 - /var/log/syslog")
        print("2 - Logs Java (/var/egsys-file/log/java/)")
        print("3 - Logs PHP (/var/egsys-file/log/php/)")
        print("4 - Caminho personalizado")
        
        choice = input("\nEscolha: ")
        
        if choice == '1':
            return "/var/log/syslog"
        elif choice == '2':
            return self.select_from_log_directory("/var/egsys-file/log/java/")
        elif choice == '3':
            return self.select_from_log_directory("/var/egsys-file/log/php/")
        elif choice == '4':
            return input("Digite o caminho completo: ")
        else:
            return "/var/log/syslog"
    
    def select_from_log_directory(self, base_path):
        """Lista subpastas e arquivos de log sem numeração."""
        import subprocess
        
        # Lista subpastas
        try:
            result = subprocess.run(
                ['ssh', '-o', 'LogLevel=ERROR', self.selected_hosts[0],
                 f'ls -d {base_path}*/ 2>/dev/null'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                print(f"{YELLOW}Nenhuma subpasta encontrada{RESET}")
                return base_path
            
            folders = [f.strip().rstrip('/').split('/')[-1] for f in result.stdout.strip().split('\n')]
            
            print(f"\n{BOLD}Subpastas disponíveis:{RESET}")
            for i, folder in enumerate(folders, 1):
                print(f"  {i}) {folder}")
            print(f"  {len(folders)+1}) Voltar")
            
            folder_choice = input("\nEscolha a pasta: ")
            
            if not folder_choice.isdigit() or int(folder_choice) > len(folders):
                return base_path
            
            selected_folder = folders[int(folder_choice) - 1]
            folder_path = f"{base_path}{selected_folder}/"
            
            # Lista arquivos .log sem numeração (ex: Service.log, não Service.1.log)
            result = subprocess.run(
                ['ssh', '-o', 'LogLevel=ERROR', self.selected_hosts[0],
                 f'ls {folder_path}*.log 2>/dev/null | grep -v "\\.[0-9]\\+\\.log$"'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                print(f"{YELLOW}Nenhum arquivo .log encontrado{RESET}")
                return folder_path + "*.log"
            
            log_files = [f.strip() for f in result.stdout.strip().split('\n')]
            
            print(f"\n{BOLD}Arquivos de log:{RESET}")
            for i, log_file in enumerate(log_files, 1):
                log_name = log_file.split('/')[-1]
                print(f"  {i}) {log_name}")
            print(f"  {len(log_files)+1}) Todos")
            
            log_choice = input("\nEscolha o arquivo: ")
            
            if not log_choice.isdigit():
                return folder_path + "*.log"
            
            choice_num = int(log_choice)
            if choice_num > len(log_files):
                return folder_path + "*.log"
            
            return log_files[choice_num - 1]
            
        except Exception as e:
            print(f"{RED}Erro ao listar logs: {e}{RESET}")
            return base_path
    
    def show_java_processes(self):
        """Lista e gerencia processos Java."""
        import subprocess
        import re
        
        print_menu_header("PROCESSOS JAVA")
        
        processes = []
        for host in self.selected_hosts:
            print(f"\n{BOLD}=== {host} ==={RESET}")
            try:
                result = subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', host, 'ps aux | grep java | grep -v grep'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            # Extrai nome do serviço
                            service_name = 'Unknown'
                            if 'wrapper.name=' in line:
                                match = re.search(r'wrapper\.name=(\S+)', line)
                                if match:
                                    service_name = match.group(1)
                            elif '.jar' in line:
                                match = re.search(r'([\w-]+)\.jar', line)
                                if match:
                                    service_name = match.group(1)
                            
                            processes.append({
                                'host': host,
                                'pid': pid,
                                'name': service_name,
                                'line': line
                            })
                            print(f"  {len(processes)}) PID: {pid} - {service_name}")
            except Exception as e:
                print(f"{RED}Erro: {e}{RESET}")
        
        if not processes:
            print(f"\n{YELLOW}Nenhum processo Java encontrado{RESET}")
            press_enter_to_continue()
            return
        
        print(f"\n{YELLOW}V{RESET} - Voltar")
        choice = input("\nSelecione processo para gerenciar (ou V): ")
        
        if choice.upper() == 'V':
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(processes):
            proc = processes[int(choice) - 1]
            self.manage_java_process(proc)
    
    def manage_java_process(self, proc):
        """Gerencia um processo Java específico."""
        import subprocess
        
        while True:
            print_menu_header(f"GERENCIAR PROCESSO - {proc['name']}")
            
            print(f"{BOLD}Host:{RESET} {proc['host']}")
            print(f"{BOLD}PID:{RESET} {proc['pid']}")
            print(f"{BOLD}Nome:{RESET} {proc['name']}\n")
            
            print("1 - Kill (SIGTERM)")
            print("2 - Kill -9 (SIGKILL)")
            print("3 - Ver detalhes")
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nAção: ")
            
            if choice.upper() == 'V':
                break
            elif choice == '1':
                cmd = f"kill {proc['pid']}"
                print(f"\n{CYAN}Executando: {cmd}{RESET}")
                subprocess.run(['ssh', '-o', 'LogLevel=ERROR', proc['host'], cmd])
                print(f"{GREEN}Sinal SIGTERM enviado{RESET}")
                press_enter_to_continue()
                break
            elif choice == '2':
                cmd = f"kill -9 {proc['pid']}"
                print(f"\n{CYAN}Executando: {cmd}{RESET}")
                subprocess.run(['ssh', '-o', 'LogLevel=ERROR', proc['host'], cmd])
                print(f"{GREEN}Sinal SIGKILL enviado{RESET}")
                press_enter_to_continue()
                break
            elif choice == '3':
                print(f"\n{CYAN}Detalhes do processo:{RESET}")
                print(proc['line'])
                press_enter_to_continue()

    
    def show_monitoring_menu(self):
        """Menu de monitoramento top/htop."""
        # Se múltiplos hosts, pede para selecionar um
        if len(self.selected_hosts) > 1:
            print_menu_header("MONITORAMENTO - SELEÇÃO DE HOST")
            print(f"{YELLOW}Selecione um servidor para monitorar:{RESET}\n")
            
            for i, host in enumerate(self.selected_hosts, 1):
                print(f"  {i}) {host}")
            
            print(f"\n{YELLOW}V{RESET} - Voltar")
            choice = input("\nEscolha o host: ")
            
            if choice.upper() == 'V':
                return
            
            if choice.isdigit() and 1 <= int(choice) <= len(self.selected_hosts):
                selected_host = self.selected_hosts[int(choice) - 1]
            else:
                print(f"{RED}Opção inválida{RESET}")
                press_enter_to_continue()
                return
        else:
            selected_host = self.selected_hosts[0]
        
        # Menu de opções de monitoramento
        while True:
            print_menu_header(f"MONITORAMENTO - {selected_host.upper()}")
            
            print(f"{BOLD}OPÇÕES DE MONITORAMENTO:{RESET}\n")
            print(f"  1) {CYAN}TOP{RESET} - Monitorar em tempo real (interativo)")
            print(f"  2) {CYAN}HTOP{RESET} - Monitorar com htop (se disponível)")
            print(f"  3) {GREEN}SALVAR{RESET} - Salvar snapshot do top em arquivo")
            print(f"  4) {YELLOW}ANALISAR{RESET} - Analisar arquivo de log existente")
            print(f"\n  {YELLOW}V{RESET} - Voltar")
            print(f"  {RED}Q{RESET} - Sair")
            
            choice = input("\nSua escolha: ")
            
            if choice.upper() == 'Q':
                sys.exit(0)
            elif choice.upper() == 'V':
                break
            elif choice == '1':
                log_action(f"Iniciou monitoramento TOP em '{selected_host}'")
                self.monitoring_manager.monitor_top_interactive(selected_host)
                press_enter_to_continue()
            elif choice == '2':
                log_action(f"Iniciou monitoramento HTOP em '{selected_host}'")
                self.monitoring_manager.monitor_htop_interactive(selected_host)
                press_enter_to_continue()
            elif choice == '3':
                log_action(f"Salvou snapshot TOP de '{selected_host}'")
                self.monitoring_manager.save_top_to_file(selected_host)
                press_enter_to_continue()
            elif choice == '4':
                log_action(f"Analisou arquivo de log existente")
                self.analyze_existing_log()
                press_enter_to_continue()
            else:
                print(f"{RED}Opção inválida{RESET}")
                press_enter_to_continue()

    
    def analyze_existing_log(self):
        """Analisa um arquivo de log existente."""
        import os
        import glob
        
        print_menu_header("ANALISAR LOG EXISTENTE")
        
        log_dir = os.path.expanduser("~/logs_scriptN1")
        
        if not os.path.exists(log_dir):
            print(f"{RED}Diretório de logs não encontrado: {log_dir}{RESET}")
            return
        
        # Lista arquivos de log (exceto análises)
        log_files = glob.glob(os.path.join(log_dir, "monitor_top_*.txt"))
        log_files = [f for f in log_files if '_ANALISE' not in f]
        log_files.sort(key=os.path.getmtime, reverse=True)
        
        if not log_files:
            print(f"{YELLOW}Nenhum arquivo de log encontrado em {log_dir}{RESET}")
            return
        
        print(f"{BOLD}Arquivos de log disponíveis (mais recentes primeiro):{RESET}\n")
        
        # Mostra últimos 20 arquivos
        display_files = log_files[:20]
        for i, log_file in enumerate(display_files, 1):
            filename = os.path.basename(log_file)
            size = os.path.getsize(log_file) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            print(f"  {i}) {filename}")
            print(f"      {CYAN}Tamanho: {size:.1f}KB | Data: {mtime.strftime('%d/%m/%Y %H:%M')}{RESET}")
        
        print(f"\n{YELLOW}V{RESET} - Voltar")
        choice = input("\nEscolha o arquivo para analisar: ")
        
        if choice.upper() == 'V':
            return
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(display_files):
            print(f"{RED}Opção inválida{RESET}")
            return
        
        selected_file = display_files[int(choice) - 1]
        
        print(f"\n{CYAN}Analisando arquivo...{RESET}\n")
        
        try:
            with open(selected_file, 'r') as f:
                content = f.read()
            
            # Extrai hostname do nome do arquivo
            filename = os.path.basename(selected_file)
            host_match = re.search(r'monitor_top_(.+?)_\d{4}-\d{2}-\d{2}', filename)
            host = host_match.group(1) if host_match else 'unknown'
            
            # Analisa
            from core.analyzer import SystemAnalyzer
            analyzer = SystemAnalyzer()
            analysis = analyzer.analyze_top_output(content)
            report = analyzer.generate_report(analysis, host)
            
            print(report)
            
            # Pergunta se quer salvar
            save = input(f"\n{BOLD}Salvar análise em arquivo? (S/N):{RESET} ")
            if save.upper() == 'S':
                report_path = selected_file.replace('.txt', '_ANALISE.txt')
                with open(report_path, 'w') as f:
                    # Remove códigos de cor
                    clean_report = report
                    for code in [GREEN, RED, YELLOW, CYAN, BOLD, RESET]:
                        clean_report = clean_report.replace(code, '')
                    f.write(clean_report)
                os.chmod(report_path, 0o777)
                print(f"{GREEN}Análise salva em: {report_path}{RESET}")
        
        except Exception as e:
            print(f"{RED}Erro ao analisar arquivo: {e}{RESET}")

    
    def manage_multiple_containers(self, containers):
        """Gerencia múltiplos containers Docker de uma vez."""
        import subprocess
        
        while True:
            print_menu_header(f"GERENCIAR {len(containers)} CONTAINERS")
            
            print(f"{BOLD}Containers selecionados:{RESET}\n")
            for container in containers:
                status_color = GREEN if 'Up' in container['status'] else RED
                print(f"  • {container['name']} ({container['host']}) - {status_color}{container['status']}{RESET}")
            
            print(f"\n{BOLD}AÇÕES DISPONÍVEIS:{RESET}")
            print("1 - Start (iniciar todos)")
            print("2 - Stop (parar todos)")
            print("3 - Restart (reiniciar todos)")
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nEscolha uma ação para aplicar a TODOS os containers: ")
            
            if choice.upper() == 'V':
                break
            
            actions = {
                '1': 'start',
                '2': 'stop',
                '3': 'restart'
            }
            
            if choice in actions:
                action = actions[choice]
                
                # Confirmação
                confirm = input(f"\n{YELLOW}CONFIRMAÇÃO:{RESET} Deseja aplicar '{action.upper()}' nos {len(containers)} containers? (S/N): ")
                
                if confirm.upper() != 'S':
                    print(f"{YELLOW}Operação cancelada{RESET}")
                    press_enter_to_continue()
                    continue
                
                print(f"\n{CYAN}Executando {action.upper()} nos containers...{RESET}\n")
                
                success_count = 0
                for container in containers:
                    print(f"{BOLD}=== {container['name']} ({container['host']}) ==={RESET}")
                    log_docker(container['host'], container['name'], action)
                    try:
                        cmd = f"docker {action} {container['id']}"
                        result = subprocess.run(
                            ['ssh', '-o', 'LogLevel=ERROR', container['host'], cmd],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode == 0:
                            print(f"{GREEN}✓ Sucesso{RESET}")
                            success_count += 1
                        else:
                            print(f"{RED}✗ Erro: {result.stderr.strip()}{RESET}")
                    except Exception as e:
                        print(f"{RED}✗ Erro: {e}{RESET}")
                    print()
                
                print(f"\n{BOLD}Resultado:{RESET} {success_count}/{len(containers)} containers processados com sucesso")
                log_action(f"Executou '{action}' em {success_count}/{len(containers)} containers")
                press_enter_to_continue()
                break
            else:
                print(f"{RED}Opção inválida{RESET}")
                press_enter_to_continue()
