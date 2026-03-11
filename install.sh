#!/bin/bash
# egSYS SAPA Tool - Instalador de Binário v2.1.2
# Baixa executável pré-compilado do GitHub Releases

set -e

# --- Configurações ---
VERSION="2.1.2"
REPO="andreprado-egsys/egsys-tool-releases"
APP_NAME="egsys"
INSTALL_DIR="/opt/egsys-tool"
BIN_DIR="/usr/local/bin"

# --- Cores ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Funções ---

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  egSYS SAPA Tool - Instalador v${VERSION}  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[ERRO]${NC} Este script precisa ser executado como root."
        echo -e "Use: ${YELLOW}sudo $0${NC}"
        exit 1
    fi
}

create_uninstaller() {
    echo -e "${CYAN}[UNINSTALLER]${NC} Criando script de desinstalação..."
    cat > "$BIN_DIR/egsys-uninstall" << 'EOFUNINSTALL'
#!/bin/bash
echo -e "\nDesinstalando egSYS SAPA Tool..."
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31mERRO:\033[0m Execute como root: sudo egsys-uninstall"
    exit 1
fi

# Remove arquivos principais
rm -f "/usr/local/bin/egsys"
rm -f "/usr/local/bin/egsys-update"
rm -f "/usr/local/bin/egsys-uninstall"
rm -rf "/opt/egsys-tool"
rm -f "/usr/share/applications/egsys.desktop"

# Remove diretórios de log (se vazios)
rmdir /var/log/egsys-tool 2>/dev/null || echo "Diretório de log não está vazio. Deixado para inspeção manual."

# Atualiza cache de aplicativos
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

echo -e "\n\033[0;32megSYS SAPA Tool foi desinstalado com sucesso.\033[0m\n"
EOFUNINSTALL
    chmod +x "$BIN_DIR/egsys-uninstall"
}

# --- Execução Principal ---

print_header
check_root

# Detecta arquitetura
echo -e "${CYAN}[SISTEMA]${NC} Detectando arquitetura..."
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        BINARY_NAME="egsys-linux-x86_64"
        ;;
    aarch64|arm64)
        BINARY_NAME="egsys-linux-arm64"
        ;;
    *)
        echo -e "${RED}[ERRO]${NC} Arquitetura $ARCH não suportada"
        echo -e "Arquiteturas suportadas: x86_64, aarch64, arm64"
        exit 1
        ;;
esac

echo -e "${GREEN}[INFO]${NC} Arquitetura: $ARCH"

# Cria diretórios
echo -e "${CYAN}[SETUP]${NC} Criando diretórios..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Baixa binário do GitHub Releases
echo -e "${CYAN}[DOWNLOAD]${NC} Baixando executável do GitHub Releases..."
DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/$BINARY_NAME"

echo -e "${YELLOW}URL:${NC} $DOWNLOAD_URL"

if command -v curl &> /dev/null; then
    if ! curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/$APP_NAME" 2>&1; then
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        echo -e "Verifique se a release v${VERSION} existe no GitHub"
        exit 1
    fi
elif command -v wget &> /dev/null; then
    if ! wget -q "$DOWNLOAD_URL" -O "$INSTALL_DIR/$APP_NAME" 2>&1; then
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        echo -e "Verifique se a release v${VERSION} existe no GitHub"
        exit 1
    fi
else
    echo -e "${RED}[ERRO]${NC} curl ou wget não encontrado"
    echo -e "Instale curl ou wget e tente novamente"
    exit 1
fi

# Verifica se o download foi bem-sucedido
if [ ! -f "$INSTALL_DIR/$APP_NAME" ] || [ ! -s "$INSTALL_DIR/$APP_NAME" ]; then
    echo -e "${RED}[ERRO]${NC} Arquivo binário não foi baixado corretamente"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Binário baixado com sucesso"

# Define permissões
chmod +x "$INSTALL_DIR/$APP_NAME"

# Cria link simbólico
echo -e "${CYAN}[LINK]${NC} Criando link simbólico..."
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/$APP_NAME"

# Baixa ícone
echo -e "${CYAN}[RECURSOS]${NC} Baixando ícone..."
mkdir -p "$INSTALL_DIR/assets"
if curl -fsSL "https://raw.githubusercontent.com/$REPO/main/egsys-icon.png" \
    -o "$INSTALL_DIR/assets/egsys-icon.png" 2>/dev/null; then
    ICON_PATH="$INSTALL_DIR/assets/egsys-icon.png"
    echo -e "${GREEN}[OK]${NC} Ícone baixado"
else
    ICON_PATH="utilities-terminal"
    echo -e "${YELLOW}[AVISO]${NC} Ícone não encontrado, usando padrão"
fi

# Cria entrada no menu
echo -e "${CYAN}[DESKTOP]${NC} Configurando atalho no menu..."
cat > /usr/share/applications/egsys.desktop << EOFDESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=egSYS SAPA Tool
Comment=Sistema de Avaliação e Performance de Ambientes
Exec=$BIN_DIR/$APP_NAME
Icon=$ICON_PATH
Terminal=true
Categories=System;Network;RemoteAccess;
Keywords=ssh;vpn;server;management;monitoring;
StartupNotify=false
EOFDESKTOP

chmod 644 /usr/share/applications/egsys.desktop

# Atualiza cache de aplicativos
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

# Configura diretórios de log
echo -e "${CYAN}[LOGS]${NC} Configurando diretórios de log..."
mkdir -p /var/log/egsys-tool
chmod 777 /var/log/egsys-tool

# Cria diretórios de log para usuários
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        user=$(basename "$user_home")
        sudo -u "$user" mkdir -p "$user_home/logs_scriptN1" 2>/dev/null || true
        chmod 777 "$user_home/logs_scriptN1" 2>/dev/null || true
    fi
done

# Cria comando de atualização
echo -e "${CYAN}[UPDATE]${NC} Criando comando de atualização..."
cat > "$BIN_DIR/egsys-update" << 'EOFUPDATE'
#!/bin/bash
echo -e "\nAtualizando egSYS SAPA Tool..."
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31mERRO:\033[0m Execute como root: sudo egsys-update"
    exit 1
fi
curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install.sh | bash
echo -e "\n\033[0;32mAtualização concluída!\033[0m\n"
EOFUPDATE

chmod +x "$BIN_DIR/egsys-update"

# Cria desinstalador
create_uninstaller

# Limpeza (se necessário)
echo -e "${CYAN}[LIMPEZA]${NC} Finalizando instalação..."

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalação Concluída com Sucesso!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "O binário foi instalado em: ${YELLOW}$BIN_DIR/$APP_NAME${NC}"
echo -e "Execute com o comando: ${YELLOW}egsys${NC}"
echo -e "Para atualizar, use: ${YELLOW}sudo egsys-update${NC}"
echo -e "Para desinstalar, use: ${YELLOW}sudo egsys-uninstall${NC}"
echo ""
