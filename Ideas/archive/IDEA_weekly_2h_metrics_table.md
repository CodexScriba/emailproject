## Weekly 2‑Hour Email Metrics Table — Idea

### Objective
- Create a weekly 2-hour metrics table, visually consistent with the daily table in `daily/dashboard/templates/kpi_cards.html`.
- Replace the SLA badge column with an Avg Unread column to better reflect backlog pressure at the week level.

### Columns
- **Block**: 2-hour range label (e.g., 07:00–08:59) and daypart icon.
- **Emails**: Sum for the week for that block; microbar scaled to weekly max.
- **Avg Unread**: Mean unread count across the week for that block; color-coded against `unread_threshold`; microbar for context.
- **Avg Response**: Badge category (Lightning/Fast/Moderate/Slow/Very Slow/Critical) + microbar scaled vs `response_time_target`.
- **Median Time**: Median response time in minutes.

### Data contract (context variables)
- `two_hour_metrics_week`: list of dicts, one per 2-hour block, ordered by start_hour.
  - `label`: string, e.g., "07:00–08:59"
  - `start_hour`: int (24h, block start)
  - `emails`: int (sum across all days for hours in block)
  - `avg_unread`: float | null (see aggregation)
  - `avg_response_time`: float | null (minutes)
  - `median_response_time`: float | null (minutes)
  - `color` (optional): string for response-time badge class mapping (if using precomputed categories)
- `two_hour_max_emails_week`: int (max of `emails` across blocks; used for microbar scaling)
- `unread_threshold`: int (target threshold for unread)
- `response_time_target`: int (target minutes for average response time)
- `business_hours_label`: string (e.g., "07:00–21:00")
- `data_days_count`: int (for tooltips indicating partial weeks)

### Aggregation rules
- **Emails (sum)**: For each block, sum all emails across included hours and all days.
- **Avg Unread (mean)**:
  - Preferred: average the per-hour unread snapshots across the block, across all days with data.
  - If only per-block daily averages exist, compute the mean of those daily block averages.
  - Display `N/A` if no inputs; otherwise show one decimal.
  - Coloring: success if `avg_unread <= unread_threshold`, danger otherwise. Optionally warning band if desired.
- **Avg Response Time**:
  - Preferred: average over per-email response durations (weighted by email count).
  - Fallback: mean of per-day block averages weighted by per-day block email counts; if counts missing, simple mean.
  - Badge mapping (same as daily): <30 ⚡, <60 🚀, <120 ⏱️, <180 🐢, <300 ⚠️, else 🔴.
- **Median Response Time**: Median over per-email durations if available; else median of per-day block medians.

### UI/behavior
- Reuse daily `a-table` styles (`.a-table`, `.a-row`, `.badge`, `.microbar`, etc.).
- Emails: microbar width = `(emails / (two_hour_max_emails_week or 1) * 100)` clamped 0–100.
- Avg Unread: microbar width relative to `unread_threshold` (e.g., `(avg_unread / max(unread_threshold,1) * 100)` clamped 0–100). Optionally cap at 150% to visualize overage.
- Response microbar: width = `((avg_response_time or 0) / (response_time_target or 60) * 100)` as in daily.
- Tooltips should include daypart label and note `Avg unread across {data_days_count} day(s)` for context on partial weeks.

### Template sketch (Jinja2 snippet)
```html
<section class="chart-section">
  <div class="card">
    <div class="chart-title">2-Hour Email Metrics — Weekly</div>
    <div class="chart-subtitle">Aggregated across {{ business_hours_label }} ({{ data_days_count }} day{% if data_days_count != 1 %}s{% endif %})</div>

    <div class="a-table">
      <div class="a-row header">
        <div>Block</div><div>Emails</div><div>Avg Unread</div><div>Avg Response</div><div>Median Time</div>
      </div>

      {% for row in two_hour_metrics_week %}
      <div class="a-row" title="{{ row.label }} • Emails: {{ row.emails }} • Avg Unread: {{ row.avg_unread if row.avg_unread is not none else 'N/A' }} • Avg Response: {{ row.avg_response_time if row.avg_response_time is not none else 'N/A' }} min • Median: {{ row.median_response_time if row.median_response_time is not none else 'N/A' }} min">
        <div class="a-cell">
          {% set s = row.start_hour %}
          {% if s <= 8 %}<div class="distribution-name">🌅 Early Morning</div>
          {% elif s <= 12 %}<div class="distribution-name">☀️ Morning</div>
          {% elif s <= 16 %}<div class="distribution-name">🌤️ Afternoon</div>
          {% else %}<div class="distribution-name">🌆 Evening</div>
          {% endif %}
          <div class="distribution-range">{{ row.label }}</div>
        </div>

        <div class="a-cell">
          <div class="microbar"><div class="fill emails" data-width="{{ (row.emails / (two_hour_max_emails_week or 1) * 100) | round(0) }}"></div></div>
          <span class="weak">{{ row.emails }}</span>
        </div>

        <div class="a-cell">
          {% set au = row.avg_unread %}
          {% if au is not none %}
            {% set unread_ok = unread_threshold is not none and au <= unread_threshold %}
            <span class="badge {% if unread_ok %}success{% else %}danger{% endif %}">{{ au | round(1) }}</span>
            <div class="microbar"><div class="fill emails" data-width="{{ ( (au or 0) / (unread_threshold or 1) * 100 ) | round(0) }}"></div></div>
          {% else %}
            <span class="weak">—</span>
          {% endif %}
        </div>

        <div class="a-cell">
          {% set art = row.avg_response_time %}
          {% if art is not none %}
            {% if art < 30 %}<span class="badge success">⚡ Lightning Fast</span>
            {% elif art < 60 %}<span class="badge success">🚀 Fast Response</span>
            {% elif art < 120 %}<span class="badge warning">⏱️ Moderate</span>
            {% elif art < 180 %}<span class="badge warning">🐢 Slow</span>
            {% elif art < 300 %}<span class="badge danger">⚠️ Very Slow</span>
            {% else %}<span class="badge danger">🔴 Critical</span>
            {% endif %}
          {% endif %}
          <div class="microbar"><div class="fill response" data-width="{{ ( (art or 0) / (response_time_target or 60) * 100 ) | round(0) }}"></div></div>
          <span class="weak">{% if art is not none %}{{ art }} min{% else %}—{% endif %}</span>
        </div>

        <div class="a-cell">{% if row.median_response_time is not none %}{{ row.median_response_time }} min{% else %}—{% endif %}</div>
      </div>
      {% endfor %}
    </div>
  </div>
  <script>
    // Reuse existing JS that applies widths from data-width attributes
    // ensure '.microbar .fill[data-width]' is covered on this page as well
  </script>
</section>
```

### Edge cases & behaviors
- Partial week: rely on `data_days_count` in subtitle/tooltips; averages must ignore missing days.
- Missing data: show `—` or `N/A`; avoid division by zero; clamp microbar widths to 0–100.
- Thresholds: if `unread_threshold` is missing, display neutral styling and no color judgment.

### Acceptance criteria
- Visual parity with daily 2-hour table (spacing, typography, microbars, badges).
- Correct weekly sums for Emails and sensible averages/medians for times and unread.
- Clear tooltips and labeling indicating weekly aggregation and number of days.


