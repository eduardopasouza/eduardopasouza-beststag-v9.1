import { INodeType, INodeTypeDescription, IExecuteFunctions } from 'n8n-workflow';

export class AbacusAI implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Abacus.AI',
    name: 'abacusAI',
    group: ['transform'],
    version: 1,
    description: 'Interage com a API do Abacus.AI',
    defaults: { name: 'Abacus.AI' },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      { name: 'abacusApi', required: true }
    ],
    properties: [
      { 
        displayName: 'Prompt', 
        name: 'prompt', 
        type: 'string', 
        default: '', 
        required: true,
        description: 'Texto ou pergunta para enviar ao modelo de IA'
      },
      { 
        displayName: 'Modelo', 
        name: 'model', 
        type: 'options',
        options: [
          { name: 'ChatGLM', value: 'chatglm' },
          { name: 'GPT-4', value: 'gpt-4' },
          { name: 'Claude', value: 'claude' }
        ],
        default: 'chatglm', 
        required: false,
        description: 'Modelo de IA a ser utilizado'
      },
      { 
        displayName: 'Agent ID', 
        name: 'agentId', 
        type: 'string', 
        default: '', 
        required: false,
        description: 'ID do agente específico (para DeepAgent)'
      },
      {
        displayName: 'Operação',
        name: 'operation',
        type: 'options',
        options: [
          { name: 'Chat Completion', value: 'chat' },
          { name: 'Deep Agent', value: 'agent' },
          { name: 'Sentiment Analysis', value: 'sentiment' }
        ],
        default: 'chat',
        required: true,
        description: 'Tipo de operação a ser executada'
      }
    ],
  };

  async execute(this: IExecuteFunctions) {
    const items = this.getInputData();
    const returnData = [];
    
    for (let i = 0; i < items.length; i++) {
      const prompt = this.getNodeParameter('prompt', i) as string;
      const model = this.getNodeParameter('model', i) as string;
      const agentId = this.getNodeParameter('agentId', i) as string;
      const operation = this.getNodeParameter('operation', i) as string;
      const credentials = this.getCredentials('abacusApi') as { apiKey: string };
      
      let endpoint = '';
      let body: any = {};
      
      switch (operation) {
        case 'chat':
          endpoint = 'https://api.abacus.ai/v1/serve/chatllm';
          body = { prompt, model };
          break;
        case 'agent':
          endpoint = 'https://api.abacus.ai/v1/serve/agent';
          body = { task: prompt, agentId };
          break;
        case 'sentiment':
          endpoint = 'https://api.abacus.ai/v1/serve/sentiment';
          body = { text: prompt };
          break;
        default:
          throw new Error(`Operação não suportada: ${operation}`);
      }
      
      try {
        const response = await this.helpers.request({
          method: 'POST',
          url: endpoint,
          headers: { 
            'Authorization': `Bearer ${credentials.apiKey}`,
            'Content-Type': 'application/json'
          },
          body,
          json: true,
        });
        
        returnData.push({
          json: {
            ...response,
            operation,
            model,
            timestamp: new Date().toISOString()
          }
        });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: {
              error: error.message,
              operation,
              model,
              timestamp: new Date().toISOString()
            }
          });
        } else {
          throw error;
        }
      }
    }
    
    return [returnData];
  }
}

