#!/bin/bash
# egSYS SAPA Tool - Instalador Arch Linux v2.1.8

set -e

VERSION="2.1.8"
APP_NAME="egsys"
INSTALL_DIR="/opt/egsys-tool"
BIN_DIR="/usr/local/bin"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  egSYS Tool - Arch Linux v${VERSION}      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[ERRO]${NC} Execute como root: ${YELLOW}sudo $0${NC}"
        exit 1
    fi
}

create_uninstaller() {
    cat > "$BIN_DIR/egsys-uninstall" << 'EOFUNINSTALL'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31mERRO:\033[0m Execute como root: sudo egsys-uninstall"
    exit 1
fi
rm -f /usr/local/bin/egsys /usr/local/bin/egsys-update /usr/local/bin/egsys-uninstall
rm -rf /opt/egsys-tool /usr/share/applications/egsys.desktop
rmdir /var/log/egsys-tool 2>/dev/null || true
command -v update-desktop-database &> /dev/null && update-desktop-database /usr/share/applications/ 2>/dev/null || true
echo -e "\n\033[0;32megSYS Tool desinstalado com sucesso.\033[0m\n"
EOFUNINSTALL
    chmod +x "$BIN_DIR/egsys-uninstall"
}

print_header
check_root

echo -e "${CYAN}[SISTEMA]${NC} Detectando distribuição..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case $ID in
        arch|manjaro|cachyos|endeavouros|garuda|artix)
            echo -e "${GREEN}[OK]${NC} Distribuição: $PRETTY_NAME"
            ;;
        *)
            echo -e "${YELLOW}[AVISO]${NC} Distribuição $ID não é oficialmente suportada"
            echo -e "${YELLOW}[INFO]${NC} Use install-ubuntu.sh para Ubuntu/Debian e derivados"
            read -p "Continuar mesmo assim? (s/N): " -n 1 -r
            echo
            [[ ! $REPLY =~ ^[Ss]$ ]] && exit 1
            ;;
    esac
else
    echo -e "${RED}[ERRO]${NC} Não foi possível detectar a distribuição"
    exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

echo -e "${CYAN}[DOWNLOAD]${NC} Baixando binário Arch v${VERSION}..."

if command -v curl &> /dev/null; then
    curl -fL "https://github.com/andreprado-egsys/egsys-tool-releases/releases/download/v${VERSION}/egsys-arch" -o "$INSTALL_DIR/$APP_NAME" || {
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        exit 1
    }
elif command -v wget &> /dev/null; then
    wget -q --show-progress "https://github.com/andreprado-egsys/egsys-tool-releases/releases/download/v${VERSION}/egsys-arch" -O "$INSTALL_DIR/$APP_NAME" || {
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        exit 1
    }
else
    echo -e "${RED}[ERRO]${NC} curl ou wget não encontrado"
    exit 1
fi

[ ! -s "$INSTALL_DIR/$APP_NAME" ] && echo -e "${RED}[ERRO]${NC} Binário vazio" && exit 1

chmod +x "$INSTALL_DIR/$APP_NAME"
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/$APP_NAME"

echo -e "${GREEN}[OK]${NC} Binário instalado: $(du -h "$INSTALL_DIR/$APP_NAME" | cut -f1)"

echo -e "${CYAN}[RECURSOS]${NC} Configurando ícone e menu..."
mkdir -p "$INSTALL_DIR/assets"

if command -v curl &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/egsys-icon.png -o "$INSTALL_DIR/assets/egsys-icon.png" 2>/dev/null && ICON_PATH="$INSTALL_DIR/assets/egsys-icon.png" || ICON_PATH="utilities-terminal"
elif command -v wget &> /dev/null; then
    wget -q https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/egsys-icon.png -O "$INSTALL_DIR/assets/egsys-icon.png" 2>/dev/null && ICON_PATH="$INSTALL_DIR/assets/egsys-icon.png" || ICON_PATH="utilities-terminal"
else
    ICON_PATH="utilities-terminal"
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
command -v update-desktop-database &> /dev/null && update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo -e "${CYAN}[LOGS]${NC} Configurando diretórios..."
mkdir -p /var/log/egsys-tool
chmod 777 /var/log/egsys-tool

for user_home in /home/*; do
    [ -d "$user_home" ] && {
        user=$(basename "$user_home")
        sudo -u "$user" mkdir -p "$user_home/logs_scriptN1" 2>/dev/null || true
        chmod 777 "$user_home/logs_scriptN1" 2>/dev/null || true
    }
done

cat > "$BIN_DIR/egsys-update" << 'EOFUPDATE'
#!/bin/bash
[ "$EUID" -ne 0 ] && echo -e "\033[0;31mERRO:\033[0m Execute como root" && exit 1
if command -v curl &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-arch.sh | bash
else
    wget -qO- https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-arch.sh | bash
fi
EOFUPDATE
chmod +x "$BIN_DIR/egsys-update"

create_uninstaller

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalação Concluída com Sucesso!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Execute: ${YELLOW}egsys${NC}"
echo -e "Atualizar: ${YELLOW}sudo egsys-update${NC}"
echo -e "Desinstalar: ${YELLOW}sudo egsys-uninstall${NC}"
echo ""
