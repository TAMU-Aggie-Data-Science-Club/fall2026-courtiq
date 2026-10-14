-- Local development foundation. This table contains fictional teaching data.
-- Application player/team/game schemas remain future reviewed work.
CREATE SCHEMA IF NOT EXISTS courtiq;

CREATE TABLE IF NOT EXISTS courtiq.player_season_stats (
    dataset_version text NOT NULL,
    source text NOT NULL CHECK (source = 'synthetic'),
    player_id text NOT NULL CHECK (player_id <> ''),
    player_name text NOT NULL CHECK (player_name <> ''),
    team_abbreviation text NOT NULL CHECK (team_abbreviation <> ''),
    season text NOT NULL CHECK (season <> ''),
    gp integer NOT NULL CHECK (gp >= 0),
    pts_total integer NOT NULL CHECK (pts_total >= 0),
    pts_per_game numeric NOT NULL CHECK (pts_per_game >= 0),
    reb_per_game numeric NOT NULL CHECK (reb_per_game >= 0),
    ast_per_game numeric NOT NULL CHECK (ast_per_game >= 0),
    PRIMARY KEY (dataset_version, season, player_id)
);
