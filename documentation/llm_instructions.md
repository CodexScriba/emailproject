# LLM Instructions for Email Dashboard Project

## Agent Roles

### Spark (@.windsurf/workflows/spark.md)
**Purpose**: Ideas, planning, and feature development guidance
- Generate creative solutions and feature ideas
- Help with planning future development phases
- Suggest improvements and optimizations
- Brainstorm dashboard layouts and visualizations
- Plan development workflows and task prioritization

### Architecture Documentation (@documentation/architecture.md)
**Purpose**: Factual project documentation - NOT planning
- Document actual project state and current assets
- Record analyzed data structures and patterns
- Catalog technical constraints and limitations
- List completed work and current objectives
- Track obstacles and blockers encountered
- Maintain accurate project structure documentation

**IMPORTANT**: Architecture documentation should only contain:
- Facts about what has been done
- Current project state and assets
- Analyzed data patterns and findings
- Technical constraints that exist
- Obstacles that have been encountered

**DO NOT include in architecture.md**:
- Future planning or roadmaps
- Proposed solutions or features
- Speculative technical decisions
- Development phases or workflows
- Success metrics or next steps

## Documentation Guidelines

### Chat Folder (@documentation/chat/)
- Conversation logs and decision records
- Analysis findings and insights
- Technical discoveries during development
- Problem-solving discussions

### When to Update Architecture
Update architecture.md when:
- New CSV files are analyzed
- Data patterns are discovered
- Technical constraints are identified
- Project structure changes
- Objectives shift based on available data
- Obstacles are encountered

### Fact-Based Documentation
Architecture documentation must be:
- Based on actual analysis and findings
- Grounded in current project state
- Free from speculative content
- Updated only when new facts emerge
- Focused on "what is" not "what will be"

## Development Approach

This project follows an iterative, data-driven approach:
1. Add and analyze one CSV file at a time
2. Update architecture with findings
3. Use Spark for planning next steps
4. Document discoveries in chat folder
5. Build solutions based on available data

The architecture document serves as the single source of truth for project status and discovered facts, while planning and ideation happen through Spark workflows.