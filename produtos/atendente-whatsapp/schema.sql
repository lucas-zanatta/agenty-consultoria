-- Agenty — Atendente WhatsApp Inteligente
-- Rodar no SQL Editor do Supabase ANTES de iniciar o app
-- Requer: extensão vector habilitada (pgvector)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS wa_clients (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    TEXT,
    email                   TEXT NOT NULL,

    -- Credenciais Meta (preenchidas por Lucas após setup do Meta App)
    phone_number_id         TEXT,
    waba_id                 TEXT,
    access_token            TEXT,

    -- Questionário do negócio (compilado em system prompt)
    biz_name                TEXT,
    biz_type                TEXT,
    biz_city                TEXT DEFAULT 'Curitiba',
    biz_services            TEXT,
    biz_prices              TEXT,
    biz_address             TEXT,
    biz_payment_methods     TEXT,
    biz_cancellation        TEXT,
    biz_differentials       TEXT,
    biz_extra               TEXT,

    -- Operação
    business_hours_start    INTEGER DEFAULT 8,
    business_hours_end      INTEGER DEFAULT 18,
    timezone                TEXT DEFAULT 'America/Sao_Paulo',
    out_of_hours_message    TEXT,

    -- Escalada para humano
    handover_keywords       TEXT[] DEFAULT ARRAY['atendente','humano','pessoa','falar com'],
    handover_phone          TEXT,
    max_auto_messages       INTEGER DEFAULT 10,

    -- Cal.com (agendamento)
    cal_api_key             TEXT,
    cal_event_type_id       TEXT,

    -- Stripe
    stripe_customer_id      TEXT,
    stripe_subscription_id  TEXT,

    -- Onboarding
    onboarding_token        UUID UNIQUE DEFAULT gen_random_uuid(),
    status                  TEXT DEFAULT 'pending_onboarding',
    -- status: pending_onboarding | pending_meta_setup | active | suspended

    created_at              TIMESTAMPTZ DEFAULT now(),
    activated_at            TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS wa_conversations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id           UUID NOT NULL REFERENCES wa_clients(id) ON DELETE CASCADE,
    customer_phone      TEXT NOT NULL,
    customer_name       TEXT,
    status              TEXT DEFAULT 'active',
    -- status: active | handed_over | closed
    message_count       INTEGER DEFAULT 0,
    lead_captured       BOOLEAN DEFAULT false,
    lead_data           JSONB,
    started_at          TIMESTAMPTZ DEFAULT now(),
    last_message_at     TIMESTAMPTZ,
    UNIQUE (client_id, customer_phone)
);

CREATE TABLE IF NOT EXISTS wa_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES wa_conversations(id) ON DELETE CASCADE,
    role                TEXT NOT NULL,
    content             TEXT NOT NULL,
    wa_message_id       TEXT UNIQUE,
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wa_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id           UUID NOT NULL REFERENCES wa_clients(id) ON DELETE CASCADE,
    filename            TEXT NOT NULL,
    storage_path        TEXT,
    chunk_index         INTEGER NOT NULL,
    content             TEXT NOT NULL,
    embedding           vector(1024),
    created_at          TIMESTAMPTZ DEFAULT now()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_wa_conversations_client ON wa_conversations (client_id, status);
CREATE INDEX IF NOT EXISTS idx_wa_messages_conversation ON wa_messages (conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_wa_clients_phone_number ON wa_clients (phone_number_id);
CREATE INDEX IF NOT EXISTS idx_wa_clients_onboarding ON wa_clients (onboarding_token);
CREATE INDEX IF NOT EXISTS idx_wa_documents_client ON wa_documents (client_id);
CREATE INDEX IF NOT EXISTS wa_documents_embedding_idx
    ON wa_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Função de similarity search para RAG
CREATE OR REPLACE FUNCTION match_wa_documents(
    p_client_id       UUID,
    query_embedding   vector(1024),
    match_count       INT DEFAULT 3
)
RETURNS TABLE (content TEXT, similarity FLOAT)
LANGUAGE sql
AS $$
    SELECT content, 1 - (embedding <=> query_embedding) AS similarity
    FROM wa_documents
    WHERE client_id = p_client_id
      AND embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
