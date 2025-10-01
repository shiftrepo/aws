# User Interaction Flows - Team Schedule Management System

## Document Version: 1.0
**Created:** October 1, 2025
**Focus:** User journeys, interaction patterns, and flow diagrams

---

## Core User Flows

### 1. Authentication Flow

#### 1.1 User Registration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                        │
└─────────────────────────────────────────────────────────────┘

[Landing Page]
      │
      ├─► Click "Sign Up"
      │
      ▼
┌──────────────────┐
│ Registration     │
│ Form Screen      │
├──────────────────┤
│ - Email          │ ◄─── Validation: Email format
│ - Password       │ ◄─── Validation: Min 8 chars, complexity
│ - Confirm Pass   │ ◄─── Validation: Match password
│ - First Name     │
│ - Last Name      │
│ - Work Hours     │ ◄─── Optional: Set default availability
│   (Optional)     │
└──────────────────┘
      │
      ├─► Submit Form
      │
      ▼
[Loading State]
  - Show spinner
  - "Creating your account..."
      │
      ├─── Success ─────► [Welcome Modal]
      │                   - "Welcome to ScheduTeam!"
      │                   - Quick tips
      │                   - "Get Started" button
      │                         │
      │                         ▼
      │                   [Dashboard]
      │
      └─── Error ───────► [Error Message]
                          - Show inline error
                          - Highlight invalid fields
                          - Suggest corrections
                          - Keep form data
```

**Interaction Details:**
- **Real-time Validation**: Email format check on blur
- **Password Strength Indicator**: Visual bar showing weak/medium/strong
- **Confirmation Match**: Green checkmark when passwords match
- **Animations**:
  - Form fields slide up on focus
  - Success: Confetti animation (subtle)
  - Error: Gentle shake animation

---

#### 1.2 User Login Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      LOGIN FLOW                             │
└─────────────────────────────────────────────────────────────┘

[Landing Page]
      │
      ├─► Click "Login"
      │
      ▼
┌──────────────────┐
│ Login Screen     │
├──────────────────┤
│ - Email          │
│ - Password       │
│ - [Remember Me]  │ ◄─── Checkbox (optional)
│ - Forgot pwd?    │ ◄─── Link to password reset
└──────────────────┘
      │
      ├─► Submit
      │
      ▼
[Authenticating...]
  - Show loading spinner
  - "Signing you in..."
      │
      ├─── Success ─────► Store JWT token
      │                         │
      │                         ▼
      │                   [Dashboard]
      │                   - Fade in animation
      │                   - Welcome back message
      │
      └─── Error ───────► [Error Toast]
                          - "Invalid email or password"
                          - Retry button
                          - Forgot password link
```

**Interaction Details:**
- **Autofocus**: Email field on page load
- **Enter Key**: Submit form
- **Rate Limiting**: Show "Too many attempts, try again in X minutes" after 5 failed attempts
- **Password Toggle**: Eye icon to show/hide password
- **Animations**:
  - Form fade in: 250ms ease-out
  - Error toast: Slide down from top
  - Success: Smooth transition to dashboard

---

### 2. Schedule Creation Flow (Primary Use Case)

#### 2.1 Quick Schedule Creation (Simple Path)

