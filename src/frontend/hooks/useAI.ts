/**
 * BestStag v9.1 + Abacus.AI - Hooks React Inteligentes
 * Fase 2: IA Contextual e Front-end Inteligente
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

// Configuração da API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Tipos TypeScript
interface SentimentResult {
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  emotions?: string[];
}

interface AIResponse {
  response: string;
  model: string;
  timestamp: string;
  metadata?: any;
}

interface InsightData {
  title: string;
  description: string;
  type: 'recommendation' | 'warning' | 'info';
  priority: 'high' | 'medium' | 'low';
  actionable: boolean;
  actions?: string[];
}

interface AutocompleteOption {
  text: string;
  confidence: number;
  category: string;
}

// Hook para análise de sentimento em tempo real
export function useSentiment(text: string, debounceMs: number = 500) {
  const [sentiment, setSentiment] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!text || text.length < 5) {
      setSentiment(null);
      return;
    }
    
    const timeoutId = setTimeout(async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.post(`${API_BASE_URL}/api/sentiment`, { text });
        setSentiment(response.data);
      } catch (err) {
        setError('Erro ao analisar sentimento');
        console.error('Sentiment analysis error:', err);
      } finally {
        setLoading(false);
      }
    }, debounceMs);
    
    return () => clearTimeout(timeoutId);
  }, [text, debounceMs]);
  
  return { sentiment, loading, error };
}

// Hook para chat inteligente com contexto
export function useIntelligentChat(userId: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const sendMessage = useCallback(async (message: string, context?: any) => {
    setLoading(true);
    setError(null);
    
    // Adicionar mensagem do usuário
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message,
        userId,
        context,
        history: messages.slice(-10) // Últimas 10 mensagens
      });
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        metadata: response.data.metadata
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      return response.data;
    } catch (err) {
      setError('Erro ao enviar mensagem');
      console.error('Chat error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [messages, userId]);
  
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);
  
  return {
    messages,
    sendMessage,
    clearChat,
    loading,
    error
  };
}

// Hook para autocomplete inteligente
export function useSmartAutocomplete(input: string, category?: string) {
  const [suggestions, setSuggestions] = useState<AutocompleteOption[]>([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  useEffect(() => {
    if (!input || input.length < 2) {
      setSuggestions([]);
      return;
    }
    
    // Cancelar requisição anterior
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const controller = new AbortController();
    abortControllerRef.current = controller;
    
    const fetchSuggestions = async () => {
      setLoading(true);
      
      try {
        const response = await axios.post(
          `${API_BASE_URL}/api/autocomplete`,
          { input, category },
          { signal: controller.signal }
        );
        
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        if (!axios.isCancel(err)) {
          console.error('Autocomplete error:', err);
        }
      } finally {
        setLoading(false);
      }
    };
    
    const timeoutId = setTimeout(fetchSuggestions, 300);
    
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [input, category]);
  
  return { suggestions, loading };
}

// Hook para insights automáticos
export function useAIInsights(data: any, refreshInterval: number = 30000) {
  const [insights, setInsights] = useState<InsightData[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  
  const generateInsights = useCallback(async () => {
    if (!data) return;
    
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/insights`, {
        data,
        timestamp: new Date().toISOString()
      });
      
      setInsights(response.data.insights || []);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Insights generation error:', err);
    } finally {
      setLoading(false);
    }
  }, [data]);
  
  useEffect(() => {
    generateInsights();
    
    const interval = setInterval(generateInsights, refreshInterval);
    
    return () => clearInterval(interval);
  }, [generateInsights, refreshInterval]);
  
  return {
    insights,
    loading,
    lastUpdate,
    refresh: generateInsights
  };
}

// Hook para assistente contextual
export function useContextualAssistant(userId: string) {
  const [context, setContext] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  
  const updateContext = useCallback(async (newContext: any) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/context`, {
        userId,
        context: newContext,
        timestamp: new Date().toISOString()
      });
      
      setContext(response.data.context);
      setSuggestions(response.data.suggestions || []);
    } catch (err) {
      console.error('Context update error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);
  
  const getSuggestions = useCallback(async (currentActivity: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/suggestions`, {
        userId,
        activity: currentActivity,
        context
      });
      
      setSuggestions(response.data.suggestions || []);
    } catch (err) {
      console.error('Suggestions error:', err);
    }
  }, [userId, context]);
  
  return {
    context,
    suggestions,
    loading,
    updateContext,
    getSuggestions
  };
}

// Hook para análise de produtividade
export function useProductivityAnalysis(userId: string, timeframe: string = '7d') {
  const [analysis, setAnalysis] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const analyzeProductivity = useCallback(async () => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/productivity`, {
        userId,
        timeframe
      });
      
      setAnalysis(response.data.analysis);
      setTrends(response.data.trends || []);
    } catch (err) {
      console.error('Productivity analysis error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, timeframe]);
  
  useEffect(() => {
    analyzeProductivity();
  }, [analyzeProductivity]);
  
  return {
    analysis,
    trends,
    loading,
    refresh: analyzeProductivity
  };
}

// Hook para recomendações personalizadas
export function usePersonalizedRecommendations(userId: string) {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const getRecommendations = useCallback(async (context?: any) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/recommendations`, {
        userId,
        context,
        timestamp: new Date().toISOString()
      });
      
      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      console.error('Recommendations error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);
  
  const markAsUsed = useCallback(async (recommendationId: string) => {
    try {
      await axios.post(`${API_BASE_URL}/api/recommendations/${recommendationId}/used`);
      
      // Atualizar estado local
      setRecommendations(prev => 
        prev.map(rec => 
          rec.id === recommendationId 
            ? { ...rec, used: true, usedAt: new Date().toISOString() }
            : rec
        )
      );
    } catch (err) {
      console.error('Mark recommendation as used error:', err);
    }
  }, []);
  
  useEffect(() => {
    getRecommendations();
  }, [getRecommendations]);
  
  return {
    recommendations,
    loading,
    refresh: getRecommendations,
    markAsUsed
  };
}

// Hook para monitoramento de bem-estar
export function useWellbeingMonitor(userId: string) {
  const [wellbeingScore, setWellbeingScore] = useState<number | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const updateWellbeing = useCallback(async (data: any) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/wellbeing`, {
        userId,
        data,
        timestamp: new Date().toISOString()
      });
      
      setWellbeingScore(response.data.score);
      setAlerts(response.data.alerts || []);
      setTrends(response.data.trends || []);
    } catch (err) {
      console.error('Wellbeing update error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);
  
  return {
    wellbeingScore,
    alerts,
    trends,
    loading,
    updateWellbeing
  };
}

// Hook para cache inteligente
export function useSmartCache<T>(key: string, fetcher: () => Promise<T>, ttl: number = 300000) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  
  const fetchData = useCallback(async (force: boolean = false) => {
    // Verificar cache
    if (!force && lastFetch && Date.now() - lastFetch.getTime() < ttl) {
      return data;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetcher();
      setData(result);
      setLastFetch(new Date());
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetcher, ttl, data, lastFetch]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  const invalidate = useCallback(() => {
    setLastFetch(null);
    setData(null);
  }, []);
  
  return {
    data,
    loading,
    error,
    refresh: () => fetchData(true),
    invalidate
  };
}

export default {
  useSentiment,
  useIntelligentChat,
  useSmartAutocomplete,
  useAIInsights,
  useContextualAssistant,
  useProductivityAnalysis,
  usePersonalizedRecommendations,
  useWellbeingMonitor,
  useSmartCache
};

