package com.testspecgenerator.model;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Represents the processing results for a single module including test cases,
 * coverage data, and processing status information.
 *
 * SIMPLIFIED: coverageData is now List<CoverageInfo> (no Map conversion)
 */
public class ModuleResult {
    private final ModuleInfo moduleInfo;
    private final List<TestCaseInfo> testCases;
    private final List<CoverageInfo> coverageData;  // SIMPLIFIED: Changed from Map to List
    private final ProcessingStatus processingStatus;
    private final String errorMessage;
    private final long processingTimeMs;

    private ModuleResult(Builder builder) {
        this.moduleInfo = builder.moduleInfo;
        this.testCases = builder.testCases;
        this.coverageData = builder.coverageData;
        this.processingStatus = builder.processingStatus;
        this.errorMessage = builder.errorMessage;
        this.processingTimeMs = builder.processingTimeMs;
    }

    public ModuleInfo getModuleInfo() {
        return moduleInfo;
    }

    public List<TestCaseInfo> getTestCases() {
        return testCases;
    }

    public List<CoverageInfo> getCoverageData() {  // SIMPLIFIED: Changed return type
        return coverageData;
    }

    public ProcessingStatus getProcessingStatus() {
        return processingStatus;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public long getProcessingTimeMs() {
        return processingTimeMs;
    }

    public boolean isSuccessful() {
        return processingStatus == ProcessingStatus.SUCCESS;
    }

    public boolean hasTestCases() {
        return testCases != null && !testCases.isEmpty();
    }

    public boolean hasCoverageData() {
        return coverageData != null && !coverageData.isEmpty();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ModuleResult that = (ModuleResult) o;
        return Objects.equals(moduleInfo, that.moduleInfo);
    }

    @Override
    public int hashCode() {
        return Objects.hash(moduleInfo);
    }

    @Override
    public String toString() {
        return String.format("ModuleResult{module='%s', status=%s, testCases=%d, hasError=%s}",
                           moduleInfo != null ? moduleInfo.getModuleName() : "unknown",
                           processingStatus,
                           testCases != null ? testCases.size() : 0,
                           errorMessage != null);
    }

    public enum ProcessingStatus {
        SUCCESS,
        PARTIAL_SUCCESS,
        FAILED,
        SKIPPED
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private ModuleInfo moduleInfo;
        private List<TestCaseInfo> testCases;
        private List<CoverageInfo> coverageData;  // SIMPLIFIED: Changed from Map to List
        private ProcessingStatus processingStatus = ProcessingStatus.SUCCESS;
        private String errorMessage;
        private long processingTimeMs;

        public Builder moduleInfo(ModuleInfo moduleInfo) {
            this.moduleInfo = moduleInfo;
            return this;
        }

        public Builder testCases(List<TestCaseInfo> testCases) {
            this.testCases = testCases;
            return this;
        }

        public Builder coverageData(List<CoverageInfo> coverageData) {  // SIMPLIFIED: Changed parameter type
            this.coverageData = coverageData;
            return this;
        }

        public Builder processingStatus(ProcessingStatus processingStatus) {
            this.processingStatus = processingStatus;
            return this;
        }

        public Builder errorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
            if (errorMessage != null && processingStatus == ProcessingStatus.SUCCESS) {
                this.processingStatus = ProcessingStatus.PARTIAL_SUCCESS;
            }
            return this;
        }

        public Builder processingTimeMs(long processingTimeMs) {
            this.processingTimeMs = processingTimeMs;
            return this;
        }

        public Builder failed(String errorMessage) {
            this.processingStatus = ProcessingStatus.FAILED;
            this.errorMessage = errorMessage;
            return this;
        }

        public ModuleResult build() {
            return new ModuleResult(this);
        }
    }
}