-- raceGPS Crowdsourced World Building Schema
-- For Supabase (PostgreSQL + PostGIS)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Player Identity (anonymous by default)
-- ============================================
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_name TEXT NOT NULL DEFAULT 'Driver',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    total_distance_km FLOAT DEFAULT 0,
    contribution_score INT DEFAULT 0,
    avatar_color TEXT DEFAULT '#00FFFF'
);

-- ============================================
-- User-Created Routes (Community Courses)
-- ============================================
CREATE TABLE IF NOT EXISTS user_routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id TEXT UNIQUE NOT NULL, -- e.g. "user_akron_001"
    city_id TEXT NOT NULL DEFAULT 'akron-oh-beta-001',
    player_id UUID REFERENCES players(id),
    route_name TEXT NOT NULL,
    route_description TEXT,
    
    -- Route geometry (array of lat/lon waypoints as JSON)
    waypoints JSONB NOT NULL,
    checkpoints JSONB NOT NULL,
    
    -- Metadata
    distance_meters FLOAT,
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard', 'extreme')),
    vehicle_class TEXT,
    
    -- Stats
    best_time_seconds FLOAT,
    play_count INT DEFAULT 0,
    rating_avg FLOAT DEFAULT 0,
    rating_count INT DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    is_official BOOL DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for city-based route discovery
CREATE INDEX IF NOT EXISTS idx_user_routes_city ON user_routes(city_id);
CREATE INDEX IF NOT EXISTS idx_user_routes_status ON user_routes(status);
CREATE INDEX IF NOT EXISTS idx_user_routes_rating ON user_routes(rating_avg DESC);

-- ============================================
-- Route Ratings (Community Curation)
-- ============================================
CREATE TABLE IF NOT EXISTS route_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID REFERENCES user_routes(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(route_id, player_id)
);

-- ============================================
-- Building Annotations (Train Mode)
-- ============================================
CREATE TABLE IF NOT EXISTS building_annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_osm_id TEXT NOT NULL,
    city_id TEXT NOT NULL DEFAULT 'akron-oh-beta-001',
    player_id UUID REFERENCES players(id),
    
    -- What the player identified
    guessed_type TEXT NOT NULL,
    guessed_name TEXT,
    confidence INT CHECK (confidence BETWEEN 1 AND 5),
    
    -- Ground truth (filled in later by admin or consensus)
    verified_type TEXT,
    verified_name TEXT,
    is_verified BOOL DEFAULT FALSE,
    
    -- Consensus
    guess_count INT DEFAULT 1,
    consensus_type TEXT,
    
    -- Location
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_building_annotations_city ON building_annotations(city_id);
CREATE INDEX IF NOT EXISTS idx_building_annotations_osm ON building_annotations(building_osm_id);

-- ============================================
-- Route Feedback (Checkpoint Moves, Issues)
-- ============================================
CREATE TABLE IF NOT EXISTS route_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id TEXT NOT NULL,
    player_id UUID REFERENCES players(id),
    feedback_type TEXT CHECK (feedback_type IN ('checkpoint_move', 'turn_too_sharp', 'missing_road', 'wrong_speed', 'other')),
    
    -- For checkpoint moves
    checkpoint_index INT,
    suggested_lat FLOAT,
    suggested_lon FLOAT,
    
    -- General feedback
    description TEXT,
    screenshot_url TEXT,
    
    -- Status
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'accepted', 'rejected')),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Traffic Reports (Live Crowdsourced Data)
-- ============================================
CREATE TABLE IF NOT EXISTS traffic_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city_id TEXT NOT NULL DEFAULT 'akron-oh-beta-001',
    player_id UUID REFERENCES players(id),
    
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    
    traffic_density INT CHECK (traffic_density BETWEEN 0 AND 10),
    time_of_day TEXT, -- e.g. "17:00"
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traffic_reports_location ON traffic_reports(city_id, lat, lon);

-- ============================================
-- Contribution Log (Audit Trail)
-- ============================================
CREATE TABLE IF NOT EXISTS contribution_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(id),
    contribution_type TEXT CHECK (contribution_type IN ('route_created', 'route_rated', 'building_annotated', 'route_feedback', 'traffic_report', 'course_played')),
    target_id TEXT, -- UUID of the thing contributed to
    points_earned INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Citypack Versions (Track City Data Updates)
-- ============================================
CREATE TABLE IF NOT EXISTS citypack_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city_id TEXT UNIQUE NOT NULL,
    version TEXT NOT NULL,
    display_name TEXT NOT NULL,
    
    building_count INT,
    road_count INT,
    route_count INT,
    poi_count INT,
    
    download_url TEXT,
    min_game_version TEXT,
    max_game_version TEXT,
    
    released_at TIMESTAMPTZ DEFAULT NOW(),
    is_latest BOOL DEFAULT TRUE
);

-- ============================================
-- Functions
-- ============================================

-- Update route average rating when a new rating is added
CREATE OR REPLACE FUNCTION update_route_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_routes
    SET rating_avg = (
        SELECT AVG(rating)::FLOAT 
        FROM route_ratings 
        WHERE route_id = NEW.route_id
    ),
    rating_count = (
        SELECT COUNT(*) 
        FROM route_ratings 
        WHERE route_id = NEW.route_id
    )
    WHERE id = NEW.route_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_route_rating ON route_ratings;
CREATE TRIGGER trg_update_route_rating
AFTER INSERT OR UPDATE ON route_ratings
FOR EACH ROW
EXECUTE FUNCTION update_route_rating();

-- Update player contribution score
CREATE OR REPLACE FUNCTION update_player_score()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE players
    SET contribution_score = contribution_score + NEW.points_earned,
        last_seen_at = NOW()
    WHERE id = NEW.player_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_player_score ON contribution_log;
CREATE TRIGGER trg_update_player_score
AFTER INSERT ON contribution_log
FOR EACH ROW
EXECUTE FUNCTION update_player_score();

-- Update building annotation consensus
CREATE OR REPLACE FUNCTION update_building_consensus()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE building_annotations
    SET guess_count = guess_count + 1,
        consensus_type = (
            SELECT guessed_type
            FROM building_annotations
            WHERE building_osm_id = NEW.building_osm_id
            GROUP BY guessed_type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )
    WHERE building_osm_id = NEW.building_osm_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_consensus ON building_annotations;
CREATE TRIGGER trg_update_consensus
AFTER INSERT ON building_annotations
FOR EACH ROW
EXECUTE FUNCTION update_building_consensus();
