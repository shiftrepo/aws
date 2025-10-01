# User Interaction Flows

## Core User Flows

### Flow 1: Adding a New Schedule

```
User Journey:
1. Click "Add Schedule" button (Dashboard or Schedule page)
2. Modal/Form appears with smooth animation
3. Fill in required fields:
   - Title (with autocomplete suggestions)
   - Date (calendar picker)
   - Start Time (dropdown or input)
   - End Time (dropdown or input)
   - Status (radio buttons or dropdown)
4. Optional: Add description and recurring settings
5. Click "Save" button
6. Form validates in real-time
7. Success animation plays
8. Dashboard updates with new schedule
9. Toast notification confirms success

Interactions:
- Real-time form validation
- Date picker with keyboard navigation
- Time input with 15-minute increments
- Visual feedback on hover/focus
- Loading state during save
- Error messages inline
- Success confirmation modal
```

### Flow 2: Viewing Team Availability

```
User Journey:
1. Navigate to "Team" or "Dashboard"
2. View availability grid with animation
3. Hover over time slots to see details
4. Click time slot to see full information
5. Filter by:
   - Team member
   - Date range
   - Department
   - Status (available/busy)
6. Click "Find Common Slots" to see overlaps
7. Export or share availability

Interactions:
- Smooth scroll through time slots
- Hover tooltips with meeting details
- Click to expand full details
- Drag to select multiple slots (optional)
- Keyboard navigation support
- Real-time updates when data changes
- Skeleton loading for initial load
```

### Flow 3: Editing Existing Schedule

```
User Journey:
1. Click on schedule card or calendar event
2. Details modal opens with current data
3. Click "Edit" button
4. Form fields become editable
5. Modify desired fields
6. See "Save" and "Cancel" options
7. Confirm changes
8. Dashboard updates with animation
9. Confirmation toast appears

Interactions:
- Pre-filled form with existing data
- Smooth transition between view/edit modes
- Unsaved changes warning
- Optimistic UI updates
- Undo option for recent changes
```

### Flow 4: Searching for Available Slots

```
User Journey:
1. Click "Find Available Slots" button
2. Advanced search modal opens
3. Set criteria:
   - Duration needed
   - Date range
   - Team members (multi-select)
   - Time preferences
4. Click "Search"
5. Loading animation plays
6. Results appear with relevance score
7. Click result to book meeting
8. Confirmation screen

Interactions:
- Multi-select dropdown for team members
- Date range picker with shortcuts
- Duration slider or input
- Real-time result count
- Sort and filter results
- One-click booking from results
```

## Micro-Interactions

### Button States

```javascript
// Normal → Hover → Active → Loading → Success

const buttonStates = {
  normal: {
    scale: 1,
    backgroundColor: '#A855F7'
  },
  hover: {
    scale: 1.02,
    backgroundColor: '#9333EA',
    boxShadow: '0 8px 16px -4px rgba(168, 85, 247, 0.2)'
  },
  active: {
    scale: 0.98
  },
  loading: {
    scale: 1,
    opacity: 0.7
  },
  success: {
    scale: 1,
    backgroundColor: '#22C55E'
  }
};
```

### Form Field Interactions

```javascript
// Input Focus Animation
const inputFocus = {
  unfocused: {
    borderColor: '#E7E5E4',
    scale: 1
  },
  focused: {
    borderColor: '#A855F7',
    scale: 1.01,
    boxShadow: '0 0 0 3px rgba(168, 85, 247, 0.1)'
  }
};

// Validation States
const validationStates = {
  initial: {
    borderColor: '#E7E5E4'
  },
  valid: {
    borderColor: '#22C55E',
    iconColor: '#22C55E'
  },
  invalid: {
    borderColor: '#EF4444',
    shake: true
  }
};
```

### Card Hover Effects

```javascript
// Card hover with lift and shadow
const cardHover = {
  rest: {
    y: 0,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.08)'
  },
  hover: {
    y: -8,
    boxShadow: '0 16px 24px -4px rgba(0, 0, 0, 0.12)',
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 25
    }
  }
};
```

### Toggle Switch

```javascript
// Smooth toggle with color transition
const toggleSwitch = {
  off: {
    x: 0,
    backgroundColor: '#D6D3D1'
  },
  on: {
    x: 24,
    backgroundColor: '#A855F7',
    transition: {
      type: 'spring',
      stiffness: 500,
      damping: 30
    }
  }
};
```

### Dropdown Menu

```javascript
// Smooth dropdown with stagger
const dropdownMenu = {
  closed: {
    opacity: 0,
    scale: 0.95,
    y: -10
  },
  open: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      staggerChildren: 0.05
    }
  }
};

const dropdownItem = {
  closed: { opacity: 0, x: -10 },
  open: { opacity: 1, x: 0 }
};
```

## Gesture Interactions (Touch/Mouse)

### Swipe Gestures (Mobile)

