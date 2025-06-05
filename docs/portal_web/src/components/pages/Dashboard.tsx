import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  CheckSquare, 
  MessageSquare, 
  TrendingUp, 
  Clock, 
  Users, 
  Bell,
  Settings,
  BarChart3,
  Activity,
  Zap,
  Target
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { useQuery } from '@tanstack/react-query';
import { format, startOfDay, endOfDay, isToday, isTomorrow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';

interface DashboardStats {
  tarefas_pendentes: number;
  tarefas_concluidas_hoje: number;
  eventos_hoje: number;
  eventos_semana: number;
  interacoes_hoje: number;
  score_produtividade: number;
  tempo_resposta_medio: number;
  meta_diaria_progresso: number;
}

interface TarefaRecente {
  id: string;
  titulo: string;
  status: 'pendente' | 'em_andamento' | 'concluida';
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente';
  data_vencimento?: string;
  progresso: number;
}

interface EventoProximo {
  id: string;
  titulo: string;
  data_inicio: string;
  data_fim: string;
  tipo: 'reuniao' | 'compromisso' | 'tarefa' | 'lembrete';
  local?: string;
}

interface InteracaoRecente {
  id: string;
  tipo: 'whatsapp' | 'portal' | 'api';
  comando: string;
  data_hora: string;
  status: 'sucesso' | 'erro';
}

const Dashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'hoje' | 'semana' | 'mes'>('hoje');

  // Query para estatísticas do dashboard
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats', selectedPeriod],
    queryFn: async () => {
      const response = await fetch(`/api/dashboard/stats?periodo=${selectedPeriod}`);
      if (!response.ok) throw new Error('Erro ao carregar estatísticas');
      return response.json();
    },
    refetchInterval: 30000, // Atualiza a cada 30 segundos
  });

  // Query para tarefas recentes
  const { data: tarefasRecentes } = useQuery<TarefaRecente[]>({
    queryKey: ['tarefas-recentes'],
    queryFn: async () => {
      const response = await fetch('/api/tarefas?limite=5&status=pendente,em_andamento');
      if (!response.ok) throw new Error('Erro ao carregar tarefas');
      return response.json();
    },
  });

  // Query para próximos eventos
  const { data: proximosEventos } = useQuery<EventoProximo[]>({
    queryKey: ['proximos-eventos'],
    queryFn: async () => {
      const response = await fetch('/api/eventos?limite=3&periodo=proximos');
      if (!response.ok) throw new Error('Erro ao carregar eventos');
      return response.json();
    },
  });

  // Query para interações recentes
  const { data: interacoesRecentes } = useQuery<InteracaoRecente[]>({
    queryKey: ['interacoes-recentes'],
    queryFn: async () => {
      const response = await fetch('/api/interacoes?limite=5&periodo=hoje');
      if (!response.ok) throw new Error('Erro ao carregar interações');
      return response.json();
    },
  });

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade) {
      case 'urgente': return 'bg-red-500';
      case 'alta': return 'bg-orange-500';
      case 'media': return 'bg-yellow-500';
      case 'baixa': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getTipoEventoIcon = (tipo: string) => {
    switch (tipo) {
      case 'reuniao': return <Users className="h-4 w-4" />;
      case 'compromisso': return <Calendar className="h-4 w-4" />;
      case 'tarefa': return <CheckSquare className="h-4 w-4" />;
      case 'lembrete': return <Bell className="h-4 w-4" />;
      default: return <Calendar className="h-4 w-4" />;
    }
  };

  const formatarHorario = (dataString: string) => {
    return format(new Date(dataString), 'HH:mm', { locale: ptBR });
  };

  const formatarDataRelativa = (dataString: string) => {
    const data = new Date(dataString);
    if (isToday(data)) return 'Hoje';
    if (isTomorrow(data)) return 'Amanhã';
    return format(data, 'dd/MM', { locale: ptBR });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Dashboard BestStag v9.0
              </h1>
              <p className="text-gray-600">
                {format(new Date(), "EEEE, dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Seletor de período */}
              <div className="flex rounded-lg bg-white p-1 shadow-sm">
                {(['hoje', 'semana', 'mes'] as const).map((periodo) => (
                  <Button
                    key={periodo}
                    variant={selectedPeriod === periodo ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setSelectedPeriod(periodo)}
                    className="capitalize"
                  >
                    {periodo}
                  </Button>
                ))}
              </div>
              
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Configurações
              </Button>
            </div>
          </div>
        </div>

        {/* Cards de estatísticas principais */}
        <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tarefas Pendentes</CardTitle>
                <CheckSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : stats?.tarefas_pendentes || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.tarefas_concluidas_hoje || 0} concluídas hoje
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Eventos Hoje</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : stats?.eventos_hoje || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.eventos_semana || 0} esta semana
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Interações</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : stats?.interacoes_hoje || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Hoje via WhatsApp
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Produtividade</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? '...' : `${stats?.score_produtividade || 0}%`}
                </div>
                <Progress 
                  value={stats?.score_produtividade || 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Grid principal */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Tarefas Recentes */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckSquare className="h-5 w-5 mr-2" />
                  Tarefas Recentes
                </CardTitle>
                <CardDescription>
                  Suas tarefas mais importantes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tarefasRecentes?.map((tarefa) => (
                    <div key={tarefa.id} className="flex items-center space-x-3">
                      <div className={`h-3 w-3 rounded-full ${getPrioridadeColor(tarefa.prioridade)}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {tarefa.titulo}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {tarefa.status}
                          </Badge>
                          {tarefa.data_vencimento && (
                            <span className="text-xs text-gray-500">
                              {formatarDataRelativa(tarefa.data_vencimento)}
                            </span>
                          )}
                        </div>
                        {tarefa.progresso > 0 && (
                          <Progress value={tarefa.progresso} className="mt-2 h-1" />
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {(!tarefasRecentes || tarefasRecentes.length === 0) && (
                    <div className="text-center py-6 text-gray-500">
                      <CheckSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Nenhuma tarefa pendente</p>
                      <p className="text-sm">Parabéns! 🎉</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Próximos Eventos */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Próximos Eventos
                </CardTitle>
                <CardDescription>
                  Sua agenda para os próximos dias
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {proximosEventos?.map((evento) => (
                    <div key={evento.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getTipoEventoIcon(evento.tipo)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {evento.titulo}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-500">
                            {formatarDataRelativa(evento.data_inicio)} às {formatarHorario(evento.data_inicio)}
                          </span>
                        </div>
                        {evento.local && (
                          <p className="text-xs text-gray-500 mt-1">
                            📍 {evento.local}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {(!proximosEventos || proximosEventos.length === 0) && (
                    <div className="text-center py-6 text-gray-500">
                      <Calendar className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Nenhum evento próximo</p>
                      <p className="text-sm">Agenda livre! 📅</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Atividade Recente */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Atividade Recente
                </CardTitle>
                <CardDescription>
                  Suas interações com o BestStag
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {interacoesRecentes?.map((interacao) => (
                    <div key={interacao.id} className="flex items-center space-x-3">
                      <div className={`h-2 w-2 rounded-full ${
                        interacao.status === 'sucesso' ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {interacao.comando}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {interacao.tipo}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {format(new Date(interacao.data_hora), 'HH:mm')}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {(!interacoesRecentes || interacoesRecentes.length === 0) && (
                    <div className="text-center py-6 text-gray-500">
                      <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Nenhuma atividade recente</p>
                      <p className="text-sm">Comece usando o WhatsApp! 📱</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Meta do Dia */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Meta do Dia
              </CardTitle>
              <CardDescription>
                Seu progresso diário de produtividade
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Progresso Geral</span>
                  <span className="text-sm text-gray-500">
                    {stats?.meta_diaria_progresso || 0}% concluído
                  </span>
                </div>
                <Progress value={stats?.meta_diaria_progresso || 0} className="h-2" />
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {stats?.tarefas_concluidas_hoje || 0}
                    </div>
                    <div className="text-sm text-gray-500">Tarefas Concluídas</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {stats?.eventos_hoje || 0}
                    </div>
                    <div className="text-sm text-gray-500">Eventos Hoje</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {stats?.tempo_resposta_medio || 0}h
                    </div>
                    <div className="text-sm text-gray-500">Tempo Médio</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-6"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="h-5 w-5 mr-2" />
                Ações Rápidas
              </CardTitle>
              <CardDescription>
                Acesso rápido às funcionalidades principais
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex-col">
                  <CheckSquare className="h-6 w-6 mb-2" />
                  Nova Tarefa
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Calendar className="h-6 w-6 mb-2" />
                  Novo Evento
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <BarChart3 className="h-6 w-6 mb-2" />
                  Relatórios
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Settings className="h-6 w-6 mb-2" />
                  Configurações
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;

