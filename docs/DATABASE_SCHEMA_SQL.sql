-- ============================================
-- Aplicación Señas - PostgreSQL Schema
-- ============================================
-- Alternative SQL schema if you prefer RDS
-- over DynamoDB
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. LANGUAGES (Idiomas)
-- ============================================

CREATE TABLE languages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,  -- 'pt_BR', 'en_US', 'es_ES'
    name VARCHAR(100) NOT NULL,        -- 'Português (Brasil)'
    native_name VARCHAR(100),          -- 'Português'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_languages_code ON languages(code);
CREATE INDEX idx_languages_active ON languages(is_active) WHERE is_active = true;

-- ============================================
-- 2. TOPICS (Temas)
-- ============================================

CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    default_title VARCHAR(200) NOT NULL,
    icon_url TEXT,
    "order" INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_topics_slug ON topics(slug);
CREATE INDEX idx_topics_order ON topics("order") WHERE is_published = true;

-- Topic translations
CREATE TABLE topic_translations (
    id SERIAL PRIMARY KEY,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    language_id INTEGER NOT NULL REFERENCES languages(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    UNIQUE(topic_id, language_id)
);

CREATE INDEX idx_topic_trans_topic ON topic_translations(topic_id);
CREATE INDEX idx_topic_trans_lang ON topic_translations(language_id);

-- ============================================
-- 3. LEVELS (Níveis)
-- ============================================

CREATE TABLE levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    slug VARCHAR(100) NOT NULL,
    position INTEGER NOT NULL,
    difficulty INTEGER DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    metadata JSONB,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(topic_id, slug),
    UNIQUE(topic_id, position)
);

CREATE INDEX idx_levels_topic ON levels(topic_id, position);
CREATE INDEX idx_levels_published ON levels(is_published) WHERE is_published = true;
CREATE INDEX idx_levels_metadata ON levels USING gin(metadata);

-- Level translations
CREATE TABLE level_translations (
    id SERIAL PRIMARY KEY,
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    language_id INTEGER NOT NULL REFERENCES languages(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    hint TEXT,
    success_message TEXT,
    UNIQUE(level_id, language_id)
);

CREATE INDEX idx_level_trans_level ON level_translations(level_id);
CREATE INDEX idx_level_trans_lang ON level_translations(language_id);

-- ============================================
-- 4. EXERCISE TYPES (Tipos de Ejercicio)
-- ============================================

CREATE TABLE exercise_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,  -- 'MCQ', 'CAMERA_PRODUCE', etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    requires_camera BOOLEAN DEFAULT false,
    requires_model BOOLEAN DEFAULT false,
    config_schema JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exercise_types_code ON exercise_types(code);

-- Insert common exercise types
INSERT INTO exercise_types (code, name, description, requires_camera, requires_model, config_schema) VALUES
('MCQ', 'Multiple Choice Question', 'Choose the correct answer from options', false, false, 
 '{"time_limit": "number", "choices_count": "number", "randomize_choices": "boolean"}'),
('CAMERA_PRODUCE', 'Camera Production', 'Record sign with camera', true, true,
 '{"time_limit": "number", "min_confidence": "number", "model_version": "string"}'),
('CAMERA_RECOGNIZE', 'Camera Recognition', 'Show sign and let AI recognize', true, true,
 '{"time_limit": "number", "min_confidence": "number"}'),
('COPY_PRACTICE', 'Copy Practice', 'Watch video and repeat', true, false,
 '{"time_limit": "number", "allow_replay": "boolean"}'),
('MATCH_PAIRS', 'Match Pairs', 'Match signs with meanings', false, false,
 '{"pairs_count": "number", "time_limit": "number"}'),
('FILL_BLANK', 'Fill the Blank', 'Complete sentences', false, false,
 '{"time_limit": "number"}');

-- ============================================
-- 5. EXERCISES (Ejercicios)
-- ============================================

CREATE TABLE exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    exercise_type_id INTEGER NOT NULL REFERENCES exercise_types(id),
    position INTEGER NOT NULL,
    config JSONB,           -- time_limit, scoring rules, choices_count
    answer_schema JSONB,    -- correct answer structure
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(level_id, position)
);

