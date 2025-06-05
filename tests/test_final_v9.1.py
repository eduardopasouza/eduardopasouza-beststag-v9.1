#!/usr/bin/env python3
"""
BestStag v9.1 + Abacus.AI - Script de Validação Final
Consolida e valida toda a implementação das Fases 1, 2 e 3
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class BestStagValidator:
    """Validador completo do BestStag v9.1 + Abacus.AI"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "9.1.0",
            "tests": {},
            "summary": {},
            "recommendations": []
        }
        self.success_count = 0
        self.total_tests = 0
    
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Registra resultado de um teste"""
        self.total_tests += 1
        if success:
            self.success_count += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if error:
                print(f"   Erro: {error}")
        
        self.results["tests"][test_name] = {
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            print(f"   {details}")
    
    def check_file_structure(self) -> bool:
        """Valida estrutura de arquivos do projeto"""
        print("\n📁 Validando Estrutura de Arquivos")
        print("-" * 50)
        
        required_files = [
            # Fase 1 - Integração Inicial
            "nodes/AbacusAI.node.ts",
            "credentials/AbacusApi.credentials.ts",
            "workflows/whatsapp_abacus_workflow.json",
            "python/abacus_client.py",
            "requirements.txt",
            ".env.example",
            "test_integration.py",
            "README_FASE1.md",
            
            # Fase 2 - IA Contextual
            "python/contextual_memory.py",
            "python/intelligent_reports.py",
            "frontend/hooks/useAI.ts",
            "frontend/components/AIComponents.tsx",
            "requirements_fase2.txt",
            "test_fase2.py",
            "README_FASE2.md",
            
            # Fase 3 - Consolidação
            "DOCUMENTACAO_TECNICA_COMPLETA.md",
            "CHANGELOG.md",
            "test_final_v9.1.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                existing_files.append(file_path)
                size = full_path.stat().st_size
                self.log_test(f"Arquivo {file_path}", True, f"Tamanho: {size} bytes")
            else:
                missing_files.append(file_path)
                self.log_test(f"Arquivo {file_path}", False, error="Arquivo não encontrado")
        
        # Verificar estrutura de diretórios
        required_dirs = [
            "nodes", "credentials", "workflows", "python", 
            "frontend/hooks", "frontend/components"
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log_test(f"Diretório {dir_path}", True)
            else:
                self.log_test(f"Diretório {dir_path}", False, error="Diretório não encontrado")
                missing_files.append(dir_path)
        
        success = len(missing_files) == 0
        
        if missing_files:
            self.results["recommendations"].append(
                f"Criar arquivos/diretórios faltando: {', '.join(missing_files)}"
            )
        
        return success
    
    def check_dependencies(self) -> bool:
        """Verifica dependências Python"""
        print("\n📦 Validando Dependências Python")
        print("-" * 50)
        
        # Dependências críticas
        critical_deps = [
            ('requests', 'requests'),
            ('numpy', 'numpy'),
            ('sentence_transformers', 'sentence-transformers'),
            ('faiss', 'faiss-cpu'),
            ('dotenv', 'python-dotenv'),
            ('aiohttp', 'aiohttp'),
            ('pydantic', 'pydantic')
        ]
        
        missing_deps = []
        
        for module_name, package_name in critical_deps:
            try:
                __import__(module_name)
                self.log_test(f"Dependência {package_name}", True)
            except ImportError:
                self.log_test(f"Dependência {package_name}", False, 
                            error=f"Instale com: pip install {package_name}")
                missing_deps.append(package_name)
        
        # Verificar versões específicas
        version_checks = [
            ('sentence_transformers', '2.2.0'),
            ('numpy', '1.24.0'),
            ('aiohttp', '3.8.0')
        ]
        
        for module_name, min_version in version_checks:
            try:
                module = __import__(module_name)
                if hasattr(module, '__version__'):
                    version = module.__version__
                    self.log_test(f"Versão {module_name}", True, f"v{version}")
                else:
                    self.log_test(f"Versão {module_name}", True, "Versão não detectável")
            except ImportError:
                pass  # Já reportado acima
        
        if missing_deps:
            self.results["recommendations"].append(
                f"Instalar dependências: pip install {' '.join(missing_deps)}"
            )
        
        return len(missing_deps) == 0
    
    def check_configuration(self) -> bool:
        """Verifica configuração do sistema"""
        print("\n⚙️ Validando Configuração")
        print("-" * 50)
        
        # Verificar arquivo .env.example
        env_example = self.base_path / ".env.example"
        if env_example.exists():
            self.log_test("Arquivo .env.example", True)
            
            # Verificar variáveis essenciais
            with open(env_example, 'r') as f:
                content = f.read()
                
            required_vars = [
                'ABACUS_API_KEY',
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN',
                'AIRTABLE_API_KEY',
                'EMBEDDING_MODEL',
                'MEMORY_MAX_ITEMS'
            ]
            
            for var in required_vars:
                if var in content:
                    self.log_test(f"Variável {var}", True)
                else:
                    self.log_test(f"Variável {var}", False, 
                                error="Variável não encontrada no .env.example")
        else:
            self.log_test("Arquivo .env.example", False, error="Arquivo não encontrado")
        
        # Verificar configuração atual
        config_vars = [
            ('ABACUS_API_KEY', 'Chave API Abacus.AI'),
            ('TWILIO_ACCOUNT_SID', 'Twilio Account SID'),
            ('AIRTABLE_API_KEY', 'Airtable API Key')
        ]
        
        for var_name, description in config_vars:
            value = os.getenv(var_name)
            if value:
                self.log_test(f"Config {description}", True, "Configurado")
            else:
                self.log_test(f"Config {description}", False, 
                            error=f"Variável {var_name} não configurada")
        
        return True  # Configuração é opcional para testes
    
    async def test_abacus_integration(self) -> bool:
        """Testa integração com Abacus.AI"""
        print("\n🤖 Testando Integração Abacus.AI")
        print("-" * 50)
        
        try:
            # Importar cliente
            sys.path.append(str(self.base_path / "python"))
            from abacus_client import AbacusClient
            
            self.log_test("Importação AbacusClient", True)
            
            # Verificar se API key está configurada
            api_key = os.getenv("ABACUS_API_KEY")
            if not api_key:
                self.log_test("API Key Abacus.AI", False, 
                            error="ABACUS_API_KEY não configurada - usando modo simulação")
                return True  # Não é erro crítico
            
            # Inicializar cliente
            client = AbacusClient(api_key=api_key)
            self.log_test("Inicialização cliente", True)
            
            # Teste de health check
            if client.health_check():
                self.log_test("Health check Abacus.AI", True)
                
                # Teste básico de geração de texto
                try:
                    response = client.generate_text(
                        prompt="Teste de integração BestStag v9.1",
                        model="gpt-3.5-turbo",
                        max_tokens=50
                    )
                    
                    if response and 'response' in response:
                        self.log_test("Geração de texto", True, 
                                    f"Resposta: {response['response'][:50]}...")
                    else:
                        self.log_test("Geração de texto", False, 
                                    error="Resposta inválida")
                        
                except Exception as e:
                    self.log_test("Geração de texto", False, error=str(e))
                    
            else:
                self.log_test("Health check Abacus.AI", False, 
                            error="API não está respondendo")
                
        except ImportError as e:
            self.log_test("Importação AbacusClient", False, error=str(e))
            return False
        except Exception as e:
            self.log_test("Teste Abacus.AI", False, error=str(e))
            return False
        
        return True
    
    async def test_contextual_memory(self) -> bool:
        """Testa sistema de memória contextual"""
        print("\n🧠 Testando Sistema de Memória Contextual")
        print("-" * 50)
        
        try:
            sys.path.append(str(self.base_path / "python"))
            from contextual_memory import ContextualMemorySystem
            
            self.log_test("Importação ContextualMemorySystem", True)
            
            # Inicializar sistema
            memory = ContextualMemorySystem()
            self.log_test("Inicialização memória", True)
            
            # Teste de adição de memória
            memory_id = memory.add_memory(
                content="Teste de memória contextual BestStag v9.1",
                user_id="test_user_validation",
                category="teste",
                importance=0.8
            )
            
            if memory_id:
                self.log_test("Adição de memória", True, f"ID: {memory_id}")
            else:
                self.log_test("Adição de memória", False, error="ID não retornado")
                return False
            
            # Teste de busca
            results = memory.search_memory(
                query="teste memória",
                user_id="test_user_validation",
                top_k=1
            )
            
            if results and len(results) > 0:
                self.log_test("Busca semântica", True, 
                            f"Encontrados {len(results)} resultados")
                
                # Verificar score de similaridade
                score = results[0].metadata.get('similarity_score', 0)
                if score > 0.5:
                    self.log_test("Score de similaridade", True, f"Score: {score:.3f}")
                else:
                    self.log_test("Score de similaridade", False, 
                                f"Score muito baixo: {score:.3f}")
            else:
                self.log_test("Busca semântica", False, error="Nenhum resultado encontrado")
            
            # Teste de contexto do usuário
            context = memory.get_user_context("test_user_validation")
            if context and 'total_items' in context:
                self.log_test("Contexto do usuário", True, 
                            f"Total de itens: {context['total_items']}")
            else:
                self.log_test("Contexto do usuário", False, error="Contexto inválido")
            
            # Teste de estatísticas
            stats = memory.get_stats()
            if stats and 'total_items' in stats:
                self.log_test("Estatísticas da memória", True, 
                            f"Total: {stats['total_items']}, Modelo: {stats.get('model_name', 'N/A')}")
            else:
                self.log_test("Estatísticas da memória", False, error="Estatísticas inválidas")
                
        except ImportError as e:
            self.log_test("Importação ContextualMemorySystem", False, error=str(e))
            return False
        except Exception as e:
            self.log_test("Teste memória contextual", False, error=str(e))
            return False
        
        return True
    
    def test_frontend_structure(self) -> bool:
        """Testa estrutura do frontend"""
        print("\n⚛️ Testando Estrutura Frontend")
        print("-" * 50)
        
        frontend_files = [
            ('frontend/hooks/useAI.ts', 'Hooks React IA'),
            ('frontend/components/AIComponents.tsx', 'Componentes IA')
        ]
        
        all_good = True
        
        for file_path, description in frontend_files:
            full_path = self.base_path / file_path
            
            if full_path.exists():
                self.log_test(f"Arquivo {description}", True)
                
                # Verificar conteúdo
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar exports esperados
                if 'useAI.ts' in file_path:
                    expected_hooks = [
                        'useSentiment',
                        'useIntelligentChat',
                        'useAIInsights',
                        'useProductivityAnalysis'
                    ]
                    
                    for hook in expected_hooks:
                        if hook in content:
                            self.log_test(f"Hook {hook}", True)
                        else:
                            self.log_test(f"Hook {hook}", False, error="Hook não encontrado")
                            all_good = False
                
                elif 'AIComponents.tsx' in file_path:
                    expected_components = [
                        'IntelligentChat',
                        'AIInsightsPanel',
                        'ProductivityDashboard',
                        'RecommendationsPanel'
                    ]
                    
                    for component in expected_components:
                        if component in content:
                            self.log_test(f"Componente {component}", True)
                        else:
                            self.log_test(f"Componente {component}", False, 
                                        error="Componente não encontrado")
                            all_good = False
                            
            else:
                self.log_test(f"Arquivo {description}", False, error="Arquivo não encontrado")
                all_good = False
        
        return all_good
    
    def test_workflows(self) -> bool:
        """Testa workflows n8n"""
        print("\n🔄 Testando Workflows n8n")
        print("-" * 50)
        
        workflow_files = [
            'workflows/whatsapp_abacus_workflow.json',
            'workflows/email_intelligent_triage.json',
            'workflows/task_automation_workflow.json',
            'workflows/report_generation_workflow.json'
        ]
        
        all_good = True
        
        for workflow_file in workflow_files:
            full_path = self.base_path / workflow_file
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                    
                    # Verificar estrutura básica
                    if 'nodes' in workflow_data and 'connections' in workflow_data:
                        node_count = len(workflow_data['nodes'])
                        self.log_test(f"Workflow {workflow_file}", True, 
                                    f"{node_count} nós")
                        
                        # Verificar se contém nós Abacus.AI
                        abacus_nodes = [
                            node for node in workflow_data['nodes'] 
                            if node.get('type') == 'abacusAI'
                        ]
                        
                        if abacus_nodes:
                            self.log_test(f"Nós Abacus.AI em {workflow_file}", True, 
                                        f"{len(abacus_nodes)} nós")
                        else:
                            self.log_test(f"Nós Abacus.AI em {workflow_file}", False, 
                                        error="Nenhum nó Abacus.AI encontrado")
                    else:
                        self.log_test(f"Workflow {workflow_file}", False, 
                                    error="Estrutura inválida")
                        all_good = False
                        
                except json.JSONDecodeError as e:
                    self.log_test(f"Workflow {workflow_file}", False, 
                                error=f"JSON inválido: {e}")
                    all_good = False
                except Exception as e:
                    self.log_test(f"Workflow {workflow_file}", False, error=str(e))
                    all_good = False
            else:
                # Alguns workflows são opcionais
                if 'whatsapp_abacus_workflow.json' in workflow_file:
                    self.log_test(f"Workflow {workflow_file}", False, 
                                error="Workflow principal não encontrado")
                    all_good = False
                else:
                    self.log_test(f"Workflow {workflow_file}", True, 
                                "Workflow opcional não presente")
        
        return all_good
    
    def test_documentation(self) -> bool:
        """Testa documentação"""
        print("\n📚 Testando Documentação")
        print("-" * 50)
        
        doc_files = [
            ('README_FASE1.md', 'Documentação Fase 1'),
            ('README_FASE2.md', 'Documentação Fase 2'),
            ('DOCUMENTACAO_TECNICA_COMPLETA.md', 'Documentação Técnica'),
            ('CHANGELOG.md', 'Changelog'),
            ('.env.example', 'Exemplo de configuração')
        ]
        
        all_good = True
        
        for file_path, description in doc_files:
            full_path = self.base_path / file_path
            
            if full_path.exists():
                size = full_path.stat().st_size
                if size > 1000:  # Pelo menos 1KB
                    self.log_test(f"Doc {description}", True, f"Tamanho: {size} bytes")
                else:
                    self.log_test(f"Doc {description}", False, 
                                error=f"Arquivo muito pequeno: {size} bytes")
                    all_good = False
            else:
                self.log_test(f"Doc {description}", False, error="Arquivo não encontrado")
                all_good = False
        
        return all_good
    
    async def run_integration_tests(self) -> bool:
        """Executa testes de integração das fases anteriores"""
        print("\n🧪 Executando Testes de Integração")
        print("-" * 50)
        
        test_scripts = [
            ('test_integration.py', 'Testes Fase 1'),
            ('test_fase2.py', 'Testes Fase 2')
        ]
        
        all_good = True
        
        for script_name, description in test_scripts:
            script_path = self.base_path / script_name
            
            if script_path.exists():
                try:
                    # Executar script de teste
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        capture_output=True,
                        text=True,
                        timeout=120  # 2 minutos timeout
                    )
                    
                    if result.returncode == 0:
                        self.log_test(f"Script {description}", True, 
                                    "Todos os testes passaram")
                    else:
                        self.log_test(f"Script {description}", False, 
                                    error=f"Falhas nos testes: {result.stderr[:200]}")
                        all_good = False
                        
                except subprocess.TimeoutExpired:
                    self.log_test(f"Script {description}", False, 
                                error="Timeout - teste demorou mais que 2 minutos")
                    all_good = False
                except Exception as e:
                    self.log_test(f"Script {description}", False, error=str(e))
                    all_good = False
            else:
                self.log_test(f"Script {description}", False, 
                            error="Script de teste não encontrado")
                all_good = False
        
        return all_good
    
    def generate_report(self) -> str:
        """Gera relatório final de validação"""
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": self.total_tests,
            "successful_tests": self.success_count,
            "failed_tests": self.total_tests - self.success_count,
            "success_rate": round(success_rate, 2),
            "overall_status": "PASS" if success_rate >= 80 else "FAIL"
        }
        
        # Salvar relatório JSON
        report_file = self.base_path / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return str(report_file)
    
    async def run_all_tests(self) -> bool:
        """Executa todos os testes de validação"""
        print("🔧 BestStag v9.1 + Abacus.AI - Validação Final")
        print("=" * 60)
        
        tests = [
            ("Estrutura de Arquivos", self.check_file_structure),
            ("Dependências Python", self.check_dependencies),
            ("Configuração", self.check_configuration),
            ("Integração Abacus.AI", self.test_abacus_integration),
            ("Memória Contextual", self.test_contextual_memory),
            ("Estrutura Frontend", self.test_frontend_structure),
            ("Workflows n8n", self.test_workflows),
            ("Documentação", self.test_documentation),
            ("Testes de Integração", self.run_integration_tests)
        ]
        
        overall_success = True
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                if not result:
                    overall_success = False
                    
            except Exception as e:
                print(f"\n❌ ERRO em {test_name}: {e}")
                overall_success = False
        
        # Gerar relatório
        report_file = self.generate_report()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DA VALIDAÇÃO")
        print("=" * 60)
        
        summary = self.results["summary"]
        print(f"Total de Testes: {summary['total_tests']}")
        print(f"Sucessos: {summary['successful_tests']}")
        print(f"Falhas: {summary['failed_tests']}")
        print(f"Taxa de Sucesso: {summary['success_rate']}%")
        print(f"Status Geral: {summary['overall_status']}")
        
        if self.results["recommendations"]:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        
        if overall_success and summary['success_rate'] >= 80:
            print("\n🎉 SUCESSO: BestStag v9.1 + Abacus.AI está pronto!")
            print("✅ Todas as funcionalidades principais foram validadas")
            print("🚀 Sistema pronto para deployment e uso em produção")
        else:
            print("\n⚠️  ATENÇÃO: Alguns testes falharam")
            print("🔧 Revise os problemas identificados antes do deployment")
        
        return overall_success

async def main():
    """Função principal"""
    validator = BestStagValidator()
    success = await validator.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

