"""Analisador automático de logs de monitoramento."""
import re
from config.constants import RED, YELLOW, GREEN, CYAN, BOLD, RESET

class SystemAnalyzer:
    def __init__(self):
        # Thresholds de alerta
        self.cpu_warning = 70.0
        self.cpu_critical = 90.0
        self.mem_warning = 80.0
        self.mem_critical = 95.0
        self.load_warning_multiplier = 0.7  # 70% do número de CPUs
        self.load_critical_multiplier = 1.0  # 100% do número de CPUs
    
    def analyze_top_output(self, top_output):
        """Analisa a saída do top e retorna diagnóstico."""
        issues = []
        warnings = []
        info = []
        
        # Parse das informações principais
        uptime_info = self._parse_uptime(top_output)
        cpu_info = self._parse_cpu(top_output)
        mem_info = self._parse_memory(top_output)
        processes = self._parse_processes(top_output)
        
        # Análise de uptime
        if uptime_info:
            info.append(f"⏱️  Uptime: {uptime_info['uptime']}")
            info.append(f"👥 Usuários conectados: {uptime_info['users']}")
            
            # Análise de load average
            load = uptime_info.get('load_avg', [0, 0, 0])
            num_cpus = self._estimate_cpu_count(top_output)
            
            if load[0] > num_cpus * self.load_critical_multiplier:
                issues.append(f"🔴 CRÍTICO: Load average muito alto ({load[0]:.2f}) - Sistema sobrecarregado!")
            elif load[0] > num_cpus * self.load_warning_multiplier:
                warnings.append(f"🟡 ATENÇÃO: Load average elevado ({load[0]:.2f}) - Monitorar de perto")
            else:
                info.append(f"✅ Load average normal: {load[0]:.2f}")
        
        # Análise de CPU
        if cpu_info:
            cpu_used = 100.0 - cpu_info.get('idle', 0)
            
            if cpu_used >= self.cpu_critical:
                issues.append(f"🔴 CRÍTICO: CPU em {cpu_used:.1f}% - Servidor sob alta carga!")
            elif cpu_used >= self.cpu_warning:
                warnings.append(f"🟡 ATENÇÃO: CPU em {cpu_used:.1f}% - Uso elevado")
            else:
                info.append(f"✅ CPU: {cpu_used:.1f}% de uso")
            
            # Análise de I/O wait
            if cpu_info.get('wa', 0) > 10:
                warnings.append(f"🟡 I/O Wait alto ({cpu_info['wa']:.1f}%) - Possível gargalo de disco")
        
        # Análise de Memória
        if mem_info:
            mem_used_pct = (mem_info['used'] / mem_info['total']) * 100
            
            if mem_used_pct >= self.mem_critical:
                issues.append(f"🔴 CRÍTICO: Memória em {mem_used_pct:.1f}% - Risco de OOM!")
            elif mem_used_pct >= self.mem_warning:
                warnings.append(f"🟡 ATENÇÃO: Memória em {mem_used_pct:.1f}% - Uso elevado")
            else:
                info.append(f"✅ Memória: {mem_used_pct:.1f}% de uso")
            
            # Análise de Swap
            if mem_info.get('swap_total', 0) > 0:
                swap_used_pct = (mem_info['swap_used'] / mem_info['swap_total']) * 100
                if swap_used_pct > 50:
                    warnings.append(f"🟡 Swap em uso ({swap_used_pct:.1f}%) - Memória insuficiente")
        
        # Análise de Processos
        if processes:
            zombie_count = sum(1 for p in processes if 'Z' in p.get('status', ''))
            stopped_count = sum(1 for p in processes if 'T' in p.get('status', ''))
            
            if zombie_count > 0:
                warnings.append(f"🟡 {zombie_count} processo(s) zombie detectado(s)")
            
            if stopped_count > 5:
                warnings.append(f"🟡 {stopped_count} processos parados - Investigar")
            
            # Top 5 processos por CPU
            top_cpu = sorted(processes, key=lambda x: x.get('cpu', 0), reverse=True)[:5]
            if top_cpu and top_cpu[0].get('cpu', 0) > 50:
                warnings.append(f"🟡 Processo '{top_cpu[0]['command']}' usando {top_cpu[0]['cpu']:.1f}% CPU")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'info': info,
            'uptime': uptime_info,
            'cpu': cpu_info,
            'memory': mem_info,
            'top_processes': processes[:10] if processes else []
        }
    
    def _parse_uptime(self, output):
        """Extrai informações de uptime."""
        match = re.search(r'up\s+(.+?),\s+(\d+)\s+users?,\s+load average:\s+([\d.]+),\s+([\d.]+),\s+([\d.]+)', output)
        if match:
            return {
                'uptime': match.group(1).strip(),
                'users': int(match.group(2)),
                'load_avg': [float(match.group(3)), float(match.group(4)), float(match.group(5))]
            }
        return None
    
    def _parse_cpu(self, output):
        """Extrai informações de CPU."""
        match = re.search(r'%Cpu\(s\):\s+([\d.]+)\s+us,\s+([\d.]+)\s+sy,\s+([\d.]+)\s+ni,\s+([\d.]+)\s+id,\s+([\d.]+)\s+wa', output)
        if match:
            return {
                'user': float(match.group(1)),
                'system': float(match.group(2)),
                'nice': float(match.group(3)),
                'idle': float(match.group(4)),
                'wa': float(match.group(5))
            }
        return None
    
    def _parse_memory(self, output):
        """Extrai informações de memória."""
        mem_match = re.search(r'MiB Mem\s*:\s*([\d.]+)\s+total,\s*([\d.]+)\s+free,\s*([\d.]+)\s+used', output)
        swap_match = re.search(r'MiB Swap:\s*([\d.]+)\s+total,\s*([\d.]+)\s+free,\s*([\d.]+)\s+used', output)
        
        result = {}
        if mem_match:
            result.update({
                'total': float(mem_match.group(1)),
                'free': float(mem_match.group(2)),
                'used': float(mem_match.group(3))
            })
        
        if swap_match:
            result.update({
                'swap_total': float(swap_match.group(1)),
                'swap_free': float(swap_match.group(2)),
                'swap_used': float(swap_match.group(3))
            })
        
        return result if result else None
    
    def _parse_processes(self, output):
        """Extrai informações dos processos."""
        processes = []
        lines = output.split('\n')
        
        # Encontra o início da lista de processos
        start_idx = -1
        for i, line in enumerate(lines):
            if 'PID' in line and 'USER' in line and 'COMMAND' in line:
                start_idx = i + 1
                break
        
        if start_idx == -1:
            return processes
        
        # Parse dos processos
        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) >= 12:
                try:
                    processes.append({
                        'pid': parts[0],
                        'user': parts[1],
                        'cpu': float(parts[8]),
                        'mem': float(parts[9]),
                        'time': parts[10],
                        'command': parts[11],
                        'status': parts[7]
                    })
                except (ValueError, IndexError):
                    continue
        
        return processes
    
    def _estimate_cpu_count(self, output):
        """Estima o número de CPUs baseado no output."""
        # Tenta encontrar informações de CPU no output
        # Por padrão, assume 4 CPUs se não conseguir determinar
        return 4
    
    def generate_report(self, analysis, host):
        """Gera relatório formatado da análise."""
        report = []
        
        report.append("=" * 80)
        report.append(f"📊 ANÁLISE AUTOMÁTICA DO SERVIDOR: {host.upper()}")
        report.append("=" * 80)
        report.append("")
        
        # Problemas críticos
        if analysis['issues']:
            report.append(f"{RED}{BOLD}🚨 PROBLEMAS CRÍTICOS:{RESET}")
            for issue in analysis['issues']:
                report.append(f"   {issue}")
            report.append("")
        
        # Avisos
        if analysis['warnings']:
            report.append(f"{YELLOW}{BOLD}⚠️  AVISOS:{RESET}")
            for warning in analysis['warnings']:
                report.append(f"   {warning}")
            report.append("")
        
        # Informações gerais
        if analysis['info']:
            report.append(f"{GREEN}{BOLD}ℹ️  INFORMAÇÕES:{RESET}")
            for info in analysis['info']:
                report.append(f"   {info}")
            report.append("")
        
        # Top processos
        if analysis['top_processes']:
            report.append(f"{CYAN}{BOLD}🔝 TOP 10 PROCESSOS (por CPU):{RESET}")
            report.append(f"   {'PID':<10} {'USER':<12} {'%CPU':<8} {'%MEM':<8} {'COMMAND'}")
            report.append("   " + "-" * 70)
            for proc in analysis['top_processes']:
                report.append(f"   {proc['pid']:<10} {proc['user']:<12} {proc['cpu']:<8.1f} {proc['mem']:<8.1f} {proc['command']}")
            report.append("")
        
        # Recomendações
        report.append(f"{BOLD}💡 RECOMENDAÇÕES:{RESET}")
        if analysis['issues']:
            report.append("   • Ação imediata necessária - Problemas críticos detectados")
            report.append("   • Considere escalar recursos ou otimizar processos")
        elif analysis['warnings']:
            report.append("   • Monitorar de perto nas próximas horas")
            report.append("   • Planejar otimizações se o padrão persistir")
        else:
            report.append("   • Sistema operando normalmente")
            report.append("   • Manter monitoramento de rotina")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
