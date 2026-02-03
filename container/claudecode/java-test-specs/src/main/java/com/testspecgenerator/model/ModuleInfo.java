package com.testspecgenerator.model;

import java.nio.file.Path;
import java.util.Objects;

/**
 * Represents information about a Maven module including its structure and paths.
 * Used for multi-module project processing.
 */
public class ModuleInfo {
    private final String moduleName;
    private final Path moduleRoot;
    private final Path sourceDir;
    private final Path testDir;
    private final Path coverageDir;
    private final Path pomPath;
    private final boolean isValid;
    private final String validationError;

    private ModuleInfo(Builder builder) {
        this.moduleName = builder.moduleName;
        this.moduleRoot = builder.moduleRoot;
        this.sourceDir = builder.sourceDir;
        this.testDir = builder.testDir;
        this.coverageDir = builder.coverageDir;
        this.pomPath = builder.pomPath;
        this.isValid = builder.isValid;
        this.validationError = builder.validationError;
    }

    public String getModuleName() {
        return moduleName;
    }

    public Path getModuleRoot() {
        return moduleRoot;
    }

    public Path getSourceDir() {
        return sourceDir;
    }

    public Path getTestDir() {
        return testDir;
    }

    public Path getCoverageDir() {
        return coverageDir;
    }

    public Path getPomPath() {
        return pomPath;
    }

    public boolean isValid() {
        return isValid;
    }

    public String getValidationError() {
        return validationError;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ModuleInfo that = (ModuleInfo) o;
        return Objects.equals(moduleName, that.moduleName) &&
               Objects.equals(moduleRoot, that.moduleRoot);
    }

    @Override
    public int hashCode() {
        return Objects.hash(moduleName, moduleRoot);
    }

    @Override
    public String toString() {
        return String.format("ModuleInfo{name='%s', root='%s', valid=%s}",
                           moduleName, moduleRoot, isValid);
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String moduleName;
        private Path moduleRoot;
        private Path sourceDir;
        private Path testDir;
        private Path coverageDir;
        private Path pomPath;
        private boolean isValid = true;
        private String validationError;

        public Builder moduleName(String moduleName) {
            this.moduleName = moduleName;
            return this;
        }

        public Builder moduleRoot(Path moduleRoot) {
            this.moduleRoot = moduleRoot;
            return this;
        }

        public Builder sourceDir(Path sourceDir) {
            this.sourceDir = sourceDir;
            return this;
        }

        public Builder testDir(Path testDir) {
            this.testDir = testDir;
            return this;
        }

        public Builder coverageDir(Path coverageDir) {
            this.coverageDir = coverageDir;
            return this;
        }

        public Builder pomPath(Path pomPath) {
            this.pomPath = pomPath;
            return this;
        }

        public Builder isValid(boolean isValid) {
            this.isValid = isValid;
            return this;
        }

        public Builder validationError(String validationError) {
            this.validationError = validationError;
            this.isValid = false;
            return this;
        }

        public ModuleInfo build() {
            return new ModuleInfo(this);
        }
    }
}