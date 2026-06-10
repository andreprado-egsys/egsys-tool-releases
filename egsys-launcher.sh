#!/bin/bash
# egSYS SAPA Tool - Launcher que detecta o terminal padrão do sistema
# Usado pelo .desktop para abrir no terminal correto independente do DE

EGSYS_BIN="/usr/local/bin/egsys"

# Detecta terminal padrão do sistema (ordem de prioridade)
detect_terminal() {
    # 1. Variável de ambiente do usuário
    [ -n "$TERMINAL" ] && command -v "$TERMINAL" &>/dev/null && echo "$TERMINAL" && return

    # 2. XDG default terminal (respeita configuração do DE)
    local xdg_term
    xdg_term=$(xdg-mime query default x-scheme-handler/terminal 2>/dev/null | sed 's/\.desktop$//')
    [ -n "$xdg_term" ] && command -v "$xdg_term" &>/dev/null && echo "$xdg_term" && return

    # 3. gsettings (GNOME/Cinnamon)
    if command -v gsettings &>/dev/null; then
        local gs_term
        gs_term=$(gsettings get org.gnome.desktop.default-applications.terminal exec 2>/dev/null | tr -d "'")
        [ -n "$gs_term" ] && command -v "$gs_term" &>/dev/null && echo "$gs_term" && return
    fi

    # 4. Detecção por DE ativo
    case "${XDG_CURRENT_DESKTOP,,}" in
        *kde*|*plasma*) command -v konsole &>/dev/null && echo "konsole" && return ;;
        *gnome*) command -v gnome-terminal &>/dev/null && echo "gnome-terminal" && return ;;
        *xfce*) command -v xfce4-terminal &>/dev/null && echo "xfce4-terminal" && return ;;
        *mate*) command -v mate-terminal &>/dev/null && echo "mate-terminal" && return ;;
        *cinnamon*) command -v gnome-terminal &>/dev/null && echo "gnome-terminal" && return ;;
        *lxqt*) command -v qterminal &>/dev/null && echo "qterminal" && return ;;
        *lxde*) command -v lxterminal &>/dev/null && echo "lxterminal" && return ;;
    esac

    # 5. Fallback: busca qualquer terminal instalado
    local terminals=(kitty alacritty wezterm foot konsole gnome-terminal xfce4-terminal mate-terminal tilix terminator lxterminal qterminal xterm)
    for t in "${terminals[@]}"; do
        command -v "$t" &>/dev/null && echo "$t" && return
    done

    echo ""
}

TERM_CMD=$(detect_terminal)

if [ -z "$TERM_CMD" ]; then
    # Sem terminal gráfico — tenta executar direto (caso seja chamado de um terminal)
    exec "$EGSYS_BIN" "$@"
fi

# Lança no terminal detectado com a flag correta para cada emulador
case "$TERM_CMD" in
    konsole)        exec konsole -e "$EGSYS_BIN" "$@" ;;
    gnome-terminal) exec gnome-terminal -- "$EGSYS_BIN" "$@" ;;
    xfce4-terminal) exec xfce4-terminal -e "$EGSYS_BIN $*" ;;
    mate-terminal)  exec mate-terminal -e "$EGSYS_BIN $*" ;;
    tilix)          exec tilix -e "$EGSYS_BIN $*" ;;
    terminator)     exec terminator -e "$EGSYS_BIN $*" ;;
    kitty)          exec kitty "$EGSYS_BIN" "$@" ;;
    alacritty)      exec alacritty -e "$EGSYS_BIN" "$@" ;;
    wezterm)        exec wezterm start -- "$EGSYS_BIN" "$@" ;;
    foot)           exec foot "$EGSYS_BIN" "$@" ;;
    qterminal)      exec qterminal -e "$EGSYS_BIN $*" ;;
    lxterminal)     exec lxterminal -e "$EGSYS_BIN $*" ;;
    xterm)          exec xterm -e "$EGSYS_BIN" "$@" ;;
    *)              exec "$TERM_CMD" -e "$EGSYS_BIN" "$@" ;;
esac
