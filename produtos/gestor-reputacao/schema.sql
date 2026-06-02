-- Agenty — Gestor de Reputação Multi-tenant
-- Rodar no SQL Editor do Supabase (Project → SQL Editor → New query)

CREATE TABLE IF NOT EXISTS clients (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Contato / dono
    name                    TEXT,
    email                   TEXT NOT NULL,

    -- Negócio
    business_name           TEXT,
    business_type           TEXT,
    business_city           TEXT DEFAULT 'Curitiba',
    tone                    TEXT DEFAULT 'proximo_descontraido',
    approval_email          TEXT,
    auto_reply_min_rating   INTEGER DEFAULT 4,

    -- Google Business Profile (preenchido no onboarding OAuth)
    google_refresh_token    TEXT,
    google_account_name     TEXT,   -- accounts/123456789
    google_location_name    TEXT,   -- accounts/123456789/locations/987654321

    -- Stripe
    stripe_customer_id      TEXT,
    stripe_subscription_id  TEXT,

    -- Onboarding
    onboarding_token        UUID UNIQUE DEFAULT gen_random_uuid(),
    status                  TEXT DEFAULT 'pending_onboarding',
    -- status: pending_onboarding | active | suspended

    created_at              TIMESTAMPTZ DEFAULT now(),
    activated_at            TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id           UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,

    review_id           TEXT NOT NULL,
    rating              INTEGER,
    author              TEXT,
    text                TEXT,
    created_at          TEXT,

    status              TEXT DEFAULT 'pending',
    -- status: pending | draft_sent | replied

    draft_response      TEXT,
    final_response      TEXT,
    approval_token      UUID UNIQUE,
    processed_at        TIMESTAMPTZ,

    UNIQUE (client_id, review_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_reviews_client_status ON reviews (client_id, status);
CREATE INDEX IF NOT EXISTS idx_reviews_approval_token ON reviews (approval_token);
CREATE INDEX IF NOT EXISTS idx_clients_onboarding_token ON clients (onboarding_token);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients (status);