CREATE INDEX idx_exercises_level ON exercises(level_id, position);
CREATE INDEX idx_exercises_type ON exercises(exercise_type_id);
CREATE INDEX idx_exercises_config ON exercises USING gin(config);

-- Exercise translations
CREATE TABLE exercise_translations (
    id SERIAL PRIMARY KEY,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    language_id INTEGER NOT NULL REFERENCES languages(id),
    prompt_text TEXT,
    choice_texts JSONB,     -- Array of choice strings
    feedback JSONB,         -- {"correct": "...", "incorrect": "..."}
    UNIQUE(exercise_id, language_id)
);

CREATE INDEX idx_exercise_trans_exercise ON exercise_translations(exercise_id);
CREATE INDEX idx_exercise_trans_lang ON exercise_translations(language_id);

-- ============================================
-- 6. ASSETS (Multimedia)
-- ============================================

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    s3_key TEXT UNIQUE NOT NULL,        -- 'levels/pt_BR/alphabet/level1/example.mp4'
    s3_bucket VARCHAR(100),              -- bucket name
    mime_type VARCHAR(100) NOT NULL,     -- 'video/mp4', 'image/jpeg'
    size_bytes BIGINT,
    duration_seconds DECIMAL(10,2),      -- for video/audio
    metadata JSONB,                      -- width, height, fps, thumbnails
    language_id INTEGER REFERENCES languages(id),  -- if asset is language-specific
    version INTEGER DEFAULT 1,
    checksum VARCHAR(100),               -- SHA-256 hash
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_assets_key ON assets(s3_key);
CREATE INDEX idx_assets_lang ON assets(language_id);
CREATE INDEX idx_assets_metadata ON assets USING gin(metadata);

-- ============================================
-- 7. EXERCISE ASSETS (Many-to-Many)
-- ============================================

CREATE TABLE exercise_assets (
    id SERIAL PRIMARY KEY,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'prompt_video', 'answer_video', 'thumbnail', 'hint_video'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(exercise_id, asset_id, role)
);

CREATE INDEX idx_exercise_assets_exercise ON exercise_assets(exercise_id);
CREATE INDEX idx_exercise_assets_asset ON exercise_assets(asset_id);
CREATE INDEX idx_exercise_assets_role ON exercise_assets(role);

-- ============================================
-- 8. ML MODELS (TensorFlow Lite)
-- ============================================

CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    language_id INTEGER REFERENCES languages(id),  -- if model is language-specific
    asset_id UUID REFERENCES assets(id),           -- TFLite file in S3
    checksum VARCHAR(100) NOT NULL,
    size_bytes BIGINT,
    metadata JSONB,           -- input_shape, output_classes, accuracy
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, version)
);

CREATE INDEX idx_models_name ON models(name, version);
CREATE INDEX idx_models_active ON models(is_active) WHERE is_active = true;
CREATE INDEX idx_models_lang ON models(language_id);

-- ============================================
-- 9. USERS (Usuarios)
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200),
    password_hash TEXT,          -- if using email/password auth
    preferred_language_id INTEGER REFERENCES languages(id),
    profile_image_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_active_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_xp ON users(total_xp DESC);
CREATE INDEX idx_users_level ON users(level DESC);

-- ============================================
-- 10. USER PROGRESS (Progreso)
-- ============================================

CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    level_id UUID NOT NULL REFERENCES levels(id),  -- denormalized for easy queries
    status VARCHAR(20) NOT NULL CHECK (status IN ('not_started', 'in_progress', 'completed', 'failed')),
    score INTEGER DEFAULT 0,
    max_score INTEGER DEFAULT 100,
    attempts INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP,
    data JSONB,  -- detailed attempt data, answers, stars, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, exercise_id)
);

CREATE INDEX idx_progress_user ON user_progress(user_id, level_id);
CREATE INDEX idx_progress_exercise ON user_progress(exercise_id);
CREATE INDEX idx_progress_status ON user_progress(status);
CREATE INDEX idx_progress_updated ON user_progress(user_id, updated_at DESC);

