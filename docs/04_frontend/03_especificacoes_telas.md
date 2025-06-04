# ESPECIFICAÇÕES TÉCNICAS DAS TELAS PRINCIPAIS
**Portal Web Completo BestStag - Expansão da Base BSFT-001**

---

## INFORMAÇÕES GERAIS

**Documento:** Especificações Técnicas das Telas Principais  
**Versão:** 1.0  
**Data:** 02/06/2025  
**Base:** Sistema de Autenticação BSFT-001 (Feedback EXCELENTE)  
**Objetivo:** Expandir portal para funcionalidades completas  

---

## ARQUITETURA GERAL DAS TELAS

### ESTRUTURA BASE HERDADA (BSFT-001)
A base sólida já estabelecida inclui:
- Sistema de autenticação completo (email/senha + OAuth)
- Roteamento e proteção de rotas
- Design responsivo mobile-first
- Gerenciamento de estado com Context API
- Componentes base com Tailwind CSS e Shadcn/ui

### EXPANSÃO PROPOSTA
Expansão para 4 telas principais integradas:
1. **Dashboard Principal** (expansão da base existente)
2. **Tela de Tarefas** (nova implementação)
3. **Tela de Contatos** (nova implementação)
4. **Tela de Agenda** (nova implementação)

---

## ESPECIFICAÇÃO DETALHADA - DASHBOARD PRINCIPAL

### VISÃO GERAL
O dashboard atual será expandido significativamente, mantendo a base excelente já implementada e adicionando funcionalidades avançadas de visualização e interação.

### LAYOUT E ESTRUTURA

#### Header Expandido
**Componente:** `DashboardHeader.jsx`
**Funcionalidades Atuais Mantidas:**
- Logo BestStag com navegação para home
- Barra de busca global
- Ícone de notificações com contador
- Avatar do usuário com dropdown menu

**Novas Funcionalidades:**
- **Busca Inteligente:** Autocomplete com resultados de todas as seções
- **Centro de Notificações:** Modal expandido com categorização
- **Configurações Rápidas:** Acesso direto a configurações principais
- **Status de Sincronização:** Indicador de conexão com Airtable

**Especificação Técnica:**
```jsx
// Estrutura expandida do header
const DashboardHeader = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [syncStatus, setSyncStatus] = useState('connected');
  
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e navegação */}
          <div className="flex items-center">
            <BestStagLogo />
            <NavigationBreadcrumb />
          </div>
          
          {/* Busca inteligente */}
          <div className="flex-1 max-w-lg mx-8">
            <SmartSearchBar 
              query={searchQuery}
              onChange={setSearchQuery}
              placeholder="Buscar tarefas, contatos, eventos..."
            />
          </div>
          
          {/* Ações do usuário */}
          <div className="flex items-center space-x-4">
            <SyncStatusIndicator status={syncStatus} />
            <NotificationCenter notifications={notifications} />
            <UserProfileDropdown />
          </div>
        </div>
      </div>
    </header>
  );
};
```

#### Grid de Widgets Inteligente
**Componente:** `DashboardGrid.jsx`
**Funcionalidades:**
- **Layout Responsivo:** Grid adaptativo baseado no tamanho da tela
- **Widgets Personalizáveis:** Usuário pode reorganizar e personalizar
- **Dados em Tempo Real:** Integração com Airtable para atualizações automáticas
- **Filtros por Período:** Visualização de dados por dia, semana, mês

**Widgets Principais:**

##### 1. Widget de Métricas Gerais
**Componente:** `MetricsWidget.jsx`
```jsx
const MetricsWidget = () => {
  const { tasks, contacts, events } = useAirtableData();
  
  const metrics = [
    {
      title: 'Tarefas Pendentes',
      value: tasks.filter(t => t.status === 'pending').length,
      change: '+12%',
      trend: 'up',
      color: 'blue'
    },
    {
      title: 'Contatos Ativos',
      value: contacts.filter(c => c.active).length,
      change: '+5%',
      trend: 'up',
      color: 'green'
    },
    {
      title: 'Eventos Hoje',
      value: events.filter(e => isToday(e.date)).length,
      change: '0%',
      trend: 'stable',
      color: 'purple'
    },
    {
      title: 'WhatsApp Status',
      value: 'Conectado',
      change: 'Online',
      trend: 'up',
      color: 'emerald'
    }
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric, index) => (
        <MetricCard key={index} {...metric} />
      ))}
    </div>
  );
};
```