```
┌─────────────────────────────────────────────────────────────┐
│               QUICK SCHEDULE CREATION FLOW                  │
└─────────────────────────────────────────────────────────────┘

[Dashboard]
      │
      ├─► Click "New Meeting" button (prominent CTA)
      │
      ▼
┌──────────────────────────────────────────────────────┐
│         Create Schedule Modal (Step 1 of 2)          │
├──────────────────────────────────────────────────────┤
│  Meeting Title: [                                ]   │
│                                                      │
│  When:                                               │
│  ┌────────────┬────────────┐                        │
│  │   Date     │    Time    │                        │
│  │ [Calendar] │ [08:00 AM] │                        │
│  └────────────┴────────────┘                        │
│                                                      │
│  Duration: [▼ 30 minutes]  ◄─── Dropdown            │
│            (15, 30, 60, 90, 120 min)                │
│                                                      │
│  Who: (Start typing to search)                      │
│  ┌──────────────────────────────────────────┐       │
│  │ [Search teammates...            ]  🔍   │       │
│  │                                          │       │
│  │  Sarah Johnson  ✓  (Available)          │◄──┐   │
│  │  Mike Chen      ⚠  (Conflict at 2 PM)   │   │   │
│  │  + Add more...                           │   │   │
│  └──────────────────────────────────────────┘   │   │
│                                                  │   │
│  ┌─────────────────────────────────────────┐    │   │
│  │ ⚠ Mike has a conflict at this time.    │    │   │
│  │   [Suggest Alternative Times]            │    │   │
│  └─────────────────────────────────────────┘    │   │
│                                                  │   │
│  [Cancel]                      [Next →]         │   │
└──────────────────────────────────────────────────┘   │
      │                                                 │
      ├─► Click "Suggest Alternative Times" ───────────┘
      │         │
      │         ▼
      │   [Smart Scheduling Overlay]
      │   - Show 5 suggested time slots
      │   - Highlight best option (green)
      │   - Click to select
      │
      ├─► Click "Next"
      │
      ▼
┌──────────────────────────────────────────────────────┐
│         Create Schedule Modal (Step 2 of 2)          │
├──────────────────────────────────────────────────────┤
│  Description (Optional):                             │
│  ┌──────────────────────────────────────────┐       │
│  │ [Add meeting notes or agenda...       ]  │       │
│  │                                          │       │
│  └──────────────────────────────────────────┘       │
│                                                      │
│  Location (Optional):                                │
│  [Conference Room A          ]                       │
│                                                      │
│  Recurrence:                                         │
│  [◉ One-time   ○ Recurring]                         │
│                                                      │
│  Summary:                                            │
│  ┌────────────────────────────────────────┐         │
│  │ "Team Standup"                        │         │
│  │ Monday, Oct 2, 2025                   │         │
│  │ 9:00 AM - 9:30 AM (30 minutes)        │         │
│  │ With: Sarah Johnson                   │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  [← Back]              [Create Meeting]             │
└──────────────────────────────────────────────────────┘
      │
      ├─► Click "Create Meeting"
      │
      ▼
[Creating...]
  - Animated checkmark
  - "Scheduling your meeting..."
      │
      ├─── Success ─────► [Success Toast]
      │                   "Meeting created! 🎉"
      │                   "Invitations sent to participants"
      │                         │
      │                         ▼
      │                   [Dashboard]
      │                   - New meeting visible in calendar
      │                   - Gentle highlight animation
      │
      └─── Error ───────► [Error Modal]
                          "Unable to create meeting"
                          - Show reason
                          - Suggest fixes
                          - [Try Again] button
```

**Interaction Details:**

**Date Picker:**
- Calendar widget with month navigation
- Hover: Highlight current day
- Click: Select date, auto-advance to time picker
- Keyboard: Arrow keys to navigate, Enter to select

**Time Picker:**
- 30-minute increments by default
- Scroll through times or type custom time
- Visual indicator for working hours (highlighted)
- Grayed out past times

**Participant Search:**
- Autocomplete with fuzzy matching
- Show avatar and availability status
- Real-time conflict detection
- Max 10 participants warning

**Animations:**
- Modal: Scale in with backdrop fade (300ms)
- Step transition: Slide left/right (250ms)
- Success: Confetti burst animation (500ms)
- Error: Gentle shake (300ms)

---

#### 2.2 Smart Scheduling Flow (Find Best Time)

