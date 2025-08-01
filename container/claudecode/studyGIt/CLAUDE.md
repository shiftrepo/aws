# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitPlayground ("Git学習プレイグラウンド") is an interactive web application designed to help beginners learn Git operations in a team development context. The application simulates file management, commit visualizations, team collaboration, and conflict resolution through an interactive interface.

## Component Relationships

The application follows these interaction patterns:

1. User enters their name on the homepage (index.js/page.tsx)
2. User is directed to the playground with their name as a URL parameter
3. The playground renders the core components in this order:
   - File Explorer for file operations
   - Command Terminal for executing Git commands
   - Git Visualizer for displaying commit history
   - Team Simulator for collaboration scenarios
4. State is shared across components using React context and props
5. Simulated Git operations update the repository state model without actual Git commands

## Commands

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Clean install (no package-lock)
npm run install:clean
```

### Podman

```bash
# Start the container
podman-compose up

# Build and start container
podman-compose up --build

# Check container status
podman ps

# View container logs
podman logs git-playground
```

> **IMPORTANT**: Only use podman-compose for running the application. Do not use docker-compose, docker run, podman run, or any other method to start containers.

### Verification Process

```bash
# Start the container with podman-compose
podman-compose up --build

# Verify the application is running (in a separate terminal)
curl http://localhost:3000

# Test with browser by opening http://localhost:3000
```

Verification requirements:
- Always verify changes using podman-compose (never docker-compose)
- Test by connecting from the host via localhost (not from inside the container)
- After making changes, repeat the verification process until no errors appear
- Document any persistent issues in GitHub issues

## Architecture

GitPlayground is built with Next.js 12.3.4 using a hybrid approach that supports both App Router pattern and Pages directory structure. The codebase is primarily written in TypeScript with some JavaScript files in the Pages directory. The application simulates Git operations without actually performing them on a real Git repository.

### Key Components

1. **FileExplorer** (`src/components/FileExplorer.tsx`)
   - Handles file creation, modification, and deletion operations
   - Displays the current files in the simulated repository

2. **GitVisualizer** (`src/components/GitVisualizer.tsx`) 
   - Visualizes Git commit history
   - Displays branches, commits, and HEAD position (always positioned at the latest commit of the current branch)
   - Shows conflict status in the commit history

3. **CommandTerminal** (`src/components/CommandTerminal.tsx`)
   - Simulates Git commands
   - Handles commit operations
   - Provides realistic Git-like command interface

4. **TeamSimulator** (`src/components/TeamSimulator.tsx`)
   - Simulates team collaboration
   - Creates virtual team members that perform actions on the repository
   - Implements interactive conflict resolution simulation
   - Allows users to manually resolve conflicts via text editor

### Conflict Resolution Feature

The TeamSimulator component implements an interactive conflict resolution experience:

- Simulates team members working on the same files
- Generates conflict markers (<<<<<<< HEAD, =======, >>>>>>> feature-branch)
- Provides a text editor for users to manually resolve conflicts
- Includes step-by-step guidance through the conflict resolution process
- Provides helpful chat interface that simulates communication with team members

### Data Model

The application uses a state model to represent Git concepts:

```typescript
interface Repository {
  files: Record<string, string>;  // Current files in the repository
  commits: Commit[];              // Commit history
  branches: string[];             // Available branches
  currentBranch: string;          // Current active branch
}

interface Commit {
  id: string;           // Unique commit ID
  message: string;      // Commit message
  author: string;       // Author name
  timestamp: string;    // Timestamp of commit
  branch: string;       // Branch name
  files: Record<string, string>; // State of files at commit
  hasConflict?: boolean;      // Whether this commit has conflicts
  resolvedConflict?: boolean; // Whether conflicts were resolved
}
```

### Page Structure

1. **Home** - Landing page with username input
   - App Router: `src/app/page.tsx` 
   - Pages Router: `src/pages/index.js`
2. **Playground** - Main interactive Git learning environment
   - App Router: `src/app/playground/page.tsx`
   - Pages Router: `src/pages/playground.js`

### Flow

1. User enters name on homepage
2. User navigates to playground with username in URL params
3. User can perform file operations, commits, and interact with simulated team members
4. A tutorial guides new users through basic operations
5. User can simulate and resolve Git conflicts with teammate changes
6. Git history is visualized to help users understand operations, with the HEAD pointer correctly tracking the latest commit on the current branch

### Technologies

- Next.js 12.3.4 (hybrid App Router/Pages Router)
- TypeScript/JavaScript
- React
- styled-components
- CSS Modules
- framer-motion
- isomorphic-git (for Git operations simulation)
- reactflow (for Git Flow diagram visualization)

### Volume Mounting

When running with Podman in development mode, the repository is configured to mount local files into the container for hot-reload capability:

```yaml
volumes:
  - .:/app:z,U    # Mount local directory with SELinux flags
  - /app/node_modules
