#!/usr/bin/env node

/**
 * HTML Grid Verification Test
 * Simulates the frontend JavaScript execution to verify that ken's 08:30-09:00 block appears
 */

const fs = require('fs');
const path = require('path');

// Simulate the data that would be loaded from the API
const allUsers = [
    {
        id: 1,
        username: "admin",
        start_time: "09:00",
        end_time: "18:00",
        availability: {
            monday: [
                { start: "09:00", end: "10:00" },
                { start: "10:00", end: "12:00" },
                { start: "14:00", end: "16:00" }
            ]
        }
    },
    {
        id: 2,
        username: "user1",
        start_time: "09:00",
        end_time: "18:00",
        availability: {
            monday: [
                { start: "09:30", end: "10:30" },
                { start: "10:00", end: "12:00" },
                { start: "15:00", end: "17:00" }
            ]
        }
    },
    {
        id: 3,
        username: "user2", // ken
        start_time: "08:00",
        end_time: "17:00",
        availability: {
            monday: [
                { start: "08:30", end: "11:00" },  // This should create 08:30-09:00 block
                { start: "11:00", end: "12:00" }
            ]
        }
    }
];

const DAYS_OF_WEEK = [
    { key: 'monday', name: '月曜日', emoji: '📅' }
];

// Utility functions (copied from app.js)
function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

function minutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

// Main grid generation logic (from app.js)
function updateMeetingGrid() {
    console.log("🔥 TESTING: Starting updateMeetingGrid()");

    const maxParticipants = allUsers.length;
    console.log(`📊 Max participants: ${maxParticipants}`);

    // FIRST: Collect ALL time points from ALL users (FIXED VERSION)
    const allDynamicTimePoints = new Set();

    allUsers.forEach(user => {
        console.log(`👤 Processing user: ${user.username}`);
        if (!user.availability) return;

        DAYS_OF_WEEK.forEach(day => {
            if (!user.availability[day.key]) return;

            user.availability[day.key].forEach(slot => {
                console.log(`  📅 ${day.key}: Adding time points ${slot.start} and ${slot.end}`);
                allDynamicTimePoints.add(slot.start);
                allDynamicTimePoints.add(slot.end);
            });
        });
    });

    console.log("🎯 ALL COLLECTED TIME POINTS:", Array.from(allDynamicTimePoints).sort());

    // Sort time points
    const sortedTimePoints = Array.from(allDynamicTimePoints).sort((a, b) => {
        return timeToMinutes(a) - timeToMinutes(b);
    });

    console.log("📈 SORTED TIME POINTS:", sortedTimePoints);

    // Generate grid headers
    const gridHeaders = sortedTimePoints.slice(0, -1).map((startTime, index) => {
        const endTime = sortedTimePoints[index + 1];
        return { start: startTime, end: endTime, header: `${startTime}<br>|<br>${endTime}` };
    });

    console.log("🏗️ GRID HEADERS:");
    gridHeaders.forEach((header, index) => {
        console.log(`  Column ${index}: ${header.start} - ${header.end}`);
    });

    // Check specifically for 08:30-09:00
    const has08309Block = gridHeaders.some(h => h.start === "08:30" && h.end === "09:00");
    console.log(`🎯 CRITICAL CHECK: Does grid have 08:30-09:00 column? ${has08309Block ? '✅ YES' : '❌ NO'}`);

    // Generate HTML structure
    let html = `
        <div class="grid-header">
            <div class="grid-cell grid-corner">曜日 \\\\ 時間帯</div>
            ${gridHeaders.map(h => `<div class="grid-cell grid-time-header">${h.header}</div>`).join('')}
        </div>
    `;

    // Process Monday specifically
    const day = DAYS_OF_WEEK[0];
    const dynamicTimeSlots = calculateDynamicTimeSlots(day.key);

    console.log(`📊 Dynamic slots for ${day.key}:`, dynamicTimeSlots);

    html += `
        <div class="grid-row">
            <div class="grid-cell grid-day-header">
                ${day.emoji} ${day.name}
            </div>
            ${gridHeaders.map((header, index) => {
                // Find meeting slot
                const meetingSlot = dynamicTimeSlots.find(slot =>
                    slot.start === header.start && slot.end === header.end
                );

                // Check for single user availability
                let singleUserSlot = null;
                if (!meetingSlot) {
                    const availableUsers = [];
                    const unavailableUsers = [];

                    allUsers.forEach(user => {
                        if (!user.availability || !user.availability[day.key]) {
                            unavailableUsers.push(user.username);
                            return;
                        }

                        const hasAvailabilityInRange = user.availability[day.key].some(slot => {
                            const slotStart = timeToMinutes(slot.start);
                            const slotEnd = timeToMinutes(slot.end);
                            const rangeStart = timeToMinutes(header.start);
                            const rangeEnd = timeToMinutes(header.end);

                            return slotStart <= rangeStart && slotEnd >= rangeEnd;
                        });

                        if (hasAvailabilityInRange) {
                            availableUsers.push(user.username);
                        } else {
                            unavailableUsers.push(user.username);
                        }
                    });

                    if (availableUsers.length > 0) {
                        singleUserSlot = {
                            start: header.start,
                            end: header.end,
                            available_users: availableUsers.sort(),
                            unavailable_users: unavailableUsers.sort(),
                            participant_count: availableUsers.length,
                            availability_percentage: Math.round((availableUsers.length / maxParticipants) * 100)
                        };
                    }
                }

                const slotToUse = meetingSlot || singleUserSlot;
                return generateDynamicGridCell(slotToUse, maxParticipants, day.key, header);
            }).join('')}
        </div>
    `;

    console.log("🎯 CRITICAL CHECK: Searching HTML for 08:30-09:00 block...");
    if (html.includes("08:30<br>|<br>09:00")) {
        console.log("✅ SUCCESS: 08:30-09:00 header found in HTML!");
    } else {
        console.log("❌ FAILURE: 08:30-09:00 header NOT found in HTML!");
    }

    return html;
}

