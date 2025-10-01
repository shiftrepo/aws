# Visual Mockups & UI Patterns

## 📱 Screen Layouts (ASCII Mockups)

### 1. Dashboard Overview (Desktop)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📅 Schedule Manager    [Dashboard] [Team] [Schedule]    [👤 Sarah ▼]  │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  Welcome back, Sarah! 👋                                                 │
│  Here's what's happening with your team today                           │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ 👥 AVAILABLE │  │ 📅 UPCOMING  │  │ ⏰ FREE SLOTS│  │ 🌴 OUT      │ │
│  │              │  │              │  │              │  │             │ │
│  │      8       │  │      3       │  │      15      │  │      2      │ │
│  │ out of 12    │  │ in 2 hours   │  │ today        │  │ members     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│                                                                           │
│  ┌────────────────────────────────────────────┐  ┌──────────────────┐   │
│  │ 📊 TEAM AVAILABILITY TODAY                 │  │ ⚡ QUICK ACTIONS │   │
│  │                                            │  │                  │   │
│  │  Name       9am 10  11  12  1   2   3  4  │  │ [+ Add Schedule] │   │
│  │  ────────── ─── ─── ─── ─── ─── ─── ─── ─ │  │                  │   │
│  │  🟢 Alice    🟢  🟢  🔴  🔴  🟢  🟢  🟡  🟢│  │ [🔍 Find Slots] │   │
│  │  🟢 Bob      🟢  🔴  🔴  🟡  🟢  🟢  🟢  🟢│  │                  │   │
│  │  🔴 Carol    🔴  🔴  🔴  🔴  🔴  🟢  🟢  🟢│  │ [📊 Analytics]   │   │
│  │  🟢 David    🟢  🟢  🟢  🔴  🔴  🟢  🟢  🟢│  │                  │   │
│  │  🟡 Emma     🟡  🟡  🟢  🟢  🟢  🟢  🟢  🟢│  ├──────────────────┤   │
│  │  🟢 Frank    🟢  🟢  🟢  🟢  🟢  🔴  🔴  🟢│  │ 📅 UPCOMING      │   │
│  │                                            │  │                  │   │
│  │  Legend: 🟢 Available  🔴 Busy             │  │ 10:00 Team Call  │   │
│  │          🟡 Tentative  ⚪ Out of Office   │  │ 14:30 Design Rev │   │
│  └────────────────────────────────────────────┘  │ 16:00 1-on-1     │   │
│                                                   └──────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📝 RECENT ACTIVITY                                              │   │
│  │                                                                 │   │
│  │  🟢 Alice added "Client Meeting" at 2:00 PM      2 mins ago    │   │
│  │  🔴 Bob marked 11:00 AM - 12:00 PM as busy       15 mins ago   │   │
│  │  🟡 Carol set tentative for "Product Review"      1 hour ago    │   │
│  │  🟢 David updated availability for next week      2 hours ago   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2. Schedule Form (Modal)

