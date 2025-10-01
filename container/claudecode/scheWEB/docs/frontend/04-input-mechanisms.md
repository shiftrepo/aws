# Input Mechanisms & Components - Team Schedule Management System

## Document Version: 1.0
**Created:** October 1, 2025
**Focus:** Mouse-friendly scheduling input, time slot selection, and interactive components

---

## Core Input Mechanisms

### 1. Time Slot Selection (Calendar Grid)

#### 1.1 Mouse-Based Time Selection

**Interaction Pattern: Click & Drag Selection**

```
Visual Representation:

┌────────────────────────────────────────────────────────┐
│  Monday, October 2                                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  9:00 ┌─────────────────────┐ ◄─ Hover: Highlight    │
│       │                     │                         │
│  9:30 │  Click to start     │                         │
│       │                     │                         │
│ 10:00 └─────────────────────┘                         │
│                                                        │
│ 10:30 ┌─────────────────────┐                         │
│       │  Drag to extend     │ ◄─ Dragging: Blue fill │
│ 11:00 │                     │                         │
│       │                     │                         │
│ 11:30 └─────────────────────┘                         │
│                                                        │
│ 12:00 ┌─────────────────────┐                         │
│       │  Release to confirm │ ◄─ Release: Open modal │
│ 12:30 └─────────────────────┘                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Implementation Behavior:**

1. **Initial Hover**
   - Background: Soft blue (`--slot-available`)
   - Cursor: `pointer`
   - Show time label (e.g., "10:00 AM")

2. **Click (Mouse Down)**
   - Record start time
   - Change background to `--color-primary-200`
   - Show selection indicator

3. **Drag (Mouse Move)**
   - Extend selection from start to current position
   - Snap to 15-minute or 30-minute increments
   - Visual feedback: Darken selected area
   - Show duration label (e.g., "1 hour 30 min")

4. **Release (Mouse Up)**
   - Calculate final time range
   - Open "Create Meeting" modal with pre-filled times
   - Highlight: Pulse animation on selected range

**Responsive Touch Behavior:**
- Touch & hold for 300ms: Start selection
- Drag: Extend selection
- Release: Confirm
- Cancel: Tap outside selection

---

### 2. Date Picker Component

#### 2.1 Calendar Dropdown

```
┌──────────────────────────────────────────────┐
│  Select Date                          [X]   │
├──────────────────────────────────────────────┤
│                                              │
│  ← October 2025 →                           │
│                                              │
│  S   M   T   W   T   F   S                  │
│ ───────────────────────────────────         │
│          1   2   3   4   5                  │
│  6   7   8  [9] 10  11  12  ◄ Today        │
│ 13  14  15  16  17  18  19                  │
│ 20  21  22  23  24  25  26                  │
│ 27  28  29  30  31                          │
│                                              │
│  Quick Picks:                                │
│  [Today] [Tomorrow] [Next Monday]           │
│                                              │
└──────────────────────────────────────────────┘
```

**Interaction Features:**

**Hover States:**
- Date hover: Light blue background
- Current date: Bold outline
- Selected date: Filled primary color
- Disabled dates (past): Grayed out, no hover

**Keyboard Navigation:**
- Arrow keys: Navigate dates
- Enter: Select date
- Escape: Close picker
- Tab: Move to quick picks

**Quick Picks:**
- One-click shortcuts for common dates
- Pre-filled with context-aware suggestions
- Hover: Lift shadow effect

**Animation:**
- Open: Scale from 0.95, fade in (200ms)
- Month transition: Slide left/right (250ms)
- Date selection: Ripple effect from center

---

### 3. Time Picker Component

#### 3.1 Scrollable Time Selector

```
┌──────────────────────────────┐
│  Start Time          [X]    │
├──────────────────────────────┤
│                              │
│      ┌────────────┐          │
│      │  8:00 AM   │          │
│      │  8:30 AM   │          │
│      │┌──────────┐│          │
│      ││ 9:00 AM  ││ ◄ Selected
│      │└──────────┘│          │
│      │  9:30 AM   │          │
│      │ 10:00 AM   │          │
│      │ 10:30 AM   │          │
│      └────────────┘          │
│                              │
│  OR Type Time:               │
│  [09:00        ] [AM ▼]     │
│                              │
│  Working Hours: 9 AM - 5 PM  │
│                              │
│  [Confirm]                   │
│                              │
└──────────────────────────────┘
```

**Interaction Features:**

**Scroll Behavior:**
- Smooth momentum scrolling
- Snap to 30-minute increments
- Highlight current selection
- Infinite scroll (loops back)

**Visual Indicators:**
- Working hours: Highlighted in green tint
- Outside work hours: Gray tint
- Selected time: Bold, primary color, larger font

**Type-to-Search:**
- Focus input field
- Type partial time (e.g., "2" → suggests "2:00 PM")
- Auto-format as you type (e.g., "230" → "2:30 PM")
- Tab between hour and AM/PM

**Smart Defaults:**
- Default to next available 30-minute slot
- Working hours highlighted
- Common meeting times suggested (9 AM, 10 AM, 2 PM, 3 PM)

---

### 4. Duration Selector

#### 4.1 Radio Button Grid

```
┌──────────────────────────────────────────────┐
│  Duration                                     │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │
│  │  15  │  │  30  │  │  60  │  │  90  │   │
│  │ min  │  │ min  │  │ min  │  │ min  │   │
│  └──────┘  └──────┘  └──────┘  └──────┘   │
│                                              │
│  ┌──────┐  ┌──────────────┐                │
│  │ 120  │  │   Custom     │                │
│  │ min  │  │ [___ min]    │                │
│  └──────┘  └──────────────┘                │
│                                              │
└──────────────────────────────────────────────┘
```

**Interaction Behavior:**

**Button States:**
- Default: White background, gray border
- Hover: Blue border, scale 1.05
- Selected: Blue background, white text, checkmark icon
- Disabled: Gray background, reduced opacity

**Custom Input:**
- Click "Custom": Enable input field
- Type duration (auto-validation: 5-480 min)
- Enter key: Confirm selection
- Blur: Validate and round to nearest 5 minutes

**Visual Feedback:**
- Selection animation: Checkmark slides in (200ms)
- Validation error: Red shake animation
- Success: Green checkmark pulse

---

### 5. Participant Selector (Multi-Select)

#### 5.1 Autocomplete Search with Chips

```
┌──────────────────────────────────────────────┐
│  Add Participants                             │
├──────────────────────────────────────────────┤
│                                              │
│  [Sarah Johnson ✕] [Mike Chen ✕]            │◄ Selected chips
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ [Search teammates...          🔍]     │ │◄ Search input
│  └────────────────────────────────────────┘ │
│                                              │
│  Suggestions:                                │
│  ┌────────────────────────────────────────┐ │
│  │ [👤] Sarah Johnson                    │ │
│  │      sarah@example.com                │ │
│  │      ✓ Available                      │ │
│  ├────────────────────────────────────────┤ │
│  │ [👤] Mike Chen                        │ │
│  │      mike@example.com                 │ │
│  │      ⚠ Conflict at 2 PM               │ │
│  ├────────────────────────────────────────┤ │
│  │ [👤] Emily Davis                      │ │
│  │      emily@example.com                │ │
│  │      ✓ Available                      │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Recently Added:                             │
│  [Alex] [John] [Lisa]                        │
│                                              │
└──────────────────────────────────────────────┘
```

**Interaction Features:**

**Search Behavior:**
- Debounced search (300ms delay)
- Fuzzy matching on name and email
- Show top 5 results
- Highlight matching characters
- Keyboard: Arrow keys to navigate, Enter to select

**Selected Chips:**
- Hover: Show "✕" remove button
- Click ✕: Remove with fade-out animation
- Draggable: Reorder priority (optional)

**Availability Indicators:**
- ✓ Green: Available at selected time
- ⚠ Yellow: Conflict (show tooltip on hover)
- ✗ Red: Not available (disabled, show reason)

**Recent Contacts:**
- Show 3-5 recently added people
- One-click to add again
- Persist across sessions

---

### 6. Recurrence Pattern Selector

#### 6.1 Progressive Disclosure UI

```
┌──────────────────────────────────────────────┐
│  Repeat                                       │
├──────────────────────────────────────────────┤
│                                              │
│  ◉ Does not repeat                           │
│  ○ Daily                                     │
│  ○ Weekly                                    │
│  ○ Monthly                                   │
│  ○ Custom...                                 │
│                                              │
│  ─────────────────────────────────────────── │
│                                              │
│  [Selected: Weekly]                          │
│                                              │
│  Repeat every: [1 ▼] week(s)                │
│                                              │
│  Repeat on:                                  │
│  [☑ Mon] [☐ Tue] [☐ Wed] [☐ Thu] [☑ Fri]  │
│  [☐ Sat] [☐ Sun]                            │
│                                              │
│  Ends:                                       │
│  ◉ Never                                     │
│  ○ On [date picker]                         │
│  ○ After [5 ▼] occurrences                  │
│                                              │
│  Summary:                                    │
│  "Weekly on Monday and Friday until         │
│   December 31, 2025"                         │
│                                              │
└──────────────────────────────────────────────┘
```

**Interaction Features:**

**Radio Selection:**
- Click: Expand detailed options
- Smooth accordion animation (350ms)
- Only one section expanded at a time

**Day-of-Week Selector:**
- Multi-select checkboxes
- Hover: Highlight entire day button
- Selected: Primary color fill
- Validation: At least one day required

**End Condition:**
- Radio buttons for 3 options
- "On date": Opens date picker inline
- "After occurrences": Numeric spinner

**Summary Preview:**
- Real-time update as options change
- Natural language description
- Confirm understanding before saving

---

### 7. Availability Pattern Editor

#### 7.1 Weekly Schedule Grid

```
┌──────────────────────────────────────────────────────────┐
│  Set Your Working Hours                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│         Start Time    End Time    Break Time            │
│  Mon   [09:00 ▼]     [17:00 ▼]   [12:00-13:00]  ☑     │
│  Tue   [09:00 ▼]     [17:00 ▼]   [12:00-13:00]  ☑     │
│  Wed   [09:00 ▼]     [17:00 ▼]   [12:00-13:00]  ☑     │
│  Thu   [09:00 ▼]     [17:00 ▼]   [12:00-13:00]  ☑     │
│  Fri   [09:00 ▼]     [17:00 ▼]   [12:00-13:00]  ☑     │
│  Sat   [──────]       [──────]     [──────────]  ☐     │
│  Sun   [──────]       [──────]     [──────────]  ☐     │
│                                                          │
│  Quick Actions:                                          │
│  [Copy Monday to all weekdays]                          │
│  [Apply standard 9-5 schedule]                          │
│  [Clear all]                                            │
│                                                          │
│  Timezone: [America/Los_Angeles (PST/PDT) ▼]           │
│                                                          │
│  [Save Changes]                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Interaction Features:**

