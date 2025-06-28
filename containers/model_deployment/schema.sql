CREATE TABLE IF NOT EXISTS model_deployment (
    id text PRIMARY KEY,
    model_name text NOT NULL,
    model_version text NOT NULL,
    port int NOT NULL,
    run_uuid text NOT NULL
)