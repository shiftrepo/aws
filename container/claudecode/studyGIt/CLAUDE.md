# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitPlayground ("Git学習プレイグラウンド") is an interactive web application designed to help beginners learn Git operations in a team development context. The application simulates file management, commit visualizations, team collaboration, and conflict resolution through an interactive interface.

## Component Relationships

The application follows these interaction patterns:

1. User enters their name on the homepage (page.tsx)
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

### Docker and Podman

```bash
# Start with Docker
docker-compose up

# Build and start Docker container
docker-compose up --build

# If using Podman instead of Docker
podman-compose up
podman-compose up --build

# Check container status
podman ps

# View container logs
podman logs git-playground
```

## Architecture

GitPlayground is built with Next.js using the App Router pattern and TypeScript. The application simulates Git operations without actually performing them on a real Git repository.

### Key Components

1. **FileExplorer** (`src/components/FileExplorer.tsx`)
   - Handles file creation, modification, and deletion operations
   - Displays the current files in the simulated repository

2. **GitVisualizer** (`src/components/GitVisualizer.tsx`) 
   - Visualizes Git commit history
   - Displays branches, commits, and HEAD position
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

1. **Home** (`src/app/page.tsx`) - Landing page with username input
2. **Playground** (`src/app/playground/page.tsx`) - Main interactive Git learning environment

### Flow

1. User enters name on homepage
2. User navigates to playground with username in URL params
3. User can perform file operations, commits, and interact with simulated team members
4. A tutorial guides new users through basic operations
5. User can simulate and resolve Git conflicts with teammate changes
6. Git history is visualized to help users understand operations

### Technologies

- Next.js (App Router)
- TypeScript
- React
- styled-components
- framer-motion
- isomorphic-git (for Git operations simulation)

### Volume Mounting

When running with Docker or Podman in development mode, the repository is configured to mount local files into the container for hot-reload capability:

```yaml
volumes:
  - .:/app:z,U    # Mount local directory with SELinux flags
  - /app/node_modules
user: "root:root" # Set user to root:root to resolve permission issues
```

The `z,U` flags are used for SELinux compatibility, and the root user setting ensures proper file permissions when mounting between host and container.

### Tutorials and Educational Content

The application includes several tutorial components:

1. **GitFlowGuide** (`src/components/GitFlowGuide.js`)
   - Teaches Git Flow branching strategy
   - Includes both ASCII art and graphical visualization modes
   - Shows step-by-step progression through the Git Flow workflow
   - Demonstrates branch operations, merges, and versioning

2. **ConflictGuide** (`src/components/ConflictGuide.js`)
   - Teaches conflict resolution workflows
   - Shows examples of conflict markers and resolution methods

### Best Development Practices

1. **Container-First Development**
   - Prefer running the application in a container for consistent environment
   - Use `podman-compose up --build` (or docker-compose) after code changes
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

