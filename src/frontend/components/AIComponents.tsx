/**
 * BestStag v9.1 + Abacus.AI - Componentes React Inteligentes
 * Fase 2: IA Contextual e Front-end Inteligente
 */

import React, { useState, useEffect } from 'react';
import {
  useSentiment,
  useIntelligentChat,
  useAIInsights,
  useProductivityAnalysis,
  usePersonalizedRecommendations
} from '../hooks/useAI';

// Componente de Chat Inteligente
export const IntelligentChat: React.FC<{ userId: string }> = ({ userId }) => {
  const [input, setInput] = useState('');
  const { messages, sendMessage, loading, error } = useIntelligentChat(userId);
  const { sentiment } = useSentiment(input);
  
  const handleSend = async () => {
    if (!input.trim()) return;
    
    try {
      await sendMessage(input, { sentiment });
      setInput('');
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
    }
  };
  
  const getSentimentColor = () => {
    if (!sentiment) return 'border-gray-300';
    switch (sentiment.sentiment) {
      case 'positive': return 'border-green-400';
      case 'negative': return 'border-red-400';
      default: return 'border-yellow-400';
    }
  };
  
  return (
    <div className="flex flex-col h-96 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h3 className="font-semibold">BestStag Assistant</h3>
        {sentiment && (
          <div className="text-sm opacity-90">
            Sentimento: {sentiment.sentiment} ({Math.round(sentiment.confidence * 100)}%)
          </div>
        )}
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Input */}
      <div className="p-4 border-t">
        {error && (
          <div className="text-red-600 text-sm mb-2">{error}</div>
        )}
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Digite sua mensagem..."
            className={`flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${getSentimentColor()}`}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
};

// Painel de Insights Automáticos
export const AIInsightsPanel: React.FC<{ data: any }> = ({ data }) => {
  const { insights, loading, lastUpdate, refresh } = useAIInsights(data);
  
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'recommendation': return '💡';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📊';
    }
  };
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50';
      case 'low': return 'border-l-green-500 bg-green-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Insights Inteligentes</h3>
        <div className="flex items-center space-x-2">
          {lastUpdate && (
            <span className="text-sm text-gray-500">
              Atualizado: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={refresh}
            disabled={loading}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>
      </div>
      
      {loading && insights.length === 0 ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Nenhum insight disponível no momento
            </div>
          ) : (
            insights.map((insight, index) => (
              <div
                key={index}
                className={`border-l-4 p-4 rounded-r-lg ${getPriorityColor(insight.priority)}`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getInsightIcon(insight.type)}</span>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800">{insight.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                    
                    {insight.actionable && insight.actions && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Ações sugeridas:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {insight.actions.map((action, actionIndex) => (
                            <li key={actionIndex} className="flex items-center space-x-2">
                              <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                              <span>{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

// Dashboard de Produtividade
export const ProductivityDashboard: React.FC<{ userId: string }> = ({ userId }) => {
  const [timeframe, setTimeframe] = useState('7d');
  const { analysis, trends, loading } = useProductivityAnalysis(userId, timeframe);
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-800">Análise de Produtividade</h3>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          className="px-3 py-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="1d">Último dia</option>
          <option value="7d">Última semana</option>
          <option value="30d">Último mês</option>
          <option value="90d">Últimos 3 meses</option>
        </select>
      </div>
      
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : analysis ? (
        <div className="space-y-6">
          {/* Score geral */}
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-blue-100 rounded-full">
              <span className="text-2xl font-bold text-blue-600">
                {Math.round(analysis.overallScore * 100)}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-600">Score de Produtividade</p>
          </div>
          
          {/* Métricas */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-800">
                {analysis.tasksCompleted || 0}
              </div>
              <div className="text-sm text-gray-600">Tarefas Concluídas</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-800">
                {analysis.focusTime || '0h'}
              </div>
              <div className="text-sm text-gray-600">Tempo de Foco</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-800">
                {analysis.meetingsAttended || 0}
              </div>
              <div className="text-sm text-gray-600">Reuniões</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-800">
                {analysis.wellbeingScore ? Math.round(analysis.wellbeingScore * 100) : 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Bem-estar</div>
            </div>
          </div>
          
          {/* Tendências */}
          {trends.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-800 mb-3">Tendências</h4>
              <div className="space-y-2">
                {trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-700">{trend.description}</span>
                    <span className={`text-sm font-medium ${
                      trend.direction === 'up' ? 'text-green-600' : 
                      trend.direction === 'down' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {trend.direction === 'up' ? '↗️' : trend.direction === 'down' ? '↘️' : '➡️'}
                      {trend.change}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Dados de produtividade não disponíveis
        </div>
      )}
    </div>
  );
};

// Painel de Recomendações Personalizadas
export const RecommendationsPanel: React.FC<{ userId: string }> = ({ userId }) => {
  const { recommendations, loading, markAsUsed } = usePersonalizedRecommendations(userId);
  
  const handleUseRecommendation = async (recommendationId: string) => {
    try {
      await markAsUsed(recommendationId);
    } catch (err) {
      console.error('Erro ao marcar recomendação como usada:', err);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Recomendações Personalizadas</h3>
      
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-3">
          {recommendations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Nenhuma recomendação disponível
            </div>
          ) : (
            recommendations.map((rec) => (
              <div
                key={rec.id}
                className={`p-4 rounded-lg border ${
                  rec.used ? 'bg-gray-50 border-gray-200' : 'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800">{rec.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                    
                    {rec.category && (
                      <span className="inline-block mt-2 px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                        {rec.category}
                      </span>
                    )}
                  </div>
                  
                  {!rec.used && (
                    <button
                      onClick={() => handleUseRecommendation(rec.id)}
                      className="ml-4 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Usar
                    </button>
                  )}
                </div>
                
                {rec.used && (
                  <div className="mt-2 text-xs text-gray-500">
                    ✅ Usado em {new Date(rec.usedAt).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

// Componente de Análise de Sentimento em Tempo Real
export const SentimentIndicator: React.FC<{ text: string }> = ({ text }) => {
  const { sentiment, loading } = useSentiment(text);
  
  if (!text || text.length < 5) return null;
  
  return (
    <div className="flex items-center space-x-2 text-sm">
      {loading ? (
        <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
      ) : sentiment ? (
        <>
          <div className={`w-3 h-3 rounded-full ${
            sentiment.sentiment === 'positive' ? 'bg-green-500' :
            sentiment.sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
          }`}></div>
          <span className="text-gray-600">
            {sentiment.sentiment} ({Math.round(sentiment.confidence * 100)}%)
          </span>
        </>
      ) : null}
    </div>
  );
};

export {
  IntelligentChat,
  AIInsightsPanel,
  ProductivityDashboard,
  RecommendationsPanel,
  SentimentIndicator
};

