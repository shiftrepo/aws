# Contributing to Organization Management System

Thank you for your interest in contributing to the Organization Management System! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Review Process](#code-review-process)
- [Documentation](#documentation)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, identity, or experience level.

### Our Standards

**Positive Behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable Behavior:**
- Harassment, discrimination, or intimidation
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Git installed and configured
- Development environment set up (see [README.md](README.md))
- Basic understanding of the project architecture
- Familiarity with the technology stack

### Finding Something to Work On

1. **Check existing issues**: Look for issues labeled `good first issue` or `help wanted`
2. **Review the roadmap**: See what features are planned
3. **Fix bugs**: Check for issues labeled `bug`
4. **Improve documentation**: Look for issues labeled `documentation`

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ArgoCD.git
cd ArgoCD

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ArgoCD.git
```

### 2. Set Up Development Environment

```bash
# Install dependencies
./scripts/setup.sh

# Verify setup
./scripts/status.sh
```

### 3. Create a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 4. Make Changes

Edit the code, write tests, and verify everything works.

### 5. Test Locally

```bash
# Run all tests
./scripts/test.sh

# Run specific tests
cd app/backend && mvn test
cd app/frontend && npm test

# Run E2E tests
./scripts/run-e2e-tests.sh
```

## How to Contribute

### Types of Contributions

1. **Bug Fixes**: Fix reported bugs or issues you discover
2. **New Features**: Implement new functionality
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Refactoring**: Improve code quality without changing behavior
6. **Performance**: Optimize performance
7. **Security**: Fix security vulnerabilities

### Contribution Workflow

1. **Discuss First**: For major changes, open an issue first to discuss
2. **Create Branch**: Create a feature branch from `main`
3. **Write Code**: Implement your changes following coding standards
4. **Write Tests**: Add tests for your changes
5. **Test Locally**: Ensure all tests pass
6. **Update Documentation**: Update relevant documentation
7. **Commit Changes**: Use conventional commit messages
8. **Push Branch**: Push to your fork
9. **Create PR**: Open a pull request to `main`
10. **Address Feedback**: Respond to code review comments
11. **Merge**: Once approved, your PR will be merged

## Coding Standards

### Java (Backend)

#### Style Guide

Follow the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html).

**Key Points:**
- Use 4 spaces for indentation (no tabs)
- Line length: 100 characters maximum
- Use braces for all control structures
- One statement per line

**Example:**
```java
public class OrganizationService {

    private final OrganizationRepository repository;

    public OrganizationDTO createOrganization(Organization organization) {
        if (repository.existsByCode(organization.getCode())) {
            throw new DuplicateResourceException("Organization code already exists");
        }

        Organization saved = repository.save(organization);
        return EntityMapper.toDTO(saved);
    }
}
```

#### Naming Conventions

- **Classes**: PascalCase (e.g., `OrganizationService`)
- **Methods**: camelCase (e.g., `createOrganization`)
- **Variables**: camelCase (e.g., `organizationId`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_ATTEMPTS`)
- **Packages**: lowercase (e.g., `com.example.orgmgmt`)

#### Best Practices

- Use dependency injection
- Favor composition over inheritance
- Write self-documenting code
- Use Optional for nullable values
- Handle exceptions appropriately
- Use Java 17 features when beneficial

### JavaScript/React (Frontend)

#### Style Guide

Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

**Key Points:**
- Use 2 spaces for indentation
- Use single quotes for strings
- Use semicolons
- Use arrow functions
- Use destructuring

**Example:**
```javascript
import React, { useState, useEffect } from 'react';
import { getOrganizations } from '../services/organizationService';

const OrganizationList = () => {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        const data = await getOrganizations();
        setOrganizations(data);
      } catch (error) {
        console.error('Error fetching organizations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {organizations.map((org) => (
        <div key={org.id}>{org.name}</div>
      ))}
    </div>
  );
};

export default OrganizationList;
```

#### Naming Conventions

- **Components**: PascalCase (e.g., `OrganizationList`)
- **Functions**: camelCase (e.g., `fetchOrganizations`)
- **Variables**: camelCase (e.g., `organizationId`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **Files**: Component files use PascalCase, others use camelCase

#### Best Practices

- Use functional components with hooks
- Keep components small and focused
- Use PropTypes or TypeScript for type checking
- Avoid inline styles, use CSS modules or styled-components
- Handle errors gracefully
- Use async/await for asynchronous operations

### SQL

- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Use meaningful names
- Add comments for complex queries
- Use transactions for multi-statement operations

**Example:**
```sql
-- Create organizations table
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(500),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on active organizations
CREATE INDEX idx_organizations_active ON organizations(active);
```

### Shell Scripts

- Use `#!/bin/bash` shebang
- Use 4 spaces for indentation
- Use lowercase with underscores for variables
- Add comments for complex logic
- Use `set -e` to exit on error
- Quote variables

**Example:**
```bash
#!/bin/bash
set -e
set -u
set -o pipefail

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to check prerequisites
check_prerequisites() {
    local required_commands=("podman" "git" "jq")

    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: $cmd is not installed"
            return 1
        fi
    done
}

# Main execution
main() {
    check_prerequisites
    echo "All prerequisites met"
}

main "$@"
```

## Testing Requirements

### Unit Tests

#### Backend (JUnit)

- Write tests for all service methods
- Use meaningful test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies
- Aim for 80%+ code coverage

**Example:**
```java
@Test
@DisplayName("Should create organization successfully")
void shouldCreateOrganizationSuccessfully() {
    // Arrange
    Organization organization = new Organization();
    organization.setName("Test Org");
    organization.setCode("TEST001");

    when(repository.existsByCode("TEST001")).thenReturn(false);
    when(repository.save(any(Organization.class))).thenReturn(organization);

    // Act
    OrganizationDTO result = service.createOrganization(organization);

    // Assert
    assertNotNull(result);
    assertEquals("Test Org", result.getName());
    verify(repository).save(any(Organization.class));
}

@Test
@DisplayName("Should throw exception when code already exists")
void shouldThrowExceptionWhenCodeExists() {
    // Arrange
    Organization organization = new Organization();
    organization.setCode("TEST001");

    when(repository.existsByCode("TEST001")).thenReturn(true);

    // Act & Assert
    assertThrows(DuplicateResourceException.class, () -> {
        service.createOrganization(organization);
    });
}
```

#### Frontend (Jest)

- Test component rendering
- Test user interactions
- Test API calls (mocked)
- Test error handling

**Example:**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import OrganizationList from './OrganizationList';
import * as organizationService from '../services/organizationService';

jest.mock('../services/organizationService');

describe('OrganizationList', () => {
  it('should render organizations', async () => {
    // Arrange
    const mockOrganizations = [
      { id: 1, name: 'Test Org 1' },
      { id: 2, name: 'Test Org 2' }
    ];
    organizationService.getOrganizations.mockResolvedValue(mockOrganizations);

    // Act
    render(<OrganizationList />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Test Org 1')).toBeInTheDocument();
      expect(screen.getByText('Test Org 2')).toBeInTheDocument();
    });
  });

  it('should handle error gracefully', async () => {
    // Arrange
    organizationService.getOrganizations.mockRejectedValue(new Error('API Error'));

    // Act
    render(<OrganizationList />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### Integration Tests

Test interactions between components:
- API integration tests
- Database integration tests
- Service integration tests

### E2E Tests (Playwright)

- Test complete user workflows
- Test critical paths
- Test error scenarios
- Use page object model

**Example:**
```typescript
import { test, expect } from '@playwright/test';
import { OrganizationsPage } from '../page-objects/OrganizationsPage';

test.describe('Organization Management', () => {
  test('should create new organization', async ({ page }) => {
    const orgPage = new OrganizationsPage(page);

    await orgPage.goto();
    await orgPage.clickCreateButton();
    await orgPage.fillOrganizationForm({
      name: 'Test Organization',
      code: 'TEST001',
      description: 'Test description'
    });
    await orgPage.submitForm();

    await expect(orgPage.successMessage).toBeVisible();
    await expect(orgPage.getOrganizationByName('Test Organization')).toBeVisible();
  });
});
```

### Running Tests

```bash
# Run all tests
./scripts/test.sh

# Run backend tests
cd app/backend
mvn test

# Run frontend tests
cd app/frontend
npm test

# Run E2E tests
./scripts/run-e2e-tests.sh

# Run with coverage
mvn test jacoco:report
npm test -- --coverage
```

## Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Other changes (dependencies, etc.)

### Examples

```bash
# Feature
feat(backend): add organization search endpoint

# Bug fix
fix(frontend): resolve form validation issue

# Documentation
docs: update API documentation

# Refactoring
refactor(backend): simplify organization service logic

# Breaking change
feat(api)!: change organization API response format

BREAKING CHANGE: The organization API now returns different field names
```

### Best Practices

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Keep first line under 72 characters
- Reference issues when applicable (`Fixes #123`)

## Pull Request Process

### Before Creating PR

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests**:
   ```bash
   ./scripts/test.sh
   ```

3. **Update documentation** if needed

4. **Verify changes locally**

### Creating PR

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR** on GitHub

3. **Fill out PR template** with:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)
   - Breaking changes (if any)

### PR Template

```markdown
## Description
Brief description of what this PR does

## Related Issues
Fixes #123
Relates to #456

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] All tests pass locally

## Screenshots (if applicable)
```

### PR Requirements

- Pass all CI/CD checks
- Have at least one approval
- No merge conflicts
- Code coverage maintained or improved
- Documentation updated
- Tests added for new features

## Code Review Process

### For Reviewers

**What to Review:**
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations
- Breaking changes

**How to Review:**
- Be constructive and respectful
- Explain why changes are needed
- Suggest alternatives
- Approve when satisfied
- Request changes if needed

### For Contributors

**Responding to Feedback:**
- Address all comments
- Ask questions if unclear
- Make requested changes
- Update the PR
- Re-request review

## Documentation

### Types of Documentation

1. **Code Comments**: Explain complex logic
2. **API Documentation**: Keep API.md updated
3. **README**: Update for new features
4. **Architecture**: Update for structural changes
5. **Troubleshooting**: Add common issues

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up to date
- Use proper markdown formatting

## Reporting Bugs

### Before Reporting

1. Check if bug already reported
2. Verify bug is reproducible
3. Test with latest version
4. Gather necessary information

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., RHEL 9]
- Version: [e.g., 1.0.0]
- Browser: [if applicable]

## Logs
```
Paste relevant logs here
```

## Screenshots
If applicable
```

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Any other information
```

## Questions?

If you have questions:
- Check existing documentation
- Search closed issues
- Open a new issue with your question
- Join community discussions

## Thank You!

Thank you for contributing to the Organization Management System. Your contributions help make this project better for everyone!

---

Happy contributing!
