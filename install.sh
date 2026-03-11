#!/bin/bash
# egSYS SAPA Tool - Instalador Automático
# Baixa binário do GitHub Releases

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

VERSION="2.1.2"
REPO="andreprado-egsys/egsys-tool-releases"
APP_NAME="egsys"
INSTALL_DIR="/opt/egsys-tool"
BIN_DIR="/usr/local/bin"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  egSYS SAPA Tool - Instalador v${VERSION}  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERRO]${NC} Execute como root: ${YELLOW}sudo $0${NC}"
    exit 1
fi

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
        exit 1
        ;;
esac

echo -e "${GREEN}[INFO]${NC} Arquitetura: $ARCH"

echo -e "${CYAN}[SETUP]${NC} Criando diretórios..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo -e "${CYAN}[DOWNLOAD]${NC} Baixando executável..."
DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/$BINARY_NAME"

echo -e "${YELLOW}URL:${NC} $DOWNLOAD_URL"

if command -v curl &> /dev/null; then
    if ! curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/$APP_NAME" 2>&1; then
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        echo -e "Verifique se a release v${VERSION} existe"
        exit 1
    fi
elif command -v wget &> /dev/null; then
    if ! wget -q "$DOWNLOAD_URL" -O "$INSTALL_DIR/$APP_NAME" 2>&1; then
        echo -e "${RED}[ERRO]${NC} Falha ao baixar binário"
        exit 1
    fi
else
    echo -e "${RED}[ERRO]${NC} curl ou wget não encontrado"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/$APP_NAME" ] || [ ! -s "$INSTALL_DIR/$APP_NAME" ]; then
    echo -e "${RED}[ERRO]${NC} Arquivo binário não foi baixado corretamente"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Binário baixado com sucesso"

chmod +x "$INSTALL_DIR/$APP_NAME"

echo -e "${CYAN}[LINK]${NC} Criando link simbólico..."
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/$APP_NAME"

echo -e "${CYAN}[LOGS]${NC} Configurando diretórios de log..."
mkdir -p /var/log/egsys-tool
chmod 777 /var/log/egsys-tool

for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        user=$(basename "$user_home")
        sudo -u "$user" mkdir -p "$user_home/logs_scriptN1" 2>/dev/null || true
        chmod 777 "$user_home/logs_scriptN1" 2>/dev/null || true
    fi
done

echo -e "${CYAN}[UPDATE]${NC} Criando comando de atualização..."
cat > "$BIN_DIR/egsys-update" << 'EOFUPDATE'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31mERRO:\033[0m Execute como root: sudo egsys-update"
    exit 1
fi
echo -e "\nAtualizando egSYS SAPA Tool..."
curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install.sh | bash
echo -e "\n\033[0;32mAtualização concluída!\033[0m\n"
EOFUPDATE

chmod +x "$BIN_DIR/egsys-update"

echo -e "${CYAN}[UNINSTALLER]${NC} Criando desinstalador..."
cat > "$BIN_DIR/egsys-uninstall" << 'EOFUNINSTALL'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[0;31mERRO:\033[0m Execute como root: sudo egsys-uninstall"
    exit 1
fi
echo -e "\nDesinstalando egSYS SAPA Tool..."
rm -f "/usr/local/bin/egsys"
rm -f "/usr/local/bin/egsys-update"
rm -f "/usr/local/bin/egsys-uninstall"
rm -rf "/opt/egsys-tool"
echo -e "\n\033[0;32m✓ egSYS SAPA Tool desinstalado.\033[0m\n"
EOFUNINSTALL

chmod +x "$BIN_DIR/egsys-uninstall"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Instalação Concluída!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Execute: ${YELLOW}egsys${NC}"
echo -e "Atualizar: ${YELLOW}sudo egsys-update${NC}"
echo -e "Desinstalar: ${YELLOW}sudo egsys-uninstall${NC}"
echo ""