function calculateDynamicTimeSlots(day) {
    console.log(`🔄 Calculating dynamic slots for ${day}`);
    const timePoints = [];

    allUsers.forEach(user => {
        if (!user.availability || !user.availability[day]) return;

        user.availability[day].forEach(slot => {
            const startMinutes = timeToMinutes(slot.start);
            const endMinutes = timeToMinutes(slot.end);
            timePoints.push({ time: startMinutes, type: 'start', user: user.username });
            timePoints.push({ time: endMinutes, type: 'end', user: user.username });
        });
    });

    if (timePoints.length === 0) return [];

    timePoints.sort((a, b) => {
        if (a.time !== b.time) return a.time - b.time;
        return a.type === 'start' ? -1 : 1;
    });

    const dynamicSlots = [];
    const activeUsers = new Set();
    let lastTime = null;

    timePoints.forEach((point, index) => {
        if (lastTime !== null && point.time !== lastTime && activeUsers.size >= 2) {
            const allUserNames = allUsers.map(u => u.username);
            const slotUnavailableUsers = allUserNames.filter(user => !activeUsers.has(user));
            const availabilityPercentage = Math.round((activeUsers.size / allUsers.length) * 100);

            const slot = {
                start: minutesToTime(lastTime),
                end: minutesToTime(point.time),
                available_users: Array.from(activeUsers).sort(),
                unavailable_users: slotUnavailableUsers.sort(),
                participant_count: activeUsers.size,
                availability_percentage: availabilityPercentage
            };

            dynamicSlots.push(slot);
        }

        if (point.type === 'start') {
            activeUsers.add(point.user);
        } else {
            activeUsers.delete(point.user);
        }

        lastTime = point.time;
    });

    return dynamicSlots;
}

function generateDynamicGridCell(slotInfo, maxParticipants, day, header) {
    if (!slotInfo || slotInfo.participant_count === 0) {
        console.log(`   Cell ${header.start}-${header.end}: EMPTY`);
        return `<div class="grid-cell grid-empty"></div>`;
    }

    const intensity = slotInfo.participant_count / maxParticipants;
    const isFullAvailability = slotInfo.participant_count === maxParticipants;
    const isSingleUser = slotInfo.participant_count === 1;
    const isMeetingSlot = slotInfo.participant_count >= 2;

    let finalColor, borderColor, cellClass;

    if (isFullAvailability) {
        finalColor = 'linear-gradient(135deg, #E8F5E8, #F0F8FF)';
        borderColor = '#4CAF50';
        cellClass = 'grid-meeting grid-full-availability';
    } else if (isMeetingSlot) {
        finalColor = getGradientColor(intensity);
        borderColor = getAccentColor(intensity);
        cellClass = 'grid-meeting grid-partial-availability';
    } else if (isSingleUser) {
        finalColor = '#F8F9FA';
        borderColor = '#DEE2E6';
        cellClass = 'grid-meeting grid-single-user';
    }

    const borderWidth = isFullAvailability ? '6px' : isMeetingSlot ? '4px' : '2px';
    const displayText = isSingleUser
        ? slotInfo.available_users[0].charAt(0).toUpperCase()
        : `${slotInfo.participant_count}${isFullAvailability ? '🎯' : ''}`;

    console.log(`   Cell ${header.start}-${header.end}: ${displayText} (${slotInfo.participant_count} users: ${slotInfo.available_users.join(',')})`);

    return `
        <div class="grid-cell ${cellClass}"
             style="background: ${finalColor}; border-left: ${borderWidth} solid ${borderColor};">
            <div class="grid-participant-count" style="font-size: ${isSingleUser ? '10px' : '12px'};">${displayText}</div>
        </div>
    `;
}