```
┌─────────────────────────────────────────────────────────────┐
│              SMART SCHEDULING FLOW                          │
└─────────────────────────────────────────────────────────────┘

[Dashboard]
      │
      ├─► Click "Find Best Time" button
      │
      ▼
┌──────────────────────────────────────────────────────┐
│           Smart Scheduling Interface                 │
├──────────────────────────────────────────────────────┤
│  Who needs to attend?                                │
│  ┌──────────────────────────────────────────┐       │
│  │ [Search teammates...            ]  🔍   │       │
│  │                                          │       │
│  │  ✓ Sarah Johnson                        │       │
│  │  ✓ Mike Chen                            │       │
│  │  ✓ Emily Davis                          │       │
│  └──────────────────────────────────────────┘       │
│                                                      │
│  Meeting Duration: [▼ 30 minutes]                   │
│                                                      │
│  Search within:                                      │
│  [◉ Next 7 days   ○ Next 14 days   ○ Custom]       │
│                                                      │
│  Preferences (Optional):                             │
│  [☑] Prefer mornings (9 AM - 12 PM)                │
│  [☑] Prefer weekdays                                │
│  [☐] Avoid lunch hours (12-1 PM)                   │
│                                                      │
│  [Find Available Times]                             │
└──────────────────────────────────────────────────────┘
      │
      ├─► Click "Find Available Times"
      │
      ▼
[Analyzing...]
  - Animated progress bar
  - "Analyzing 3 schedules..."
  - "Found 12 available slots"
      │
      ▼
┌──────────────────────────────────────────────────────┐
│          Available Time Slots (Ranked)               │
├──────────────────────────────────────────────────────┤
│  🏆 Best Match (Score: 95%)                         │
│  ┌────────────────────────────────────────┐         │
│  │ Monday, Oct 2                          │         │
│  │ 10:00 AM - 10:30 AM                    │         │
│  │ All 3 participants available           │         │
│  │                        [Select This]   │ ◄─── Primary
│  └────────────────────────────────────────┘         │
│                                                      │
│  ⭐ Great Option (Score: 88%)                       │
│  ┌────────────────────────────────────────┐         │
│  │ Tuesday, Oct 3                         │         │
│  │ 2:00 PM - 2:30 PM                      │         │
│  │ All 3 participants available           │         │
│  │                        [Select This]   │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  👍 Good Option (Score: 75%)                        │
│  ┌────────────────────────────────────────┐         │
│  │ Wednesday, Oct 4                       │         │
│  │ 4:00 PM - 4:30 PM                      │         │
│  │ All 3 participants available           │         │
│  │                        [Select This]   │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  [Show More Options (9 more)]                       │
│                                                      │
│  [← Back]                                           │
└──────────────────────────────────────────────────────┘
      │
      ├─► Click "Select This" on chosen slot
      │
      ▼
[Go to Schedule Creation Modal - Step 2]
  - Pre-filled with selected time
  - Add title and details
  - Confirm and create
```

**Interaction Details:**

**Slot Ranking:**
- Visual badges (🏆 Best, ⭐ Great, 👍 Good)
- Color-coded borders (green, blue, gray)
- Hover: Show detailed breakdown (working hours, proximity, etc.)

**Slot Card Animations:**
- Stagger animation on load (each card 50ms delay)
- Hover: Lift shadow, scale 1.02
- Click: Pulse animation, then transition

**Expand/Collapse:**
- "Show More Options" accordion
- Smooth height transition (350ms)

---

### 3. Dashboard View & Navigation Flow

#### 3.1 Main Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DASHBOARD VIEW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Top Navigation Bar                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ [Logo] ScheduTeam    🏠 Dashboard  👥 Teams  📅 My Schedule          │ │
│  │                                                     🔔 [Profile 👤]   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Main Content Area                                                          │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                  Quick Actions                             │            │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │            │
│  │  │  + New       │  │  🔍 Find     │  │  👥 Create   │    │            │
│  │  │  Meeting     │  │  Best Time   │  │  Team        │    │            │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
│  ┌─────────────────────────────────┬────────────────────────────────────┐  │
│  │  📅 This Week's Schedule        │  🎯 Upcoming Events                │  │
│  ├─────────────────────────────────┤                                    │  │
│  │                                 │  Today, 10:00 AM                   │  │
│  │  Monday   Oct 2                 │  ┌──────────────────────────┐     │  │
│  │  ┌─────────────────────┐        │  │ Team Standup             │     │  │
│  │  │ 9:00 AM - 9:30 AM   │        │  │ with Sarah, Mike         │     │  │
│  │  │ Team Standup        │        │  │ Conference Room A        │     │  │
│  │  │ 🟢 Confirmed        │        │  └──────────────────────────┘     │  │
│  │  └─────────────────────┘        │                                    │  │
│  │                                 │  Tomorrow, 2:00 PM                 │  │
│  │  ┌─────────────────────┐        │  ┌──────────────────────────┐     │  │
│  │  │ 2:00 PM - 3:00 PM   │        │  │ Client Review            │     │  │
│  │  │ Client Review       │        │  │ with Emily, John         │     │  │
│  │  │ 🟡 Tentative        │        │  │ Zoom Meeting             │     │  │
│  │  └─────────────────────┘        │  └──────────────────────────┘     │  │
│  │                                 │                                    │  │
│  │  Tuesday  Oct 3                 │  [View All →]                      │  │
│  │  (No events)                    │                                    │  │
│  │                                 │                                    │  │
│  │  Wednesday Oct 4                │                                    │  │
│  │  ┌─────────────────────┐        │                                    │  │
│  │  │ 10:00 AM - 11:00 AM │        │                                    │  │
│  │  │ Sprint Planning     │        │                                    │  │
│  │  │ 🟢 Confirmed        │        │                                    │  │
│  │  └─────────────────────┘        │                                    │  │
│  │                                 │                                    │  │
│  └─────────────────────────────────┴────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────┬────────────────────────────────────┐  │
│  │  👥 My Teams (3)                │  ⚡ Quick Stats                    │  │
│  ├─────────────────────────────────┤                                    │  │
│  │  Engineering Team (12 members) │  📊 This Week:                     │  │
│  │  Marketing Team (8 members)    │  • 8 meetings scheduled            │  │
│  │  Executive Team (5 members)    │  • 12 hours in meetings            │  │
│  │                                 │  • 3 invitations pending           │  │
│  │  [+ Create New Team]            │                                    │  │
│  └─────────────────────────────────┴────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Navigation Interactions:**
- Top nav: Hover shows tooltip, click navigates with smooth transition
- Notification bell: Badge with count, dropdown on click
- Profile menu: Dropdown with Settings, Availability, Logout

