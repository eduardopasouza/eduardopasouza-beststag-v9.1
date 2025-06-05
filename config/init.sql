
-- BestStag v9.1 - Inicialização do Banco de Dados
-- Script executado automaticamente na criação do container PostgreSQL

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Criar schema principal
CREATE SCHEMA IF NOT EXISTS beststag;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS beststag.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Tabela de sessões/conversas
CREATE TABLE IF NOT EXISTS beststag.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES beststag.users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL, -- whatsapp, telegram, web, etc
    channel_user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    context JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de mensagens
CREATE TABLE IF NOT EXISTS beststag.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES beststag.conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    processing_time FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de memória contextual
CREATE TABLE IF NOT EXISTS beststag.contextual_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES beststag.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES beststag.conversations(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL, -- preference, fact, pattern, etc
    key VARCHAR(255) NOT NULL,
    value JSONB NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source VARCHAR(100),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios inteligentes
CREATE TABLE IF NOT EXISTS beststag.intelligent_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES beststag.users(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de análise de sentimentos
CREATE TABLE IF NOT EXISTS beststag.sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES beststag.messages(id) ON DELETE CASCADE,
    sentiment VARCHAR(20) NOT NULL, -- positive, negative, neutral
    confidence FLOAT NOT NULL,
    emotions JSONB DEFAULT '{}',
    analysis_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de integrações
CREATE TABLE IF NOT EXISTS beststag.integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES beststag.users(id) ON DELETE CASCADE,
    integration_type VARCHAR(100) NOT NULL, -- abacus, n8n, whatsapp, etc
    name VARCHAR(255) NOT NULL,
    config JSONB NOT NULL,
    credentials JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de sistema
CREATE TABLE IF NOT EXISTS beststag.system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    logger VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    user_id UUID REFERENCES beststag.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON beststag.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_channel ON beststag.conversations(channel);
CREATE INDEX IF NOT EXISTS idx_conversations_active ON beststag.conversations(is_active);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON beststag.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON beststag.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_role ON beststag.messages(role);

CREATE INDEX IF NOT EXISTS idx_contextual_memory_user_id ON beststag.contextual_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_contextual_memory_type ON beststag.contextual_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_contextual_memory_key ON beststag.contextual_memory(key);

CREATE INDEX IF NOT EXISTS idx_sentiment_message_id ON beststag.sentiment_analysis(message_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_sentiment ON beststag.sentiment_analysis(sentiment);

CREATE INDEX IF NOT EXISTS idx_system_logs_level ON beststag.system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON beststag.system_logs(created_at);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON beststag.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON beststag.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contextual_memory_updated_at BEFORE UPDATE ON beststag.contextual_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON beststag.integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir usuário admin padrão (senha: admin123)
INSERT INTO beststag.users (username, email, password_hash, full_name, is_admin)
VALUES (
    'admin',
    'admin@beststag.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', -- admin123
    'Administrador BestStag',
    true
) ON CONFLICT (username) DO NOTHING;

-- Inserir usuário de teste
INSERT INTO beststag.users (username, email, password_hash, full_name)
VALUES (
    'testuser',
    'test@beststag.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', -- admin123
    'Usuário de Teste'
) ON CONFLICT (username) DO NOTHING;

-- Configurações iniciais
CREATE TABLE IF NOT EXISTS beststag.system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserir configurações padrão
INSERT INTO beststag.system_config (key, value, description) VALUES
('app_version', '"9.1.0"', 'Versão atual da aplicação'),
('max_conversation_history', '100', 'Máximo de mensagens por conversa'),
('default_ai_model', '"gpt-3.5-turbo"', 'Modelo de IA padrão'),
('sentiment_analysis_enabled', 'true', 'Análise de sentimentos habilitada'),
('contextual_memory_enabled', 'true', 'Memória contextual habilitada'),
('max_tokens_per_request', '4000', 'Máximo de tokens por requisição')
ON CONFLICT (key) DO NOTHING;

-- Comentários nas tabelas
COMMENT ON TABLE beststag.users IS 'Usuários do sistema BestStag';
COMMENT ON TABLE beststag.conversations IS 'Conversas/sessões dos usuários';
COMMENT ON TABLE beststag.messages IS 'Mensagens das conversas';
COMMENT ON TABLE beststag.contextual_memory IS 'Memória contextual do assistente';
COMMENT ON TABLE beststag.intelligent_reports IS 'Relatórios inteligentes gerados';
COMMENT ON TABLE beststag.sentiment_analysis IS 'Análises de sentimento das mensagens';
COMMENT ON TABLE beststag.integrations IS 'Configurações de integrações externas';
COMMENT ON TABLE beststag.system_logs IS 'Logs do sistema';
COMMENT ON TABLE beststag.system_config IS 'Configurações do sistema';
