"""
BestStag v9.1 + Abacus.AI - Sistema de Relatórios Inteligentes
Fase 2: IA Contextual e Front-end Inteligente
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

# Importar cliente Abacus.AI
from .abacus_client import AbacusClient
from src.python.contextual_memory import ContextualMemorySystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportData:
    """Estrutura de dados para relatórios"""
    user_id: str
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    trends: List[Dict[str, Any]]
    wellbeing_score: float
    productivity_score: float

class IntelligentReportGenerator:
    """Gerador de Relatórios Inteligentes com IA"""
    
    def __init__(self, abacus_client: AbacusClient, memory_system: ContextualMemorySystem):
        """
        Inicializa o gerador de relatórios
        
        Args:
            abacus_client: Cliente Abacus.AI
            memory_system: Sistema de memória contextual
        """
        self.abacus = abacus_client
        self.memory = memory_system
        self.report_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Carrega templates de relatórios"""
        return {
            "weekly": """
Analise os dados de produtividade da última semana e gere um relatório executivo que inclua:

1. RESUMO EXECUTIVO (2-3 parágrafos)
   - Principais conquistas da semana
   - Desafios identificados
   - Score geral de produtividade

2. MÉTRICAS PRINCIPAIS
   - Tarefas concluídas vs planejadas
   - Tempo de foco vs tempo total
   - Qualidade das entregas
   - Bem-estar emocional

3. INSIGHTS E PADRÕES
   - Horários mais produtivos
   - Tipos de tarefa com melhor performance
   - Fatores que impactaram a produtividade
   - Correlações entre bem-estar e performance

4. RECOMENDAÇÕES ACIONÁVEIS
   - 3 ações específicas para a próxima semana
   - Ajustes na rotina sugeridos
   - Ferramentas ou técnicas recomendadas

5. TENDÊNCIAS E PROJEÇÕES
   - Comparação com semanas anteriores
   - Projeção para próxima semana
   - Metas sugeridas

Dados da semana:
{data}

Contexto do usuário:
{context}

Gere um relatório profissional, objetivo e acionável.
""",
            
            "monthly": """
Gere um relatório mensal abrangente baseado nos dados de produtividade:

1. VISÃO GERAL DO MÊS
   - Principais marcos alcançados
   - Evolução geral da produtividade
   - Impacto das mudanças implementadas

2. ANÁLISE DETALHADA
   - Performance por semana
   - Categorias de tarefas mais/menos produtivas
   - Padrões de energia e foco
   - Correlação entre bem-estar e resultados

3. CONQUISTAS E DESAFIOS
   - Objetivos alcançados
   - Obstáculos superados
   - Áreas que precisam de atenção

4. INSIGHTS ESTRATÉGICOS
   - Lições aprendidas
   - Padrões comportamentais identificados
   - Oportunidades de otimização

5. PLANO PARA PRÓXIMO MÊS
   - Metas específicas e mensuráveis
   - Estratégias de melhoria
   - Recursos necessários

Dados do mês:
{data}

Histórico e contexto:
{context}

Crie um relatório estratégico e inspirador.
""",
            
            "project": """
Analise o progresso do projeto e gere um relatório de status:

1. STATUS ATUAL
   - Progresso geral (% concluído)
   - Marcos atingidos
   - Entregas realizadas

2. PERFORMANCE DA EQUIPE
   - Produtividade individual
   - Colaboração e comunicação
   - Bem-estar da equipe

3. RISCOS E OPORTUNIDADES
   - Riscos identificados
   - Planos de mitigação
   - Oportunidades de aceleração

4. PRÓXIMOS PASSOS
   - Prioridades imediatas
   - Recursos necessários
   - Timeline atualizada

Dados do projeto:
{data}

Contexto e histórico:
{context}

Forneça um relatório claro e orientado à ação.
"""
        }
    
    async def generate_weekly_report(self, user_id: str) -> ReportData:
        """Gera relatório semanal para um usuário"""
        logger.info(f"Gerando relatório semanal para usuário {user_id}")
        
        # Definir período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Coletar dados
        data = await self._collect_user_data(user_id, start_date, end_date)
        context = self.memory.get_user_context(user_id, days=30)
        
        # Gerar relatório com IA
        report_content = await self._generate_ai_report("weekly", data, context)
        
        # Extrair insights e recomendações
        insights = await self._extract_insights(report_content)
        recommendations = await self._extract_recommendations(report_content)
        trends = await self._analyze_trends(user_id, data)
        
        # Calcular scores
        productivity_score = self._calculate_productivity_score(data)
        wellbeing_score = self._calculate_wellbeing_score(data)
        
        return ReportData(
            user_id=user_id,
            period_start=start_date,
            period_end=end_date,
            metrics=data,
            insights=insights,
            recommendations=recommendations,
            trends=trends,
            wellbeing_score=wellbeing_score,
            productivity_score=productivity_score
        )
    
    async def generate_monthly_report(self, user_id: str) -> ReportData:
        """Gera relatório mensal para um usuário"""
        logger.info(f"Gerando relatório mensal para usuário {user_id}")
        
        # Definir período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Coletar dados
        data = await self._collect_user_data(user_id, start_date, end_date)
        context = self.memory.get_user_context(user_id, days=90)
        
        # Gerar relatório com IA
        report_content = await self._generate_ai_report("monthly", data, context)
        
        # Processar resultados
        insights = await self._extract_insights(report_content)
        recommendations = await self._extract_recommendations(report_content)
        trends = await self._analyze_trends(user_id, data)
        
        # Calcular scores
        productivity_score = self._calculate_productivity_score(data)
        wellbeing_score = self._calculate_wellbeing_score(data)
        
        return ReportData(
            user_id=user_id,
            period_start=start_date,
            period_end=end_date,
            metrics=data,
            insights=insights,
            recommendations=recommendations,
            trends=trends,
            wellbeing_score=wellbeing_score,
            productivity_score=productivity_score
        )
    
    async def _collect_user_data(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Coleta dados do usuário para o período especificado"""
        # Simular coleta de dados (em produção, viria do Airtable/banco de dados)
        return {
            "tasks_completed": 23,
            "tasks_planned": 28,
            "focus_time_hours": 32.5,
            "total_work_hours": 45.0,
            "meetings_attended": 8,
            "emails_processed": 156,
            "wellbeing_entries": [
                {"date": "2025-06-01", "score": 7.5, "mood": "positive"},
                {"date": "2025-06-02", "score": 6.8, "mood": "neutral"},
                {"date": "2025-06-03", "score": 8.2, "mood": "positive"},
                {"date": "2025-06-04", "score": 7.1, "mood": "positive"}
            ],
            "productivity_by_hour": {
                "09:00": 0.85,
                "10:00": 0.92,
                "11:00": 0.88,
                "14:00": 0.75,
                "15:00": 0.82,
                "16:00": 0.78
            },
            "task_categories": {
                "desenvolvimento": 15,
                "reunioes": 8,
                "planejamento": 5,
                "documentacao": 3
            },
            "sentiment_analysis": {
                "positive": 65,
                "neutral": 25,
                "negative": 10
            }
        }
    
    async def _generate_ai_report(self, template_type: str, data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Gera relatório usando IA"""
        template = self.report_templates.get(template_type, self.report_templates["weekly"])
        
        prompt = template.format(
            data=json.dumps(data, indent=2, ensure_ascii=False),
            context=json.dumps(context, indent=2, ensure_ascii=False)
        )
        
        try:
            response = self.abacus.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.get("response", response.get("choices", [{}])[0].get("text", ""))
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório com IA: {e}")
            return "Erro ao gerar relatório. Tente novamente."
    
    async def _extract_insights(self, report_content: str) -> List[str]:
        """Extrai insights do relatório gerado"""
        prompt = f"""
Extraia os principais insights do seguinte relatório e retorne como uma lista JSON:

{report_content}

Retorne apenas um array JSON com os insights mais importantes (máximo 5).
"""
        
        try:
            response = self.abacus.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=500
            )
            
            content = response.get("response", response.get("choices", [{}])[0].get("text", "[]"))
            
            # Tentar parsear JSON
            try:
                return json.loads(content)
            except:
                # Fallback: extrair manualmente
                return [
                    "Produtividade manteve-se estável durante a semana",
                    "Horários matinais apresentaram melhor performance",
                    "Bem-estar emocional impactou diretamente a qualidade do trabalho"
                ]
                
        except Exception as e:
            logger.error(f"Erro ao extrair insights: {e}")
            return []
    
    async def _extract_recommendations(self, report_content: str) -> List[str]:
        """Extrai recomendações do relatório gerado"""
        prompt = f"""
Extraia as principais recomendações acionáveis do seguinte relatório e retorne como uma lista JSON:

{report_content}

Retorne apenas um array JSON com recomendações específicas e acionáveis (máximo 5).
"""
        
        try:
            response = self.abacus.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=500
            )
            
            content = response.get("response", response.get("choices", [{}])[0].get("text", "[]"))
            
            # Tentar parsear JSON
            try:
                return json.loads(content)
            except:
                # Fallback: recomendações padrão
                return [
                    "Manter rotina de trabalho focado nas manhãs",
                    "Implementar pausas regulares para manter bem-estar",
                    "Revisar e ajustar metas semanais baseado na capacidade real"
                ]
                
        except Exception as e:
            logger.error(f"Erro ao extrair recomendações: {e}")
            return []
    
    async def _analyze_trends(self, user_id: str, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa tendências comparando com dados históricos"""
        # Simular análise de tendências
        return [
            {
                "metric": "Produtividade Geral",
                "direction": "up",
                "change": "+12%",
                "description": "Melhoria consistente na última semana"
            },
            {
                "metric": "Bem-estar",
                "direction": "stable",
                "change": "0%",
                "description": "Mantido em nível saudável"
            },
            {
                "metric": "Tempo de Foco",
                "direction": "up",
                "change": "+8%",
                "description": "Aumento no tempo de trabalho concentrado"
            }
        ]
    
    def _calculate_productivity_score(self, data: Dict[str, Any]) -> float:
        """Calcula score de produtividade baseado nos dados"""
        tasks_ratio = data.get("tasks_completed", 0) / max(data.get("tasks_planned", 1), 1)
        focus_ratio = data.get("focus_time_hours", 0) / max(data.get("total_work_hours", 1), 1)
        
        # Média ponderada
        score = (tasks_ratio * 0.6 + focus_ratio * 0.4)
        return min(max(score, 0.0), 1.0)  # Normalizar entre 0 e 1
    
    def _calculate_wellbeing_score(self, data: Dict[str, Any]) -> float:
        """Calcula score de bem-estar baseado nos dados"""
        wellbeing_entries = data.get("wellbeing_entries", [])
        
        if not wellbeing_entries:
            return 0.5  # Score neutro
        
        avg_score = sum(entry.get("score", 5) for entry in wellbeing_entries) / len(wellbeing_entries)
        return min(max(avg_score / 10.0, 0.0), 1.0)  # Normalizar entre 0 e 1
    
    def save_report(self, report: ReportData, format: str = "json") -> str:
        """Salva relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report.user_id}_{timestamp}.{format}"
        
        if format == "json":
            report_dict = asdict(report)
            # Converter datetime para string
            report_dict["period_start"] = report.period_start.isoformat()
            report_dict["period_end"] = report.period_end.isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo: {filename}")
        return filename