**Row-Level Actions:**
- Checkbox: Enable/disable entire day
- Disabled state: Gray out time pickers
- Hover row: Show edit icon

**Time Picker Dropdowns:**
- 30-minute increments
- Validation: End > Start
- Smart defaults: Round to nearest half-hour

**Quick Actions:**
- One-click to apply common patterns
- Confirmation modal for destructive actions (Clear all)
- Undo button after bulk operations

**Visual Feedback:**
- Valid range: Green checkmark
- Invalid range: Red warning icon
- Unsaved changes: Yellow dot indicator

---

### 8. Conflict Resolution Interface

#### 8.1 Side-by-Side Comparison

```
┌──────────────────────────────────────────────────────────┐
│  ⚠ Schedule Conflict Detected                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Your meeting overlaps with:                             │
│                                                          │
│  ┌─────────────────────────┬──────────────────────────┐ │
│  │  Existing Meeting       │  New Meeting             │ │
│  ├─────────────────────────┼──────────────────────────┤ │
│  │  Client Review          │  Team Standup            │ │
│  │  2:00 PM - 3:00 PM      │  2:30 PM - 3:00 PM       │ │
│  │  Required attendee      │  Optional attendee       │ │
│  │  📍 Zoom Meeting        │  📍 Conference Room A    │ │
│  └─────────────────────────┴──────────────────────────┘ │
│                                                          │
│  Overlapping time: 2:30 PM - 3:00 PM (30 minutes)       │
│                                                          │
│  Options:                                                │
│  ◉ Find alternative time automatically                   │
│  ○ Adjust new meeting time manually                     │
│  ○ Proceed anyway (mark as tentative)                   │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Suggested Alternative Times:                            │
│  ┌────────────────────────────────────┐                 │
│  │ 🏆 Monday, 3:00 PM - 3:30 PM       │ [Select]       │
│  │    All participants available      │                 │
│  └────────────────────────────────────┘                 │
│                                                          │
│  ┌────────────────────────────────────┐                 │
│  │ ⭐ Tuesday, 10:00 AM - 10:30 AM    │ [Select]       │
│  │    All participants available      │                 │
│  └────────────────────────────────────┘                 │
│                                                          │
│  [Cancel]                            [Resolve]          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Interaction Features:**

**Visual Comparison:**
- Side-by-side layout for clarity
- Color-coded: Red (existing), Blue (new)
- Highlighted overlap region

**Resolution Options:**
- Radio buttons for clear choice
- Auto-suggest: Default selected
- Manual: Opens time picker
- Proceed anyway: Show warning

**Alternative Times:**
- Ranked by quality score
- One-click selection
- Real-time availability check
- Hover: Show detailed participant availability

---

## Animation Specifications

### Hover Effects

```css
/* Time slot hover */
.time-slot:hover {
  background-color: var(--slot-available);
  transform: scale(1.02);
  transition: all 150ms ease-out;
  box-shadow: inset 0 0 0 2px var(--color-primary-300);
}

