# KPI Cards — Weekly Dashboard Decisions

This document captures the decisions for recreating the four KPI cards from `daily/dashboard/templates/kpi_cards.html` for the weekly dashboard.

- **Goal**: Create equivalent weekly KPI cards that summarize the week, following the project's constraint: HTML/CSS-only dashboards (no JavaScript in final output).

- **Scope**: The four KPI cards mirror the daily dashboard but aggregate over the selected week (ISO week or last 7 days):
  - Total Emails
  - Avg Unread Count
  - Avg Response Time (business hours)
  - SLA Compliance (%)

- **Header / Title**:
  - Keep the title exactly as in `kpi_cards.html` ("Email Performance Dashboard"), but append the **ISO week number** and the **date range** the dashboard covers.
  - Example header subtitle: "Week 34 — Aug 19, 2024 – Aug 25, 2024". Use Monday–Sunday week boundaries.

- **Data Source**: `database/email_database.json` aggregated across the week. Use only fields present in the unified JSON; if missing, document fallback rules.

- **Card Definitions & Calculation Rules**:
  1. **Total Emails**
     - Definition: Sum of `daily_summary.total_emails` across the selected week (Monday–Sunday).
     - Additional display: Show **Avg # of emails per day** underneath or as subtitle text; calculation = total_emails / number_of_days_with_data (rounded to 1 decimal).
     - Fallback: If `daily_summary.total_emails` missing for any day, compute from hourly sums for that day.
     - Display: Integer for total, and avg with 1 decimal.
     - Subtitle: "Emails received this week" and secondary line "Avg: X per day"

  2. **Avg Unread Count**
     - Definition: Weekly mean of each day's `daily_summary.avg_unread_count` (rounded to 1 decimal). Equivalent to (sum of daily averages)/number_of_days_with_data.
     - Alternative (if daily averages missing): compute mean across all business-hour `unread_count` hourly values in the week, ignoring nulls.
     - SLA Threshold: Use `config/sla_config.json` -> `sla_thresholds.unread_email_threshold` (default 30) and display it in the subtitle.
     - Display rule: If avg_unread <= threshold -> mark card `success`; else `danger`.

  3. **Avg Response Time (business hours)**
     - Definition: Weighted average (by `emails_replied`) of per-hour `avg_response_time` across all business-hour hourly entries during the week.
     - Calculation: For each hourly entry with `avg_response_time` and `emails_replied` > 0, accumulate weighted_sum += avg_response_time * emails_replied and total_weight += emails_replied; final = weighted_sum / total_weight.
     - Fallback: If no replied emails, use weekly mean of `daily_summary.avg_response_time_minutes` where present.
     - Display: Minutes rounded to 1 decimal with "min" suffix.
     - Card color: `success` if <= response_time_target, `warning` if <= 2x target, `danger` otherwise. `response_time_target` from `config/sla_config.json` -> `kpi_targets.response_time_target_minutes` (default 60).

  4. **SLA Compliance (%)**
     - Definition: Weighted compliance across the week. Preferred: average of daily `daily_summary.sla_compliance_rate` weighted by that day's `daily_summary.total_emails`. Formula: (sum over days of (sla_compliance_rate * total_emails)) / (sum total_emails).
     - Fallback: If total_emails missing, compute unweighted mean of daily SLA rates across days with data.
     - Display: Percentage with 1 decimal, e.g., "87.4%".
     - Target: `kpi_targets.sla_compliance_target_percent` from `config/sla_config.json` (default 85%). Card styled `success` if >= target.

- **Design**:
  - The KPI cards should be visually identical to the cards in `daily/dashboard/templates/kpi_cards.html` (same classes, color semantics, and layout).
  - Ensure the Total Emails card includes both the total and the Avg per day as specified.

- **Update Notes (Decisions made)**:
  - Title will include "Week {ISOweek} — {Mon Date} – {Sun Date}".
  - Week boundaries: Monday to Sunday (ISO week conversion).
  - All KPI aggregations use Monday–Sunday inclusive.
  - Total Emails card will display total and avg per day.
  - Other cards are the weekly aggregation (7-day) equivalents of daily cards.

- **Edge Cases & Missing Data**:
  - Days with `has_email_data == false` or `has_sla_data == false` are excluded from averages unless no days remain; then show N/A with clear messaging.
  - Null `unread_count` hourly values are ignored in mean calculations.
  - If the week contains fewer than 3 days of data, display a warning badge and include a message: "Partial week — metrics computed from N day(s)".

- **Acceptance Criteria**:
  - Title includes week number and date range.
  - Total Emails card shows total and average per day.
  - All four cards are visually and semantically identical to daily versions but aggregated over Monday–Sunday.

- **Next Steps**:
  1. Approve these decisions.  
  2. Draft `Ideas/weekly_dashboard.idea.md` with other widgets and layout details.  
