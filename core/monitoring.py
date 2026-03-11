"""Módulo de monitoramento de servidores (top/htop)."""
import subprocess
import os
from datetime import datetime
from config.constants import GREEN, RED, YELLOW, CYAN, BOLD, RESET
from core.logger import log_auditoria, dprint
from core.analyzer import SystemAnalyzer

class MonitoringManager:
    def __init__(self):
        self.analyzer = SystemAnalyzer()
    
    def monitor_top_interactive(self, host):
        """Executa top interativo no servidor remoto."""
        print(f"\n{CYAN}Iniciando monitoramento interativo em '{host}'...{RESET}")
        print(f"{YELLOW}Pressione 'q' para sair do monitoramento.{RESET}\n")
        
        dprint(f"Iniciando top interativo em '{host}'")
        log_auditoria("MONITOR_TOP_INTERACTIVE", "START", host, "Iniciou monitoramento interativo")
        
        try:
            subprocess.run(["ssh", "-t", host, "top"], env=os.environ)
            log_auditoria("MONITOR_TOP_INTERACTIVE", "SUCCESS", host, "Monitoramento concluído")
        except Exception as e:
            print(f"{RED}Erro ao iniciar monitoramento: {e}{RESET}")
            log_auditoria("MONITOR_TOP_INTERACTIVE", "FAILURE", host, f"Erro: {e}")
    
    def save_top_to_file(self, host):
        """Salva saída do top em arquivo local."""
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, "logs_scriptN1")
        
        print(f"\n{CYAN}Salvando monitoramento de '{host}'...{RESET}")
        print(f"{BOLD}Diretório de destino:{RESET} {log_dir}\n")
        
        # Cria diretório se não existir
        try:
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir, mode=0o777, exist_ok=True)
                os.chmod(log_dir, 0o777)
                print(f"[{GREEN}OK{RESET}] Diretório criado: {log_dir}")
            else:
                print(f"[{YELLOW}INFO{RESET}] Diretório já existe: {log_dir}")
        except Exception as e:
            print(f"[{RED}ERRO{RESET}] Falha ao criar diretório: {e}")
            return False
        
        # Captura saída do top
        print(f"\n{CYAN}Capturando dados do servidor...{RESET}")
        command = "top -b -n 1"
        
        try:
            result = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no", host, command],
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Gera nome do arquivo
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%Mhs")
                filename = f"monitor_top_{host}_{timestamp}.txt"
                full_path = os.path.join(log_dir, filename)
                
                # Salva arquivo
                with open(full_path, 'w') as f:
                    f.write(output)
                
                os.chmod(full_path, 0o777)
                
                # Análise automática
                print(f"\n{CYAN}Analisando dados do servidor...{RESET}\n")
                analysis = self.analyzer.analyze_top_output(output)
                report = self.analyzer.generate_report(analysis, host)
                
                # Exibe relatório na tela
                print(report)
                
                # Salva relatório junto com o arquivo
                report_path = full_path.replace('.txt', '_ANALISE.txt')
                with open(report_path, 'w') as f:
                    # Remove códigos de cor para o arquivo
                    clean_report = report
                    for code in [GREEN, RED, YELLOW, CYAN, BOLD, RESET]:
                        clean_report = clean_report.replace(code, '')
                    f.write(clean_report)
                os.chmod(report_path, 0o777)
                
                print(f"\n{GREEN}ARQUIVOS SALVOS COM SUCESSO!{RESET}")
                print(f"{BOLD}Log completo:{RESET} {full_path}")
                print(f"{BOLD}Análise:{RESET} {report_path}")
                
                log_auditoria("MONITOR_TOP_SAVE", "SUCCESS", host, f"Arquivo salvo: {full_path}")
                dprint(f"Arquivo de monitoramento salvo: {full_path}")
                
                return True
            else:
                print(f"{RED}Falha ao capturar dados do servidor{RESET}")
                log_auditoria("MONITOR_TOP_SAVE", "FAILURE", host, "Falha ao executar comando top")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{RED}Timeout ao conectar com o servidor{RESET}")
            log_auditoria("MONITOR_TOP_SAVE", "FAILURE", host, "Timeout na conexão")
            return False
        except Exception as e:
            print(f"{RED}Erro inesperado: {e}{RESET}")
            log_auditoria("MONITOR_TOP_SAVE", "FAILURE", host, f"Erro: {e}")
            return False
    
    def monitor_htop_interactive(self, host):
        """Executa htop interativo no servidor remoto (se disponível)."""
        print(f"\n{CYAN}Verificando disponibilidade do htop em '{host}'...{RESET}")
        
        # Verifica se htop está instalado
        try:
            check = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no", host, "which htop"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if check.returncode != 0:
                print(f"{YELLOW}htop não está instalado em '{host}'{RESET}")
                print(f"{CYAN}Usando 'top' como alternativa...{RESET}\n")
                return self.monitor_top_interactive(host)
            
            print(f"{GREEN}htop disponível!{RESET}")
            print(f"{YELLOW}Pressione 'q' ou F10 para sair.{RESET}\n")
            
            dprint(f"Iniciando htop em '{host}'")
            log_auditoria("MONITOR_HTOP_INTERACTIVE", "START", host, "Iniciou htop interativo")
            
            subprocess.run(["ssh", "-t", host, "htop"], env=os.environ)
            log_auditoria("MONITOR_HTOP_INTERACTIVE", "SUCCESS", host, "Monitoramento concluído")
            
        except Exception as e:
            print(f"{RED}Erro: {e}{RESET}")
            print(f"{CYAN}Tentando com 'top'...{RESET}\n")
            return self.monitor_top_interactive(host)