##### 2. Widget de Tarefas Prioritárias
**Componente:** `PriorityTasksWidget.jsx`
```jsx
const PriorityTasksWidget = () => {
  const { tasks } = useAirtableData();
  const priorityTasks = tasks
    .filter(t => t.priority === 'high' && t.status !== 'completed')
    .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
    .slice(0, 5);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Tarefas Prioritárias
        </h3>
        <Link to="/tasks" className="text-blue-600 hover:text-blue-800">
          Ver todas
        </Link>
      </div>
      
      <div className="space-y-3">
        {priorityTasks.map(task => (
          <TaskQuickItem 
            key={task.id} 
            task={task}
            onComplete={handleTaskComplete}
            onEdit={handleTaskEdit}
          />
        ))}
      </div>
      
      <button className="w-full mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium">
        + Nova Tarefa Prioritária
      </button>
    </div>
  );
};
```

##### 3. Widget de Agenda do Dia
**Componente:** `TodayAgendaWidget.jsx`
```jsx
const TodayAgendaWidget = () => {
  const { events } = useAirtableData();
  const todayEvents = events
    .filter(e => isToday(e.date))
    .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Agenda de Hoje
        </h3>
        <span className="text-sm text-gray-500">
          {format(new Date(), 'dd/MM/yyyy')}
        </span>
      </div>
      
      {todayEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CalendarIcon className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-2">Nenhum evento hoje</p>
        </div>
      ) : (
        <div className="space-y-3">
          {todayEvents.map(event => (
            <EventQuickItem 
              key={event.id} 
              event={event}
              onEdit={handleEventEdit}
            />
          ))}
        </div>
      )}
      
      <button className="w-full mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium">
        + Novo Evento
      </button>
    </div>
  );
};
```

##### 4. Widget de Contatos Recentes
**Componente:** `RecentContactsWidget.jsx`
```jsx
const RecentContactsWidget = () => {
  const { contacts, interactions } = useAirtableData();
  const recentContacts = interactions
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
    .map(interaction => 
      contacts.find(c => c.id === interaction.contactId)
    )
    .filter(Boolean);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Contatos Recentes
        </h3>
        <Link to="/contacts" className="text-blue-600 hover:text-blue-800">
          Ver todos
        </Link>
      </div>
      
      <div className="space-y-3">
        {recentContacts.map(contact => (
          <ContactQuickItem 
            key={contact.id} 
            contact={contact}
            onMessage={handleSendMessage}
            onCall={handleCall}
          />
        ))}
      </div>
      
      <button className="w-full mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium">
        + Novo Contato
      </button>
    </div>
  );
};
```

### SIDEBAR DE NAVEGAÇÃO
**Componente:** `DashboardSidebar.jsx`
**Funcionalidades:**
- **Navegação Principal:** Links para todas as seções
- **Indicadores de Status:** Contadores e notificações por seção
- **Ações Rápidas:** Botões para criação rápida
- **Configurações:** Acesso a configurações e perfil

