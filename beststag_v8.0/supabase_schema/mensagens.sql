-- Tabela para armazenar mensagens do chat
CREATE TABLE IF NOT EXISTS public.mensagens (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.usuarios(id),
    telefone text,
    role text,
    content text,
    created_at timestamp with time zone DEFAULT now()
);

-- Habilita RLS
ALTER TABLE public.mensagens ENABLE ROW LEVEL SECURITY;

-- Permite SELECT de qualquer registro (apenas para teste)
CREATE POLICY "Mensagens Select" ON public.mensagens
    FOR SELECT USING (true);

-- Permite INSERT de qualquer registro (apenas para teste)
CREATE POLICY "Mensagens Insert" ON public.mensagens
    FOR INSERT WITH CHECK (true);

-- Em ambientes reais, refine as políticas de acordo com a necessidade
