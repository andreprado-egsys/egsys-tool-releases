"""Sistema de ajuda do egSYS Tool."""
from config.constants import GREEN, RED, YELLOW, CYAN, BOLD, RESET, MAGENTA, BLUE
from utils.helpers import press_enter_to_continue, print_menu_header

class HelpManager:
    def __init__(self):
        pass
    
    def show_help_menu(self):
        """Menu principal de ajuda."""
        while True:
            print_menu_header("MENU DE AJUDA")
            
            print(f"{BOLD}TÓPICOS DISPONÍVEIS:{RESET}\n")
            print(f"  1) {CYAN}Visão Geral{RESET} - O que é o egSYS SAPA")
            print(f"  2) {CYAN}Primeiros Passos{RESET} - Como começar a usar")
            print(f"  3) {CYAN}Navegação{RESET} - Teclas e atalhos")
            print(f"  4) {CYAN}Gerenciamento de Servidores{RESET} - Estados e hosts")
            print(f"  5) {CYAN}VPN e SSH{RESET} - Conexões seguras")
            print(f"  6) {CYAN}Comandos Disponíveis{RESET} - O que você pode fazer")
            print(f"  7) {CYAN}Serviços e Docker{RESET} - Gerenciamento")
            print(f"  8) {CYAN}Monitoramento{RESET} - Top, htop e análises")
            print(f"  9) {CYAN}Logs e Busca{RESET} - Encontrar informações")
            print(f"  10) {CYAN}Menu Administrativo{RESET} - Gestão de usuários")
            print(f"  11) {CYAN}Auditoria{RESET} - Rastreamento de ações")
            print(f"  12) {CYAN}Dicas e Truques{RESET} - Uso avançado")
            
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nEscolha um tópico: ")
            
            if choice.upper() == 'V':
                break
            elif choice == '1':
                self.show_overview()
            elif choice == '2':
                self.show_getting_started()
            elif choice == '3':
                self.show_navigation()
            elif choice == '4':
                self.show_server_management()
            elif choice == '5':
                self.show_vpn_ssh()
            elif choice == '6':
                self.show_commands()
            elif choice == '7':
                self.show_services_docker()
            elif choice == '8':
                self.show_monitoring()
            elif choice == '9':
                self.show_logs()
            elif choice == '10':
                self.show_admin()
            elif choice == '11':
                self.show_audit()
            elif choice == '12':
                self.show_tips()
    
    def show_overview(self):
        """Visão geral."""
        print_menu_header("VISÃO GERAL")
        
        print(f"{BOLD}O que é o egSYS SAPA?{RESET}\n")
        print("Sistema de Avaliação e Performance de Ambientes")
        print("Ferramenta de gerenciamento multi-servidor inteligente\n")
        
        print(f"{BOLD}Principais Funcionalidades:{RESET}\n")
        print(f"  {GREEN}✓{RESET} Gerenciamento centralizado de múltiplos servidores")
        print(f"  {GREEN}✓{RESET} Conexão automática via VPN (SNX e NetworkManager)")
        print(f"  {GREEN}✓{RESET} Agente SSH inteligente (senha única por sessão)")
        print(f"  {GREEN}✓{RESET} Gerenciamento de serviços do SO e Docker")
        print(f"  {GREEN}✓{RESET} Monitoramento em tempo real (top/htop)")
        print(f"  {GREEN}✓{RESET} Busca avançada em logs")
        print(f"  {GREEN}✓{RESET} Sistema de auditoria completo")
        print(f"  {GREEN}✓{RESET} Menu administrativo para gestão de usuários")
        
        print(f"\n{BOLD}Benefícios:{RESET}\n")
        print("  • Economia de tempo (sem digitar senhas repetidamente)")
        print("  • Segurança (auditoria de todas as ações)")
        print("  • Organização (servidores agrupados por estado)")
        print("  • Produtividade (comandos rápidos e intuitivos)")
        
        press_enter_to_continue()
    
    def show_getting_started(self):
        """Primeiros passos."""
        print_menu_header("PRIMEIROS PASSOS")
        
        print(f"{BOLD}1. Login{RESET}\n")
        print("   • Digite seu usuário e senha")
        print("   • Você tem 3 tentativas\n")
        
        print(f"{BOLD}2. Selecione um Estado ou Host{RESET}\n")
        print("   • Estados: Grupos de servidores (AM, TO, SC, etc.)")
        print("   • Hosts Avulsos: Servidores individuais\n")
        
        print(f"{BOLD}3. Conexão Automática{RESET}\n")
        print("   • VPN: Conecta automaticamente se necessário")
        print("   • SSH: Solicita senha da chave apenas uma vez\n")
        
        print(f"{BOLD}4. Selecione Servidores{RESET}\n")
        print("   • Digite números separados por espaço: 1 3 5")
        print("   • Ou intervalos: 1-5")
        print("   • Ou combinados: 1 3 5-7 10\n")
        
        print(f"{BOLD}5. Execute Comandos{RESET}\n")
        print("   • Escolha ações do menu")
        print("   • Comandos são executados em todos os servidores selecionados")
        
        press_enter_to_continue()
    
    def show_navigation(self):
        """Navegação e teclas."""
        print_menu_header("NAVEGAÇÃO E TECLAS")
        
        print(f"{BOLD}Teclas Principais:{RESET}\n")
        print(f"  {CYAN}Q{RESET} - Sair do sistema")
        print(f"  {CYAN}V{RESET} - Voltar ao menu anterior")
        print(f"  {MAGENTA}A{RESET} - Menu Administrativo (requer senha)")
        print(f"  {YELLOW}H{RESET} - Ajuda (este menu)")
        
        print(f"\n{BOLD}Seleção Múltipla:{RESET}\n")
        print(f"  {GREEN}Exemplos:{RESET}")
        print("    1 3 5       → Seleciona servidores 1, 3 e 5")
        print("    1-5         → Seleciona servidores de 1 a 5")
        print("    1 3 5-7 10  → Seleciona 1, 3, 5, 6, 7 e 10")
        
        print(f"\n{BOLD}Navegação por Menus:{RESET}\n")
        print("  • Digite o número da opção desejada")
        print("  • Pressione Enter para confirmar")
        print("  • Use V para voltar ao menu anterior")
        print("  • Use Q para sair completamente")
        
        print(f"\n{BOLD}Breadcrumb (Navegação):{RESET}\n")
        print("  🏠 Home ➤ TO ➤ Servidores")
        print("  Mostra onde você está no sistema")
        
        press_enter_to_continue()
    
    def show_server_management(self):
        """Gerenciamento de servidores."""
        print_menu_header("GERENCIAMENTO DE SERVIDORES")
        
        print(f"{BOLD}Estados:{RESET}\n")
        print("  Grupos de servidores organizados por localização")
        print(f"  {CYAN}[VPN]{RESET} indica que requer conexão VPN\n")
        
        print(f"{BOLD}Tipos de Servidor:{RESET}\n")
        print(f"  {BLUE}📱{RESET} Mobile  - Servidores de aplicação mobile")
        print(f"  {BLUE}🌐{RESET} Web     - Servidores web (nginx/apache)")
        print(f"  {BLUE}🗄️{RESET}  BD      - Bancos de dados")
        print(f"  {BLUE}🔌{RESET} API     - Servidores de API/backend")
        
        print(f"\n{BOLD}Hosts Avulsos:{RESET}\n")
        print("  Servidores que não pertencem a um estado específico")
        print("  Acesso direto sem passar por seleção de grupo")
        
        print(f"\n{BOLD}Seleção de Servidores:{RESET}\n")
        print("  • Múltipla seleção: 1 3 5")
        print("  • Intervalo: 1-5")
        print("  • Combinado: 1 3 5-7 10")
        print("  • Comandos executam em TODOS os selecionados")
        
        press_enter_to_continue()
    
    def show_vpn_ssh(self):
        """VPN e SSH."""
        print_menu_header("VPN E SSH")
        
        print(f"{BOLD}Conexão VPN:{RESET}\n")
        print("  • Automática ao selecionar estado que requer VPN")
        print("  • Desconecta outras VPNs para evitar conflitos")
        print("  • Valida conectividade com ping no gateway")
        print("  • Permanece conectada durante toda a sessão")
        
        print(f"\n{BOLD}Tipos de VPN:{RESET}\n")
        print("  • SNX (Check Point) - PR, RO, MT")
        print("  • NetworkManager - SC, TO")
        
        print(f"\n{BOLD}Agente SSH:{RESET}\n")
        print("  • Carrega chave SSH automaticamente")
        print("  • Solicita senha apenas UMA vez por estado")
        print("  • Reutiliza chave em todas as conexões")
        print("  • Suporta múltiplas chaves (uma por estado)")
        
        print(f"\n{BOLD}Chaves SSH:{RESET}\n")
        print("  Localização: ~/.ssh/id_rsa_<estado>")
        print("  Exemplo: ~/.ssh/id_rsa_to")
        print("  Fallback: ~/.ssh/id_rsa (chave padrão)")
        
        press_enter_to_continue()
    
    def show_commands(self):
        """Comandos disponíveis."""
        print_menu_header("COMANDOS DISPONÍVEIS")
        
        print(f"{BOLD}Comandos Comuns:{RESET}\n")
        print(f"  {CYAN}Checar espaço em disco{RESET}")
        print("    df -h - Mostra uso de disco\n")
        
        print(f"  {CYAN}Uso de memória{RESET}")
        print("    free -h - Mostra memória disponível\n")
        
        print(f"  {CYAN}Tempo de atividade{RESET}")
        print("    uptime - Mostra há quanto tempo o servidor está ligado\n")
        
        print(f"  {CYAN}Conexões ativas{RESET}")
        print("    ss -tunap - Lista conexões de rede estabelecidas\n")
        
        print(f"{BOLD}Comandos Especiais:{RESET}\n")
        print(f"  {GREEN}Gerenciar serviços do SO{RESET}")
        print("    nginx, apache, mysql, postgresql, php-fpm, docker\n")
        
        print(f"  {GREEN}Gerenciar Docker{RESET}")
        print("    Lista, inicia, para, reinicia containers\n")
        
        print(f"  {GREEN}Gerenciar serviços Mobile{RESET}")
        print("    Serviços Java em /var/servicos/\n")
        
        print(f"  {GREEN}Buscar nos logs{RESET}")
        print("    Busca por texto, data, erro\n")
        
        print(f"  {GREEN}Monitoramento{RESET}")
        print("    top, htop, salvar snapshot, análise automática")
        
        press_enter_to_continue()
    
    def show_services_docker(self):
        """Serviços e Docker."""
        print_menu_header("SERVIÇOS E DOCKER")
        
        print(f"{BOLD}Serviços do SO:{RESET}\n")
        print("  Ações disponíveis:")
        print(f"    {GREEN}Start{RESET}    - Iniciar serviço")
        print(f"    {RED}Stop{RESET}     - Parar serviço")
        print(f"    {YELLOW}Restart{RESET}  - Reiniciar serviço")
        print(f"    {CYAN}Enable{RESET}   - Iniciar com o sistema")
        print(f"    {CYAN}Disable{RESET}  - Não iniciar com o sistema")
        print(f"    {BLUE}Status{RESET}   - Ver status detalhado")
        
        print(f"\n{BOLD}Docker:{RESET}\n")
        print("  Gerenciamento de containers:")
        print(f"    {GREEN}Start{RESET}    - Iniciar container")
        print(f"    {RED}Stop{RESET}     - Parar container")
        print(f"    {YELLOW}Restart{RESET}  - Reiniciar container")
        print(f"    {CYAN}Logs{RESET}     - Ver logs do container")
        print(f"    {BLUE}Inspect{RESET}  - Inspecionar configuração")
        
        print(f"\n{BOLD}Serviços Mobile (Java):{RESET}\n")
        print("  Localização: /var/servicos/*/bin/*")
        print("  Ações: start, stop, restart, condrestart, status")
        print("  Seleção múltipla: Aplica ação em vários serviços")
        
        print(f"\n{BOLD}Dica:{RESET}")
        print("  Você pode selecionar múltiplos containers/serviços")
        print("  e aplicar a mesma ação em todos de uma vez!")
        
        press_enter_to_continue()
    
    def show_monitoring(self):
        """Monitoramento."""
        print_menu_header("MONITORAMENTO")
        
        print(f"{BOLD}Top Interativo:{RESET}\n")
        print("  • Monitora servidor em tempo real")
        print("  • Atualização automática")
        print("  • Pressione 'q' para sair")
        
        print(f"\n{BOLD}Htop:{RESET}\n")
        print("  • Interface mais amigável que o top")
        print("  • Usa htop se disponível, senão usa top")
        print("  • Navegação com setas, F10 para sair")
        
        print(f"\n{BOLD}Salvar Snapshot:{RESET}\n")
        print("  • Captura saída do top em arquivo")
        print("  • Salvo em: ~/logs_scriptN1/monitor_top_<host>_<timestamp>.txt")
        print("  • Permissões 777 (fácil compartilhamento)")
        
        print(f"\n{BOLD}Análise Automática:{RESET}\n")
        print("  Detecta automaticamente:")
        print(f"    {RED}✗{RESET} Uso crítico de CPU (>80%)")
        print(f"    {RED}✗{RESET} Uso crítico de memória (>90%)")
        print(f"    {YELLOW}⚠{RESET} Processos zombie")
        print(f"    {YELLOW}⚠{RESET} Load average alto")
        print(f"    {YELLOW}⚠{RESET} I/O wait elevado")
        
        print(f"\n  Gera relatório com:")
        print("    • Problemas identificados")
        print("    • Severidade (Crítico/Alto/Médio/Baixo)")
        print("    • Recomendações de ação")
        
        print(f"\n{BOLD}Analisar Log Existente:{RESET}\n")
        print("  • Analisa arquivos salvos anteriormente")
        print("  • Lista últimos 20 arquivos")
        print("  • Gera relatório de análise")
        
        press_enter_to_continue()
    
    def show_logs(self):
        """Logs e busca."""
        print_menu_header("LOGS E BUSCA")
        
        print(f"{BOLD}Opções de Busca:{RESET}\n")
        
        print(f"  {CYAN}1. Últimas linhas (tail){RESET}")
        print("     Mostra as últimas N linhas do log")
        print("     Útil para ver eventos recentes\n")
        
        print(f"  {CYAN}2. Buscar por texto/padrão{RESET}")
        print("     Busca texto específico no log")
        print("     Case sensitive opcional\n")
        
        print(f"  {CYAN}3. Buscar por data/hora{RESET}")
        print("     Filtra logs por período")
        print("     Formato: 2026-03-09 ou Mar 09\n")
        
        print(f"  {CYAN}4. Buscar erro específico{RESET}")
        print("     Tipos: ERROR, Exception, FATAL, WARNING")
        print("     Ou padrão personalizado\n")
        
        print(f"{BOLD}Locais de Log:{RESET}\n")
        print("  • /var/log/syslog - Logs do sistema")
        print("  • /var/egsys-file/log/java/ - Logs Java")
        print("  • /var/egsys-file/log/php/ - Logs PHP")
        print("  • Caminho personalizado")
        
        print(f"\n{BOLD}Logs Docker:{RESET}\n")
        print("  • Últimas linhas")
        print("  • Buscar texto")
        print("  • Buscar erros (ERROR|Exception|FATAL)")
        
        press_enter_to_continue()
    
    def show_admin(self):
        """Menu administrativo."""
        print_menu_header("MENU ADMINISTRATIVO")
        
        print(f"{BOLD}Acesso:{RESET}\n")
        print(f"  Pressione {MAGENTA}A{RESET} na tela de seleção de estados")
        print(f"  Senha padrão: {YELLOW}admin123{RESET}")
        print(f"  {RED}IMPORTANTE:{RESET} Altere a senha após primeiro acesso!\n")
        
        print(f"{BOLD}Funcionalidades:{RESET}\n")
        
        print(f"  {CYAN}1. Listar usuários{RESET}")
        print("     Visualiza todos os usuários cadastrados\n")
        
        print(f"  {CYAN}2. Adicionar usuário{RESET}")
        print("     Cria novo usuário com senha")
        print("     Senha mínima: 6 caracteres\n")
        
        print(f"  {CYAN}3. Remover usuário{RESET}")
        print("     Remove usuário do sistema")
        print("     Requer confirmação\n")
        
        print(f"  {CYAN}4. Alterar senha de usuário{RESET}")
        print("     Altera senha de qualquer usuário\n")
        
        print(f"  {CYAN}5. Alterar senha administrativa{RESET}")
        print("     Altera senha de acesso ao menu admin")
        print("     Requer senha atual\n")
        
        print(f"  {CYAN}6. Ver logs de auditoria{RESET}")
        print("     • Últimas 50/100 linhas")
        print("     • Filtrar por usuário (com lista)")
        print("     • Filtrar por host")
        print("     • Ver TODOS os usuários (opção 0)")
        
        print(f"\n{BOLD}Segurança:{RESET}\n")
        print("  • Senhas com hash SHA256 + salt único")
        print("  • Arquivos protegidos (permissão 600)")
        print("  • 3 tentativas de acesso")
        
        press_enter_to_continue()
    
    def show_audit(self):
        """Auditoria."""
        print_menu_header("SISTEMA DE AUDITORIA")
        
        print(f"{BOLD}O que é auditado:{RESET}\n")
        print(f"  {GREEN}✓{RESET} Login/Logout de usuários")
        print(f"  {GREEN}✓{RESET} Conexões VPN (tentativa, sucesso, falha)")
        print(f"  {GREEN}✓{RESET} TODOS os comandos SSH executados")
        print(f"  {GREEN}✓{RESET} Gerenciamento de serviços (start/stop/restart)")
        print(f"  {GREEN}✓{RESET} Operações Docker")
        print(f"  {GREEN}✓{RESET} Acesso administrativo")
        print(f"  {GREEN}✓{RESET} Gerenciamento de serviços mobile")
        print(f"  {GREEN}✓{RESET} Buscas em logs")
        print(f"  {GREEN}✓{RESET} Monitoramento")
        
        print(f"\n{BOLD}Localização:{RESET}\n")
        print("  ~/logs_scriptN1/egsys_audit.log")
        
        print(f"\n{BOLD}Formato:{RESET}\n")
        print("  [timestamp] | user=<user> | host=<host> | action=<action> | status=<status>")
        
        print(f"\n{BOLD}Exemplo:{RESET}\n")
        print("  [2026-03-09 15:30:45] | user=andre.prado | host=to-mobile-prd |")
        print("  action=SSH_COMMAND: docker ps | status=executed")
        
        print(f"\n{BOLD}Benefícios:{RESET}\n")
        print("  • Rastreabilidade completa")
        print("  • Compliance (SOX, LGPD, ISO 27001)")
        print("  • Troubleshooting")
        print("  • Análise forense")
        print("  • Relatórios gerenciais")
        
        print(f"\n{BOLD}Acesso aos Logs:{RESET}\n")
        print("  • Menu Admin → Opção 6")
        print("  • Filtros: usuário, host, período")
        print("  • Opção 0: Ver TODOS os usuários")
        
        press_enter_to_continue()
    
    def show_tips(self):
        """Dicas e truques."""
        print_menu_header("DICAS E TRUQUES")
        
        print(f"{BOLD}Produtividade:{RESET}\n")
        
        print(f"  {CYAN}Seleção Múltipla Rápida{RESET}")
        print("    1-10  → Seleciona todos de 1 a 10")
        print("    Economiza tempo em grupos grandes\n")
        
        print(f"  {CYAN}Reutilização de Chave SSH{RESET}")
        print("    Senha solicitada apenas UMA vez")
        print("    Todas as conexões seguintes são automáticas\n")
        
        print(f"  {CYAN}VPN Persistente{RESET}")
        print("    VPN permanece conectada durante toda a sessão")
        print("    Não precisa reconectar a cada comando\n")
        
        print(f"{BOLD}Monitoramento:{RESET}\n")
        
        print(f"  {CYAN}Salvar Snapshots{RESET}")
        print("    Capture estado do servidor para análise posterior")
        print("    Compartilhe com a equipe (permissão 777)\n")
        
        print(f"  {CYAN}Análise Automática{RESET}")
        print("    Deixe o sistema identificar problemas")
        print("    Receba recomendações de ação\n")
        
        print(f"{BOLD}Segurança:{RESET}\n")
        
        print(f"  {CYAN}Auditoria Completa{RESET}")
        print("    Todos os comandos são registrados")
        print("    Use para compliance e troubleshooting\n")
        
        print(f"  {CYAN}Senhas Fortes{RESET}")
        print("    Use mínimo 8 caracteres")
        print("    Combine letras, números e símbolos")
        print("    Altere periodicamente (90 dias)\n")
        
        print(f"{BOLD}Organização:{RESET}\n")
        
        print(f"  {CYAN}Breadcrumb{RESET}")
        print("    Sempre saiba onde está: 🏠 Home ➤ TO ➤ Servidores\n")
        
        print(f"  {CYAN}Logs Organizados{RESET}")
        print("    Todos em ~/logs_scriptN1/")
        print("    Fácil de encontrar e compartilhar\n")
        
        print(f"{BOLD}Atalhos:{RESET}\n")
        print(f"  {MAGENTA}A{RESET} - Menu Admin (rápido)")
        print(f"  {YELLOW}H{RESET} - Ajuda (sempre disponível)")
        print(f"  {CYAN}V{RESET} - Voltar (navegação rápida)")
        print(f"  {RED}Q{RESET} - Sair (em qualquer lugar)")
        
        press_enter_to_continue()
