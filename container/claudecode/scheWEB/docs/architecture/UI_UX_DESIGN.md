# UI/UX Design - Team Schedule Management System

## Design System

### Color Palette (Light, Poppy Theme)

```css
:root {
  /* Primary Colors - Blue (Trust, Professional) */
  --color-primary-50: #EFF6FF;
  --color-primary-100: #DBEAFE;
  --color-primary-200: #BFDBFE;
  --color-primary-300: #93C5FD;
  --color-primary-400: #60A5FA;
  --color-primary-500: #3B82F6;  /* Main primary */
  --color-primary-600: #2563EB;
  --color-primary-700: #1D4ED8;
  --color-primary-800: #1E40AF;
  --color-primary-900: #1E3A8A;

  /* Secondary Colors - Purple (Creative, Modern) */
  --color-secondary-50: #FAF5FF;
  --color-secondary-100: #F3E8FF;
  --color-secondary-200: #E9D5FF;
  --color-secondary-300: #D8B4FE;
  --color-secondary-400: #C084FC;
  --color-secondary-500: #A855F7;  /* Main secondary */
  --color-secondary-600: #9333EA;
  --color-secondary-700: #7E22CE;
  --color-secondary-800: #6B21A8;
  --color-secondary-900: #581C87;

  /* Accent Colors - Vibrant Pops */
  --color-accent-orange: #FB923C;
  --color-accent-pink: #F472B6;
  --color-accent-green: #4ADE80;
  --color-accent-yellow: #FBBF24;
  --color-accent-teal: #2DD4BF;

  /* Neutral Colors - Clean Backgrounds */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;

  /* Semantic Colors */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* Background Colors */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-tertiary: #F3F4F6;

  /* Text Colors */
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-tertiary: #9CA3AF;
  --text-inverse: #FFFFFF;

  /* Border Colors */
  --border-light: #E5E7EB;
  --border-medium: #D1D5DB;
  --border-dark: #9CA3AF;

  /* Shadow Colors */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  /* Shift Type Colors */
  --shift-morning: #FBBF24;   /* Yellow */
  --shift-day: #3B82F6;       /* Blue */
  --shift-evening: #A855F7;   /* Purple */
  --shift-night: #374151;     /* Dark Gray */
  --shift-split: #10B981;     /* Green */
}
```

### Typography

```css
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */

  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Letter Spacing */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
}
```

### Spacing Scale

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
}
```

### Border Radius

```css
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;   /* 2px */
  --radius-base: 0.25rem;  /* 4px */
  --radius-md: 0.375rem;   /* 6px */
  --radius-lg: 0.5rem;     /* 8px */
  --radius-xl: 0.75rem;    /* 12px */
  --radius-2xl: 1rem;      /* 16px */
  --radius-full: 9999px;   /* Circular */
}
```

## Wireframes

### 1. Login Page

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                    [Background Animation]                   │
│                         Gradient                           │
│                                                            │
│            ┌─────────────────────────────────┐            │
│            │                                 │            │
│            │    [Logo] Schedule Pro          │            │
│            │                                 │            │
│            │    ┌─────────────────────────┐ │            │
│            │    │ Email                   │ │            │
│            │    │ john@example.com        │ │            │
│            │    └─────────────────────────┘ │            │
│            │                                 │            │
│            │    ┌─────────────────────────┐ │            │
│            │    │ Password                │ │            │
│            │    │ ••••••••••              │ │            │
│            │    └─────────────────────────┘ │            │
│            │                                 │            │
│            │    ☐ Remember me                │            │
│            │                                 │            │
│            │    ┌─────────────────────────┐ │            │
│            │    │      Sign In   →       │ │            │
│            │    └─────────────────────────┘ │            │
│            │                                 │            │
│            │         Forgot password?        │            │
│            │                                 │            │
│            └─────────────────────────────────┘            │
│                                                            │
│                  © 2025 Schedule Pro                       │
│                                                            │
└────────────────────────────────────────────────────────────┘

Animation: Card slides up with fade-in (0.5s ease-out)
Background: Animated gradient mesh
```