```javascript
// Swipe to delete/archive
const swipeActions = {
  threshold: 100, // pixels
  actions: {
    left: 'delete',
    right: 'archive'
  },
  hapticFeedback: true
};

// Implementation with Framer Motion
<motion.div
  drag="x"
  dragConstraints={{ left: -200, right: 0 }}
  dragElastic={0.1}
  onDragEnd={(e, info) => {
    if (info.offset.x < -100) {
      handleDelete();
    }
  }}
>
  {/* Content */}
</motion.div>
```

### Drag to Reorder

```javascript
// Drag cards to reorder
<Reorder.Group values={items} onReorder={setItems}>
  {items.map(item => (
    <Reorder.Item key={item.id} value={item}>
      <Card>{item.content}</Card>
    </Reorder.Item>
  ))}
</Reorder.Group>
```

### Long Press

```javascript
// Long press to show context menu
const longPressHandler = {
  duration: 500, // ms
  onLongPress: () => {
    showContextMenu();
  }
};
```

## Loading States

### Skeleton Screens

```jsx
// ScheduleCardSkeleton
export const ScheduleCardSkeleton = () => {
  return (
    <div className="card p-6 animate-pulse">
      <div className="h-6 bg-neutral-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-neutral-200 rounded w-1/2 mb-2"></div>
      <div className="h-4 bg-neutral-200 rounded w-2/3 mb-4"></div>
      <div className="flex gap-2">
        <div className="h-8 bg-neutral-200 rounded w-20"></div>
        <div className="h-8 bg-neutral-200 rounded w-20"></div>
      </div>
    </div>
  );
};
```

### Progressive Loading

```javascript
// Load critical content first, then secondary
const loadingPhases = [
  { phase: 1, content: 'header', duration: 0 },
  { phase: 2, content: 'stats', duration: 100 },
  { phase: 3, content: 'availability', duration: 200 },
  { phase: 4, content: 'activity', duration: 300 }
];
```

### Optimistic Updates

```javascript
// Update UI immediately, revert on error
const handleScheduleCreate = async (data) => {
  // Optimistic update
  const tempId = Date.now();
  setSchedules(prev => [...prev, { ...data, id: tempId }]);

  try {
    const result = await api.createSchedule(data);
    // Replace temp with real data
    setSchedules(prev =>
      prev.map(s => s.id === tempId ? result : s)
    );
    showSuccess('Schedule created!');
  } catch (error) {
    // Revert on error
    setSchedules(prev => prev.filter(s => s.id !== tempId));
    showError('Failed to create schedule');
  }
};
```

## Error Handling

### Error Messages

```jsx
// Inline Error
<Input
  error="This field is required"
  // Shows red border + message below
/>

// Toast Notification
showToast({
  variant: 'error',
  title: 'Failed to save',
  message: 'Please try again or contact support',
  duration: 5000
});

// Modal Error
<ErrorModal
  isOpen={hasError}
  title="Something went wrong"
  message={errorMessage}
  actions={[
    { label: 'Try Again', onClick: retry },
    { label: 'Contact Support', onClick: contactSupport }
  ]}
/>
```

### Network Error Handling

```javascript
// Show offline indicator
if (!navigator.onLine) {
  showBanner({
    variant: 'warning',
    message: 'You are offline. Changes will sync when connection is restored.',
    persistent: true
  });
}

// Retry failed requests
const retryStrategy = {
  maxAttempts: 3,
  delay: 1000, // ms
  backoff: 2 // exponential
};
```

## Accessibility Interactions

### Keyboard Navigation

```javascript
// Focus management
const handleKeyDown = (e) => {
  switch(e.key) {
    case 'ArrowDown':
      focusNextItem();
      break;
    case 'ArrowUp':
      focusPreviousItem();
      break;
    case 'Enter':
    case ' ':
      selectCurrentItem();
      break;
    case 'Escape':
      closeDropdown();
      break;
  }
};
```

### Screen Reader Support

```jsx
// Proper ARIA labels
<button
  aria-label="Close modal"
  aria-pressed={isOpen}
  onClick={handleClose}
>
  <CloseIcon aria-hidden="true" />
</button>

// Live region for dynamic content
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {statusMessage}
</div>
```

### Focus Indicators

```css
/* Visible focus for keyboard navigation */
.focusable:focus-visible {
  outline: 3px solid var(--primary-500);
  outline-offset: 2px;
  border-radius: 0.5rem;
}
```

## Feedback Mechanisms

### Success Feedback

```javascript
// Multi-sensory feedback
const showSuccess = () => {
  // Visual
  playSuccessAnimation();
  showToast({ variant: 'success' });

  // Audio (optional)
  playSuccessSound();

  // Haptic (mobile)
  if (navigator.vibrate) {
    navigator.vibrate(50);
  }
};
```

### Progress Indicators

```jsx
// Multi-step form progress
<ProgressBar
  steps={[
    'Basic Info',
    'Time & Date',
    'Details',
    'Confirmation'
  ]}
  currentStep={2}
/>

// Upload progress
<ProgressCircle
  progress={uploadProgress}
  label={`${uploadProgress}% uploaded`}
/>
```