-- ============================================
-- 11. LEVEL SUMMARIES (Agregado de progreso)
-- ============================================

CREATE TABLE level_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('not_started', 'in_progress', 'completed', 'failed')),
    total_exercises INTEGER DEFAULT 0,
    completed_exercises INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    stars_earned INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    first_attempt_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, level_id)
);

CREATE INDEX idx_summaries_user ON level_summaries(user_id);
CREATE INDEX idx_summaries_level ON level_summaries(level_id);
CREATE INDEX idx_summaries_status ON level_summaries(status);

-- ============================================
-- 12. LEADERBOARDS (Clasificación)
-- ============================================

CREATE TABLE leaderboards (
    id SERIAL PRIMARY KEY,
    scope VARCHAR(50) NOT NULL,      -- 'global', 'topic', 'country', 'friends'
    scope_id VARCHAR(100),            -- topic_id, country_code, user_id
    period VARCHAR(20) NOT NULL,      -- '2025-W45', '2025-11', 'all-time'
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    rank INTEGER,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(scope, scope_id, period, user_id)
);

CREATE INDEX idx_leaderboards_scope ON leaderboards(scope, scope_id, period, score DESC);
CREATE INDEX idx_leaderboards_user ON leaderboards(user_id);
CREATE INDEX idx_leaderboards_rank ON leaderboards(scope, scope_id, period, rank);

-- ============================================
-- TRIGGERS & FUNCTIONS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_levels_updated_at BEFORE UPDATE ON levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_updated_at BEFORE UPDATE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS (for easier queries)
-- ============================================

-- View: Topics with translations
CREATE VIEW topics_with_translations AS
SELECT 
    t.id,
    t.slug,
    t.default_title,
    t."order",
    t.is_published,
    json_agg(
        json_build_object(
            'language_code', l.code,
            'title', tt.title,
            'description', tt.description
        )
    ) as translations
FROM topics t
LEFT JOIN topic_translations tt ON t.id = tt.topic_id
LEFT JOIN languages l ON tt.language_id = l.id
GROUP BY t.id, t.slug, t.default_title, t."order", t.is_published;

-- View: Levels with translations
CREATE VIEW levels_with_translations AS
SELECT 
    lv.id,
    lv.topic_id,
    lv.slug,
    lv.position,
    lv.difficulty,
    lv.is_published,
    json_agg(
        json_build_object(
            'language_code', l.code,
            'title', lt.title,
            'description', lt.description,
            'hint', lt.hint
        )
    ) as translations
FROM levels lv
LEFT JOIN level_translations lt ON lv.id = lt.level_id
LEFT JOIN languages l ON lt.language_id = l.id
GROUP BY lv.id, lv.topic_id, lv.slug, lv.position, lv.difficulty, lv.is_published;

-- View: User progress summary
CREATE VIEW user_progress_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.total_xp,
    u.level,
    COUNT(DISTINCT up.level_id) as levels_started,
    COUNT(DISTINCT CASE WHEN up.status = 'completed' THEN up.level_id END) as levels_completed,
    COUNT(DISTINCT up.exercise_id) as exercises_attempted,
    COUNT(DISTINCT CASE WHEN up.status = 'completed' THEN up.exercise_id END) as exercises_completed,
    AVG(up.score) as average_score
FROM users u
LEFT JOIN user_progress up ON u.id = up.user_id
GROUP BY u.id, u.name, u.total_xp, u.level;

-- ============================================
-- SEED DATA
-- ============================================

-- Insert default languages
INSERT INTO languages (code, name, native_name) VALUES
('pt_BR', 'Portuguese (Brazil)', 'Português'),
('en_US', 'English (US)', 'English'),
('es_ES', 'Spanish (Spain)', 'Español');

-- Sample topic
INSERT INTO topics (slug, default_title, "order", is_published) VALUES
('alphabet', 'Alphabet', 1, true);

-- Sample level
INSERT INTO levels (topic_id, slug, position, difficulty, is_published)
SELECT id, 'alphabet-1', 1, 1, true FROM topics WHERE slug = 'alphabet';

COMMIT;
