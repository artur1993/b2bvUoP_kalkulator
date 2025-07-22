# AI Assistant Complete Instructions
## Quick Start**For immediate setup, just tell any AI agent:**> "Przeczytaj te instrukcje i skonfiguruj projekt zgodnie z wytycznymi."
This single file contains all instructions needed for any AI assistant (Gemini CLI, Claude Code, Copilot, etc.) to create and maintain professional software projects with continuous workflow capabilities.
---
## Core Principles
### 1. Continuity & Recovery- **ALWAYS** maintain ability to resume work after disconnection- **NEVER** lose context or progress on task interruption- Use file system markers (â†’ CURRENT) to track exact work position- Verify project state before continuing any interrupted work
### 2. Language Standards- **ALL** project files, documentation, comments, and names: English only- **ALL** communication with user: Polish language- Code comments, variable names, function names: English- README, documentation, commit messages: English
### 3. Professional Quality- Every project needs comprehensive testing at multiple levels- Documentation must always be current and complete- Version control with meaningful commit messages following standards- Clean, maintainable code with proper architecture
---
## Project Structure
Every project must have this exact structure:
```project-root/â”œâ”€â”€ README.md # Complete documentation (English)â”œâ”€â”€ .ai/ # AI agent filesâ”‚ â”œâ”€â”€ instructions.md # Copy of these instructionsâ”‚ â”œâ”€â”€ context.md # Project context & assumptionsâ”‚ â”œâ”€â”€ tasks.md # Current tasks with statusâ”‚ â””â”€â”€ session-state.md # Current session stateâ”œâ”€â”€ docs/ # Additional documentationâ”œâ”€â”€ src/ # Source codeâ”œâ”€â”€ tests/ # All test filesâ”‚ â”œâ”€â”€ unit/ # Unit testsâ”‚ â”œâ”€â”€ integration/ # Integration testsâ”‚ â””â”€â”€ e2e/ # End-to-end testsâ”œâ”€â”€ .github/workflows/ # CI/CD configurationâ”œâ”€â”€ scripts/ # Build/deployment scriptsâ”œâ”€â”€ .gitignore # Git ignore fileâ””â”€â”€ package.json/.requirements.txt # Dependencies```
---
## 4-Phase Development Workflow
### Phase 1: Analysis & PlanningWhen receiving any user request:
1. **Read current state**: Check `.ai/tasks.md` for ongoing work2. **Analyze request**: Understand requirements completely3. **Create detailed plan**: Break down into specific, testable steps4. **Update tasks file**: Add new plan with priorities and dependencies5. **Present plan**: Show user the complete implementation strategy6. **Wait for approval**: Do not proceed without explicit user confirmation
### Phase 2: Implementation PreparationAfter user approves plan:
1. **Mark current task**: Add "â†’ CURRENT" marker in `.ai/tasks.md`2. **Update context**: Record all relevant decisions in `.ai/context.md`3. **Set session state**: Update `.ai/session-state.md` with environment info4. **Begin implementation**: Start with marked task
### Phase 3: Code Implementation & TestingFor each implementation step:
1. **Write/modify code**: Implement the planned functionality2. **Run existing tests**: Ensure no regressions3. **Fix any failures**: Address test failures immediately4. **Add new tests**: Create tests for new functionality   - Unit tests for individual functions/methods   - Integration tests for component interactions   - E2E tests for complete user workflows5. **Verify test coverage**: Ensure comprehensive coverage6. **Test in real environment**: Run the actual application7. **User verification**: If user interface changes, ask user to verify8. **Prepare commit**: Create detailed commit message
### Phase 4: Finalization & ContinuationAfter successful implementation:
1. **Create commit**: Use Conventional Commits format:   ```   <type>(<scope>): <description>      - Detailed explanation of changes made   - Why the change was necessary   - Important implementation notes   - Impact on other components   ```
2. **Update README**: Ensure all documentation remains current3. **Update task status**: Mark completed in `.ai/tasks.md`4. **Clean session state**: Update `.ai/session-state.md`5. **Ask user**: "Continue with next task or do something else?"
---
## Testing Requirements
### Mandatory Tests- **Unit tests**: For every function, method, class- **Integration tests**: For component interactions- **End-to-end tests**: For complete user workflows
### Optional Tests (Ask User First)- **Performance tests**: When performance is critical- **Security tests**: For authentication/authorization features  - **Load tests**: For high-traffic scenarios- **API tests**: For RESTful services- **UI tests**: For complex user interfaces
### Test Standards- Minimum 80% code coverage- Tests must be automated and runnable via CI/CD- Clear test names describing what is being tested- Tests must be independent and deterministic- Include positive, negative, and edge case scenarios
---
## Documentation Standards
### README.md Structure (Always in English)```markdown# Project Name
Brief description of what the project does and its main purpose.
## Installation
Step-by-step installation instructions including:- Prerequisites- Dependencies- Environment setup- Configuration steps
## Usage
### Basic UsageExamples of how to use the project
### Advanced FeaturesMore complex usage scenarios
### API DocumentationIf applicable, document all endpoints/functions
## Development
### Setup Development EnvironmentInstructions for developers
### Running TestsHow to run different types of tests
### ContributingGuidelines for contributors
### ArchitectureHigh-level system architecture explanation
## Deployment
### Production SetupDeployment instructions for production
### Environment VariablesList and explain all required configuration
## Troubleshooting
Common issues and their solutions
## License
License information```
### Code Documentation- All functions/methods have clear docstrings (English)- Complex algorithms explained with comments- API endpoints documented with examples- Configuration files commented appropriately
---
## Commit Message Standards
Use Conventional Commits format:
**Types:**- `feat`: New feature- `fix`: Bug fix- `docs`: Documentation changes- `style`: Code formatting (no logic change)- `refactor`: Code restructuring (no functionality change)- `test`: Adding or modifying tests- `chore`: Maintenance tasks- `ci`: CI/CD changes- `perf`: Performance improvements
**Examples:**```feat(auth): add user login functionality
- Implement JWT authentication- Add login/logout endpoints- Create user session management- Include password validation
fix(database): resolve connection pool leak
- Fix connection not being properly closed- Add connection timeout configuration- Improve error handling for failed connections
docs(api): update endpoint documentation
- Add examples for all REST endpoints- Document request/response formats- Include authentication requirements```
---
## Session Recovery Protocol
### On Starting New Session:1. **Check `.ai/context.md`**: Understand project purpose and background2. **Read `.ai/tasks.md`**: Find current task marked with "â†’ CURRENT"3. **Verify environment**: Run tests to ensure system is working4. **Check session state**: Review `.ai/session-state.md` for last known state5. **Continue from checkpoint**: Resume work from exact interruption point
### Session State Tracking:Always update `.ai/session-state.md` with:- Current task being worked on- Files being modified- Environment configuration- Any temporary states or variables- Next steps to be performed
---
## Error Handling & Recovery
### When Tests Fail:1. **Stop immediately**: Do not proceed with failed tests2. **Analyze failure**: Understand root cause3. **Fix the issue**: Address the actual problem, don't just make tests pass4. **Re-run tests**: Ensure fix works5. **Update documentation**: If needed
### When Build Fails:1. **Check dependencies**: Ensure all requirements are met2. **Verify configuration**: Check environment settings3. **Fix step by step**: Address one issue at a time4. **Test incrementally**: Verify each fix
### When Code Review Issues:1. **Address all feedback**: Fix every noted issue2. **Update tests**: If behavior changes3. **Update documentation**: If interfaces change4. **Re-submit for review**
---
## Communication Guidelines
### With User:- **Always in Polish**: All communication with user in Polish- **Confirm understanding**: Before starting complex tasks- **Regular updates**: Keep user informed of progress- **Ask for clarification**: When requirements are unclear- **Request verification**: For UI/UX changes
### In Code/Documentation:- **Always in English**: All code, comments, documentation- **Be descriptive**: Clear variable/function names- **Explain complex logic**: Add comments for non-obvious code- **Document decisions**: Explain why something was done a certain way
---
## Tool-Specific Adaptations
### For Any AI Tool:- Read this file completely before starting any work- Follow the 4-phase workflow for every task- Maintain the file structure exactly as specified- Use the session recovery protocol after any disconnection- Always update progress markers in task files
### Integration with Different Tools:- **Gemini CLI**: Focus on analysis and complex problem-solving- **Claude Code**: Emphasize code review and optimization  - **GitHub Copilot**: Use for code completion and suggestions- **Others**: Adapt as needed while following core workflow
---
## Quality Assurance
### Before Any Commit:- [ ] All tests passing- [ ] Code follows project standards- [ ] Documentation (README, etc.) updated to reflect changes
- [ ] Dependency files (requirements.txt, package.json, etc.) updated- [ ] No debug code or comments left- [ ] Proper error handling implemented- [ ] Performance impact considered
### Before Finishing Session:- [ ] All files saved- [ ] Progress marked in `.ai/tasks.md`- [ ] Session state updated in `.ai/session-state.md`- [ ] Any temporary files cleaned up- [ ] Next steps documented
### Project Health Checks:- Regular dependency updates- Security vulnerability scans- Performance monitoring- Code quality metrics- Test coverage reporting
---
## Emergency Procedures
### If Session Ends Unexpectedly:1. Next session starts by reading this file2. Check all `.ai/` files for last known state3. Verify system integrity with test runs4. Resume from last marked checkpoint5. If unclear, ask user for clarification
### If Project Becomes Corrupted:1. Check version control history2. Identify last working commit3. Assess what needs to be recovered4. Implement fixes systematically5. Update all documentation
### If Tests Start Failing:1. Don't ignore failing tests2. Investigate root cause immediately3. Fix issues before proceeding4. Update tests if requirements changed5. Ensure all tests pass before continuing
---
## Final Notes
This instruction set enables:- **Complete project autonomy**: Any AI can pick up and continue work- **Professional standards**: All outputs meet industry standards- **Seamless handoffs**: Work continues perfectly after disconnections- **Quality assurance**: Comprehensive testing and documentation- **User satisfaction**: Clear communication and reliable delivery
**Remember**: The goal is to create maintainable, testable, well-documented software that can be easily understood and extended by any developer or AI assistant.