# egSYS SAPA Tool - Releases Públicos

**Versão Atual: 2.1.7**

Sistema de Avaliação e Performance de Ambientes para gerenciamento multi-servidor.

## 🚀 Instalação Rápida

### Ubuntu / Debian / Zorin / Linux Mint
```bash
wget -qO- https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-ubuntu.sh | sudo bash
```

**Ou com curl:**
```bash
curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-ubuntu.sh | sudo bash
```

### Arch Linux / Manjaro / CachyOS / EndeavourOS
```bash
curl -fsSL https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-arch.sh | sudo bash
```

**Ou com wget:**
```bash
wget -qO- https://raw.githubusercontent.com/andreprado-egsys/egsys-tool-releases/main/install-arch.sh | sudo bash
```

## 📦 Binários Disponíveis

- **egsys-ubuntu**: Compilado em Ubuntu 22.04 (Python 3.10, GLIBC 2.35)
  - Compatível com: Ubuntu 20.04+, Debian 11+, Zorin OS, Linux Mint
  
- **egsys-arch**: Compilado em Arch Linux (Python 3.14, GLIBC 2.43)
  - Compatível com: Arch Linux, Manjaro, CachyOS, EndeavourOS, Garuda

## 🔧 Comandos Pós-Instalação

```bash
# Executar a ferramenta
egsys

# Atualizar para versão mais recente
sudo egsys-update

# Desinstalar
sudo egsys-uninstall
```

## 📋 Requisitos

- Sistema operacional: Linux (64-bit)
- Privilégios: sudo/root para instalação
- Ferramentas: wget ou curl
- Espaço em disco: ~10 MB

## 🔐 Segurança

- Binários compilados em containers Docker isolados
- Código-fonte mantido em repositório privado
- Releases assinados e verificáveis via GitHub

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões.

## 🆘 Suporte

Para problemas ou dúvidas:
- Abra uma issue neste repositório
- Entre em contato com a equipe egSYS

## 📄 Licença

Propriedade da egSYS. Todos os direitos reservados.