### 2. Dashboard Page

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [☰] Schedule Pro          [🔍] Search...     [🔔]3  [👤] John Doe ▼       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Welcome back, John! 👋                                  October 1, 2025  │
│                                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ This Week        │  │ Your Shifts      │  │ Team Status      │       │
│  │ ───────────────  │  │ ───────────────  │  │ ───────────────  │       │
│  │   5 Shifts       │  │   40 Hours       │  │   8 Active       │       │
│  │   40 Hours       │  │   Next: Today    │  │   2 Off Today    │       │
│  │   [View →]       │  │   9:00 AM        │  │   [View →]       │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ Upcoming Shifts                                    [Week ▼] [+]    │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  Mon Oct 1      [═══════════] Day Shift          9:00 - 17:00    │  │
│  │                                                                    │  │
│  │  Tue Oct 2      ------ Off ------                                 │  │
│  │                                                                    │  │
│  │  Wed Oct 3      [═══════════] Day Shift          9:00 - 17:00    │  │
│  │                                                                    │  │
│  │  Thu Oct 4      [════════════════] Evening      14:00 - 22:00    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ Recent Notifications                              [Mark all read]  │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  • New shift assigned for Oct 5                      2 hours ago   │  │
│  │  • Jane Smith requested shift swap                   5 hours ago   │  │
│  │  • Schedule published for next week              Yesterday 3:00 PM │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

Animations:
- Stat cards slide in from bottom with stagger (100ms delay each)
- Timeline items fade in with slight left slide
- Hover effects: cards lift with shadow increase
```

### 3. Schedule Calendar Page

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ [☰] Schedule Pro                                  [🔔]  [👤] John Doe ▼        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Schedule                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ [◄] Week of October 1-7, 2025 [►]    [Day|Week|Month]  [+ Assign Shift]│   │
│  ├────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                        │   │
│  │  Filters:  [All Users ▼]  [All Shifts ▼]  [Status: All ▼]  [Clear] │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │     Mon 1  │  Tue 2  │  Wed 3  │  Thu 4  │  Fri 5  │  Sat 6  │ Sun 7 │   │
│  ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼───────┤   │
│  │ John       │         │         │         │         │         │       │   │
│  │ ┌────────┐ │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │   OFF   │  OFF  │   │
│  │ │ 9-17   │ │ │9-17 │ │ │9-17 │ │ │14-22│ │ │9-17 │ │         │       │   │
│  │ │ Day    │ │ │Day  │ │ │Day  │ │ │Eve  │ │ │Day  │ │         │       │   │
│  │ └────────┘ │ └─────┘ │ └─────┘ │ └─────┘ │ └─────┘ │         │       │   │
│  ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼───────┤   │
│  │ Jane       │         │         │         │         │         │       │   │
│  │   OFF      │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │   OFF   │ ┌─────┐ │┌─────┐│   │
│  │            │ │6-14 │ │ │14-22│ │ │6-14 │ │         │ │14-22│ ││6-14 ││   │
│  │            │ │Morn │ │ │Eve  │ │ │Morn │ │         │ │Eve  │ ││Morn ││   │
│  │            │ └─────┘ │ └─────┘ │ └─────┘ │         │ └─────┘ │└─────┘│   │
│  ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼───────┤   │
│  │ Mike       │         │         │         │         │         │       │   │
│  │ ┌────────┐ │ ┌─────┐ │   OFF   │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │┌─────┐│   │
│  │ │ 14-22  │ │ │14-22│ │         │ │22-6 │ │ │9-17 │ │ │9-17 │ ││14-22││   │
│  │ │ Eve    │ │ │Eve  │ │         │ │Night│ │ │Day  │ │ │Day  │ ││Eve  ││   │
│  │ └────────┘ │ └─────┘ │         │ └─────┘ │ └─────┘ │ └─────┘ │└─────┘│   │
│  └────────────┴─────────┴─────────┴─────────┴─────────┴─────────┴───────┘   │
│                                                                                │
│  Color Legend:                                                                │
│  [█] Morning (6-14)  [█] Day (9-17)  [█] Evening (14-22)  [█] Night (22-6)  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

Interactions:
- Drag and drop shifts between users
- Click shift to edit details
- Double-click empty slot to create shift
- Right-click for context menu (swap, delete, copy)

Animations:
- Smooth drag shadow effect
- Drop zone highlight (pulse)
- Cell hover: subtle scale and shadow
```

### 4. Shift Assignment Modal