**Quick Actions:**
- Large, tap-friendly buttons (min 44px height)
- Hover: Lift shadow, scale 1.03
- Click: Scale down 0.98, then navigate

---

### 4. Calendar Grid Interaction Flow

#### 4.1 Weekly Calendar View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WEEKLY CALENDAR VIEW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [← Oct 2025 →]              Week of October 2 - 8              [Today]    │
│                                                                             │
│  Time    Mon     Tue     Wed     Thu     Fri     Sat     Sun               │
│  ─────┬────────┬────────┬────────┬────────┬────────┬────────┬────────      │
│  8:00 │        │        │        │        │        │        │              │
│       │        │        │        │        │        │        │              │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│  9:00 │╔══════╗│        │        │        │        │        │              │
│       │║Standup│        │        │        │        │        │              │
│  9:30 │╚══════╝│        │        │        │        │        │              │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│ 10:00 │        │╔══════╗│╔══════╗│        │        │        │              │
│       │        │║Client║│║Sprint║        │        │        │              │
│ 10:30 │        │║Review║│║Plan  ║        │        │        │              │
│       │        │╚══════╝│║      ║        │        │        │              │
│ 11:00 │        │        │╚══════╝│        │        │        │              │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│ 12:00 │ (Lunch time - grayed out)                                          │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│  1:00 │        │        │        │        │        │        │              │
│       │        │        │        │        │        │        │              │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│  2:00 │        │        │        │╔══════╗│        │        │              │
│       │        │        │        │║1-on-1║        │        │              │
│  2:30 │        │        │        │╚══════╝│        │        │              │
│  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────      │
│  ... (continues to 6:00 PM)                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Interaction Behaviors:**

**Hover on Time Slot:**
```
┌────────────────────────┐
│  Monday, 10:00 AM      │
│  [+ Create Meeting]    │ ◄─── Button appears
└────────────────────────┘
- Background: Soft blue highlight
- Cursor: Pointer
- Animation: Fade in 150ms
```

**Hover on Meeting Block:**
```
┌────────────────────────┐
│  Team Standup          │
│  9:00 - 9:30 AM        │
│  📍 Room A             │
│  👥 3 participants     │
│  ─────────────────     │
│  [Edit] [Delete]       │ ◄─── Action buttons
└────────────────────────┘
- Shadow: Elevate (shadow-md)
- Scale: 1.02
- Tooltip with details
```

**Click on Meeting Block:**
```
[Meeting Detail Modal Opens]
- Smooth scale-in animation (250ms)
- Backdrop blur effect
- Shows full details, participants, actions
```

**Drag & Drop (Future Feature):**
```
[User drags meeting block]
  │
  ├─► Lift shadow, opacity 0.8
  │   Follow cursor position
  │
  ├─► Hover over valid time slot
  │   └─► Highlight target slot (green outline)
  │
  ├─► Drop on valid slot
  │   └─► Animate move to new position
  │       Show "Meeting rescheduled" toast
  │
  └─► Drop on invalid slot (conflict)
      └─► Snap back to original position
          Show error message
```

---

### 5. Mobile Interaction Patterns

#### 5.1 Mobile Navigation

```
┌──────────────────────┐
│   ☰  ScheduTeam  🔔 │ ◄─── Hamburger menu, notifications
├──────────────────────┤
│                      │
│  [Bottom Tab Bar]    │
│                      │
│  🏠      📅      👥  │
│  Home  Calendar Teams│
│                      │
└──────────────────────┘
```

