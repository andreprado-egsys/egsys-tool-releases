"""Módulo de administração do sistema."""
import hashlib
import os
import pwinput
from config.constants import GREEN, RED, YELLOW, CYAN, BOLD, RESET
from config.users import USUARIOS_AUTORIZADOS
from utils.helpers import press_enter_to_continue, print_menu_header

class AdminManager:
    def __init__(self):
        self.admin_password_file = os.path.expanduser("~/.egsys_admin_pass")
        self.users_file = os.path.expanduser("~/.egsys_users.py")
        self._ensure_admin_password()
    
    def _ensure_admin_password(self):
        """Garante que existe senha de admin."""
        if not os.path.exists(self.admin_password_file):
            # Senha padrão: egsys!@0000
            default_hash = hashlib.sha256("egsys!@0000".encode()).hexdigest()
            with open(self.admin_password_file, 'w') as f:
                f.write(default_hash)
            os.chmod(self.admin_password_file, 0o600)
    
    def _load_admin_password(self):
        """Carrega hash da senha admin."""
        try:
            with open(self.admin_password_file, 'r') as f:
                return f.read().strip()
        except:
            return None
    
    def _save_admin_password(self, password):
        """Salva nova senha admin."""
        hash_pass = hashlib.sha256(password.encode()).hexdigest()
        with open(self.admin_password_file, 'w') as f:
            f.write(hash_pass)
        os.chmod(self.admin_password_file, 0o600)
    
    def validate_admin(self):
        """Valida acesso administrativo."""
        print_menu_header("ACESSO ADMINISTRATIVO")
        print(f"{YELLOW}Digite a senha de administrador{RESET}\n")
        
        for attempt in range(3):
            password = pwinput.pwinput(prompt="Senha Admin: ", mask='*')
            hash_input = hashlib.sha256(password.encode()).hexdigest()
            
            if hash_input == self._load_admin_password():
                return True
            
            if attempt < 2:
                print(f"{RED}Senha incorreta. Tentativas restantes: {2 - attempt}{RESET}")
        
        print(f"\n{RED}Acesso negado!{RESET}")
        return False
    
    def show_admin_menu(self):
        """Mostra menu administrativo."""
        while True:
            print_menu_header("MENU ADMINISTRATIVO")
            
            print(f"{BOLD}GERENCIAMENTO:{RESET}")
            print("  1) Listar usuários")
            print("  2) Adicionar usuário")
            print("  3) Remover usuário")
            print("  4) Alterar senha de usuário")
            print("  5) Alterar senha administrativa")
            print("\n  6) Ver logs de auditoria")
            print(f"\n{YELLOW}V{RESET} - Voltar")
            
            choice = input("\nSua escolha: ")
            
            if choice.upper() == 'V':
                break
            elif choice == '1':
                self.list_users()
            elif choice == '2':
                self.add_user()
            elif choice == '3':
                self.remove_user()
            elif choice == '4':
                self.change_user_password()
            elif choice == '5':
                self.change_admin_password()
            elif choice == '6':
                self.view_audit_logs()
    
    def list_users(self):
        """Lista todos os usuários."""
        print_menu_header("USUÁRIOS CADASTRADOS")
        
        users = self._load_users()
        print(f"{BOLD}Total: {len(users)} usuários{RESET}\n")
        for i, username in enumerate(sorted(users.keys()), 1):
            print(f"  {i}) {username}")
        
        press_enter_to_continue()
    
    def add_user(self):
        """Adiciona novo usuário."""
        print_menu_header("ADICIONAR USUÁRIO")
        
        username = input("Nome de usuário: ").strip().lower()
        
        if not username:
            print(f"{RED}Nome inválido{RESET}")
            press_enter_to_continue()
            return
        
        users = self._load_users()
        
        if username in users:
            print(f"{RED}Usuário já existe!{RESET}")
            press_enter_to_continue()
            return
        
        password = pwinput.pwinput(prompt="Senha: ", mask='*')
        password_confirm = pwinput.pwinput(prompt="Confirme: ", mask='*')
        
        if password != password_confirm or len(password) < 6:
            print(f"{RED}Senhas não conferem ou muito curta (mín. 6){RESET}")
            press_enter_to_continue()
            return
        
        salt = hashlib.md5(os.urandom(16)).hexdigest()
        hash_pass = hashlib.sha256((salt + password).encode()).hexdigest()
        
        users[username] = (salt, hash_pass)
        self._save_users(users)
        
        print(f"\n{GREEN}✓ Usuário '{username}' adicionado!{RESET}")
        press_enter_to_continue()
    
    def remove_user(self):
        """Remove usuário."""
        print_menu_header("REMOVER USUÁRIO")
        
        users = self._load_users()
        user_list = sorted(users.keys())
        
        for i, username in enumerate(user_list, 1):
            print(f"  {i}) {username}")
        
        choice = input(f"\n{YELLOW}V{RESET} - Cancelar | Selecione: ")
        
        if choice.upper() == 'V' or not choice.isdigit():
            return
        
        idx = int(choice) - 1
        if idx < 0 or idx >= len(user_list):
            return
        
        username = user_list[idx]
        confirm = input(f"\n{YELLOW}Confirma remoção de '{username}'? (S/N):{RESET} ")
        
        if confirm.upper() == 'S':
            del users[username]
            self._save_users(users)
            print(f"\n{GREEN}✓ Usuário removido!{RESET}")
        
        press_enter_to_continue()
    
    def change_user_password(self):
        """Altera senha de usuário."""
        print_menu_header("ALTERAR SENHA")
        
        users = self._load_users()
        user_list = sorted(users.keys())
        
        for i, username in enumerate(user_list, 1):
            print(f"  {i}) {username}")
        
        choice = input(f"\n{YELLOW}V{RESET} - Cancelar | Selecione: ")
        
        if choice.upper() == 'V' or not choice.isdigit():
            return
        
        idx = int(choice) - 1
        if idx < 0 or idx >= len(user_list):
            return
        
        username = user_list[idx]
        password = pwinput.pwinput(prompt="Nova senha: ", mask='*')
        password_confirm = pwinput.pwinput(prompt="Confirme: ", mask='*')
        
        if password != password_confirm or len(password) < 6:
            print(f"{RED}Senhas não conferem ou muito curta{RESET}")
            press_enter_to_continue()
            return
        
        salt = hashlib.md5(os.urandom(16)).hexdigest()
        hash_pass = hashlib.sha256((salt + password).encode()).hexdigest()
        users[username] = (salt, hash_pass)
        self._save_users(users)
        
        print(f"\n{GREEN}✓ Senha alterada!{RESET}")
        press_enter_to_continue()
    
    def change_admin_password(self):
        """Altera senha administrativa."""
        print_menu_header("ALTERAR SENHA ADMIN")
        
        current = pwinput.pwinput(prompt="Senha atual: ", mask='*')
        
        if hashlib.sha256(current.encode()).hexdigest() != self._load_admin_password():
            print(f"\n{RED}Senha incorreta!{RESET}")
            press_enter_to_continue()
            return
        
        password = pwinput.pwinput(prompt="Nova senha: ", mask='*')
        password_confirm = pwinput.pwinput(prompt="Confirme: ", mask='*')
        
        if password != password_confirm or len(password) < 6:
            print(f"{RED}Senhas não conferem ou muito curta{RESET}")
            press_enter_to_continue()
            return
        
        self._save_admin_password(password)
        print(f"\n{GREEN}✓ Senha admin alterada!{RESET}")
        press_enter_to_continue()
    
    def view_audit_logs(self):
        """Visualiza logs de auditoria."""
        print_menu_header("LOGS DE AUDITORIA")
        
        log_file = os.path.expanduser("~/logs_scriptN1/egsys_audit.log")
        
        if not os.path.exists(log_file):
            print(f"{YELLOW}Nenhum log encontrado{RESET}")
            press_enter_to_continue()
            return
        
        print(f"{BOLD}Opções:{RESET}")
        print("  1) Últimas 50 linhas")
        print("  2) Últimas 100 linhas")
        print("  3) Filtrar por usuário")
        print("  4) Filtrar por host")
        
        choice = input(f"\n{YELLOW}V{RESET} - Voltar | Escolha: ")
        
        if choice.upper() == 'V':
            return
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            if choice == '1':
                display_lines = lines[-50:]
            elif choice == '2':
                display_lines = lines[-100:]
            elif choice == '3':
                # Extrai usuários únicos dos logs
                users = set()
                for line in lines:
                    if 'user=' in line:
                        try:
                            user_part = line.split('user=')[1].split('|')[0].strip()
                            if user_part:  # Ignora usuários vazios
                                users.add(user_part)
                        except:
                            pass
                
                if not users:
                    print(f"\n{YELLOW}Nenhum usuário encontrado nos logs{RESET}")
                    press_enter_to_continue()
                    return
                
                print(f"\n{BOLD}Usuários disponíveis:{RESET}")
                print(f"  0) {CYAN}TODOS OS USUÁRIOS{RESET}")
                user_list = sorted(users)
                for i, u in enumerate(user_list, 1):
                    print(f"  {i}) {u}")
                
                user_choice = input(f"\n{YELLOW}V{RESET} - Voltar | Selecione: ")
                if user_choice.upper() == 'V':
                    return
                
                if not user_choice.isdigit():
                    return
                
                idx = int(user_choice)
                
                if idx == 0:
                    # Todos os usuários
                    display_lines = lines
                elif idx > 0 and idx <= len(user_list):
                    user = user_list[idx - 1]
                    display_lines = [l for l in lines if f"user={user}" in l]
                else:
                    return
            elif choice == '4':
                host = input("Host: ").strip()
                display_lines = [l for l in lines if f"host={host}" in l]
            else:
                return
            
            print(f"\n{BOLD}Registros: {len(display_lines)}{RESET}\n")
            for line in display_lines:
                print(line.strip())
        except Exception as e:
            print(f"{RED}Erro: {e}{RESET}")
        
        press_enter_to_continue()
    
    def _load_users(self):
        """Carrega usuários."""
        return dict(USUARIOS_AUTORIZADOS)
    
    def _save_users(self, users):
        """Salva usuários."""
        users_config = os.path.join(os.path.dirname(__file__), '..', 'config', 'users.py')
        with open(users_config, 'w') as f:
            f.write('"""Gerenciamento de usuários e autenticação."""\n')
            f.write('import hashlib\n\n')
            f.write('USUARIOS_AUTORIZADOS = {\n')
            for user, (salt, hash_val) in sorted(users.items()):
                f.write(f"    '{user}': ('{salt}', '{hash_val}'),\n")
            f.write('}\n\n')
            f.write('def validar_credenciais(username, password):\n')
            f.write('    """Valida credenciais do usuário."""\n')
            f.write('    if username not in USUARIOS_AUTORIZADOS:\n')
            f.write('        return False\n')
            f.write('    \n')
            f.write('    sal_armazenado, hash_armazenado = USUARIOS_AUTORIZADOS[username]\n')
            f.write('    senha_com_sal = sal_armazenado + password\n')
            f.write('    hash_digitado = hashlib.sha256(senha_com_sal.encode()).hexdigest()\n')
            f.write('    \n')
            f.write('    return hash_digitado == hash_armazenado\n')
