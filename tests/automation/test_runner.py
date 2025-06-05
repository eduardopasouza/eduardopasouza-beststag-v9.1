
"""
BestStag v9.1 - Test Runner Automatizado
Script para executar diferentes suites de testes com relatórios
"""

import os
import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class TestRunner:
    """
    Runner automatizado para execução de testes
    Suporta diferentes tipos de teste e geração de relatórios
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configurações de teste
        self.test_configs = {
            "unit": {
                "path": "tests/",
                "markers": "not integration and not e2e and not performance",
                "timeout": 300,
                "description": "Testes unitários rápidos"
            },
            "integration": {
                "path": "tests/integration/",
                "markers": "integration",
                "timeout": 600,
                "description": "Testes de integração"
            },
            "e2e": {
                "path": "tests/e2e/",
                "markers": "e2e",
                "timeout": 900,
                "description": "Testes end-to-end"
            },
            "performance": {
                "path": "tests/performance/",
                "markers": "performance",
                "timeout": 1800,
                "description": "Testes de performance"
            },
            "all": {
                "path": "tests/",
                "markers": "",
                "timeout": 2400,
                "description": "Todos os testes"
            }
        }
    
    def setup_environment(self):
        """Configura ambiente para testes"""
        print("🔧 Configurando ambiente de testes...")
        
        # Verificar se está no diretório correto
        if not (self.project_root / "src").exists():
            raise FileNotFoundError(f"Diretório src não encontrado em {self.project_root}")
        
        # Configurar variáveis de ambiente para testes
        test_env = {
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "DEBUG",
            "REDIS_URL": "redis://localhost:6379/1",
            "WHATSAPP_WEBHOOK_SECRET": "test_webhook_secret_123",
            "WHATSAPP_VERIFY_TOKEN": "test_verify_token_456",
            "ABACUS_API_KEY": "test_abacus_key",
            "ABACUS_DEPLOYMENT_ID": "test_deployment_123"
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        print("✅ Ambiente configurado")
    
    def check_dependencies(self):
        """Verifica dependências necessárias"""
        print("📦 Verificando dependências...")
        
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "pytest-html",
            "pytest-cov",
            "locust",
            "httpx",
            "redis"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
            print("Instalando dependências...")
            
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)
            
            print("✅ Dependências instaladas")
        else:
            print("✅ Todas as dependências estão disponíveis")
    
    def start_services(self):
        """Inicia serviços necessários para testes"""
        print("🚀 Iniciando serviços...")
        
        # Verificar se Redis está rodando
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=1)
            r.ping()
            print("✅ Redis está rodando")
        except Exception:
            print("⚠️  Redis não está rodando. Tentando iniciar...")
            try:
                subprocess.run(["redis-server", "--daemonize", "yes"], check=True)
                time.sleep(2)
                print("✅ Redis iniciado")
            except Exception as e:
                print(f"❌ Erro ao iniciar Redis: {e}")
                print("Por favor, inicie o Redis manualmente")
    
    def run_pytest(self, test_type: str, verbose: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Executa pytest com configurações específicas"""
        config = self.test_configs[test_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Preparar comando pytest
        cmd = [
            sys.executable, "-m", "pytest",
            config["path"],
            "-v" if verbose else "-q",
            f"--timeout={config['timeout']}",
            "--tb=short"
        ]
        
        # Adicionar marcadores se especificados
        if config["markers"]:
            cmd.extend(["-m", config["markers"]])
        
        # Adicionar cobertura se solicitado
        if coverage and test_type != "performance":
            coverage_file = self.reports_dir / f"coverage_{test_type}_{timestamp}.xml"
            cmd.extend([
                "--cov=src",
                "--cov-report=xml:" + str(coverage_file),
                "--cov-report=term-missing"
            ])
        
        # Adicionar relatório HTML
        html_report = self.reports_dir / f"report_{test_type}_{timestamp}.html"
        cmd.extend([
            "--html=" + str(html_report),
            "--self-contained-html"
        ])
        
        # Adicionar relatório JUnit XML
        junit_report = self.reports_dir / f"junit_{test_type}_{timestamp}.xml"
        cmd.extend(["--junitxml=" + str(junit_report)])
        
        print(f"🧪 Executando {config['description']}...")
        print(f"Comando: {' '.join(cmd)}")
        
        # Executar testes
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=config["timeout"]
            )
            
            duration = time.time() - start_time
            
            # Processar resultado
            test_result = {
                "test_type": test_type,
                "success": result.returncode == 0,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "reports": {
                    "html": str(html_report),
                    "junit": str(junit_report)
                },
                "timestamp": timestamp
            }
            
            if coverage and test_type != "performance":
                test_result["reports"]["coverage"] = str(coverage_file)
            
            # Extrair estatísticas do output
            test_result["stats"] = self._extract_test_stats(result.stdout)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                "test_type": test_type,
                "success": False,
                "duration": duration,
                "return_code": -1,
                "error": "Timeout",
                "timestamp": timestamp
            }
        
        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_type": test_type,
                "success": False,
                "duration": duration,
                "return_code": -1,
                "error": str(e),
                "timestamp": timestamp
            }
    
    def run_locust_tests(self, duration: str = "60s", users: int = 50, spawn_rate: int = 5) -> Dict[str, Any]:
        """Executa testes de carga com Locust"""
        print("🔥 Executando testes de carga com Locust...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_prefix = self.reports_dir / f"locust_{timestamp}"
        
        cmd = [
            sys.executable, "-m", "locust",
            "-f", "tests/performance/locustfile.py",
            "--headless",
            "--host", "http://localhost:8000",
            "-u", str(users),
            "-r", str(spawn_rate),
            "-t", duration,
            "--csv", str(csv_prefix)
        ]
        
        print(f"Comando Locust: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos max
            )
            
            duration_actual = time.time() - start_time
            
            # Processar resultado
            locust_result = {
                "test_type": "locust",
                "success": result.returncode == 0,
                "duration": duration_actual,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "reports": {
                    "csv_stats": f"{csv_prefix}_stats.csv",
                    "csv_failures": f"{csv_prefix}_failures.csv",
                    "csv_stats_history": f"{csv_prefix}_stats_history.csv"
                },
                "timestamp": timestamp,
                "config": {
                    "users": users,
                    "spawn_rate": spawn_rate,
                    "duration": duration
                }
            }
            
            # Extrair estatísticas do Locust
            locust_result["stats"] = self._extract_locust_stats(result.stdout)
            
            return locust_result
            
        except Exception as e:
            return {
                "test_type": "locust",
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "timestamp": timestamp
            }
    
    def _extract_test_stats(self, output: str) -> Dict[str, Any]:
        """Extrai estatísticas do output do pytest"""
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            if "passed" in line and "failed" in line:
                # Linha de resumo: "5 passed, 2 failed, 1 skipped"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        count = int(part)
                        if i + 1 < len(parts):
                            status = parts[i + 1].rstrip(',')
                            if status in stats:
                                stats[status] = count
                                stats["total"] += count
                break
        
        return stats
    
    def _extract_locust_stats(self, output: str) -> Dict[str, Any]:
        """Extrai estatísticas do output do Locust"""
        stats = {
            "total_requests": 0,
            "total_failures": 0,
            "average_response_time": 0,
            "requests_per_second": 0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            if "Total requests" in line:
                try:
                    stats["total_requests"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif "Total failures" in line:
                try:
                    stats["total_failures"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif "Average response time" in line:
                try:
                    stats["average_response_time"] = float(line.split(':')[1].strip().replace('ms', ''))
                except:
                    pass
            elif "Requests per second" in line:
                try:
                    stats["requests_per_second"] = float(line.split(':')[1].strip())
                except:
                    pass
        
        return stats
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """Gera relatório resumo de todos os testes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"summary_report_{timestamp}.json"
        
        summary = {
            "timestamp": timestamp,
            "total_duration": sum(r.get("duration", 0) for r in results),
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "failed_tests": len([r for r in results if not r.get("success", False)]),
            "results": results
        }
        
        # Salvar relatório JSON
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Gerar relatório HTML
        html_file = self.reports_dir / f"summary_report_{timestamp}.html"
        self._generate_html_summary(summary, html_file)
        
        print(f"\n📊 Relatório resumo gerado:")
        print(f"   JSON: {report_file}")
        print(f"   HTML: {html_file}")
        
        return summary
    
    def _generate_html_summary(self, summary: Dict[str, Any], output_file: Path):
        """Gera relatório HTML resumo"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>BestStag v9.1 - Relatório de Testes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
                .success {{ background: #2ecc71; color: white; }}
                .failure {{ background: #e74c3c; color: white; }}
                .test-result {{ margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .test-success {{ background: #d5f4e6; border-left: 4px solid #2ecc71; }}
                .test-failure {{ background: #fdf2f2; border-left: 4px solid #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #34495e; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BestStag v9.1 - Relatório de Testes</h1>
                <p>Gerado em: {summary['timestamp']}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total de Testes</h3>
                    <h2>{summary['total_tests']}</h2>
                </div>
                <div class="metric success">
                    <h3>Sucessos</h3>
                    <h2>{summary['successful_tests']}</h2>
                </div>
                <div class="metric failure">
                    <h3>Falhas</h3>
                    <h2>{summary['failed_tests']}</h2>
                </div>
                <div class="metric">
                    <h3>Duração Total</h3>
                    <h2>{summary['total_duration']:.1f}s</h2>
                </div>
            </div>
            
            <h2>Resultados Detalhados</h2>
            <table>
                <tr>
                    <th>Tipo de Teste</th>
                    <th>Status</th>
                    <th>Duração</th>
                    <th>Estatísticas</th>
                </tr>
        """
        
        for result in summary['results']:
            status_class = "test-success" if result.get('success', False) else "test-failure"
            status_text = "✅ Sucesso" if result.get('success', False) else "❌ Falha"
            
            stats_text = ""
            if 'stats' in result:
                stats = result['stats']
                if 'total' in stats:
                    stats_text = f"Total: {stats['total']}, Passou: {stats.get('passed', 0)}, Falhou: {stats.get('failed', 0)}"
                elif 'total_requests' in stats:
                    stats_text = f"Requisições: {stats['total_requests']}, RPS: {stats.get('requests_per_second', 0):.1f}"
            
            html_content += f"""
                <tr class="{status_class}">
                    <td>{result.get('test_type', 'Unknown')}</td>
                    <td>{status_text}</td>
                    <td>{result.get('duration', 0):.1f}s</td>
                    <td>{stats_text}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    def run_all_tests(self, include_performance: bool = True, include_locust: bool = True):
        """Executa toda a suite de testes"""
        print("🚀 Iniciando execução completa de testes BestStag v9.1")
        print("=" * 60)
        
        # Setup
        self.setup_environment()
        self.check_dependencies()
        self.start_services()
        
        results = []
        
        # Testes unitários
        print("\n" + "=" * 60)
        result = self.run_pytest("unit", verbose=True, coverage=True)
        results.append(result)
        self._print_result_summary(result)
        
        # Testes de integração
        print("\n" + "=" * 60)
        result = self.run_pytest("integration", verbose=True, coverage=True)
        results.append(result)
        self._print_result_summary(result)
        
        # Testes E2E
        print("\n" + "=" * 60)
        result = self.run_pytest("e2e", verbose=True, coverage=True)
        results.append(result)
        self._print_result_summary(result)
        
        # Testes de performance
        if include_performance:
            print("\n" + "=" * 60)
            result = self.run_pytest("performance", verbose=True, coverage=False)
            results.append(result)
            self._print_result_summary(result)
        
        # Testes de carga com Locust
        if include_locust:
            print("\n" + "=" * 60)
            result = self.run_locust_tests(duration="60s", users=20, spawn_rate=5)
            results.append(result)
            self._print_result_summary(result)
        
        # Gerar relatório final
        print("\n" + "=" * 60)
        summary = self.generate_summary_report(results)
        
        # Resumo final
        print(f"\n🎯 RESUMO FINAL:")
        print(f"   Total de testes: {summary['total_tests']}")
        print(f"   Sucessos: {summary['successful_tests']}")
        print(f"   Falhas: {summary['failed_tests']}")
        print(f"   Duração total: {summary['total_duration']:.1f}s")
        
        if summary['failed_tests'] == 0:
            print("🎉 Todos os testes passaram!")
            return True
        else:
            print("⚠️  Alguns testes falharam. Verifique os relatórios.")
            return False
    
    def _print_result_summary(self, result: Dict[str, Any]):
        """Imprime resumo de um resultado de teste"""
        test_type = result.get('test_type', 'Unknown')
        success = result.get('success', False)
        duration = result.get('duration', 0)
        
        status = "✅ SUCESSO" if success else "❌ FALHA"
        print(f"\n{status} - {test_type.upper()}")
        print(f"Duração: {duration:.1f}s")
        
        if 'stats' in result:
            stats = result['stats']
            if 'total' in stats:
                print(f"Testes: {stats['total']} total, {stats.get('passed', 0)} passou, {stats.get('failed', 0)} falhou")
            elif 'total_requests' in stats:
                print(f"Requisições: {stats['total_requests']}, RPS: {stats.get('requests_per_second', 0):.1f}")
        
        if not success and 'error' in result:
            print(f"Erro: {result['error']}")


def main():
    """Função principal do test runner"""
    parser = argparse.ArgumentParser(description="BestStag v9.1 Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance", "locust", "all"], 
                       default="all", help="Tipo de teste para executar")
    parser.add_argument("--no-performance", action="store_true", help="Pular testes de performance")
    parser.add_argument("--no-locust", action="store_true", help="Pular testes de carga")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto")
    
    args = parser.parse_args()
    
    # Determinar diretório do projeto
    if args.project_root == ".":
        # Tentar encontrar automaticamente
        current_dir = Path.cwd()
        if (current_dir / "src").exists():
            project_root = current_dir
        elif (current_dir.parent / "src").exists():
            project_root = current_dir.parent
        else:
            project_root = current_dir
    else:
        project_root = Path(args.project_root)
    
    runner = TestRunner(str(project_root))
    
    try:
        if args.type == "all":
            success = runner.run_all_tests(
                include_performance=not args.no_performance,
                include_locust=not args.no_locust
            )
            sys.exit(0 if success else 1)
        
        elif args.type == "locust":
            result = runner.run_locust_tests()
            runner._print_result_summary(result)
            sys.exit(0 if result['success'] else 1)
        
        else:
            result = runner.run_pytest(args.type)
            runner._print_result_summary(result)
            sys.exit(0 if result['success'] else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Execução interrompida pelo usuário")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
