# Screen Layouts & UI Mockups - Team Schedule Management System

## Document Version: 1.0
**Created:** October 1, 2025
**Purpose:** Detailed screen-by-screen layout specifications with visual mockup descriptions

---

## Screen Index

1. [Landing Page](#1-landing-page)
2. [Login Screen](#2-login-screen)
3. [Registration Screen](#3-registration-screen)
4. [Main Dashboard](#4-main-dashboard)
5. [Calendar View](#5-calendar-view)
6. [Schedule Creation Modal](#6-schedule-creation-modal)
7. [Smart Scheduling Interface](#7-smart-scheduling-interface)
8. [Team Management](#8-team-management)
9. [User Profile & Settings](#9-user-profile--settings)
10. [Availability Settings](#10-availability-settings)
11. [Mobile Views](#11-mobile-views)

---

## 1. Landing Page

### Layout Structure (Desktop: 1280px × 800px)

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (Fixed, Transparent → Solid on scroll)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [Logo] ScheduTeam          [Features] [Pricing] [Login] │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                     Hero Section                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │        Schedule meetings without the back-and-forth      │  │
│  │                                                          │  │
│  │      Smart scheduling for teams that work together       │  │
│  │                                                          │  │
│  │    ┌──────────────────┐        ┌──────────────────┐    │  │
│  │    │  Get Started →   │        │  Watch Demo ▶    │    │  │
│  │    └──────────────────┘        └──────────────────┘    │  │
│  │                                                          │  │
│  │            [Animated Calendar Illustration]              │  │
│  │            (Showing time slots aligning)                 │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   Features Section (3 columns)                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   🤖 Smart   │    │   ⚡ Fast    │    │   👥 Teams   │    │
│  │  Scheduling  │    │  Conflict    │    │ Collaboration│    │
│  │              │    │  Detection   │    │              │    │
│  │  Find best   │    │  Automatic   │    │  Manage team │    │
│  │  meeting     │    │  overlap     │    │  schedules   │    │
│  │  times auto  │    │  checking    │    │  easily      │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                Footer (Soft Gray Background)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  © 2025 ScheduTeam  |  Privacy  |  Terms  |  Contact    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Color Scheme:**
- Background: Gradient from `#F0F9FF` (soft blue) to `#FFFFFF`
- Header: White with subtle shadow on scroll
- Primary CTA: `--color-primary-400` with hover lift
- Secondary CTA: Outline style with `--color-primary-400` border

**Typography:**
- Hero Title: `--text-4xl`, `--font-bold`, `--color-gray-800`
- Hero Subtitle: `--text-xl`, `--font-normal`, `--color-gray-600`
- Feature Cards: `--text-lg` headings, `--text-base` body

**Animations:**
- Hero illustration: Gentle floating animation (3s loop)
- Feature cards: Fade up on scroll (stagger 100ms)
- CTA buttons: Hover lift with shadow (250ms)

---

## 2. Login Screen

### Layout Structure (Centered Modal: 400px × 500px)

```
┌────────────────────────────────────────────┐
│                                            │
│              [Logo + App Name]             │
│                                            │
│           Welcome back! 👋                 │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Email Address                       │ │
│  │  [                                ]  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Password                            │ │
│  │  [                              ]👁  │ │ ◄── Show/hide toggle
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │ ☐ Remember me    Forgot password?  │  │
│  └─────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │         Sign In                      │ │ ◄── Full-width button
│  └──────────────────────────────────────┘ │
│                                            │
│  ─────────── or continue with ───────────  │
│                                            │
│  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │Google│  │GitHub│  │ SSO  │            │ ◄── Social login (optional)
│  └──────┘  └──────┘  └──────┘            │
│                                            │
│       Don't have an account? Sign up      │ ◄── Link
│                                            │
└────────────────────────────────────────────┘
```

### Visual Design Details

**Background:**
- Light gradient: `linear-gradient(135deg, #E6F4FF 0%, #F0FFF4 100%)`
- Centered white card with `--shadow-lg`

**Input Fields:**
- Height: `--input-height` (44px)
- Border: `1px solid --color-gray-300`
- Focus: `--input-focus-ring` (blue ring)
- Icon positioning: Absolute right, padding-right compensation

**Button States:**
- Default: `--color-primary-400` background
- Hover: Scale 1.02, `--shadow-primary`
- Active: Scale 0.98
- Disabled: Opacity 0.5, no hover

**Animations:**
- Card entrance: Scale from 0.95, fade in (300ms)
- Input focus: Ring expands from 0 (150ms)
- Error shake: Horizontal translate ±5px (300ms)

---

## 3. Registration Screen

### Layout Structure (Centered: 480px × 700px)

```
┌────────────────────────────────────────────┐
│                                            │
│          Create your account 🎉            │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  First Name                          │ │
│  │  [                                ]  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Last Name                           │ │
│  │  [                                ]  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Email Address                       │ │
│  │  [                                ]✓ │ │ ◄── Validation checkmark
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Password                            │ │
│  │  [                              ]👁  │ │
│  │  ████████░░░░░░░░ Strong             │ │ ◄── Strength indicator
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Confirm Password                    │ │
│  │  [                              ]✓   │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Work Hours (Optional)               │ │
│  │  [9:00 AM] to [5:00 PM]              │ │ ◄── Dropdowns
│  └──────────────────────────────────────┘ │
│                                            │
│  ☑ I agree to Terms and Privacy Policy   │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │         Create Account               │ │
│  └──────────────────────────────────────┘ │
│                                            │
│       Already have an account? Sign in    │
│                                            │
└────────────────────────────────────────────┘
```

### Visual Design Details

**Password Strength Indicator:**
- Weak (0-40%): Red bar, "Weak" label
- Medium (41-70%): Yellow bar, "Medium" label
- Strong (71-100%): Green bar, "Strong" label
- Animation: Bar grows with typing (smooth transition)

**Real-time Validation:**
- Email: Check format on blur, show ✓ or ✗
- Password match: Live comparison, show ✓ when matching
- Required fields: Red border if empty on submit attempt

**Animations:**
- Field-by-field reveal: Slide up with 50ms stagger
- Validation icons: Scale in (200ms)
- Success: Confetti burst, then transition to welcome modal

---

## 4. Main Dashboard

### Layout Structure (Full Width: 1280px × 900px)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Top Navigation (Fixed, 64px height)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ [Logo] ScheduTeam    🏠 Dashboard  📅 Calendar  👥 Teams           │ │
│  │                                              🔔(3)  Sarah J. 👤 ▼  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────────────┤
│  Content Area (Padding: 32px)                                             │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Good morning, Sarah! ☀️                                           │ │
│  │  You have 3 meetings today                                          │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Quick Actions (3 cards, horizontal)                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   + New         │  │   🔍 Find       │  │   👥 Create     │         │
│  │   Meeting       │  │   Best Time     │  │   Team          │         │
│  │                 │  │                 │  │                 │         │
│  │  Schedule a new │  │  Let AI suggest │  │  Set up a new   │         │
│  │  meeting        │  │  optimal times  │  │  team           │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                           │
│  Main Content (2-column grid)                                             │
│  ┌──────────────────────────────────────┬──────────────────────────────┐ │
│  │  📅 This Week's Schedule             │  🎯 Upcoming Events         │ │
│  │  (8 columns: 30px + 7 days)          │  (Event list cards)         │ │
│  ├──────────────────────────────────────┤                              │ │
│  │        Mon  Tue  Wed  Thu  Fri       │  Today, 10:00 AM            │ │
│  │  8:00                                │  ┌──────────────────────┐   │ │
│  │  9:00  [===]                         │  │ 🟢 Team Standup      │   │ │
│  │ 10:00       [===][===]               │  │  with Sarah, Mike    │   │ │
│  │ 11:00       [===][███]               │  │  📍 Room A           │   │ │
│  │ 12:00  (Lunch)                       │  └──────────────────────┘   │ │
│  │  1:00                                │                              │ │
│  │  2:00            [===]               │  Tomorrow, 2:00 PM          │ │
│  │  3:00                                │  ┌──────────────────────┐   │ │
│  │  4:00                 [===]          │  │ 🟡 Client Review     │   │ │
│  │  5:00                                │  │  with Emily, John    │   │ │
│  │                                      │  │  📍 Zoom Meeting     │   │ │
│  │  Color Key:                          │  └──────────────────────┘   │ │
│  │  🟢 Confirmed  🟡 Tentative          │                              │ │
│  │  🔴 Conflict   ⚪ Available          │  [View All Events →]        │ │
│  └──────────────────────────────────────┴──────────────────────────────┘ │
│                                                                           │
│  Bottom Section (2 cards)                                                 │
│  ┌──────────────────────────────────────┬──────────────────────────────┐ │
│  │  👥 My Teams (3)                     │  📊 Quick Stats             │ │
│  ├──────────────────────────────────────┤                              │ │
│  │  🏢 Engineering Team (12)            │  This Week:                 │ │
│  │  📢 Marketing Team (8)               │  • 8 meetings               │ │
│  │  👔 Executive Team (5)               │  • 12 hours                 │ │
│  │                                      │  • 3 pending invites        │ │
│  │  [+ Create New Team]                 │                              │ │
│  └──────────────────────────────────────┴──────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Card Styling:**
- Background: White
- Border: None (shadow only)
- Shadow: `--shadow-sm` default, `--shadow-md` on hover
- Radius: `--radius-lg`
- Padding: `--space-6`

**Color Coding:**
- Confirmed meetings: `--slot-meeting` (soft blue)
- Tentative: `--slot-tentative` (soft peach)
- Conflicts: `--slot-busy` (soft pink)
- Available: `--slot-available` (soft cyan)

**Hover Interactions:**
- Quick action cards: Lift 4px, add shadow
- Meeting blocks: Show tooltip with details
- Team names: Underline, cursor pointer

**Responsive Breakpoints:**
- Desktop (1280px+): 2-column layout
- Tablet (768px-1279px): Stacked layout, full-width cards
- Mobile (<768px): Single column, simplified views

---

## 5. Calendar View

### Layout Structure (Full Width: 1280px × 900px)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Calendar Header (64px)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  ← October 2025 →          Week  Day  Month           [+ New] [🔍]  │ │
│  │                      Week of October 2 - 8                [Today]   │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────────────┤
│  Calendar Grid (Week View)                                                │
│                                                                           │
│  Time  │  Mon 2    Tue 3    Wed 4    Thu 5    Fri 6    Sat 7    Sun 8   │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  8:00  │            (Working hours start - light highlight)              │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  9:00  │  ┌───────┐                                                      │
│        │  │Standup│                                                      │
│  9:30  │  └───────┘                                                      │
│  ──────┼─────────────────────────────────────────────────────────────── │
│ 10:00  │           ┌───────┐ ┌───────────┐                              │
│        │           │Client │ │  Sprint   │                              │
│ 10:30  │           │Review │ │  Planning │                              │
│        │           └───────┘ │           │                              │
│ 11:00  │                     └───────────┘                              │
│  ──────┼─────────────────────────────────────────────────────────────── │
│ 12:00  │                 (Lunch time - grayed out)                       │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  1:00  │                                                                 │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  2:00  │                          ┌───────┐                             │
│        │                          │1-on-1 │                             │
│  2:30  │                          └───────┘                             │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  3:00  │                                                                 │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  4:00  │                                    ┌──────────┐                │
│        │                                    │Team Retro│                │
│  4:30  │                                    └──────────┘                │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  5:00  │            (Working hours end - light highlight)               │
│  ──────┼─────────────────────────────────────────────────────────────── │
│  6:00  │                                                                 │
│        │                                                                 │
│  (Scrollable to show more hours)                                         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Grid Styling:**
- Time column: 60px width, `--color-gray-700` text
- Day columns: Equal width, flexible
- Gridlines: `1px solid --color-gray-200`
- Current time indicator: Red horizontal line with dot

**Meeting Blocks:**
- Border-radius: `--radius-sm`
- Padding: `--space-2`
- Font-size: `--text-sm`
- Overflow: Truncate title, show tooltip on hover
- Color-coded by status (confirmed, tentative, etc.)

**Hover States:**
- Empty slots: Show `+ Create meeting` button overlay
- Meeting blocks: Lift shadow, show action buttons (Edit, Delete)
- Day headers: Highlight entire column

**Interactive Features:**
- Click empty slot: Open create modal (pre-filled time)
- Click meeting: Open detail modal
- Right-click: Context menu (optional)
- Scroll: Smooth momentum scrolling
- Zoom controls: Adjust hour height (30min vs 60min slots)

---

## 6. Schedule Creation Modal

### Layout Structure (Modal: 600px × 700px)

```
┌────────────────────────────────────────────────────────────┐
│  Create New Meeting                               [✕ Close]│
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Step 1 of 2: Basic Details                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│  Meeting Title *                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [e.g., Team Standup                               ]  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  When *                                                    │
│  ┌─────────────────────────┬──────────────────────────┐   │
│  │ 📅 Date                 │ ⏰ Time                  │   │
│  │ [Monday, Oct 2, 2025 ▼] │ [10:00 AM ▼]            │   │
│  └─────────────────────────┴──────────────────────────┘   │
│                                                            │
│  Duration *                                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [◉ 30 min  ○ 1 hour  ○ 1.5 hours  ○ 2 hours  ○ Custom] │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Participants *                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [Search teammates...                              🔍] │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Selected (2):                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  [👤 Sarah Johnson]  ✓ Available            [✕]    │  │
│  │  [👤 Mike Chen]      ⚠ Conflict at 2 PM     [✕]    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌───────────────────────────────────────────────────────┐│
│  │ ⚠ Mike Chen has a conflict at this time.             ││
│  │   [Suggest Alternative Times →]                       ││
│  └───────────────────────────────────────────────────────┘│
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │ [Cancel]                             [Next Step →] │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Step 2: Additional Details

```
┌────────────────────────────────────────────────────────────┐
│  Create New Meeting                               [✕ Close]│
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Step 2 of 2: Additional Details                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│  Description (Optional)                                    │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [Add meeting agenda or notes...                    ] │ │
│  │ [                                                  ] │ │
│  │ [                                                  ] │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Location (Optional)                                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [e.g., Conference Room A or Zoom link            ]  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Recurrence                                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [◉ One-time   ○ Daily   ○ Weekly   ○ Custom]        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Reminders                                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [☑] Email reminder 15 minutes before                 │ │
│  │ [☑] Push notification 5 minutes before               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Summary                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  "Team Standup"                                      │ │
│  │  Monday, October 2, 2025                             │ │
│  │  10:00 AM - 10:30 AM (30 minutes)                    │ │
│  │  With: Sarah Johnson, Mike Chen                      │ │
│  │  Location: Conference Room A                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │ [← Back]                        [Create Meeting]   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Modal Behavior:**
- Entrance: Scale from 0.95, fade in backdrop (300ms)
- Exit: Scale to 0.95, fade out (250ms)
- Backdrop: `rgba(0, 0, 0, 0.5)`, blur effect
- Close actions: [✕] button, Escape key, click backdrop

**Step Indicator:**
- Active step: Bold, primary color
- Progress bar: Blue fill animating left to right
- Step transition: Slide left/right (250ms ease-out)

**Participant Search:**
- Debounced search (300ms delay)
- Dropdown results: Max 5 visible, scroll for more
- Avatars: Circular, 32px diameter
- Status badges: Green ✓ (available), Yellow ⚠ (conflict), Red ✗ (unavailable)

**Conflict Warning:**
- Background: `--color-warning-light`
- Border-left: 4px solid `--color-warning`
- Icon: Animated attention-grabber (pulse)
- Action link: Underlined, opens smart scheduling overlay

---

## 7. Smart Scheduling Interface

### Layout Structure (Full-page Overlay: 1000px × 800px)

```
┌──────────────────────────────────────────────────────────────────┐
│  Find Best Time                                      [✕ Close]    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Configure Search                                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Who needs to attend? *                                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ [Search teammates...                              🔍] │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                                                            │ │
│  │  Selected (3):                                             │ │
│  │  [👤 Sarah]  [👤 Mike]  [👤 Emily]                        │ │
│  │                                                            │ │
│  │  Duration: [▼ 30 minutes]                                 │ │
│  │                                                            │ │
│  │  Search within: [◉ Next 7 days  ○ Next 14 days  ○ Custom]│ │
│  │                                                            │ │
│  │  Preferences:                                              │ │
│  │  [☑] Prefer mornings (9 AM - 12 PM)                      │ │
│  │  [☑] Prefer weekdays                                      │ │
│  │  [☐] Avoid lunch hours (12-1 PM)                         │ │
│  │                                                            │ │
│  │  [Find Available Times]                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  Available Time Slots (Found 12 options)                        │
│                                                                  │
│  🏆 Best Match (Score: 95%)                                     │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  Monday, October 2, 2025                                   ││
│  │  10:00 AM - 10:30 AM                                       ││
│  │                                                            ││
│  │  ✓ All 3 participants available                           ││
│  │  ✓ Within working hours                                   ││
│  │  ✓ Morning slot (preferred)                               ││
│  │                                                            ││
│  │                                    [Select This Time →]   ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ⭐ Great Option (Score: 88%)                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  Tuesday, October 3, 2025                                  ││
│  │  2:00 PM - 2:30 PM                                         ││
│  │                                                            ││
│  │  ✓ All 3 participants available                           ││
│  │  ✓ Within working hours                                   ││
│  │  ⚠ Afternoon slot (not preferred)                         ││
│  │                                                            ││
│  │                                    [Select This Time →]   ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  👍 Good Option (Score: 75%)                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  Wednesday, October 4, 2025                                ││
│  │  4:00 PM - 4:30 PM                                         ││
│  │                                                            ││
│  │  ✓ All 3 participants available                           ││
│  │  ⚠ Late afternoon (close to end of day)                   ││
│  │                                                            ││
│  │                                    [Select This Time →]   ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [▼ Show More Options (9 more)]                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Slot Ranking Badges:**
- 🏆 Best: Gold gradient background, `--color-success` border
- ⭐ Great: Silver gradient, `--color-info` border
- 👍 Good: Standard white, `--color-gray-300` border

**Score Display:**
- Progress bar: Visual 0-100% indicator
- Color scale: Red → Yellow → Green gradient
- Tooltip: Detailed breakdown on hover

**Slot Cards:**
- Entrance animation: Stagger 50ms per card
- Hover: Lift 4px, `--shadow-md`
- Selected state: `--color-primary-100` background, checkmark icon

**Expand/Collapse:**
- "Show More": Accordion animation (350ms)
- Lazy loading: Load 3 more options at a time
- Scroll position: Maintain position after expansion

---

## 8. Team Management

### Layout Structure (Full Page: 1280px × 900px)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Teams                                             [+ Create New Team]    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Your Teams (3)                                                           │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  🏢 Engineering Team                            [Manage →]          │ │
│  │  ───────────────────────────────────────────────────────────────    │ │
│  │  12 members  •  Owner: You  •  Created 3 months ago                 │ │
│  │                                                                     │ │
│  │  Recent members:                                                    │ │
│  │  [👤] [👤] [👤] [👤] [👤] [+7 more]                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  📢 Marketing Team                              [Manage →]          │ │
│  │  ───────────────────────────────────────────────────────────────    │ │
│  │  8 members  •  Admin  •  Joined 1 month ago                         │ │
│  │                                                                     │ │
│  │  Recent members:                                                    │ │
│  │  [👤] [👤] [👤] [👤] [👤] [+3 more]                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  👔 Executive Team                              [Manage →]          │ │
│  │  ───────────────────────────────────────────────────────────────    │ │
│  │  5 members  •  Member  •  Joined 2 weeks ago                        │ │
│  │                                                                     │ │
│  │  Recent members:                                                    │ │
│  │  [👤] [👤] [👤] [👤] [👤]                                         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Team Detail View (Click "Manage")

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ← Back to Teams          Engineering Team                    [⚙ Settings]│
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┬───────────────────────────────────────────────┐ │
│  │  Team Info          │  Team Members (12)        [+ Add Member]      │ │
│  ├─────────────────────┤                                               │ │
│  │  12 members         │  ┌─────────────────────────────────────────┐  │ │
│  │  Owner: You         │  │ 🔍 [Search members...              ]    │  │ │
│  │  Created: 3 mo ago  │  └─────────────────────────────────────────┘  │ │
│  │                     │                                               │ │
│  │  Description:       │  ┌─────────────────────────────────────────┐  │ │
│  │  Core engineering   │  │ [👤 Avatar]                             │  │ │
│  │  team for product   │  │ Sarah Johnson                           │  │ │
│  │  development        │  │ Owner  •  sarah@example.com             │  │ │
│  │                     │  │                              [Remove ▼] │  │ │
│  │  [Edit Info]        │  └─────────────────────────────────────────┘  │ │
│  │                     │                                               │ │
│  │  Quick Actions:     │  ┌─────────────────────────────────────────┐  │ │
│  │  • Schedule meeting │  │ [👤 Avatar]                             │  │ │
│  │  • View calendar    │  │ Mike Chen                               │  │ │
│  │  • Find common time │  │ Admin  •  mike@example.com              │  │ │
│  │                     │  │                        [Change Role ▼]  │  │ │
│  │                     │  └─────────────────────────────────────────┘  │ │
│  │                     │                                               │ │
│  │                     │  ┌─────────────────────────────────────────┐  │ │
│  │                     │  │ [👤 Avatar]                             │  │ │
│  │                     │  │ Emily Davis                             │  │ │
│  │                     │  │ Member  •  emily@example.com            │  │ │
│  │                     │  │                        [Change Role ▼]  │  │ │
│  │                     │  └─────────────────────────────────────────┘  │ │
│  │                     │                                               │ │
│  │                     │  (... 9 more members ...)                    │ │
│  └─────────────────────┴───────────────────────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Team Cards:**
- Hover: Lift 2px, `--shadow-sm` → `--shadow-md`
- Color coding: Emoji + team name color
- Member avatars: Overlap stack (z-index progression)

**Role Badges:**
- Owner: Gold badge, crown icon
- Admin: Blue badge, star icon
- Member: Gray badge, user icon

**Actions Menu:**
- Dropdown: Slide down (200ms)
- Options: Change role, Remove member, View profile
- Danger actions: Red text with confirmation modal

---

## 9. User Profile & Settings

### Layout Structure (Two-Column: 1000px × 700px)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Settings                                                                 │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┬───────────────────────────────────────────────────┐ │
│  │  Navigation     │  Profile Settings                                 │ │
│  ├─────────────────┤                                                   │ │
│  │  ► Profile      │  ┌─────────────────────────────────────────────┐  │ │
│  │    Availability │  │  [👤 Avatar - Click to change]              │  │ │
│  │    Preferences  │  └─────────────────────────────────────────────┘  │ │
│  │    Teams        │                                                   │ │
│  │    Security     │  Personal Information                             │ │
│  │    Notifications│  ┌─────────────────────────────────────────────┐  │ │
│  │                 │  │  First Name: [Sarah                      ]  │  │ │
│  │                 │  │  Last Name:  [Johnson                    ]  │  │ │
│  │                 │  │  Email:      [sarah@example.com          ]  │  │ │
│  │                 │  │  Phone:      [+1 (555) 123-4567          ]  │  │ │
│  │                 │  └─────────────────────────────────────────────┘  │ │
│  │                 │                                                   │ │
│  │                 │  Work Information                                 │ │
│  │                 │  ┌─────────────────────────────────────────────┐  │ │
│  │                 │  │  Title:      [Senior Developer           ]  │  │ │
│  │                 │  │  Department: [Engineering                ]  │  │ │
│  │                 │  │  Location:   [San Francisco, CA          ]  │  │ │
│  │                 │  └─────────────────────────────────────────────┘  │ │
│  │                 │                                                   │ │
│  │                 │  Timezone                                         │ │
│  │                 │  ┌─────────────────────────────────────────────┐  │ │
│  │                 │  │  [America/Los_Angeles (PST/PDT)         ▼]  │  │ │
│  │                 │  └─────────────────────────────────────────────┘  │ │
│  │                 │                                                   │ │
│  │                 │  ┌────────────────┐                              │ │
│  │                 │  │  Save Changes  │                              │ │
│  │                 │  └────────────────┘                              │ │
│  └─────────────────┴───────────────────────────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Navigation Sidebar:**
- Active item: `--color-primary-100` background, bold text
- Hover: `--color-gray-100` background
- Icons: 20px, aligned left

**Avatar Upload:**
- Hover: Overlay with "Change photo" text
- Click: File picker modal
- Supported formats: JPG, PNG, max 5MB
- Preview: Circular crop before upload

**Form Validation:**
- Real-time validation on blur
- Success: Green checkmark icon
- Error: Red border + error message below field

---

## 10. Availability Settings

### Layout Structure (Full Width: 900px × 700px)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Availability Settings                                   [+ Add Rule]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Set your working hours and availability patterns                         │
│                                                                           │
│  Default Working Hours                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Monday     [✓ Working]  [09:00 AM ▼] to [05:00 PM ▼]              │ │
│  │  Tuesday    [✓ Working]  [09:00 AM ▼] to [05:00 PM ▼]              │ │
│  │  Wednesday  [✓ Working]  [09:00 AM ▼] to [05:00 PM ▼]              │ │
│  │  Thursday   [✓ Working]  [09:00 AM ▼] to [05:00 PM ▼]              │ │
│  │  Friday     [✓ Working]  [09:00 AM ▼] to [05:00 PM ▼]              │ │
│  │  Saturday   [☐ Working]  [──────────] to [──────────]              │ │
│  │  Sunday     [☐ Working]  [──────────] to [──────────]              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Break Times                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  [☑] Lunch Break: [12:00 PM ▼] to [01:00 PM ▼] every workday       │ │
│  │  [☐] Morning Break: [──────────] to [──────────]                    │ │
│  │  [☐] Afternoon Break: [──────────] to [──────────]                  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Custom Availability Rules (2)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  🚫 Out of Office                                          [Edit ✕] │ │
│  │  December 20 - December 31, 2025                                    │ │
│  │  Reason: Holiday vacation                                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  ⏰ Extended Hours                                         [Edit ✕] │ │
│  │  Every Tuesday: 08:00 AM - 06:00 PM                                 │ │
│  │  Reason: Client calls                                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌────────────────┐                                                      │
│  │  Save Changes  │                                                      │
│  └────────────────┘                                                      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Visual Design Details

**Day Toggles:**
- Checkbox: Large (24px), easy to click
- Disabled state: Gray out time pickers
- Hover: Highlight entire row

**Time Pickers:**
- 30-minute increments
- Scroll or type custom time
- Validation: End time must be after start time

**Custom Rules:**
- Color-coded icons: 🚫 Out of office (red), ⏰ Extended (green), 🏠 Remote (blue)
- Hover: Lift shadow
- Click: Edit modal
- Delete: Confirmation dialog

---

## 11. Mobile Views

### 11.1 Mobile Dashboard (375px × 667px - iPhone SE)

```
┌─────────────────────────┐
│  ☰  ScheduTeam  🔔(3)  │
├─────────────────────────┤
│                         │
│  Good morning, Sarah!   │
│  You have 3 meetings    │
│                         │
│  ┌───────────────────┐  │
│  │   + New Meeting   │  │
│  └───────────────────┘  │
│                         │
│  Today's Schedule       │
│  ┌───────────────────┐  │
│  │ 10:00 AM          │  │
│  │ Team Standup      │  │
│  │ 🟢 Confirmed      │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │ 2:00 PM           │  │
│  │ Client Review     │  │
│  │ 🟡 Tentative      │  │
│  └───────────────────┘  │
│                         │
│  [View Full Calendar]   │
│                         │
├─────────────────────────┤
│  🏠    📅    👥    ⚙   │
│  Home  Cal  Teams  Me  │
└─────────────────────────┘
```

### 11.2 Mobile Calendar (Swipeable Day View)

```
┌─────────────────────────┐
│  ← Oct 2 →      [Today] │
│  Monday                  │
├─────────────────────────┤
│  8:00 ─────────────────  │
│  9:00 ┌───────────────┐ │
│       │ Team Standup  │ │
│  9:30 └───────────────┘ │
│ 10:00 ─────────────────  │
│ 11:00 ─────────────────  │
│ 12:00 (Lunch)            │
│  1:00 ─────────────────  │
│  2:00 ┌───────────────┐ │
│       │ Client Review │ │
│  3:00 └───────────────┘ │
│  4:00 ─────────────────  │
│  5:00 ─────────────────  │
│                         │
│  [+ New Meeting]        │
│                         │
└─────────────────────────┘
```

### Visual Design Details

**Mobile-Specific Interactions:**
- Swipe left/right: Navigate days
- Pull down: Refresh data
- Pull up: Access quick actions
- Long press: Context menu on meetings

**Touch Targets:**
- Minimum 44px height for all tappable elements
- Increased spacing between interactive elements
- Large, thumb-friendly buttons at bottom

**Responsive Typography:**
- Reduce font sizes by 20% from desktop
- Maintain readability with 16px minimum

---

## Summary & Next Steps

### Delivered Specifications:
- ✅ 11 detailed screen layouts with visual mockups
- ✅ Color palette and design tokens
- ✅ Interaction patterns and animations
- ✅ Responsive breakpoints (desktop, tablet, mobile)
- ✅ Accessibility considerations

### Recommended Implementation Order:
1. **Phase 1**: Core screens (Login, Registration, Dashboard)
2. **Phase 2**: Calendar and scheduling (Calendar view, Create modal)
3. **Phase 3**: Advanced features (Smart scheduling, Team management)
4. **Phase 4**: Settings and profile management
5. **Phase 5**: Mobile optimization and polish

### Design Handoff Assets Needed:
- [ ] Figma/Sketch files with interactive prototypes
- [ ] Icon sprite sheet or library
- [ ] Image assets (logos, illustrations, placeholders)
- [ ] Design tokens as CSS custom properties file
- [ ] Component library documentation

---

**Document Status:** Complete ✓
**Ready for:** Frontend development implementation
