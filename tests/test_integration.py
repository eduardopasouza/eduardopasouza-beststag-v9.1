#!/usr/bin/env python3
"""
Script de teste para validar a integração BestStag v9.1 + Abacus.AI
Fase 1: Integração Inicial
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório python ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from abacus_client import AbacusClient

def test_abacus_integration():
    """Testa a integração com Abacus.AI"""
    print("🚀 Iniciando testes de integração BestStag v9.1 + Abacus.AI")
    print("=" * 60)
    
    # Verificar variáveis de ambiente
    api_key = os.getenv("ABACUS_API_KEY")
    if not api_key:
        print("❌ ERRO: ABACUS_API_KEY não encontrada")
        print("   Configure a variável de ambiente ou arquivo .env")
        return False
    
    print(f"✅ API Key configurada: {api_key[:10]}...")
    
    try:
        # Inicializar cliente
        client = AbacusClient(api_key=api_key)
        print("✅ Cliente Abacus.AI inicializado")
        
        # Teste 1: Health Check
        print("\n📋 Teste 1: Health Check")
        if client.health_check():
            print("✅ API Abacus.AI está funcionando")
        else:
            print("❌ API Abacus.AI não está respondendo")
            return False
        
        # Teste 2: Geração de Texto
        print("\n📋 Teste 2: Geração de Texto")
        response = client.generate_text(
            prompt="Você é o BestStag. Apresente-se em uma frase.",
            model="chatglm"
        )
        print(f"✅ Resposta: {response.get('response', response)}")
        
        # Teste 3: Análise de Sentimento
        print("\n📋 Teste 3: Análise de Sentimento")
        sentiment_positive = client.analyze_sentiment("Estou muito feliz hoje!")
        sentiment_negative = client.analyze_sentiment("Estou muito triste e frustrado")
        
        print(f"✅ Sentimento positivo: {sentiment_positive}")
        print(f"✅ Sentimento negativo: {sentiment_negative}")
        
        # Teste 4: Chat Completion
        print("\n📋 Teste 4: Chat Completion")
        chat_response = client.chat_completion([
            {"role": "system", "content": "Você é o BestStag, um assistente virtual inteligente."},
            {"role": "user", "content": "Como você pode me ajudar com produtividade?"}
        ])
        print(f"✅ Chat response: {chat_response}")
        
        # Teste 5: Cache
        print("\n📋 Teste 5: Sistema de Cache")
        start_time = time.time()
        client.generate_text("Teste de cache", model="chatglm")
        first_request_time = time.time() - start_time
        
        start_time = time.time()
        client.generate_text("Teste de cache", model="chatglm")  # Mesma requisição
        cached_request_time = time.time() - start_time
        
        print(f"✅ Primeira requisição: {first_request_time:.2f}s")
        print(f"✅ Requisição em cache: {cached_request_time:.2f}s")
        print(f"✅ Speedup: {first_request_time/cached_request_time:.1f}x")
        
        # Teste 6: Estatísticas
        print("\n📋 Teste 6: Estatísticas de Uso")
        stats = client.get_stats()
        print(f"✅ Estatísticas: {json.dumps(stats, indent=2)}")
        
        print("\n🎉 Todos os testes passaram!")
        print("✅ Integração BestStag v9.1 + Abacus.AI está funcionando")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_n8n_workflow():
    """Testa se o workflow n8n está configurado corretamente"""
    print("\n📋 Verificando configuração do workflow n8n")
    
    workflow_path = os.path.join(os.path.dirname(__file__), 'workflows', 'whatsapp_abacus_workflow.json')
    
    if os.path.exists(workflow_path):
        print(f"✅ Workflow encontrado: {workflow_path}")
        
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        # Verificar nós essenciais
        node_names = [node['name'] for node in workflow['nodes']]
        required_nodes = ['Webhook WhatsApp', 'Analisar Sentimento', 'Enviar WhatsApp']
        
        for node in required_nodes:
            if node in node_names:
                print(f"✅ Nó encontrado: {node}")
            else:
                print(f"❌ Nó não encontrado: {node}")
                return False
        
        print("✅ Workflow n8n está configurado corretamente")
        return True
    else:
        print(f"❌ Workflow não encontrado: {workflow_path}")
        return False

def main():
    """Função principal"""
    print("🔧 BestStag v9.1 + Abacus.AI - Teste de Integração")
    print("Fase 1: Integração Inicial")
    print("=" * 60)
    
    success = True
    
    # Teste da integração Abacus.AI
    if not test_abacus_integration():
        success = False
    
    # Teste do workflow n8n
    if not test_n8n_workflow():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCESSO: Todos os testes passaram!")
        print("✅ BestStag v9.1 + Abacus.AI está pronto para uso")
        print("\n📝 Próximos passos:")
        print("   1. Importe o workflow no n8n")
        print("   2. Configure as credenciais Abacus.AI e Twilio")
        print("   3. Ative o webhook do WhatsApp")
        print("   4. Teste enviando uma mensagem")
    else:
        print("❌ FALHA: Alguns testes falharam")
        print("🔧 Verifique a configuração e tente novamente")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