```jsx
const DashboardSidebar = () => {
  const { pathname } = useLocation();
  const { counts } = useAirtableData();
  
  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: HomeIcon,
      current: pathname === '/dashboard'
    },
    {
      name: 'Tarefas',
      href: '/tasks',
      icon: CheckSquareIcon,
      current: pathname.startsWith('/tasks'),
      count: counts.pendingTasks
    },
    {
      name: 'Contatos',
      href: '/contacts',
      icon: UsersIcon,
      current: pathname.startsWith('/contacts'),
      count: counts.activeContacts
    },
    {
      name: 'Agenda',
      href: '/calendar',
      icon: CalendarIcon,
      current: pathname.startsWith('/calendar'),
      count: counts.todayEvents
    }
  ];
  
  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="flex-1 flex flex-col min-h-0 bg-gray-800">
        <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
          <nav className="mt-5 flex-1 px-2 space-y-1">
            {navigationItems.map((item) => (
              <NavigationItem key={item.name} {...item} />
            ))}
          </nav>
          
          <div className="px-2 space-y-2">
            <QuickActionButton 
              icon={PlusIcon}
              text="Nova Tarefa"
              onClick={() => openModal('createTask')}
            />
            <QuickActionButton 
              icon={UserPlusIcon}
              text="Novo Contato"
              onClick={() => openModal('createContact')}
            />
            <QuickActionButton 
              icon={CalendarPlusIcon}
              text="Novo Evento"
              onClick={() => openModal('createEvent')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## ESPECIFICAÇÃO DETALHADA - TELA DE TAREFAS

### VISÃO GERAL
Tela completa para gerenciamento de tarefas com funcionalidades avançadas de organização, filtros, visualizações múltiplas e integração total com Airtable.

### LAYOUT E ESTRUTURA

#### Header da Tela de Tarefas
**Componente:** `TasksHeader.jsx`
```jsx
const TasksHeader = () => {
  const [viewMode, setViewMode] = useState('list'); // list, kanban, calendar
  const [filters, setFilters] = useState({});
  
  return (
    <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tarefas</h1>
          <p className="text-sm text-gray-500">
            Gerencie suas tarefas e projetos
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <ViewModeToggle 
            mode={viewMode} 
            onChange={setViewMode}
            options={['list', 'kanban', 'calendar']}
          />
          <FilterDropdown 
            filters={filters}
            onChange={setFilters}
          />
          <CreateTaskButton />
        </div>
      </div>
    </div>
  );
};
```

#### Área Principal de Tarefas
**Componente:** `TasksMainArea.jsx`
```jsx
const TasksMainArea = () => {
  const { tasks, loading } = useAirtableData();
  const [viewMode] = useViewMode();
  const [filters] = useFilters();
  
  const filteredTasks = useMemo(() => {
    return applyFilters(tasks, filters);
  }, [tasks, filters]);
  
  if (loading) return <TasksLoadingSkeleton />;
  
  return (
    <div className="flex-1 overflow-hidden">
      {viewMode === 'list' && (
        <TasksListView tasks={filteredTasks} />
      )}
      {viewMode === 'kanban' && (
        <TasksKanbanView tasks={filteredTasks} />
      )}
      {viewMode === 'calendar' && (
        <TasksCalendarView tasks={filteredTasks} />
      )}
    </div>
  );
};
```

#### Visualização em Lista
**Componente:** `TasksListView.jsx`
```jsx
const TasksListView = ({ tasks }) => {
  const [sortBy, setSortBy] = useState('dueDate');
  const [sortOrder, setSortOrder] = useState('asc');
  
  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [tasks, sortBy, sortOrder]);
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Lista de Tarefas ({tasks.length})
          </h3>
          <SortControls 
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSortChange={setSortBy}
            onOrderChange={setSortOrder}
          />
        </div>
        
        <div className="space-y-3">
          {sortedTasks.map(task => (
            <TaskListItem 
              key={task.id}
              task={task}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
              onComplete={handleCompleteTask}
            />
          ))}
        </div>
        
        {tasks.length === 0 && (
          <EmptyState 
            icon={CheckSquareIcon}
            title="Nenhuma tarefa encontrada"
            description="Crie sua primeira tarefa para começar"
            action={<CreateTaskButton />}
          />
        )}
      </div>
    </div>
  );
};
```

#### Visualização Kanban
**Componente:** `TasksKanbanView.jsx`
```jsx
const TasksKanbanView = ({ tasks }) => {
  const columns = [
    { id: 'todo', title: 'A Fazer', status: 'pending' },
    { id: 'inProgress', title: 'Em Andamento', status: 'in_progress' },
    { id: 'review', title: 'Revisão', status: 'review' },
    { id: 'done', title: 'Concluído', status: 'completed' }
  ];
  
  const tasksByStatus = useMemo(() => {
    return columns.reduce((acc, column) => {
      acc[column.id] = tasks.filter(task => task.status === column.status);
      return acc;
    }, {});
  }, [tasks]);
  
  return (
    <div className="flex-1 overflow-x-auto">
      <div className="inline-flex h-full space-x-6 p-6">
        {columns.map(column => (
          <KanbanColumn
            key={column.id}
            column={column}
            tasks={tasksByStatus[column.id]}
            onTaskMove={handleTaskMove}
            onTaskEdit={handleEditTask}
          />
        ))}
      </div>
    </div>
  );
};
```

### FUNCIONALIDADES AVANÇADAS

#### Sistema de Filtros
**Componente:** `TaskFilters.jsx`
```jsx
const TaskFilters = ({ filters, onChange }) => {
  const filterOptions = {
    status: ['pending', 'in_progress', 'review', 'completed'],
    priority: ['low', 'medium', 'high', 'urgent'],
    category: ['work', 'personal', 'project', 'meeting'],
    assignee: [], // Carregado dinamicamente
    dueDate: ['today', 'this_week', 'this_month', 'overdue']
  };
  
  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-gray-900 mb-3">Filtros</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {Object.entries(filterOptions).map(([key, options]) => (
          <FilterSelect
            key={key}
            label={key}
            options={options}
            value={filters[key]}
            onChange={(value) => onChange({ ...filters, [key]: value })}
          />
        ))}
      </div>
      
      <div className="mt-4 flex justify-between">
        <button
          onClick={() => onChange({})}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Limpar Filtros
        </button>
        <span className="text-sm text-gray-500">
          {getFilteredCount(filters)} tarefas encontradas
        </span>
      </div>
    </div>
  );
};
```

#### Modal de Criação/Edição de Tarefas
**Componente:** `TaskModal.jsx`
```jsx
const TaskModal = ({ task, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState(task || {
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
    category: 'work',
    dueDate: '',
    assignee: '',
    tags: []
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSave(formData);
      onClose();
      toast.success(task ? 'Tarefa atualizada!' : 'Tarefa criada!');
    } catch (error) {
      toast.error('Erro ao salvar tarefa');
    }
  };
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            {task ? 'Editar Tarefa' : 'Nova Tarefa'}
          </h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <Input
              label="Título"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
          </div>
          
          <div className="md:col-span-2">
            <Textarea
              label="Descrição"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>
          
          <Select
            label="Status"
            value={formData.status}
            onChange={(value) => setFormData({...formData, status: value})}
            options={statusOptions}
          />
          
          <Select
            label="Prioridade"
            value={formData.priority}
            onChange={(value) => setFormData({...formData, priority: value})}
            options={priorityOptions}
          />
          
          <Select
            label="Categoria"
            value={formData.category}
            onChange={(value) => setFormData({...formData, category: value})}
            options={categoryOptions}
          />
          
          <DatePicker
            label="Data de Vencimento"
            value={formData.dueDate}
            onChange={(date) => setFormData({...formData, dueDate: date})}
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit">
            {task ? 'Atualizar' : 'Criar'} Tarefa
          </Button>
        </div>
      </form>
    </Modal>
  );
};
```

---

## ESPECIFICAÇÃO DETALHADA - TELA DE CONTATOS

### VISÃO GERAL
Tela completa para gerenciamento de contatos com funcionalidades de CRM básico, histórico de interações, categorização e integração com WhatsApp e email.

### LAYOUT E ESTRUTURA

#### Header da Tela de Contatos
**Componente:** `ContactsHeader.jsx`
```jsx
const ContactsHeader = () => {
  const [viewMode, setViewMode] = useState('grid'); // grid, list, map
  const [searchQuery, setSearchQuery] = useState('');
  
  return (
    <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contatos</h1>
          <p className="text-sm text-gray-500">
            Gerencie seus contatos e relacionamentos
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <SearchBar 
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Buscar contatos..."
          />
          <ViewModeToggle 
            mode={viewMode} 
            onChange={setViewMode}
            options={['grid', 'list', 'map']}
          />
          <ImportContactsButton />
          <CreateContactButton />
        </div>
      </div>
    </div>
  );
};
```

#### Sidebar de Categorias
**Componente:** `ContactsSidebar.jsx`
```jsx
const ContactsSidebar = () => {
  const { contacts } = useAirtableData();
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  const categories = [
    { id: 'all', name: 'Todos os Contatos', count: contacts.length },
    { id: 'clients', name: 'Clientes', count: contacts.filter(c => c.type === 'client').length },
    { id: 'suppliers', name: 'Fornecedores', count: contacts.filter(c => c.type === 'supplier').length },
    { id: 'partners', name: 'Parceiros', count: contacts.filter(c => c.type === 'partner').length },
    { id: 'leads', name: 'Leads', count: contacts.filter(c => c.type === 'lead').length },
    { id: 'favorites', name: 'Favoritos', count: contacts.filter(c => c.favorite).length }
  ];
  
  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 p-4">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Categorias</h3>
      
      <nav className="space-y-1">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-md ${
              selectedCategory === category.id
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <span>{category.name}</span>
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
              {category.count}
            </span>
          </button>
        ))}
      </nav>
      
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Tags</h4>
        <TagCloud tags={getContactTags(contacts)} />
      </div>
    </div>
  );
};
```

#### Área Principal de Contatos
**Componente:** `ContactsMainArea.jsx`
```jsx
const ContactsMainArea = () => {
  const { contacts, loading } = useAirtableData();
  const [viewMode] = useViewMode();
  const [selectedCategory] = useSelectedCategory();
  const [searchQuery] = useSearchQuery();
  
  const filteredContacts = useMemo(() => {
    let filtered = contacts;
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(contact => {
        if (selectedCategory === 'favorites') return contact.favorite;
        return contact.type === selectedCategory;
      });
    }
    
    if (searchQuery) {
      filtered = filtered.filter(contact =>
        contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    return filtered;
  }, [contacts, selectedCategory, searchQuery]);
  
  if (loading) return <ContactsLoadingSkeleton />;
  
  return (
    <div className="flex-1 overflow-hidden">
      {viewMode === 'grid' && (
        <ContactsGridView contacts={filteredContacts} />
      )}
      {viewMode === 'list' && (
        <ContactsListView contacts={filteredContacts} />
      )}
      {viewMode === 'map' && (
        <ContactsMapView contacts={filteredContacts} />
      )}
    </div>
  );
};
```

#### Visualização em Grid
**Componente:** `ContactsGridView.jsx`
```jsx
const ContactsGridView = ({ contacts }) => {
  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {contacts.map(contact => (
          <ContactCard
            key={contact.id}
            contact={contact}
            onEdit={handleEditContact}
            onDelete={handleDeleteContact}
            onMessage={handleSendMessage}
            onCall={handleCall}
            onEmail={handleSendEmail}
          />
        ))}
      </div>
      
      {contacts.length === 0 && (
        <EmptyState 
          icon={UsersIcon}
          title="Nenhum contato encontrado"
          description="Adicione seu primeiro contato para começar"
          action={<CreateContactButton />}
        />
      )}
    </div>
  );
};
```

#### Card de Contato
**Componente:** `ContactCard.jsx`
```jsx
const ContactCard = ({ contact, onEdit, onDelete, onMessage, onCall, onEmail }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Avatar
            src={contact.avatar}
            name={contact.name}
            size="lg"
          />
          <div className="ml-3">
            <h3 className="text-lg font-medium text-gray-900">{contact.name}</h3>
            <p className="text-sm text-gray-500">{contact.title}</p>
            {contact.company && (
              <p className="text-sm text-gray-500">{contact.company}</p>
            )}
          </div>
        </div>
        
        <ContactTypeBadge type={contact.type} />
      </div>
      
      <div className="space-y-2 mb-4">
        {contact.email && (
          <div className="flex items-center text-sm text-gray-600">
            <MailIcon className="h-4 w-4 mr-2" />
            <span>{contact.email}</span>
          </div>
        )}
        {contact.phone && (
          <div className="flex items-center text-sm text-gray-600">
            <PhoneIcon className="h-4 w-4 mr-2" />
            <span>{contact.phone}</span>
          </div>
        )}
        {contact.location && (
          <div className="flex items-center text-sm text-gray-600">
            <MapPinIcon className="h-4 w-4 mr-2" />
            <span>{contact.location}</span>
          </div>
        )}
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <ActionButton
            icon={MessageSquareIcon}
            onClick={() => onMessage(contact)}
            tooltip="Enviar mensagem"
            color="green"
          />
          <ActionButton
            icon={PhoneIcon}
            onClick={() => onCall(contact)}
            tooltip="Ligar"
            color="blue"
          />
          <ActionButton
            icon={MailIcon}
            onClick={() => onEmail(contact)}
            tooltip="Enviar email"
            color="gray"
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuItem onClick={() => onEdit(contact)}>
            Editar
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => toggleFavorite(contact)}>
            {contact.favorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => onDelete(contact)}
            className="text-red-600"
          >
            Excluir
          </DropdownMenuItem>
        </DropdownMenu>
      </div>
    </div>
  );
};
```

### FUNCIONALIDADES AVANÇADAS

#### Modal de Perfil Detalhado
**Componente:** `ContactProfileModal.jsx`
```jsx
const ContactProfileModal = ({ contact, isOpen, onClose }) => {
  const { interactions } = useAirtableData();
  const contactInteractions = interactions.filter(i => i.contactId === contact.id);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Avatar src={contact.avatar} name={contact.name} size="xl" />
            <div className="ml-4">
              <h2 className="text-2xl font-bold text-gray-900">{contact.name}</h2>
              <p className="text-lg text-gray-600">{contact.title}</p>
              {contact.company && (
                <p className="text-gray-500">{contact.company}</p>
              )}
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => handleEdit(contact)}>
              Editar
            </Button>
            <Button onClick={() => handleMessage(contact)}>
              Enviar Mensagem
            </Button>
          </div>
        </div>
        
        <Tabs defaultValue="info">
          <TabsList>
            <TabsTrigger value="info">Informações</TabsTrigger>
            <TabsTrigger value="interactions">Histórico</TabsTrigger>
            <TabsTrigger value="notes">Notas</TabsTrigger>
            <TabsTrigger value="files">Arquivos</TabsTrigger>
          </TabsList>
          
          <TabsContent value="info">
            <ContactInfoTab contact={contact} />
          </TabsContent>
          
          <TabsContent value="interactions">
            <InteractionsHistoryTab interactions={contactInteractions} />
          </TabsContent>
          
          <TabsContent value="notes">
            <ContactNotesTab contact={contact} />
          </TabsContent>
          
          <TabsContent value="files">
            <ContactFilesTab contact={contact} />
          </TabsContent>
        </Tabs>
      </div>
    </Modal>
  );
};
```

---

## ESPECIFICAÇÃO DETALHADA - TELA DE AGENDA

### VISÃO GERAL
Tela completa de agenda com visualizações múltiplas (mensal, semanal, diária), integração com Google Calendar e Outlook, criação de eventos e lembretes.

### LAYOUT E ESTRUTURA

#### Header da Agenda
**Componente:** `CalendarHeader.jsx`
```jsx
const CalendarHeader = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month'); // month, week, day, agenda
  
  return (
    <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">Agenda</h1>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentDate(new Date())}
            >
              Hoje
            </Button>
            
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateDate('prev')}
              >
                <ChevronLeftIcon className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateDate('next')}
              >
                <ChevronRightIcon className="h-4 w-4" />
              </Button>
            </div>
            
            <span className="text-lg font-medium text-gray-900">
              {formatDate(currentDate, viewMode)}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <ViewModeToggle 
            mode={viewMode} 
            onChange={setViewMode}
            options={['month', 'week', 'day', 'agenda']}
          />
          <SyncCalendarsButton />
          <CreateEventButton />
        </div>
      </div>
    </div>
  );
};
```

#### Área Principal do Calendário
**Componente:** `CalendarMainArea.jsx`
```jsx
const CalendarMainArea = () => {
  const { events, loading } = useAirtableData();
  const [viewMode] = useViewMode();
  const [currentDate] = useCurrentDate();
  
  if (loading) return <CalendarLoadingSkeleton />;
  
  return (
    <div className="flex-1 overflow-hidden">
      {viewMode === 'month' && (
        <MonthView 
          events={events} 
          currentDate={currentDate}
          onEventClick={handleEventClick}
          onDateClick={handleDateClick}
        />
      )}
      {viewMode === 'week' && (
        <WeekView 
          events={events} 
          currentDate={currentDate}
          onEventClick={handleEventClick}
          onTimeSlotClick={handleTimeSlotClick}
        />
      )}
      {viewMode === 'day' && (
        <DayView 
          events={events} 
          currentDate={currentDate}
          onEventClick={handleEventClick}
          onTimeSlotClick={handleTimeSlotClick}
        />
      )}
      {viewMode === 'agenda' && (
        <AgendaView 
          events={events} 
          currentDate={currentDate}
          onEventClick={handleEventClick}
        />
      )}
    </div>
  );
};
```

#### Visualização Mensal
**Componente:** `MonthView.jsx`
```jsx
const MonthView = ({ events, currentDate, onEventClick, onDateClick }) => {
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  const weeks = chunk(days, 7);
  
  const getEventsForDate = (date) => {
    return events.filter(event => 
      isSameDay(new Date(event.date), date)
    );
  };
  
  return (
    <div className="flex-1 bg-white">
      <div className="grid grid-cols-7 border-b border-gray-200">
        {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(day => (
          <div key={day} className="py-3 px-4 text-sm font-medium text-gray-500 text-center">
            {day}
          </div>
        ))}
      </div>
      
      <div className="grid grid-rows-6 flex-1">
        {weeks.map((week, weekIndex) => (
          <div key={weekIndex} className="grid grid-cols-7 border-b border-gray-200">
            {week.map(day => {
              const dayEvents = getEventsForDate(day);
              const isCurrentMonth = isSameMonth(day, currentDate);
              const isToday = isSameDay(day, new Date());
              
              return (
                <div
                  key={day.toISOString()}
                  className={`min-h-32 p-2 border-r border-gray-200 cursor-pointer hover:bg-gray-50 ${
                    !isCurrentMonth ? 'bg-gray-50 text-gray-400' : ''
                  }`}
                  onClick={() => onDateClick(day)}
                >
                  <div className={`text-sm font-medium mb-1 ${
                    isToday ? 'bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : ''
                  }`}>
                    {format(day, 'd')}
                  </div>
                  
                  <div className="space-y-1">
                    {dayEvents.slice(0, 3).map(event => (
                      <EventChip
                        key={event.id}
                        event={event}
                        onClick={() => onEventClick(event)}
                      />
                    ))}
                    {dayEvents.length > 3 && (
                      <div className="text-xs text-gray-500">
                        +{dayEvents.length - 3} mais
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### Visualização Semanal
**Componente:** `WeekView.jsx`
```jsx
const WeekView = ({ events, currentDate, onEventClick, onTimeSlotClick }) => {
  const weekStart = startOfWeek(currentDate);
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const timeSlots = Array.from({ length: 24 }, (_, i) => i);
  
  const getEventsForDateTime = (date, hour) => {
    return events.filter(event => {
      const eventDate = new Date(event.date);
      const eventHour = new Date(event.startTime).getHours();
      return isSameDay(eventDate, date) && eventHour === hour;
    });
  };
  
  return (
    <div className="flex-1 overflow-auto">
      <div className="grid grid-cols-8 border-b border-gray-200">
        <div className="p-4"></div>
        {weekDays.map(day => (
          <div key={day.toISOString()} className="p-4 text-center">
            <div className="text-sm font-medium text-gray-900">
              {format(day, 'EEE')}
            </div>
            <div className={`text-2xl font-bold mt-1 ${
              isSameDay(day, new Date()) ? 'text-blue-600' : 'text-gray-900'
            }`}>
              {format(day, 'd')}
            </div>
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-8">
        {timeSlots.map(hour => (
          <React.Fragment key={hour}>
            <div className="p-2 text-right text-sm text-gray-500 border-r border-gray-200">
              {format(new Date().setHours(hour, 0, 0, 0), 'HH:mm')}
            </div>
            {weekDays.map(day => {
              const slotEvents = getEventsForDateTime(day, hour);
              
              return (
                <div
                  key={`${day.toISOString()}-${hour}`}
                  className="min-h-16 p-1 border-r border-b border-gray-200 cursor-pointer hover:bg-gray-50"
                  onClick={() => onTimeSlotClick(day, hour)}
                >
                  {slotEvents.map(event => (
                    <EventBlock
                      key={event.id}
                      event={event}
                      onClick={() => onEventClick(event)}
                    />
                  ))}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
```

### FUNCIONALIDADES AVANÇADAS

#### Modal de Criação/Edição de Eventos
**Componente:** `EventModal.jsx`
```jsx
const EventModal = ({ event, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState(event || {
    title: '',
    description: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    startTime: '09:00',
    endTime: '10:00',
    location: '',
    attendees: [],
    reminder: '15',
    recurrence: 'none',
    category: 'meeting'
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSave(formData);
      onClose();
      toast.success(event ? 'Evento atualizado!' : 'Evento criado!');
    } catch (error) {
      toast.error('Erro ao salvar evento');
    }
  };
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            {event ? 'Editar Evento' : 'Novo Evento'}
          </h3>
        </div>
        
        <div className="space-y-4">
          <Input
            label="Título"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            required
          />
          
          <Textarea
            label="Descrição"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={3}
          />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <DatePicker
              label="Data"
              value={formData.date}
              onChange={(date) => setFormData({...formData, date})}
              required
            />
            
            <TimePicker
              label="Início"
              value={formData.startTime}
              onChange={(time) => setFormData({...formData, startTime: time})}
              required
            />
            
            <TimePicker
              label="Fim"
              value={formData.endTime}
              onChange={(time) => setFormData({...formData, endTime: time})}
              required
            />
          </div>
          
          <Input
            label="Local"
            value={formData.location}
            onChange={(e) => setFormData({...formData, location: e.target.value})}
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Categoria"
              value={formData.category}
              onChange={(value) => setFormData({...formData, category: value})}
              options={categoryOptions}
            />
            
            <Select
              label="Lembrete"
              value={formData.reminder}
              onChange={(value) => setFormData({...formData, reminder: value})}
              options={reminderOptions}
            />
          </div>
          
          <Select
            label="Recorrência"
            value={formData.recurrence}
            onChange={(value) => setFormData({...formData, recurrence: value})}
            options={recurrenceOptions}
          />
          
          <AttendeesSelector
            value={formData.attendees}
            onChange={(attendees) => setFormData({...formData, attendees})}
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit">
            {event ? 'Atualizar' : 'Criar'} Evento
          </Button>
        </div>
      </form>
    </Modal>
  );
};
```

---

## INTEGRAÇÃO ENTRE TELAS

### NAVEGAÇÃO CONTEXTUAL
Todas as telas terão navegação contextual inteligente:
- **Dashboard → Tarefas:** Clicar em tarefa prioritária abre tela de tarefas filtrada
- **Dashboard → Contatos:** Clicar em contato recente abre perfil do contato
- **Dashboard → Agenda:** Clicar em evento abre agenda no dia específico
- **Tarefas → Contatos:** Tarefas podem ser associadas a contatos
- **Agenda → Tarefas:** Eventos podem gerar tarefas automaticamente

### COMPONENTES COMPARTILHADOS
Componentes que serão reutilizados entre telas:
- **SearchBar:** Busca global inteligente
- **NotificationCenter:** Centro de notificações unificado
- **QuickActions:** Ações rápidas contextuais
- **DataSync:** Indicador de sincronização com Airtable
- **UserProfile:** Perfil e configurações do usuário

### ESTADO GLOBAL
Gerenciamento de estado compartilhado:
```jsx
const AppContext = createContext();

const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [syncStatus, setSyncStatus] = useState('connected');
  const [theme, setTheme] = useState('light');
  
  const value = {
    user, setUser,
    notifications, setNotifications,
    syncStatus, setSyncStatus,
    theme, setTheme
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
```

---

## CONSIDERAÇÕES TÉCNICAS

### PERFORMANCE
- **Lazy Loading:** Componentes carregados sob demanda
- **Virtual Scrolling:** Para listas grandes de dados
- **Memoização:** React.memo e useMemo para otimização
- **Code Splitting:** Divisão do bundle por rotas
- **Image Optimization:** Lazy loading e compressão de imagens

### ACESSIBILIDADE
- **Navegação por Teclado:** Todos os elementos acessíveis via teclado
- **Screen Readers:** Labels e descrições apropriadas
- **Contraste:** Mínimo 4.5:1 em todos os elementos
- **Focus Management:** Indicadores visuais claros
- **ARIA Labels:** Implementação completa de ARIA

### RESPONSIVIDADE
- **Mobile First:** Design começando pelo mobile
- **Breakpoints:** 320px, 768px, 1024px, 1280px, 1536px
- **Touch Targets:** Mínimo 44px para elementos tocáveis
- **Gestures:** Suporte a gestos em dispositivos móveis
- **Orientation:** Suporte a mudanças de orientação

---

**Próximos Passos:**
1. Implementar dashboard expandido
2. Desenvolver tela de tarefas completa
3. Criar tela de contatos com CRM básico
4. Implementar agenda com múltiplas visualizações
5. Integrar todas as telas com Airtable

**Status:** Especificações técnicas completas - Pronto para implementação

