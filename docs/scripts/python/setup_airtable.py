#!/usr/bin/env python3
"""
BestStag v9.0 - Setup do Airtable
Script para configuração automática da base de dados Airtable

Autor: Manus AI
Versão: 9.0
Data: 2025-06-03
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AirtableSetup:
    def __init__(self):
        """Inicializa o setup do Airtable com configurações do ambiente"""
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        
        if not self.api_key or not self.base_id:
            raise ValueError("AIRTABLE_API_KEY e AIRTABLE_BASE_ID devem estar definidos no .env")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Carregar schema do arquivo de configuração
        with open('configs/airtable_schema.json', 'r', encoding='utf-8') as f:
            self.schema = json.load(f)['airtable_schema']
    
    def verificar_conexao(self) -> bool:
        """Verifica se a conexão com o Airtable está funcionando"""
        try:
            response = requests.get(f"{self.base_url}/Usuarios", headers=self.headers)
            if response.status_code == 200:
                print("✅ Conexão com Airtable estabelecida com sucesso!")
                return True
            else:
                print(f"❌ Erro na conexão: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {str(e)}")
            return False
    
    def criar_usuario_exemplo(self) -> Dict[str, Any]:
        """Cria um usuário de exemplo para testes"""
        usuario_exemplo = {
            "fields": {
                "nome": "Usuário Teste BestStag",
                "email": "teste@beststag.com",
                "telefone": "+5511999999999",
                "status": "trial",
                "plano": "free",
                "configuracoes": json.dumps({
                    "notificacoes": True,
                    "fuso_horario": "America/Sao_Paulo",
                    "idioma": "pt-BR"
                }),
                "fuso_horario": "America/Sao_Paulo",
                "idioma": "pt-BR"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/Usuarios",
                headers=self.headers,
                json=usuario_exemplo
            )
            
            if response.status_code == 200:
                usuario = response.json()
                print(f"✅ Usuário exemplo criado: {usuario['id']}")
                return usuario
            else:
                print(f"❌ Erro ao criar usuário: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {str(e)}")
            return None
    
    def criar_dados_exemplo(self, usuario_id: str) -> bool:
        """Cria dados de exemplo para demonstração"""
        try:
            # Criar tarefas de exemplo
            tarefas_exemplo = [
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "titulo": "Configurar BestStag v9.0",
                        "descricao": "Finalizar configuração do sistema",
                        "status": "em_andamento",
                        "prioridade": "alta",
                        "categoria": "trabalho",
                        "estimativa_horas": 2,
                        "progresso": 75
                    }
                },
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "titulo": "Testar comandos WhatsApp",
                        "descricao": "Validar todos os comandos básicos",
                        "status": "pendente",
                        "prioridade": "media",
                        "categoria": "trabalho",
                        "estimativa_horas": 1
                    }
                },
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "titulo": "Revisar documentação",
                        "descricao": "Ler toda a documentação do projeto",
                        "status": "pendente",
                        "prioridade": "baixa",
                        "categoria": "estudo",
                        "estimativa_horas": 3
                    }
                }
            ]
            
            for tarefa in tarefas_exemplo:
                response = requests.post(
                    f"{self.base_url}/Tarefas",
                    headers=self.headers,
                    json=tarefa
                )
                if response.status_code == 200:
                    print(f"✅ Tarefa criada: {tarefa['fields']['titulo']}")
                else:
                    print(f"❌ Erro ao criar tarefa: {response.text}")
            
            # Criar eventos de exemplo
            agora = datetime.now()
            eventos_exemplo = [
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "titulo": "Reunião de planejamento",
                        "descricao": "Planejar próximas funcionalidades",
                        "data_inicio": (agora + timedelta(hours=2)).isoformat(),
                        "data_fim": (agora + timedelta(hours=3)).isoformat(),
                        "tipo": "reuniao",
                        "status": "agendado",
                        "local": "Sala de reuniões virtual",
                        "lembrete_minutos": 15
                    }
                },
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "titulo": "Demo BestStag",
                        "descricao": "Demonstração das funcionalidades",
                        "data_inicio": (agora + timedelta(days=1, hours=10)).isoformat(),
                        "data_fim": (agora + timedelta(days=1, hours=11)).isoformat(),
                        "tipo": "compromisso",
                        "status": "agendado",
                        "lembrete_minutos": 30
                    }
                }
            ]
            
            for evento in eventos_exemplo:
                response = requests.post(
                    f"{self.base_url}/Eventos",
                    headers=self.headers,
                    json=evento
                )
                if response.status_code == 200:
                    print(f"✅ Evento criado: {evento['fields']['titulo']}")
                else:
                    print(f"❌ Erro ao criar evento: {response.text}")
            
            # Criar interações de exemplo
            interacoes_exemplo = [
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "tipo": "whatsapp",
                        "canal": "whatsapp_command",
                        "comando": "/ajuda",
                        "mensagem_usuario": "/ajuda",
                        "resposta_sistema": "Sistema de ajuda do BestStag v9.0",
                        "status": "sucesso",
                        "modelo_ia_usado": "sistema",
                        "memoria_camada": "MCP",
                        "relevancia_score": 60
                    }
                },
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "tipo": "whatsapp",
                        "canal": "whatsapp_command",
                        "comando": "/status",
                        "mensagem_usuario": "/status",
                        "resposta_sistema": "Status geral do usuário",
                        "status": "sucesso",
                        "modelo_ia_usado": "sistema",
                        "memoria_camada": "MCP",
                        "relevancia_score": 70
                    }
                }
            ]
            
            for interacao in interacoes_exemplo:
                response = requests.post(
                    f"{self.base_url}/Interacoes",
                    headers=self.headers,
                    json=interacao
                )
                if response.status_code == 200:
                    print(f"✅ Interação criada: {interacao['fields']['comando']}")
                else:
                    print(f"❌ Erro ao criar interação: {response.text}")
            
            # Criar configurações de exemplo
            configuracoes_exemplo = [
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "tipo": "preferencia",
                        "nome": "Notificações WhatsApp",
                        "descricao": "Configuração de notificações via WhatsApp",
                        "ativa": True,
                        "configuracao_json": json.dumps({
                            "horario_inicio": "08:00",
                            "horario_fim": "18:00",
                            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"]
                        }),
                        "frequencia": "tempo_real"
                    }
                },
                {
                    "fields": {
                        "usuario": [usuario_id],
                        "tipo": "automacao",
                        "nome": "Lembrete de tarefas",
                        "descricao": "Lembrete automático de tarefas vencendo",
                        "ativa": True,
                        "configuracao_json": json.dumps({
                            "antecedencia_horas": 24,
                            "repetir": True,
                            "canais": ["whatsapp"]
                        }),
                        "frequencia": "diaria"
                    }
                }
            ]
            
            for config in configuracoes_exemplo:
                response = requests.post(
                    f"{self.base_url}/Configuracoes",
                    headers=self.headers,
                    json=config
                )
                if response.status_code == 200:
                    print(f"✅ Configuração criada: {config['fields']['nome']}")
                else:
                    print(f"❌ Erro ao criar configuração: {response.text}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar dados de exemplo: {str(e)}")
            return False
    
    def validar_estrutura(self) -> bool:
        """Valida se todas as tabelas necessárias existem"""
        tabelas_necessarias = ['Usuarios', 'Emails', 'Eventos', 'Tarefas', 'Interacoes', 'Configuracoes']
        
        for tabela in tabelas_necessarias:
            try:
                response = requests.get(f"{self.base_url}/{tabela}?maxRecords=1", headers=self.headers)
                if response.status_code == 200:
                    print(f"✅ Tabela {tabela} encontrada")
                else:
                    print(f"❌ Tabela {tabela} não encontrada ou inacessível")
                    return False
            except Exception as e:
                print(f"❌ Erro ao verificar tabela {tabela}: {str(e)}")
                return False
        
        return True
    
    def gerar_relatorio_setup(self) -> Dict[str, Any]:
        """Gera relatório do setup realizado"""
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "versao": "9.0",
            "status": "completo",
            "tabelas": {},
            "estatisticas": {}
        }
        
        tabelas = ['Usuarios', 'Emails', 'Eventos', 'Tarefas', 'Interacoes', 'Configuracoes']
        
        for tabela in tabelas:
            try:
                response = requests.get(f"{self.base_url}/{tabela}", headers=self.headers)
                if response.status_code == 200:
                    dados = response.json()
                    total_registros = len(dados.get('records', []))
                    relatorio['tabelas'][tabela] = {
                        "status": "ok",
                        "total_registros": total_registros
                    }
                    relatorio['estatisticas'][f"total_{tabela.lower()}"] = total_registros
                else:
                    relatorio['tabelas'][tabela] = {
                        "status": "erro",
                        "erro": response.text
                    }
            except Exception as e:
                relatorio['tabelas'][tabela] = {
                    "status": "erro",
                    "erro": str(e)
                }
        
        return relatorio
    
    def executar_setup_completo(self) -> bool:
        """Executa o setup completo do Airtable"""
        print("🚀 Iniciando setup do BestStag v9.0 no Airtable...")
        print("=" * 50)
        
        # 1. Verificar conexão
        if not self.verificar_conexao():
            return False
        
        # 2. Validar estrutura
        print("\n📋 Validando estrutura das tabelas...")
        if not self.validar_estrutura():
            print("❌ Estrutura inválida. Verifique se as tabelas foram criadas corretamente.")
            return False
        
        # 3. Criar usuário exemplo
        print("\n👤 Criando usuário de exemplo...")
        usuario = self.criar_usuario_exemplo()
        if not usuario:
            print("❌ Falha ao criar usuário exemplo")
            return False
        
        # 4. Criar dados exemplo
        print("\n📊 Criando dados de exemplo...")
        if not self.criar_dados_exemplo(usuario['id']):
            print("❌ Falha ao criar dados de exemplo")
            return False
        
        # 5. Gerar relatório
        print("\n📈 Gerando relatório do setup...")
        relatorio = self.gerar_relatorio_setup()
        
        # Salvar relatório
        with open('setup_airtable_relatorio.json', 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Setup do Airtable concluído com sucesso!")
        print("=" * 50)
        print(f"📊 Relatório salvo em: setup_airtable_relatorio.json")
        print(f"👤 ID do usuário exemplo: {usuario['id']}")
        print(f"📱 Telefone para testes: +5511999999999")
        print("\n🎯 Próximos passos:")
        print("1. Configure o webhook do n8n")
        print("2. Teste os comandos WhatsApp")
        print("3. Acesse o portal web")
        
        return True

def main():
    """Função principal"""
    try:
        setup = AirtableSetup()
        sucesso = setup.executar_setup_completo()
        
        if sucesso:
            print("\n🎉 BestStag v9.0 está pronto para uso!")
            exit(0)
        else:
            print("\n💥 Setup falhou. Verifique os logs acima.")
            exit(1)
            
    except Exception as e:
        print(f"\n💥 Erro crítico no setup: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()

