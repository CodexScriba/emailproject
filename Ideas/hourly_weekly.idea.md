# Hourly Weekly Email Volume Idea

## Goal
Create a weekly visualization of email volume by hour, building on the existing daily email dashboard (e.g., email_dashboard_2024-08-20.html). This will help showcase trends and patterns across multiple days for better decision-making.

## Visualization Options
Prototype two options in a single simple HTML file for comparison:
- **7 Lines**: A line chart with one line per day (similar to the daily dashboard's hourly chart) to show day-to-day variations.
- **Bars**: A bar chart displaying email volume per hour, potentially aggregated or per day, to highlight peaks and troughs clearly.

## Purpose
Present both options to management for feedback on preferences. Focus on evaluating based on readability, space efficiency, and how well they reveal weekly patterns without overwhelming the viewer.

## Key Details
- **Timeframe**: August 13-19, 2024 (7 days starting from August 13, based on user correction for accurate alignment).
- **Metrics**: Primarily email volume (matching the daily dashboard), with optional inclusion of unread counts if it enhances clarity.
- **Data Source**: Pull from the existing unified JSON database structure used in the daily dashboard.
- **Scope**: Focus on business hours (e.g., 7 AM–9 PM) for consistency with the original.

## Prototype Guidelines
- Create a basic HTML file with sample/mock data (e.g., fictional email volumes for each hour/day) to avoid complexity.
- Include side-by-side comparisons of the 7 lines and bars options.
- Keep styling minimal (no advanced CSS) to prioritize functionality and quick iteration.
- Base structure loosely on the daily dashboard for familiarity, but simplify for prototyping.

## Next Steps
1. Build the HTML prototype with both visualizations.
2. Review internally and gather management feedback on preferences.
3. Decide on the preferred option based on feedback.
4. Integrate the chosen visualization into the main dashboard or create an updated version.
5. Test with real data and refine as needed.

## Additional Notes
- Prioritize ease of comparison and pattern recognition.
- Consider space constraints for bars and potential clutter for 7 lines.
- Document any further decisions or adjustments here for reference.

*Last Updated: [Current Date]*
