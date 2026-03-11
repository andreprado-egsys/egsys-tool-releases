# egSYS SAPA Tool - Instalação

**Versão 2.1.2** - Sistema de Gerenciamento Multi-Servidor

[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

## 🚀 Instalação Rápida

```bash
curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install.sh | sudo bash
```

## 📋 Requisitos

- Linux (Ubuntu, Debian, Arch, Fedora, etc)
- Acesso root/sudo

## 🔧 Instalação Manual

```bash
# 1. Baixe o instalador
wget https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install.sh

# 2. Execute
chmod +x install.sh
sudo ./install.sh
```

## 📦 O que será instalado

- Binário em `/opt/egsys-tool/`
- Comando global `egsys`
- Diretórios de log
- Comandos de atualização e desinstalação

## 🔄 Atualizar

```bash
sudo egsys-update
```

## 🗑️ Desinstalar

```bash
sudo egsys-uninstall
```

## 📖 Uso

Após instalação, execute:

```bash
egsys
```

## 🆘 Suporte

Para suporte, entre em contato com a equipe egSYS.

## 📄 Licença

Proprietary - egSYS © 2026
