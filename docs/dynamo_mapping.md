# DynamoDB mapping for the relational schema

This document describes an opinionated single-table design for your relational schema so it maps efficiently to DynamoDB.

Core idea: store all domain entities in a single table with `PK` and `SK`, plus a few index attributes used by GSIs.

Item types: languages, topics, levels, level_translations, exercises, exercise_translations, exercise_types, assets, exercise_assets, models, users, user_progress, leaderboards.

Base attributes per item:
- PK: string (e.g. TOPIC#<topic_id>)
- SK: string (e.g. METADATA or LEVEL#<level_id> or EXERCISE#<exercise_id>)
- entity_type: string (e.g. "topic", "level", "exercise")
- created_at: ISO8601 timestamp

Suggested key patterns
- Topic metadata:
  - PK = "TOPIC#<topic_id>", SK = "METADATA"
  - entity_type = "topic", topic_id = <topic_id>

- Level metadata:
  - PK = "LEVEL#<level_id>", SK = "METADATA"
  - entity_type = "level", topic_id = <topic_id>, position, difficulty, published

- Level translations (one item per language):
  - PK = "LEVEL#<level_id>", SK = "TRANS#<language_code>"
  - entity_type = "level_translation", language = "pt_BR"

- Exercise metadata:
  - PK = "EXERCISE#<exercise_id>", SK = "METADATA"
  - entity_type = "exercise", level_id = <level_id>

- Exercise translations:
  - PK = "EXERCISE#<exercise_id>", SK = "TRANS#<language_code>"

- Assets:
  - PK = "ASSET#<asset_id>", SK = "METADATA"
  - store S3 key, mime_type, size, locale_id, version

Queries & GSIs
- GSI1 (gsi1-entity-type-created-at): partition on `entity_type`, sort on `created_at` — list all topics/levels/exercises by recency.
- GSI2 (gsi2-topic-sortkey): partition on `topic_id`, sort on `SK` — list levels/exercises within a topic.

Notes on modeling decisions
- Use JSON attributes for translatable fields (title, description) if you prefer one record per level containing translations; alternatively keep translations as separate items for efficient per-language reads.
- Avoid large items; keep exercise assets references (keys) rather than embedding heavy binary data.
- For leaderboards or counters use separate items keyed by scope (e.g. PK = "LEADERBOARD#TOPIC#<topic_id>", SK = "SCORE#<timestamp>#<user_id>") and consider DynamoDB streams for analytics.

Security & performance
- Use IAM roles with least-privilege: Lambda gets access only to the specific table and S3 bucket.
- Use on-demand billing (PAY_PER_REQUEST) for initial simplicity; move to provisioned + autoscaling if you need predictable cost/performance tradeoffs.
