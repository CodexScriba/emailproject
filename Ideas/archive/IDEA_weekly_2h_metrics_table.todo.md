# Weekly 2‑Hour Email Metrics Table — Todo

Source: `Ideas/IDEA_weekly_2h_metrics_table.md`

## User Stories
- As a dashboard viewer, I want a weekly 2‑hour table so I can compare activity across time blocks at a glance.
- As an operations lead, I want an Avg Unread column so I can gauge backlog pressure across the week.
- As a manager, I want response‑time badges and microbars so I can quickly identify blocks that meet or miss targets.
- As an analyst, I want clear tooltips and labeling so I understand aggregation scope and any partial‑week caveats.

## Phase 1: Foundation
- [ ] Create a Jinja2 template for the weekly 2‑hour table that mirrors styles from `daily/dashboard/templates/kpi_cards.html` (reuse `.a-table`, `.a-row`, `.a-cell`, `.badge`, `.microbar`).
- [ ] Add table header with columns: Block, Emails, Avg Unread, Avg Response, Median Time.
- [ ] Add table body loop over `two_hour_metrics_week` with placeholder values to verify structure.
- [ ] Ensure microbar DOM structure exists (`.microbar > .fill[data-width]`) to interoperate with existing width‑application JS.
- [ ] Add a subtitle area to display `business_hours_label` and `data_days_count` context.

## Phase 2: Core Functionality
- [ ] Implement data aggregation that produces the context contract:
  - `two_hour_metrics_week` (list of dicts with: `label`, `start_hour`, `emails`, `avg_unread`, `avg_response_time`, `median_response_time`, optional `color`).
  - `two_hour_max_emails_week` (int), `unread_threshold` (int | null), `response_time_target` (int | null), `business_hours_label` (string), `data_days_count` (int).
- [ ] Emails: compute weekly sum per 2‑hour block across all included days/hours.
- [ ] Avg Unread: mean across per‑hour snapshots for the block across all days (fallback: mean of per‑day block averages). Use one decimal when present; `N/A` if no inputs.
- [ ] Avg Response Time: preferred average over per‑email durations; fallback to mean of per‑day block averages weighted by email counts (or simple mean if counts missing).
- [ ] Median Response Time: preferred median of per‑email durations; fallback to median of per‑day block medians.
- [ ] Compute `two_hour_max_emails_week` for microbar scaling and clamp widths to 0–100.
- [ ] Map `avg_response_time` to badge categories: <30 ⚡, <60 🚀, <120 ⏱️, <180 🐢, <300 ⚠️, else 🔴; style success/warning/danger accordingly.
- [ ] Avg Unread coloring: success if `avg_unread <= unread_threshold`, danger otherwise; neutral if threshold missing.
- [ ] Render microbars:
  - Emails width: `(emails / (two_hour_max_emails_week or 1) * 100)`.
  - Avg Unread width: `((avg_unread or 0) / (unread_threshold or 1) * 100)`; optionally cap at 150% to visualize overage while clamping CSS width to 100%.
  - Avg Response width: `((avg_response_time or 0) / (response_time_target or 60) * 100)`.

## Phase 3: Enhanced Features & Polish
- [ ] Show daypart label and icon in Block cell based on `start_hour` (e.g., 🌅 Early Morning, ☀️ Morning, 🌤️ Afternoon, 🌆 Evening) matching the daily view.
- [ ] Add tooltips per row showing: label, Emails, Avg Unread (or N/A), Avg Response (or N/A) in minutes, Median (or N/A) in minutes.
- [ ] Subtitle: "Aggregated across {{ business_hours_label }} ({{ data_days_count }} day(s))" with correct pluralization.
- [ ] Handle missing values gracefully: show `—` for nulls; avoid division by zero in width calculations; clamp widths to 0–100.
- [ ] Ensure responsive layout and visual parity with the daily 2‑hour table (spacing, typography, badge styles, microbars).
- [ ] Verify the page includes or inherits the JS that applies widths from `data-width` attributes to `.microbar .fill` elements.

## Phase 4: Testing & Optimization
- [ ] Unit tests for aggregation logic: correct weekly sums, correct means/medians, fallbacks when per‑email data is missing, and edge cases (no data, partial weeks).
- [ ] Tests for badge mapping thresholds and unread coloring against `unread_threshold`.
- [ ] Template rendering tests (e.g., snapshot or DOM checks) to verify headers, tooltips, and data‑width attributes are present and correctly computed.
- [ ] Performance: ensure aggregation runs efficiently on typical week‑scale datasets; add caching if upstream data is reused across requests.
- [ ] Documentation: note assumptions, data sources, and how to adjust thresholds; link to the daily table for style parity.

## Technical Specifications
- **Templating**: Jinja2; reuse daily `a-table` styles and DOM structure.
- **Data contract** (context variables):
  - `two_hour_metrics_week`: list[dict]
    - `label`: string (e.g., "07:00–08:59")
    - `start_hour`: int (24h, block start)
    - `emails`: int (weekly sum across hours/days in block)
    - `avg_unread`: float | null (weekly mean per rules)
    - `avg_response_time`: float | null (minutes)
    - `median_response_time`: float | null (minutes)
    - `color` (optional): string for badge class mapping
  - `two_hour_max_emails_week`: int
  - `unread_threshold`: int | null
  - `response_time_target`: int | null
  - `business_hours_label`: string
  - `data_days_count`: int
- **UI rules**:
  - Emails microbar width scales to weekly max; Avg Unread and Avg Response microbars scale to their respective targets.
  - Badges: success/warning/danger per thresholds; neutral styling if threshold missing.
  - Display `—` when data is missing.
- **Edge cases**:
  - Partial weeks: indicate in subtitle/tooltips via `data_days_count`; ignore missing days in averages.
  - Avoid divide‑by‑zero and clamp widths 0–100.

## Acceptance Criteria
- Visual parity with the daily 2‑hour table (spacing, typography, microbars, badges).
- Correct weekly sums for Emails and sensible averages/medians for times and unread per rules above.
- Clear tooltips and labeling indicating weekly aggregation and number of days.
- All microbars and badges render with correct categories, widths, and styles across edge cases.