```
┌────────────────────────────────────────────────────────────┐
│  Assign New Shift                                      [×] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Employee *                                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [👤] Select employee...                            ▼│ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Date *                                                    │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [📅] 10/01/2025                                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Shift Template (Optional)                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ ○ Day Shift (9:00 - 17:00)                          │ │
│  │ ○ Evening Shift (14:00 - 22:00)                     │ │
│  │ ○ Night Shift (22:00 - 6:00)                        │ │
│  │ ● Custom                                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Time *                                                    │
│  ┌──────────────────────┐  ┌──────────────────────────┐  │
│  │ Start: [09:00     ▼] │  │ End: [17:00         ▼]  │  │
│  └──────────────────────┘  └──────────────────────────┘  │
│                                                            │
│  Notes                                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Front desk coverage...                               │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ⚠ Conflicts Detected:                                    │
│  • User has another shift at 14:00 on this date          │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │     Cancel       │  │       Assign Shift           │  │
│  └──────────────────┘  └──────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘

Animations:
- Modal slides down from top with fade-in
- Conflict warning pulsing red border
- Success: green checkmark animation before close
```

### 5. Team Members Page

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [☰] Schedule Pro                                  [🔔]  [👤] John Doe ▼    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Team Members                              [🔍] Search...  [+ Add Member] │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  Filters:  [All Roles ▼]  [Active Only ☑]  [Sort: Name ▼]        │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ [👤]  John Doe                            [Admin] [Active]   │  │   │
│  │  │       john.doe@example.com                                   │  │   │
│  │  │       +1 (555) 123-4567                                      │  │   │
│  │  │                                                              │  │   │
│  │  │       This Week: 40 hours  |  Total Shifts: 156  |  [...]  │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ [👤]  Jane Smith                        [Manager] [Active]   │  │   │
│  │  │       jane.smith@example.com                                 │  │   │
│  │  │       +1 (555) 234-5678                                      │  │   │
│  │  │                                                              │  │   │
│  │  │       This Week: 35 hours  |  Total Shifts: 142  |  [...]  │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ [👤]  Mike Johnson                    [Employee] [Active]    │  │   │
│  │  │       mike.j@example.com                                     │  │   │
│  │  │       +1 (555) 345-6789                                      │  │   │
│  │  │                                                              │  │   │
│  │  │       This Week: 40 hours  |  Total Shifts: 98   |  [...]  │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  Showing 3 of 25 members                                    [1][2][3][4]  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

Animations:
- Cards fade in with stagger
- Hover: card lifts with shadow
- Click: expand for detailed view
- Avatar pulse on hover
```

### 6. Mobile View (Responsive)

```
┌──────────────────────────┐
│ [☰] Schedule  [🔔]3 [👤] │
├──────────────────────────┤
│                          │
│  Welcome, John! 👋       │
│  October 1, 2025         │
│                          │
│  ┌────────────────────┐  │
│  │ This Week          │  │
│  │ 5 Shifts  40 Hours │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │ Your Next Shift    │  │
│  │ Today 9:00 AM      │  │
│  │ Day Shift          │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │ Upcoming Shifts    │  │
│  ├────────────────────┤  │
│  │ Mon Oct 1          │  │
│  │ [═══] 9:00-17:00   │  │
│  │ Day Shift          │  │
│  ├────────────────────┤  │
│  │ Wed Oct 3          │  │
│  │ [═══] 9:00-17:00   │  │
│  │ Day Shift          │  │
│  ├────────────────────┤  │
│  │ Thu Oct 4          │  │
│  │ [════] 14:00-22:00 │  │
│  │ Evening Shift      │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │ [View Calendar →]  │  │
│  └────────────────────┘  │
│                          │
└──────────────────────────┘

Navigation:
- Bottom tab bar for mobile
- Swipe gestures for navigation
- Pull to refresh
```

## Component UI Specifications

### Button Variants

```jsx
// Primary Button
<Button variant="primary">
  Sign In
</Button>
// Style: bg-primary-500 text-white hover:bg-primary-600 rounded-lg px-4 py-2

// Secondary Button
<Button variant="secondary">
  Cancel
</Button>
// Style: bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-lg px-4 py-2

// Outline Button
<Button variant="outline">
  View Details
</Button>
// Style: border-2 border-primary-500 text-primary-500 hover:bg-primary-50

