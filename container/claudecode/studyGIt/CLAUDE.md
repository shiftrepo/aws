# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitPlayground is an interactive web application designed to help beginners learn Git operations in a team development context. The application simulates file management, commit visualizations, team collaboration, and conflict resolution through an interactive interface.

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