```
┌─────────────────────────────────────────────────────────────┐
│  Add New Schedule                                      [✕]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Title *                                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Team Standup Meeting                                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Date *                     Start Time *    End Time *     │
│  ┌──────────────────┐      ┌─────────┐    ┌─────────┐    │
│  │ 2024-06-15  📅  │      │ 10:00  │    │ 11:00  │    │
│  └──────────────────┘      └─────────┘    └─────────┘    │
│                                                             │
│  Status *                                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🔴 Busy                                            ▼ │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Description (Optional)                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Daily standup with the engineering team               │ │
│  │                                                        │ │
│  │                                                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ☐ Recurring Event                                         │
│                                                             │
│            [Cancel]  [✓ Create Schedule]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Team Availability Grid (Expanded)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Team Availability                    [Today] [This Week]  [⚙ Filter]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Member          9:00  9:30  10:00  10:30  11:00  11:30  12:00  12:30  │
│  ────────────── ───── ───── ────── ────── ────── ────── ────── ──────  │
│                                                                           │
│  🟢 Alice Smith                                                          │
│   Product Lead   [🟢] [🟢] [🟢]  [🔴]  [🔴]  [🟢]  [🟢]  [🟢]         │
│                    ↑ Hover shows: "Available"                           │
│                                                                           │
│  🔴 Bob Johnson                                                          │
│   Engineer       [🟢] [🟢] [🔴]  [🔴]  [🔴]  [🔴]  [🟢]  [🟢]         │
│                              ↑ "Team Meeting 10:00-12:00"               │
│                                                                           │
│  🟡 Carol White                                                          │
│   Designer       [🟡] [🟡] [🟡]  [🟢]  [🟢]  [🟢]  [🔴]  [🔴]         │
│                    ↑ "Client Call (Tentative)"                          │
│                                                                           │
│  🟢 David Lee                                                            │
│   Manager        [🟢] [🟢] [🟢]  [🟢]  [🟢]  [🔴]  [🔴]  [🟢]         │
│                                                                           │
│  ⚪ Emma Davis                                                           │
│   Marketing      [⚪] [⚪] [⚪]  [⚪]  [⚪]  [⚪]  [⚪]  [⚪]             │
│                    ↑ "Out of Office - Vacation"                         │
│                                                                           │
│  🟢 Frank Miller                                                         │
│   Engineer       [🟢] [🟢] [🟢]  [🟢]  [🟢]  [🟢]  [🔴]  [🔴]         │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Legend:  🟢 Available   🔴 Busy   🟡 Tentative   ⚪ Out of Office     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4. Mobile View (Stack Layout)

```
┌─────────────────────────────────────┐
│  ≡  Schedule Manager         [👤]  │
├─────────────────────────────────────┤
│                                     │
│  Welcome back, Sarah! 👋            │
│  Tuesday, June 15, 2024             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 👥 AVAILABLE NOW                ││
│  │                                 ││
│  │        8 / 12                   ││
│  │   team members online           ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 📅 UPCOMING MEETINGS            ││
│  │                                 ││
│  │        3                        ││
│  │   in the next 2 hours           ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ⚡ QUICK ACTIONS                ││
│  │                                 ││
│  │  [+ Add Schedule]               ││
│  │  [🔍 Find Available Slots]      ││
│  │  [👥 View Team]                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 📅 TODAY'S SCHEDULE             ││
│  │                                 ││
│  │  🟢 10:00 AM - Team Standup     ││
│  │  🔴 11:00 AM - Client Call      ││
│  │  🟢 02:00 PM - Code Review      ││
│  │  🟡 04:00 PM - Planning (Tent.) ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 📝 RECENT ACTIVITY              ││
│  │                                 ││
│  │  Alice added "Client Meeting"   ││
│  │  2 minutes ago                  ││
│  │                                 ││
│  │  Bob marked 11:00 AM as busy    ││
│  │  15 minutes ago                 ││
│  │                                 ││
│  │  Carol set tentative event      ││
│  │  1 hour ago                     ││
│  └─────────────────────────────────┘│
│                                     │
├─────────────────────────────────────┤
│  [🏠]  [📅]  [👥]  [⚙]            │
└─────────────────────────────────────┘
```

### 5. Search Available Slots Modal

```
┌─────────────────────────────────────────────────────────────┐
│  Find Available Slots                                  [✕]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Select Team Members *                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ✓ Alice Smith    ✓ Bob Johnson    □ Carol White      │ │
│  │ ✓ David Lee      □ Emma Davis     ✓ Frank Miller     │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Meeting Duration *                                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ [────●────────────────────────────]  60 minutes       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Date Range *                                               │
│  ┌──────────────────┐      to     ┌──────────────────┐    │
│  │ Jun 15, 2024    │              │ Jun 22, 2024    │    │
│  └──────────────────┘              └──────────────────┘    │
│                                                             │
│  Time Preferences (Optional)                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ □ Morning (9am-12pm)                                  │ │
│  │ ✓ Afternoon (12pm-5pm)                                │ │
│  │ □ Evening (5pm-8pm)                                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│                       [🔍 Search Slots]                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  RESULTS (12 slots found)              [Sort by ▼]         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ⭐ Thu, Jun 16 • 2:00 PM - 3:00 PM                    │ │
│  │    4 members available • Best match                   │ │
│  │                                          [Book Now]   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ⭐ Fri, Jun 17 • 10:00 AM - 11:00 AM                  │ │
│  │    4 members available                                │ │
│  │                                          [Book Now]   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ⭐ Fri, Jun 17 • 3:00 PM - 4:00 PM                    │ │
│  │    4 members available                                │ │
│  │                                          [Book Now]   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme Examples

### Buttons
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PRIMARY       │  │   SECONDARY     │  │   SUCCESS       │
│   #A855F7       │  │   #FF6B9D       │  │   #14B8A6       │
│   (Purple)      │  │   (Pink)        │  │   (Mint)        │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐
│   OUTLINE       │  │   GHOST         │
│   Border Purple │  │   Text Purple   │
└──────────────────┘  └──────────────────┘
```

### Status Badges
```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ ● Available│  │ ● Busy     │  │ ● Tentative│  │ ● Out      │
│   #22C55E  │  │   #EF4444  │  │   #F97316  │  │   #A8A29E  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

### Cards
```
┌─────────────────────────────────────┐
│ ELEVATED CARD (with shadow)         │
│ Background: White                   │
│ Shadow: 0 4px 6px rgba(0,0,0,0.08) │
│ Radius: 12px                        │
│ Padding: 24px                       │
│                                     │
│ Hover: Lift -4px + shadow increase  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ GRADIENT CARD                       │
│ From: Purple-50 (#FAF5FF)          │
│ To: Pink-50 (#FFF5F7)              │
│ Radius: 16px                        │
│ Padding: 24px                       │
└─────────────────────────────────────┘
```

## 📐 Spacing Examples

