#!/bin/bash

echo "=== Coverage Mapping Debug Test ==="
echo "Testing with real JaCoCo data from user report"
echo

# Change to the test directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo "Test structure:"
find . -name "*.java" -o -name "*.xml" | sort

echo
echo "=== Running tool with DEBUG logging ==="

# Run the tool with detailed debug logging
java -jar ../target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output debug-test-result.xlsx \
  --log-level DEBUG 2>&1 | tee debug-output.log

echo
echo "=== Debug Output Analysis ==="
echo "Coverage entries extracted:"
grep -E "\[Coverage Debug\].*coverage entry" debug-output.log | head -10

echo
echo "Test cases found:"
grep -E "\[Coverage Debug\].*test case" debug-output.log | head -10

echo
echo "Coverage merge results:"
grep -E "\[Coverage Debug\].*merge" debug-output.log

echo
echo "Generated files:"
ls -la *.xlsx *.log 2>/dev/null || echo "No output files generated"

echo
echo "=== Investigation Complete ==="