/* Button hover */
.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary);
  transition: all 200ms var(--ease-gentle);
}
```

### Selection Animations

```css
/* Slot selection */
@keyframes slot-select {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.time-slot.selected {
  animation: slot-select 300ms var(--ease-bounce);
}

/* Chip add animation */
@keyframes chip-add {
  0% {
    opacity: 0;
    transform: translateX(-10px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

.participant-chip {
  animation: chip-add 250ms var(--ease-out);
}
```

---

## Accessibility Considerations

### Keyboard Shortcuts

```
Global:
- Tab: Navigate between input fields
- Shift+Tab: Navigate backwards
- Enter: Submit/confirm current action
- Escape: Close modal/cancel operation

Calendar Grid:
- Arrow keys: Navigate time slots
- Space: Select/deselect slot
- Shift+Click: Multi-select range
- Ctrl+A: Select all available slots

Date Picker:
- Arrow keys: Navigate dates
- PageUp/Down: Change month
- Home: Go to today
- End: Go to last day of month
```

### Screen Reader Support

```html
<!-- Time slot example -->
<button
  role="button"
  aria-label="Schedule meeting at 10:00 AM on Monday, October 2"
  aria-pressed="false"
  aria-describedby="slot-status">
  10:00 AM
</button>
<span id="slot-status" class="sr-only">Available</span>

<!-- Selected participant example -->
<div
  role="listitem"
  aria-label="Sarah Johnson selected, available at this time">
  <span>Sarah Johnson</span>
  <button aria-label="Remove Sarah Johnson">✕</button>
</div>
```

### Focus Management

```css
/* High-visibility focus indicator */
*:focus-visible {
  outline: 3px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Skip link for keyboard users */
.skip-link:focus {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 9999;
  padding: 10px 20px;
  background: var(--color-primary-500);
  color: white;
}
```

---

## Mobile-Specific Adaptations

### Touch-Friendly Sizing

```css
/* Minimum touch target: 44x44px */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
}

/* Increased spacing between interactive elements */
.mobile-input-group > * + * {
  margin-top: 16px;
}
```

### Mobile Time Picker

```
┌───────────────────────┐
│  Select Time     [✕] │
├───────────────────────┤
│                       │
│  ┌─────┐  ┌─────┐    │
│  │ 09  │  │ 30  │    │
│  │  ▲  │  │  ▲  │    │
│  │     │  │     │    │
│  │ 10  │  │ 00  │    │◄ Scrollable drums
│  │     │  │     │    │
│  │  ▼  │  │  ▼  │    │
│  │ 11  │  │ 30  │    │
│  └─────┘  └─────┘    │
│   Hour    Minute     │
│                       │
│  [AM]    [PM]        │◄ Toggle buttons
│                       │
│  [Set Time]           │
│                       │
└───────────────────────┘
```

---

## Performance Optimizations

### Debouncing & Throttling

```javascript
// Search input debounce
const debouncedSearch = debounce((query) => {
  searchParticipants(query);
}, 300);

// Scroll throttle for time picker
const throttledScroll = throttle((scrollTop) => {
  updateSelectedTime(scrollTop);
}, 100);
```

### Lazy Loading

```javascript
// Load participant avatars on demand
const observerOptions = {
  root: null,
  rootMargin: '50px',
  threshold: 0.1
};

const avatarObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadAvatar(entry.target);
    }
  });
}, observerOptions);
```

---

## Summary

### Key Input Mechanisms Delivered:
- ✅ Mouse-friendly time slot selection (click & drag)
- ✅ Calendar date picker with keyboard navigation
- ✅ Scrollable time picker with type-ahead
- ✅ Duration selector with custom input
- ✅ Multi-select participant search with chips
- ✅ Recurrence pattern builder
- ✅ Weekly availability editor
- ✅ Conflict resolution interface

### Design Principles Applied:
- **Mouse-First**: Optimized for mouse interactions, touch as secondary
- **Progressive Disclosure**: Show simple options first, reveal complexity on demand
- **Real-Time Feedback**: Instant visual response to all interactions
- **Error Prevention**: Smart defaults, validation, and helpful suggestions
- **Accessibility**: Full keyboard support, screen reader compatibility

**Document Status:** Complete ✓
**Ready for:** Frontend implementation