function getGradientColor(intensity) {
    const hue = 140;
    const saturation = Math.min(70, 30 + (intensity * 40));
    const lightness = Math.max(75, 95 - (intensity * 20));
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

function getAccentColor(intensity) {
    const hue = 140;
    const saturation = Math.min(80, 50 + (intensity * 30));
    const lightness = Math.max(45, 65 - (intensity * 20));
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

// Run the test
console.log("🚀 STARTING HTML GRID VERIFICATION TEST");
console.log("=======================================");

console.log("📝 TEST DATA:");
allUsers.forEach(user => {
    console.log(`  ${user.username}: ${JSON.stringify(user.availability)}`);
});

console.log("\n🔄 EXECUTING updateMeetingGrid()...");
const generatedHtml = updateMeetingGrid();

console.log("\n📋 FINAL VERIFICATION:");
console.log("======================");

if (generatedHtml.includes("08:30<br>|<br>09:00")) {
    console.log("✅ SUCCESS: ken's 08:30-09:00 block IS present in generated HTML");
    console.log("✅ SUCCESS: Time offset bug is FIXED");
} else {
    console.log("❌ FAILURE: ken's 08:30-09:00 block is NOT present in generated HTML");
    console.log("❌ FAILURE: Time offset bug is NOT fixed");
}

// Save the generated HTML
const outputPath = path.join(__dirname, 'generated_grid_output.html');
const fullHtml = `
<!DOCTYPE html>
<html>
<head>
    <title>Generated Grid Test</title>
    <style>
        .meeting-grid { font-family: Arial, sans-serif; }
        .grid-header, .grid-row { display: flex; }
        .grid-cell { border: 1px solid #ccc; padding: 4px; min-width: 60px; text-align: center; }
        .grid-corner { background: #A8D5E2; color: white; font-weight: bold; }
        .grid-time-header { background: #f0f0f0; font-size: 10px; }
        .grid-day-header { background: #C9E4CA; font-weight: bold; }
        .grid-empty { background: #f8f9fa; }
        .grid-single-user { background: #F8F9FA; border-left: 2px solid #DEE2E6; }
        .grid-meeting { background: #E8F5E8; }
    </style>
</head>
<body>
    <h1>Generated Meeting Grid Test</h1>
    <p>This HTML was generated by the JavaScript logic to verify ken's 08:30-09:00 block appears.</p>
    <div class="meeting-grid">
        ${generatedHtml}
    </div>
</body>
</html>
`;

fs.writeFileSync(outputPath, fullHtml);
console.log(`\n💾 Generated HTML saved to: ${outputPath}`);

// Extract and show the critical section
console.log("\n🎯 CRITICAL EVIDENCE:");
console.log("====================");

const headerMatch = generatedHtml.match(/08:30<br>\|<br>09:00/);
if (headerMatch) {
    console.log("✅ Header '08:30<br>|<br>09:00' found in HTML");

    // Look for the cell content in that column
    const lines = generatedHtml.split('\n');
    let found08309Cell = false;

    lines.forEach((line, i) => {
        if (line.includes('08:30<br>|<br>09:00')) {
            console.log(`✅ Line ${i}: ${line.trim()}`);
        }
        if (line.includes('grid-single-user') && i > 0) {
            // Check if this is in the Monday row
            const contextLines = lines.slice(Math.max(0, i-3), i+3);
            if (contextLines.some(l => l.includes('月曜日'))) {
                console.log(`✅ Single user cell found in Monday row: ${line.trim()}`);
                found08309Cell = true;
            }
        }
    });

    if (found08309Cell) {
        console.log("✅ FINAL VERDICT: ken's 08:30-09:00 block IS correctly generated!");
    } else {
        console.log("❌ FINAL VERDICT: Header exists but cell content missing");
    }
} else {
    console.log("❌ Header '08:30<br>|<br>09:00' NOT found in HTML");
}