"""Módulo de autenticação e gerenciamento de sessão."""
import hashlib
import pwinput
from config.users import validar_credenciais, USUARIOS_AUTORIZADOS
from config.constants import ADMIN_PASSWORD_HASH, PASSWORD_SAFEGUARD
from core.logger import log_action

class AuthManager:
    def __init__(self):
        self.current_user = None
        self.tentativas_maximas = 3
    
    def realizar_login(self):
        """Realiza login do usuário."""
        tentativas = self.tentativas_maximas
        
        while tentativas > 0:
            username = input(f"\nUsuário: ")
            
            if username in USUARIOS_AUTORIZADOS:
                password = pwinput.pwinput(prompt="Senha: ", mask='*')
                
                if validar_credenciais(username, password):
                    self.current_user = username
                    log_action(f"Login bem-sucedido para '{username}'")
                    return username
                else:
                    tentativas -= 1
                    print(f"\nSenha incorreta. Tentativas restantes: {tentativas}")
            else:
                tentativas -= 1
                print(f"\nUsuário não encontrado. Tentativas restantes: {tentativas}")
        
        print("\nNúmero máximo de tentativas excedido.")
        return None
    
    def validar_admin(self, password):
        """Valida senha de administrador."""
        return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH
    
    def validar_salvaguarda(self, password):
        """Valida senha de salvaguarda."""
        return hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(PASSWORD_SAFEGUARD.encode()).hexdigest()
