-- Initial schema source: src/models/*.py; metadata.create_all creates missing tables.
-- Raw batches and label-independent policy frozen per study; immutable run/review/report IDs.
-- sigma DOUBLE, permutation counts/seed INTEGER; calculations NumPy Float64.
-- Run attempts: distribution_runs is the per-study task identity; each retry
-- appends an immutable run_attempts row. attempt_no is the ownership token, so
-- a stale worker result can never publish over a newer attempt. Cancels are
-- cooperative for running attempts (cancel_requested_at) and immediate for queued.
-- shift_reviews/reports bind attempt_id+attempt_no so archived CSV stays stable.

CREATE TABLE IF NOT EXISTS run_attempts (
 id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL REFERENCES distribution_runs(id),
 study_id TEXT NOT NULL REFERENCES distribution_studies(id),
 attempt_no INTEGER NOT NULL,
 status TEXT NOT NULL,
 cancel_requested_at TEXT,
 cancel_reason TEXT,
 error TEXT NOT NULL DEFAULT '',
 result JSON NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL,
 started_at TEXT,
 finished_at TEXT,
 CONSTRAINT uq_run_attempts_run_no UNIQUE (run_id, attempt_no)
);
ALTER TABLE distribution_runs ADD COLUMN IF NOT EXISTS attempt_no INTEGER NOT NULL DEFAULT 0;
ALTER TABLE distribution_runs ADD COLUMN IF NOT EXISTS study_checksum TEXT;
ALTER TABLE distribution_runs ADD COLUMN IF NOT EXISTS updated_at TEXT;
ALTER TABLE shift_reviews ADD COLUMN IF NOT EXISTS attempt_id TEXT REFERENCES run_attempts(id);
ALTER TABLE shift_reviews ADD COLUMN IF NOT EXISTS attempt_no INTEGER;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS attempt_id TEXT REFERENCES run_attempts(id);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS attempt_no INTEGER;
-- A study may carry one run record; retries append attempts to that record
-- instead of writing a separate run row.
