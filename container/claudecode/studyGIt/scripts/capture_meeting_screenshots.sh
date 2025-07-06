#!/bin/bash

# Docker Visualizer Meeting Screenshots Generator
# This script creates screenshots of the Docker Visualizer component in various states
# to showcase its features during the meeting presentation

# Make sure we're in the project root
cd "$(dirname "$0")/.."

# Create screenshots directory if it doesn't exist
mkdir -p screenshots/meeting

echo "📸 Capturing screenshots for meeting presentation..."

# Use puppeteer to capture screenshots in different states
node <<EOF
const puppeteer = require('puppeteer');

(async () => {
  // Launch browser
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  console.log('Navigating to Docker Playground...');
  await page.goto('http://localhost:3000/playground?user=presenter');
  await page.waitForSelector('.dockerVisualizer', { timeout: 10000 });
  
  // Wait for page to fully render
  await page.waitForTimeout(2000);
  
  // Capture empty state
  console.log('Capturing initial empty state');
  await page.screenshot({ path: 'screenshots/meeting/01_initial_state.png' });
  
  // Create a container to show animations
  console.log('Creating container');
  await page.evaluate(() => {
    // Simulate Docker command execution to create a container
    window.dockerSimulator.executeCommand('docker run -d --name web nginx:latest');
  });
  
  // Wait for animation to complete
  await page.waitForTimeout(1500);
  console.log('Capturing container creation');
  await page.screenshot({ path: 'screenshots/meeting/02_container_created.png' });
  
  // Create a network to show relationships
  console.log('Creating network');
  await page.evaluate(() => {
    window.dockerSimulator.executeCommand('docker network create app-net');
    window.dockerSimulator.executeCommand('docker network connect app-net web');
  });
  
  await page.waitForTimeout(1500);
  console.log('Capturing network relationships');
  await page.screenshot({ path: 'screenshots/meeting/03_network_relationships.png' });
  
  // Show educational tooltips
  console.log('Showing educational tooltips');
  await page.evaluate(() => {
    // Click on a container to show tooltips
    document.querySelector('.container').click();
  });
  
  await page.waitForTimeout(500);
  console.log('Capturing educational tooltips');
  await page.screenshot({ path: 'screenshots/meeting/04_educational_tooltips.png' });
  
  // Create volume to show complete visualization
  console.log('Creating volume');
  await page.evaluate(() => {
    window.dockerSimulator.executeCommand('docker volume create data-vol');
    window.dockerSimulator.executeCommand('docker run -d --name db --mount source=data-vol,target=/data postgres:latest');
  });
  
  await page.waitForTimeout(1500);
  console.log('Capturing full visualization with multiple components');
  await page.screenshot({ path: 'screenshots/meeting/05_complete_visualization.png' });
  
  // Close browser
  await browser.close();
  console.log('Screenshots captured successfully!');
})().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
EOF

echo "✅ Screenshots saved to screenshots/meeting/ directory"
echo "Ready for the meeting presentation!"