user: "root:root" # Set user to root:root to resolve permission issues
```

The `z,U` flags are used for SELinux compatibility, and the root user setting ensures proper file permissions when mounting between host and container.

### Container Configuration Notes

The docker-compose.yml configuration includes important volume mounts:

```yaml
volumes:
  - .:/app:z,U    # Mount local directory with SELinux flags
  - /app/node_modules
```

This configuration ensures:
1. The first mount maps the current directory to /app with SELinux permissions
2. The second mount preserves the container's node_modules directory even when the host directory is mounted
3. This setup prevents the container's installed dependencies from being overwritten

### Tutorials and Educational Content

The application includes several tutorial components:

1. **GitFlowGuide** (`src/components/GitFlowGuide.js`)
   - Teaches Git Flow branching strategy
   - Includes both ASCII art and graphical visualization modes using ReactFlow
   - Shows step-by-step progression through the Git Flow workflow
   - Demonstrates branch operations, merges, and versioning
   - Uses ReactFlowGitGraph component for interactive diagrams

2. **ConflictGuide** (`src/components/ConflictGuide.js`)
   - Teaches conflict resolution workflows
   - Shows examples of conflict markers and resolution methods

### Known Issues

Next.js Module Resolution:
- This project uses Next.js 12.3.4 to avoid the "Cannot find module '../server/require-hook'" error that occurs with newer versions
- The project has been configured to work with both App Router pattern and Pages directory structure
- This compatibility solution allows the app to run without errors while maintaining the modern App Router structure

### Best Development Practices

1. **Container-First Development**
   - Prefer running the application in a container for consistent environment
   - Use `podman-compose up --build` after code changes
   - Use volume mounting for hot-reload development

2. **UI/UX Considerations**
   - All components should support both English and Japanese text
   - Visual elements should include clear annotations for educational purposes
   - Use consistent styling and animations from existing components

3. **Testing the Application**
   - Test all Git simulation operations with various scenarios
   - Ensure conflict resolution guides work correctly
   - Verify all tutorial steps are clear and accurate

4. **Git Collaboration Guidelines**
   - Use feature branches for all new developments (`feature/feature-name`)
   - Create descriptive commit messages with prefix format: `[component]: action description`
   - Rebase feature branches on main before submitting pull requests
   - Pull requests should include testing instructions and screenshots
   - All pull requests require at least one code review before merging
   - Resolve merge conflicts by communicating with the team member who wrote the conflicting code
   - Use GitHub issues for tracking bugs and feature requests

> **CRITICAL REQUIREMENT**: All GitHub repository operations MUST use the mcp's github-org tools. Direct GitHub CLI commands, GitHub web interface, or other GitHub access methods are prohibited.

### GitHub Operations

```bash
# Use these tools for all GitHub operations
mcp__github-org__search_repositories
mcp__github-org__create_repository
mcp__github-org__get_file_contents
mcp__github-org__create_or_update_file
mcp__github-org__push_files
mcp__github-org__create_issue
mcp__github-org__create_pull_request
mcp__github-org__search_code
mcp__github-org__search_issues
# ... and other mcp__github-org tools as needed
```

Examples:
- For creating issues: Use mcp__github-org__create_issue instead of GitHub web interface
- For checking repositories: Use mcp__github-org__search_repositories instead of browsing GitHub
- For all code changes: Use mcp__github-org__push_files or mcp__github-org__create_or_update_file

5. **Code Review Process**
   - Review for functionality, code quality, and adherence to project patterns
   - Use constructive comments and suggestions for improvements
   - Address all review comments before merging
   - Acknowledge good practices and innovative solutions
   - Ensure proper test coverage for all new code

# Agent Communication System

# Agent Communication System

## エージェント構成
- **ProductOwner** (別セッション): 統括責任者
- **ScrumMaster1** (multiagent:0.0): チームリーダー
- **worker1,2,3** (multiagent:0.1-3): 実行担当

## あなたの役割
- **ProductOwner**: @instructions/ProductOwner.md
- **ScrumMaster1**: @instructions/ScrumMaster.md
- **worker1,2,3**: @instructions/worker.md

## メッセージ送信
```bash
./agent-send.sh [相手] "[メッセージ]"
```

## 基本フロー
ProductOwner → ScrumMaster1 → workers → ScrumMaster1 → ProductOwner

