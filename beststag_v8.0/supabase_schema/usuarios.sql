-- Script de criação da tabela de usuários
CREATE TABLE IF NOT EXISTS public.usuarios (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    nome text,
    telefone text,
    email text,
    created_at timestamp with time zone DEFAULT now()
);

-- Ativa RLS (Row Level Security)
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

-- Política de SELECT aberta para testes (MVP)
CREATE POLICY "Usuarios Select" ON public.usuarios
    FOR SELECT USING (true);

-- Política de INSERT aberta para testes (MVP)
CREATE POLICY "Usuarios Insert" ON public.usuarios
    FOR INSERT WITH CHECK (true);

-- Observação: em produção, restrinja as políticas conforme necessário
