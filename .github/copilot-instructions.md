# GitHub Copilot Instructions for Co-ci-pokaze2

## Project Overview
This repository is currently in its initial setup phase. It serves as a project workspace that will be developed over time.

## Repository Structure
```
Co-ci-pokaze2/
├── .github/               # GitHub configuration and workflows
│   └── copilot-instructions.md  # This file
└── README.md              # Project documentation
```

## Development Workflow

### General Guidelines
- Keep changes minimal and focused
- Follow best practices for the language/framework being used
- Write clean, readable, and maintainable code
- Add appropriate comments for complex logic

### Git Conventions
- Use descriptive commit messages
- Reference issue numbers in commits when applicable
- Keep commits atomic and focused on a single change
- Branch naming: use descriptive names like `feature/add-login` or `fix/bug-description`

## Code Style

### General Conventions
- Use consistent indentation (2 or 4 spaces depending on language conventions)
- Follow language-specific style guides (PEP 8 for Python, Airbnb for JavaScript, etc.)
- Use meaningful variable and function names
- Keep functions small and focused on a single responsibility

### Naming Conventions
- **Variables**: camelCase or snake_case (depending on language)
- **Functions**: camelCase or snake_case (depending on language)
- **Classes**: PascalCase
- **Constants**: UPPER_CASE
- **Files**: kebab-case or match language conventions

## Testing

### Testing Practices
- Write tests for new features when test infrastructure is in place
- Run existing tests before committing changes
- Ensure tests are readable and maintainable
- Test edge cases and error conditions

### Test Organization
- Place test files alongside source files or in dedicated test directories
- Use clear test names that describe what is being tested
- Follow Arrange-Act-Assert pattern

## Documentation

### When to Document
- Public APIs and interfaces
- Complex algorithms or business logic
- Non-obvious design decisions
- Setup and configuration instructions

### Documentation Style
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples where helpful
- Update README.md for significant changes

## Security Best Practices

### Important Security Rules
- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Validate and sanitize user inputs
- Follow OWASP security guidelines
- Keep dependencies up-to-date

## Architecture

### Design Principles
- Keep code modular and reusable
- Separate concerns appropriately
- Follow SOLID principles when applicable
- Prefer composition over inheritance
- Write code that is easy to test

## Important Notes

### General Reminders
- This repository is in early stages and will evolve over time
- Follow established patterns as the codebase grows
- Update these instructions as new conventions are established
- Ask questions if requirements are unclear

### What NOT to Do
- Do not commit build artifacts or dependencies
- Do not make breaking changes without discussion
- Do not bypass existing workflows or processes
- Do not introduce new dependencies without consideration

## Future Considerations

As this project grows, consider adding:
- Specific build and test commands
- Technology stack details (languages, frameworks, tools)
- CI/CD pipeline information
- Deployment procedures
- Contribution guidelines
- Code review processes

---

**Note**: These instructions should be updated as the project evolves and more specific conventions are established.