// Icon Button
<Button variant="icon">
  <IconPlus />
</Button>
// Style: w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center
```

### Card Variants

```jsx
// Basic Card
<Card>
  <CardHeader>Title</CardHeader>
  <CardBody>Content</CardBody>
</Card>
// Style: bg-white rounded-xl shadow-md p-6

// Shift Card
<ShiftCard shift={shift} color="blue">
  9:00 - 17:00
  Day Shift
</ShiftCard>
// Style: bg-shift-color rounded-lg p-4 cursor-pointer hover:scale-102

// Stat Card
<StatCard icon={<IconClock />} value="40" label="Hours">
// Style: bg-gradient rounded-lg p-6 text-white
```

### Input Fields

```jsx
// Text Input
<Input
  type="text"
  label="Email"
  placeholder="john@example.com"
  error="Invalid email"
/>
// Style: border-2 border-gray-300 focus:border-primary-500 rounded-lg px-4 py-2

// Select Dropdown
<Select label="Role" options={roles}>
// Style: Dropdown with smooth animation, search functionality

// Date Picker
<DatePicker value={date} onChange={setDate}>
// Style: Calendar popup with month/year navigation

// Time Picker
<TimePicker value={time} onChange={setTime}>
// Style: Dropdown with hour/minute selectors
```

## Animation Library

### Transition Timings

```css
/* Durations */
--duration-fast: 150ms;
--duration-base: 250ms;
--duration-slow: 350ms;
--duration-slower: 500ms;

/* Easings */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Common Animations

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale In */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Spin */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Bounce */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Shimmer (Loading) */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}
```

### Page Transitions

```jsx
const pageVariants = {
  initial: {
    opacity: 0,
    x: -20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: 0.2,
      ease: 'easeIn'
    }
  }
};
```

## Accessibility (a11y) Guidelines

### Color Contrast
- Text: Minimum 4.5:1 contrast ratio (WCAG AA)
- Large text: Minimum 3:1 contrast ratio
- Interactive elements: Clear focus indicators

### Keyboard Navigation
- All interactive elements accessible via Tab
- Escape key closes modals/dropdowns
- Arrow keys navigate lists/calendars
- Enter/Space activates buttons

### Screen Reader Support
- Semantic HTML elements
- ARIA labels for icons
- Alt text for images
- Live regions for notifications

### Focus Management
```css
/* Visible focus indicator */
*:focus {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-500);
  color: white;
  padding: 8px;
}

.skip-link:focus {
  top: 0;
}
```

## Responsive Breakpoints

### Mobile First Approach

```css
/* Mobile: < 640px (default) */
.container {
  padding: 1rem;
}

/* Tablet: >= 640px */
@media (min-width: 640px) {
  .container {
    padding: 1.5rem;
  }
}

/* Desktop: >= 1024px */
@media (min-width: 1024px) {
  .container {
    padding: 2rem;
    max-width: 1280px;
    margin: 0 auto;
  }
}

/* Large Desktop: >= 1536px */
@media (min-width: 1536px) {
  .container {
    max-width: 1536px;
  }
}
```

## Loading States

### Skeleton Loaders

```jsx
<SkeletonCard>
  <SkeletonHeader />
  <SkeletonText lines={3} />
  <SkeletonButton />
</SkeletonCard>

// Shimmer effect with CSS gradient animation
```

### Progress Indicators

```jsx
// Linear Progress
<ProgressBar value={75} max={100} />

// Circular Spinner
<Spinner size="md" color="primary" />

// Dots Animation
<LoadingDots />
```

## Empty States

```jsx
<EmptyState
  icon={<IconCalendar />}
  title="No shifts scheduled"
  description="Get started by assigning your first shift"
  action={<Button>Assign Shift</Button>}
/>
```

## Error States

```jsx
<ErrorMessage
  type="error"
  title="Failed to load schedule"
  message="Please try again or contact support"
  action={<Button onClick={retry}>Retry</Button>}
/>
```

## Success Feedback

```jsx
// Toast Notification
<Toast
  type="success"
  message="Shift assigned successfully!"
  duration={3000}
  position="top-right"
/>

// Inline Success
<SuccessBanner icon={<IconCheck />}>
  Changes saved
</SuccessBanner>
```