**Hamburger Menu (Slide-in):**
- Swipe right from left edge: Open menu
- Tap outside: Close menu
- Animation: Slide from left (300ms)

**Bottom Navigation:**
- Tap: Switch view, highlight active tab
- Hold: Show tooltip (optional)
- Swipe gesture between tabs (optional)

#### 5.2 Mobile Schedule Creation

```
[Simplified Flow - Single Page]

┌──────────────────────┐
│  New Meeting         │
├──────────────────────┤
│  Title:              │
│  [              ]    │
│                      │
│  When:               │
│  [📅 Select Date]   │ ◄─── Opens date picker overlay
│  [⏰ Select Time]   │ ◄─── Opens time picker overlay
│                      │
│  Duration:           │
│  [● 30 min ○ 1 hr]  │ ◄─── Radio buttons
│                      │
│  Who:                │
│  [+ Add People]      │ ◄─── Opens contact picker
│                      │
│  ┌────────────────┐  │
│  │ Create Meeting │  │ ◄─── Full-width button
│  └────────────────┘  │
└──────────────────────┘
```

**Touch Interactions:**
- Input focus: Zoom to prevent layout shift
- Date/time picker: Native pickers for better UX
- Scroll momentum: Smooth, natural feel

---

## Animation Specifications

### Page Transitions

```javascript
// Fade + Slide Navigation
const pageTransition = {
  enter: {
    opacity: 0,
    transform: 'translateX(20px)'
  },
  active: {
    opacity: 1,
    transform: 'translateX(0)'
  },
  exit: {
    opacity: 0,
    transform: 'translateX(-20px)'
  },
  duration: 250,
  easing: 'ease-out'
}
```

### Microinteractions

**Button Click:**
```css
.button:active {
  transform: scale(0.98);
  transition: transform 100ms ease-out;
}
```

**Card Hover:**
```css
.card {
  transition: all 250ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
```

**Loading Spinner:**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 800ms linear infinite;
}
```

**Success Checkmark:**
```css
@keyframes checkmark {
  0% {
    stroke-dashoffset: 50;
    opacity: 0;
  }
  50% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 1;
    transform: scale(1.1);
  }
}

.checkmark {
  animation: checkmark 500ms ease-out forwards;
}
```

---

## Accessibility Flow Considerations

### Keyboard Navigation

**Tab Order Priority:**
1. Skip to main content link
2. Logo (home link)
3. Main navigation items
4. Primary action buttons
5. Content interactive elements
6. Secondary actions
7. Footer links

**Keyboard Shortcuts:**
- `N`: New meeting
- `F`: Find best time
- `T`: Go to teams
- `D`: Go to dashboard
- `/`: Focus search
- `Esc`: Close modal/overlay

### Screen Reader Announcements

```html
<!-- Live region for dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  {statusMessage}
</div>

<!-- Example announcements -->
"Meeting created successfully. Team Standup scheduled for Monday, October 2 at 9:00 AM"
"Conflict detected. Mike Chen has an existing meeting at this time."
"Loading available time slots. Please wait."
```

---

## Error States & Recovery Flows

### Network Error
```
[Action fails due to network]
  │
  ▼
[Error Toast]
"Unable to connect. Please check your internet connection."
  │
  ├─► [Retry] button
  └─► Auto-retry after 5 seconds (with countdown)
```

### Validation Error
```
[Form submission fails validation]
  │
  ▼
[Inline Error Messages]
- Scroll to first error field
- Highlight field with red border
- Show specific error message
- Focus field for correction
```

### Session Expiration
```
[JWT token expired]
  │
  ▼
[Modal Overlay]
"Your session has expired for security."
  │
  ├─► [Login Again] ─── Redirect to login (preserve current page)
  └─► Form data preserved for after re-login
```

---

## Summary of Key Interaction Principles

1. **Progressive Disclosure**: Show basic options first, reveal advanced on demand
2. **Immediate Feedback**: Every action receives visual confirmation
3. **Forgiving Design**: Easy undo, clear error messages, helpful suggestions
4. **Touch-Friendly**: 44px minimum touch targets, appropriate spacing
5. **Smooth Animations**: Enhance, don't distract; respect prefers-reduced-motion
6. **Context Preservation**: Maintain user's place when navigating back
7. **Predictable Patterns**: Consistent interactions across similar components

---

**Next Document:** Screen-by-Screen Layouts & Mockup Descriptions
