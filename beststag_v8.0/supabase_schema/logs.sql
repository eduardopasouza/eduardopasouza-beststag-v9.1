-- Tabela de logs para registrar erros e eventos
CREATE TABLE IF NOT EXISTS public.logs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    origem text,
    mensagem text,
    data timestamp with time zone DEFAULT now()
);

-- Ativa RLS
ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;

-- Política de INSERT aberta para testes (MVP)
CREATE POLICY "Logs Insert" ON public.logs
    FOR INSERT WITH CHECK (true);
