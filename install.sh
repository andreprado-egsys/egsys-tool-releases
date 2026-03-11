#!/bin/bash
# egSYS SAPA Tool - Instalador e Compilador Universal v2.1.2
# Gera um binário standalone e cria um desinstalador.

set -e

# --- Configurações ---
APP_NAME="egsys"
INSTALL_DIR="/opt/egsys-tool"
BIN_DIR="/usr/local/bin"
BUILD_DIR="/tmp/egsys-build"
REPO_PUBLIC="https://github.com/andreprado-egsys/egsys-tool-releases.git"
CONSTANTS_URL="https://raw.githubusercontent.com/andreprado-egsys/egsys-tool/main/config/constants.py"

# --- Cores ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Funções ---

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  egSYS SAPA Tool - Build & Install v2.1║${NC}"
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
rmdir /var/log/egsys-tool 2>/dev/null || echo "Diretório de log /var/log/egsys-tool não está vazio. Deixado para inspeção manual."

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

# Clona repositório público
echo -e "${GREEN}[MODO]${NC} Clonando repositório público..."
rm -rf "$BUILD_DIR/repo"
mkdir -p "$BUILD_DIR/repo"
git clone "$REPO_PUBLIC" "$BUILD_DIR/repo"
SOURCE_DIR="$BUILD_DIR/repo"

# Baixa constants.py do repositório privado (com dados reais)
echo -e "${CYAN}[CONFIG]${NC} Baixando configurações do repositório privado..."
if ! curl -fsSL "$CONSTANTS_URL" -o "$SOURCE_DIR/config/constants.py" 2>/dev/null; then
    echo -e "${RED}[ERRO]${NC} Falha ao baixar configurações do repositório privado"
    echo -e "${YELLOW}[INFO]${NC} Verifique se você tem acesso ao repositório privado"
    exit 1
fi

# Detecta Distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}[ERRO]${NC} Distribuição não detectada."
    exit 1
fi

# Instala dependências de build
echo -e "${CYAN}[DEPS]${NC} Instalando dependências de compilação..."
case $DISTRO in
    ubuntu|debian|zorin|linuxmint|pop|kali)
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-venv python3-dev build-essential git curl
        ;;
    arch|manjaro|cachyos|endeavouros)
        pacman -Sy --noconfirm --needed python python-pip python-virtualenv base-devel git curl
        ;;
    fedora|rhel|centos)
        dnf install -y python3 python3-pip python3-devel gcc git curl
        ;;
esac

# Prepara ambiente de build
echo -e "${CYAN}[BUILD]${NC} Preparando ambiente virtual..."
rm -rf "$BUILD_DIR/venv"
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"

# Instala dependências Python e PyInstaller
echo -e "${CYAN}[PIP]${NC} Instalando PyInstaller e dependências..."
pip install --upgrade pip --quiet
pip install -r "$SOURCE_DIR/requirements.txt" --quiet

# Compila o binário
echo -e "${CYAN}[COMPILANDO]${NC} Gerando binário standalone..."
cd "$SOURCE_DIR"
pyinstaller --clean --onefile --name "$APP_NAME" --strip --paths=. main.py

# Instala o binário
echo -e "${CYAN}[INSTALANDO]${NC} Movendo binário para $BIN_DIR..."
if [ -f "dist/$APP_NAME" ]; then
    cp "dist/$APP_NAME" "$BIN_DIR/$APP_NAME"
    chmod +x "$BIN_DIR/$APP_NAME"
else
    echo -e "${RED}[ERRO]${NC} Falha na compilação. Binário não encontrado."
    exit 1
fi

# Instala recursos (ícone e .desktop)
echo -e "${CYAN}[RECURSOS]${NC} Configurando atalhos..."
mkdir -p "$INSTALL_DIR/assets"

# Baixa ícone do repositório público
if curl -fsSL "https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/egsys-icon.png" \
    -o "$INSTALL_DIR/assets/egsys-icon.png" 2>/dev/null; then
    ICON_PATH="$INSTALL_DIR/assets/egsys-icon.png"
    echo -e "${GREEN}[OK]${NC} Ícone baixado"
else
    ICON_PATH="utilities-terminal"
    echo -e "${YELLOW}[AVISO]${NC} Ícone não encontrado, usando padrão"
fi

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
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

# Configura logs
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

# Limpeza
echo -e "${CYAN}[LIMPEZA]${NC} Removendo arquivos temporários..."
deactivate
rm -rf "$BUILD_DIR"

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