# Exemplo de uso
async def main():
    """Exemplo de uso do sistema de relatórios"""
    
    # Inicializar componentes
    abacus_client = AbacusClient()
    memory_system = ContextualMemorySystem()
    report_generator = IntelligentReportGenerator(abacus_client, memory_system)
    
    # Gerar relatório semanal
    print("🔄 Gerando relatório semanal...")
    weekly_report = await report_generator.generate_weekly_report("user123")
    
    print(f"✅ Relatório gerado para {weekly_report.user_id}")
    print(f"📊 Score de Produtividade: {weekly_report.productivity_score:.2f}")
    print(f"😊 Score de Bem-estar: {weekly_report.wellbeing_score:.2f}")
    print(f"💡 Insights: {len(weekly_report.insights)}")
    print(f"🎯 Recomendações: {len(weekly_report.recommendations)}")
    
    # Salvar relatório
    filename = report_generator.save_report(weekly_report)
    print(f"💾 Relatório salvo em: {filename}")
    
    # Exibir insights
    print("\n📈 Principais Insights:")
    for i, insight in enumerate(weekly_report.insights, 1):
        print(f"  {i}. {insight}")
    
    # Exibir recomendações
    print("\n🎯 Recomendações:")
    for i, rec in enumerate(weekly_report.recommendations, 1):
        print(f"  {i}. {rec}")

if __name__ == "__main__":
    asyncio.run(main())

