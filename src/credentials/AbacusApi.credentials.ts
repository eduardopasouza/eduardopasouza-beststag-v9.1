import { ICredentialType, INodeProperties } from 'n8n-workflow';

export class AbacusApi implements ICredentialType {
  name = 'abacusApi';
  displayName = 'Abacus.AI API';
  documentationUrl = 'https://docs.abacus.ai/';
  properties: INodeProperties[] = [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: {
        password: true,
      },
      default: '',
      required: true,
      description: 'Chave de API do Abacus.AI',
    },
  ];
}