### Card Spacing
```
┌─────────────────────────────────┐ ← 24px padding
│   ← 24px                        │
│   ┌─────────────────────────┐   │
│   │ Card Header             │   │
│   └─────────────────────────┘   │
│          ↕ 16px gap             │
│   ┌─────────────────────────┐   │
│   │ Card Content            │   │
│   │                         │   │
│   └─────────────────────────┘   │
│                          24px → │
└─────────────────────────────────┘
```

### Form Spacing
```
Label
↕ 8px
┌────────────────────┐
│ Input Field        │
└────────────────────┘
↕ 4px (helper/error)
Helper text or error
↕ 20px (between fields)

Label
↕ 8px
┌────────────────────┐
│ Input Field        │
└────────────────────┘
```

### Grid Gaps
```
┌────┐ ← 24px gap → ┌────┐ ← 24px gap → ┌────┐
│Card│               │Card│               │Card│
└────┘               └────┘               └────┘
  ↕ 24px gap
┌────┐               ┌────┐               ┌────┐
│Card│               │Card│               │Card│
└────┘               └────┘               └────┘
```

## ✨ Animation States

### Button Hover Sequence
```
NORMAL STATE:
┌──────────┐
│  Button  │  scale: 1.0
└──────────┘  shadow: small

     ↓ hover (200ms ease-out)

HOVER STATE:
┌──────────┐
│  Button  │  scale: 1.02
└──────────┘  shadow: medium
              y: -2px

     ↓ click

ACTIVE STATE:
┌──────────┐
│  Button  │  scale: 0.98
└──────────┘  duration: 100ms
```

### Card Entrance Animation
```
FRAME 1 (0ms):
  opacity: 0
  y: +20px

FRAME 2 (150ms):
  opacity: 0.5
  y: +10px

FRAME 3 (300ms):
  opacity: 1
  y: 0px
  ✓ Complete
```

### List Stagger
```
ITEM 1: Animates at 0ms
ITEM 2: Animates at 80ms
ITEM 3: Animates at 160ms
ITEM 4: Animates at 240ms
ITEM 5: Animates at 320ms

Each item: fade in + slide up (300ms)
```

## 🖱️ Interactive States

### Time Slot Hover
```
REST STATE:
┌───┐
│🟢 │  Cursor: pointer
└───┘  Height: 32px

HOVER STATE:
┌───┐
│🟢 │  Transform: scale(1.1) translateY(-2px)
└───┘  Tooltip appears
       Shadow increases
       Duration: 150ms

CLICK STATE:
[MODAL OPENS]
└─── Full schedule details
```

### Input Focus
```
UNFOCUSED:
┌──────────────────┐
│                  │  Border: neutral-200
└──────────────────┘

FOCUSED:
┌──────────────────┐
│   |              │  Border: primary-500
└──────────────────┘  Ring: 3px primary-200
                      Transition: 200ms
```

## 📊 Data Visualization

### Availability Percentage
```
Alice Smith        ████████░░  80% Available
Bob Johnson        ██████░░░░  60% Available
Carol White        ██████████  100% Available
David Lee          ████░░░░░░  40% Available

Color: Green gradient
Animation: Width animates in on load
```

### Meeting Distribution
```
Morning   (9am-12pm)  ████████░░░░ 8 meetings
Afternoon (12pm-5pm)  ████████████ 12 meetings
Evening   (5pm-8pm)   ████░░░░░░░░ 4 meetings

Colors: Time-of-day gradient
Hover: Show detailed breakdown
```

## 🎭 Component States

### Schedule Card States

```
NORMAL STATE:
┌──────────────────────────┐
│ 🔴 Team Meeting          │
│ 10:00 AM - 11:00 AM      │
│ ────────────────────     │
│ [Edit] [Delete]          │
└──────────────────────────┘

HOVER STATE:
┌──────────────────────────┐
│ 🔴 Team Meeting          │
│ 10:00 AM - 11:00 AM      │
│ ────────────────────     │
│ [Edit] [Delete]          │ ← Lift effect
└──────────────────────────┘   Cursor changes
                               Shadow increases

LOADING STATE:
┌──────────────────────────┐
│ ⏳ Updating...           │
│ [Spinner]                │
│ ────────────────────     │
│                          │
└──────────────────────────┘

SUCCESS STATE:
┌──────────────────────────┐
│ ✅ Updated Successfully! │
│ [Checkmark animation]    │
│ ────────────────────     │
│ Auto-dismiss in 2s       │
└──────────────────────────┘
```

---

## 🎨 Design Tokens Reference

```javascript
// Use in components
import { colors, spacing, animations } from '@/styles/tokens';

// Example usage
<Button
  bg={colors.primary[500]}
  padding={spacing[4]}
  transition={animations.standard}
/>
```

**All mockups follow:**
- Poppy, friendly design language
- Light pastel color palette
- Smooth animations (60fps)
- Mouse-friendly interactions
- Mobile-responsive layouts
- Accessibility-first approach

---

✅ **Visual Design Complete** - Ready for implementation with clear visual reference
