# Plan: Update unified database with new daily event CSVs and summary sources

Generated: 2025-08-18 15:16 (-06)

## Objective
Integrate three new daily email event CSVs and enrich with SLA/hourly unread and optional daily summaries to expand `email_database.json` without changing dashboard code.

Sources:
- Email events (new): `data/08-14-25.csv`, `data/08-15-25.csv`, `data/08-16-25.csv`
- SLA hourly unread: `data/UnreadCount.csv`
- Optional daily rollups for validation/fallback: `data/DailySummary.csv`

Consumers:
- Unified DB: `email_database.json`
- Dashboard generator: `dashboard/scripts/generate_dashboard.py`

## Current grounding
- `documentation/architecture.md` describes a unified JSON with per-day entries and 24-hr `hourly_data` items.
- `daily/scripts/email_classifier.py` currently:
  - Processes events from `data/Complete_List_Raw.csv` (Aug 13) only.
  - Loads SLA from `data/UnreadCount.csv` and merges per-day.
  - Hardcodes single email day handling (`email_date_str = "2025-08-13"`).
- `dashboard/scripts/generate_dashboard.py` already supports any day present in JSON and selects the latest complete day (has both email + SLA).

## Desired end state
- `email_database.json` contains new days for 2025-08-14, 2025-08-15, 2025-08-16 with:
  - has_email_data = true (from per-day event CSVs)
  - has_sla_data = true if UnreadCount has those dates/hours
  - `daily_summary` filled from computed metrics; optionally cross-checked with `DailySummary.csv`
  - `hourly_data[0..23]` merged:
    - `emails_received`, `emails_replied`, `avg_response_time` from event analysis
    - `unread_count`, `sla_met` from SLA file
- JSON metadata updated with new totals and sources list including the three dated CSVs (and DailySummary if used).

## Field mapping
- Event CSVs (08-14/15/16 and `Complete_List_Raw.csv`):
  - Conversation-Id → conversation grouping for matching replies/completions
  - EventType → {Inbox, Replied, Completed}
  - TimeStamp → parse to datetime (naive), derive date (YYYY-MM-DD) and `Hour`
  - Emails, MessageId, Subject → kept for traceability; not all emitted to JSON
- UnreadCount.csv:
  - Date → day key (YYYY-MM-DD)
  - Hour of the Day → hour index (int 0–23)
  - TotalUnread → `unread_count`
  - Title == "SLA MET" → `sla_met` true else false
- DailySummary.csv (optional)
  - InboxTotal → daily_summary.total_emails (fallback only)
  - CompletedTotal → daily completions (cross-check)
  - AvgResponseInMinutes → daily_summary.avg_response_time_minutes (fallback only)
  - Within SLA (string like "22%") → record as `external_within_sla_reported` for reference; do not override computed SLA
  - Average Unread → cross-check vs SLA-derived average

## Implementation plan (code-level changes in `daily/scripts/email_classifier.py`)
1. Ingestion: support multiple event CSVs
   - New argument or config: list/glob of event CSV paths, defaulting to existing `Complete_List_Raw.csv`.
   - Implement `load_event_data(paths: List[str]) -> DataFrame` that concatenates, enforces dtypes, and deduplicates rows.
2. Classification unchanged
   - Reuse `process_conversations()` to produce per-email results with `Inbox_TimeStamp` and `Response_Time_Business_Minutes`.
3. Per-day analytics
   - Replace current single-day `analyze_hourly_distribution()` and `analyze_response_time_by_hour()` with per-day outputs:
     - `analyze_hourly_distribution_by_day(results_df) -> Dict[date_str, DataFrame]`
     - `analyze_response_time_by_hour_by_day(results_df) -> Dict[date_str, DataFrame]`
   - Group by `Inbox_TimeStamp.dt.date`. For each day, compute 0–23 distribution table and response-time-by-hour table (weighted averages, medians, counts).
4. SLA merge per day (already supported)
   - Use existing `load_sla_data()` and `process_sla_hourly_data(date)` per day when building JSON day entries.
5. Save to unified JSON (generalize from single day → N days)
   - Iterate `all_days = union(SLA days, event days)`.
   - For each `date_str`:
     - Start with 24 `hourly_data` entries (0–23) with nulls.
     - If SLA day exists: fill `unread_count` and `sla_met`.
     - If event day exists: fill `emails_received`, `emails_replied`, `avg_response_time` from per-day hourly tables.
     - Compute `daily_summary`:
       - From classification summary for that day (totals, reply/completion %, avg/median response times within business hours).
       - Fallbacks from `DailySummary.csv` only if event-derived values missing.
     - Set flags `has_email_data`, `has_sla_data`.
   - Update top-level `metadata` (last_updated, total_days_processed, earliest/latest date, data_sources).
6. Idempotency & safety
   - Deduplicate conversations across files by `(Conversation-Id, EventType, MessageId, TimeStamp)`.
   - Do not mutate source CSVs. Always re-generate JSON from inputs for reproducibility.
7. Config alignment
   - Ensure business hours and days come from `config/sla_config.json` and are used consistently for response time calculations and 2-hour aggregation downstream.
8. Optional: incorporate `DailySummary.csv`
   - Load into a dict keyed by date; attach `external_daily_summary` block to each day for traceability (optional).

## Validation & acceptance criteria
- JSON contains keys: `days["2025-08-14"]`, `days["2025-08-15"]`, `days["2025-08-16"]`.
- For each of the three days:
  - `hourly_data` has 24 entries (0–23).
  - Business-hours entries (from SLA config, default 7–21) populated with SLA fields when available.
  - Email fields populated where events exist; hours with no activity show zeros/nulls appropriately.
  - `daily_summary.total_emails` equals count of Inbox events for that day (or matches `DailySummary.InboxTotal` if used as fallback).
  - `has_email_data == True`; `has_sla_data == True` when UnreadCount has entries for that date.
- `metadata.data_sources` lists: `UnreadCount.csv`, `Complete_List_Raw.csv`, `08-14-25.csv`, `08-15-25.csv`, `08-16-25.csv` (and `DailySummary.csv` if referenced).
- Dashboard generation picks the latest complete day automatically and renders without code changes.

## Risks & considerations
- Per-day event CSVs may contain only Inbox events; replies/completions could be sparse → metrics degrade gracefully; pending share will rise.
- Timezones are not encoded; treat timestamps as local; business-hours calculator remains consistent with config.
- `DailySummary.csv` may not always align with computed metrics; treat as reference/fallback to avoid conflicting sources.
- Performance: concatenating a few daily files is trivial; no special optimization needed.

---

# TODO checklist (for approval)

- [x] Update classifier to accept multiple event CSV inputs (CLI arg or config) and implement `load_event_data()`
- [x] Generalize hourly analyses to return per-day results (`analyze_*_by_day`)
- [x] Refactor `save_to_unified_json()` to iterate all days and merge SLA + events per day
- [x] Ensure deduplication across files and idempotent re-generation of `email_database.json`
- [x] Extend `metadata.data_sources` and update earliest/latest dates and totals
- [x] Validate three new days (Aug 14–16): counts, flags, hourly merges, summaries
- [x] Regenerate dashboard and verify latest complete day selection and charts
- [ ] Update `documentation/architecture.md` stats and examples to reflect new range/days

If this plan looks good, I’ll implement in small, reviewable commits starting with ingestion + per-day save, then validation and docs.
