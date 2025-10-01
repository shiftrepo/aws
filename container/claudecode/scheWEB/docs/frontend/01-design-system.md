# Design System - Team Schedule Management System

## Document Version: 1.0
**Created:** October 1, 2025
**Design Philosophy:** Poppy, Friendly, Accessible
**Visual Language:** Soft colors (淡い色基調) with smooth animations

---

## Color Palette

### Primary Colors (淡い色基調 - Soft Color Base)

#### Main Brand Colors
```css
/* Primary - Soft Sky Blue */
--color-primary-50:  #E6F4FF;   /* Lightest - backgrounds */
--color-primary-100: #BAE0FF;   /* Light - hover states */
--color-primary-200: #91D5FF;   /* Soft - borders */
--color-primary-300: #69BFFF;   /* Default - main actions */
--color-primary-400: #40A9FF;   /* Medium - active states */
--color-primary-500: #1890FF;   /* Bold - emphasis */
--color-primary-600: #096DD9;   /* Dark - text on light */

/* Secondary - Soft Mint Green */
--color-secondary-50:  #F0FFF4;
--color-secondary-100: #C6F6D5;
--color-secondary-200: #9AE6B4;
--color-secondary-300: #68D391;  /* Default - success states */
--color-secondary-400: #48BB78;
--color-secondary-500: #38A169;

/* Accent - Soft Coral */
--color-accent-50:  #FFF5F5;
--color-accent-100: #FED7D7;
--color-accent-200: #FEB2B2;
--color-accent-300: #FC8181;     /* Default - highlights */
--color-accent-400: #F56565;
--color-accent-500: #E53E3E;
```

#### Neutral Grays (Soft Tone)
```css
--color-gray-50:  #FAFAFA;    /* Lightest background */
--color-gray-100: #F5F5F5;    /* Light background */
--color-gray-200: #EEEEEE;    /* Borders, dividers */
--color-gray-300: #E0E0E0;    /* Disabled states */
--color-gray-400: #BDBDBD;    /* Placeholder text */
--color-gray-500: #9E9E9E;    /* Secondary text */
--color-gray-600: #757575;    /* Body text */
--color-gray-700: #616161;    /* Headings */
--color-gray-800: #424242;    /* Dark text */
--color-gray-900: #212121;    /* Darkest text */
```

#### Semantic Colors
```css
/* Success - Soft Green */
--color-success-light: #C6F6D5;
--color-success:       #48BB78;
--color-success-dark:  #2F855A;

/* Warning - Soft Amber */
--color-warning-light: #FEEBC8;
--color-warning:       #ED8936;
--color-warning-dark:  #C05621;

/* Error - Soft Red */
--color-error-light: #FED7D7;
--color-error:       #F56565;
--color-error-dark:  #C53030;

/* Info - Soft Blue */
--color-info-light: #BEE3F8;
--color-info:       #4299E1;
--color-info-dark:  #2B6CB0;
```

#### Calendar Time Slot Colors (Soft Pastels)
```css
/* Available slots */
--slot-available:       #D4F1F4;  /* Soft cyan */
--slot-available-hover: #A8E6CF;  /* Soft mint */

/* Busy/Occupied slots */
--slot-busy:       #FFB6C1;       /* Soft pink */
--slot-busy-hover: #FFA07A;       /* Light salmon */

/* Tentative/Maybe */
--slot-tentative:       #FFE4B5;  /* Soft peach */
--slot-tentative-hover: #FFD700;  /* Light gold */

/* Meeting slots (confirmed) */
--slot-meeting:       #B4D7FF;    /* Soft blue */
--slot-meeting-hover: #9AC8FF;    /* Brighter blue */

/* Personal/Private */
--slot-private:       #E0BBE4;    /* Soft lavender */
--slot-private-hover: #D4A5D7;    /* Light purple */
```

---

## Typography

### Font Families
```css
/* Primary Font - Clean, Modern Sans-Serif */
--font-primary: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont,
                'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* Monospace - For timestamps, IDs */
--font-mono: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;

/* Japanese Support (if needed) */
--font-japanese: 'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', sans-serif;
```

### Type Scale (Responsive)
```css
/* Headings */
--text-4xl: 2.5rem;    /* 40px - Page titles */
--text-3xl: 2rem;      /* 32px - Section headers */
--text-2xl: 1.75rem;   /* 28px - Card headers */
--text-xl:  1.5rem;    /* 24px - Subheadings */
--text-lg:  1.25rem;   /* 20px - Large body */

/* Body Text */
--text-base: 1rem;     /* 16px - Default body */
--text-sm:   0.875rem; /* 14px - Small text */
--text-xs:   0.75rem;  /* 12px - Captions, labels */

/* Line Heights */
--leading-tight:  1.25;
--leading-normal: 1.5;
--leading-loose:  1.75;

/* Font Weights */
--font-light:   300;
--font-normal:  400;
--font-medium:  500;
--font-semibold: 600;
--font-bold:    700;
```

### Typography Usage Guidelines
```css
/* Page Title */
h1 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-gray-800);
  line-height: var(--leading-tight);
  margin-bottom: 1.5rem;
}

/* Section Heading */
h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-gray-700);
  line-height: var(--leading-tight);
  margin-bottom: 1rem;
}

/* Card/Component Heading */
h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-medium);
  color: var(--color-gray-700);
  line-height: var(--leading-normal);
}

/* Body Text */
p {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  color: var(--color-gray-600);
  line-height: var(--leading-normal);
}

/* Labels */
label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-gray-700);
  line-height: var(--leading-normal);
}

/* Caption/Helper Text */
.caption {
  font-size: var(--text-xs);
  font-weight: var(--font-normal);
  color: var(--color-gray-500);
  line-height: var(--leading-normal);
}
```

---

## Spacing System

### Spacing Scale (8px base unit)
```css
--space-0:   0;
--space-1:   0.25rem;  /* 4px */
--space-2:   0.5rem;   /* 8px - base unit */
--space-3:   0.75rem;  /* 12px */
--space-4:   1rem;     /* 16px */
--space-5:   1.25rem;  /* 20px */
--space-6:   1.5rem;   /* 24px */
--space-8:   2rem;     /* 32px */
--space-10:  2.5rem;   /* 40px */
--space-12:  3rem;     /* 48px */
--space-16:  4rem;     /* 64px */
--space-20:  5rem;     /* 80px */
--space-24:  6rem;     /* 96px */
```

### Spacing Usage Guidelines
- **Component padding**: `--space-4` to `--space-6` (16-24px)
- **Card padding**: `--space-6` to `--space-8` (24-32px)
- **Section spacing**: `--space-12` to `--space-16` (48-64px)
- **Element gap**: `--space-2` to `--space-4` (8-16px)
- **Form field gap**: `--space-4` (16px)

---

## Border Radius & Shadows

### Border Radius
```css
--radius-sm:   0.25rem;  /* 4px - buttons, inputs */
--radius-md:   0.5rem;   /* 8px - cards */
--radius-lg:   0.75rem;  /* 12px - modals */
--radius-xl:   1rem;     /* 16px - large cards */
--radius-full: 9999px;   /* Circular - avatars, badges */
```

### Box Shadows (Soft, Elevated)
```css
/* Elevation system for depth */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
             0 1px 2px -1px rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -2px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -4px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 8px 10px -6px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Colored shadows for interactive elements */
--shadow-primary: 0 4px 14px 0 rgba(24, 144, 255, 0.25);
--shadow-success: 0 4px 14px 0 rgba(72, 187, 120, 0.25);
--shadow-error:   0 4px 14px 0 rgba(245, 101, 101, 0.25);
```

---

## Animations & Transitions

### Timing Functions
```css
/* Standard easing curves */
--ease-linear:     cubic-bezier(0, 0, 1, 1);
--ease-in:         cubic-bezier(0.4, 0, 1, 1);
--ease-out:        cubic-bezier(0, 0, 0.2, 1);
--ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);

/* Custom friendly animations */
--ease-bounce:     cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-smooth:     cubic-bezier(0.25, 0.46, 0.45, 0.94);
--ease-gentle:     cubic-bezier(0.33, 1, 0.68, 1);
```

### Transition Durations
```css
--duration-fast:   150ms;   /* Quick feedback */
--duration-base:   250ms;   /* Standard transitions */
--duration-slow:   350ms;   /* Deliberate animations */
--duration-slower: 500ms;   /* Attention-grabbing */
```

### Common Transitions
```css
/* Button hover/press */
.button {
  transition: all var(--duration-fast) var(--ease-out);
}

/* Card hover */
.card {
  transition: transform var(--duration-base) var(--ease-gentle),
              box-shadow var(--duration-base) var(--ease-gentle);
}

/* Modal/overlay fade */
.modal-overlay {
  transition: opacity var(--duration-base) var(--ease-in-out);
}

/* Dropdown slide */
.dropdown {
  transition: transform var(--duration-base) var(--ease-smooth),
              opacity var(--duration-base) var(--ease-smooth);
}
```

### Keyframe Animations
```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale in (poppy effect) */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Gentle bounce */
@keyframes gentleBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

/* Pulse (for notifications) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Shimmer (loading state) */
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

---

## Component-Specific Design Tokens

### Buttons
```css
/* Button sizes */
--btn-height-sm: 2rem;      /* 32px */
--btn-height-md: 2.5rem;    /* 40px - default */
--btn-height-lg: 3rem;      /* 48px */

--btn-padding-sm: 0.5rem 1rem;    /* 8px 16px */
--btn-padding-md: 0.75rem 1.5rem; /* 12px 24px */
--btn-padding-lg: 1rem 2rem;      /* 16px 32px */

/* Button states */
--btn-disabled-opacity: 0.5;
--btn-hover-brightness: 1.05;
--btn-active-scale: 0.98;
```

### Input Fields
```css
--input-height: 2.75rem;    /* 44px - touch-friendly */
--input-padding: 0.75rem 1rem;
--input-border-width: 1px;
--input-focus-ring: 0 0 0 3px rgba(24, 144, 255, 0.15);
```

### Cards
```css
--card-padding: var(--space-6);
--card-radius: var(--radius-lg);
--card-shadow: var(--shadow-sm);
--card-shadow-hover: var(--shadow-md);
--card-border: 1px solid var(--color-gray-200);
```

### Modals
```css
--modal-max-width: 600px;
--modal-padding: var(--space-8);
--modal-radius: var(--radius-lg);
--modal-shadow: var(--shadow-2xl);
--modal-backdrop: rgba(0, 0, 0, 0.5);
```

### Time Slots (Calendar Grid)
```css
--slot-height: 60px;        /* Each 30-minute slot */
--slot-border: 1px solid var(--color-gray-200);
--slot-padding: 0.5rem;
--slot-hover-scale: 1.02;
--slot-active-scale: 0.98;
```

---

## Accessibility

### Focus States
```css
/* Keyboard focus indicator */
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Skip link */
.skip-link:focus {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 9999;
  padding: 1rem;
  background: var(--color-primary-500);
  color: white;
}
```

### Contrast Ratios (WCAG 2.1 AA)
- **Normal text**: 4.5:1 minimum
- **Large text** (18pt+): 3:1 minimum
- **UI components**: 3:1 minimum

### Motion Preferences
```css
/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Responsive Breakpoints

```css
/* Mobile-first approach */
--breakpoint-sm: 640px;   /* Small tablets */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Laptops */
--breakpoint-xl: 1280px;  /* Desktops */
--breakpoint-2xl: 1536px; /* Large desktops */
```

### Responsive Typography
```css
/* Fluid typography */
@media (max-width: 640px) {
  :root {
    --text-4xl: 2rem;
    --text-3xl: 1.75rem;
    --text-2xl: 1.5rem;
    --text-xl: 1.25rem;
  }
}
```

---

## Dark Mode Support (Optional - Future)

```css
/* Dark mode color palette */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #1A202C;
    --color-bg-secondary: #2D3748;
    --color-text-primary: #F7FAFC;
    --color-text-secondary: #E2E8F0;
    /* ... additional dark mode tokens */
  }
}
```

---

## Icon System

### Icon Sizes
```css
--icon-xs: 1rem;    /* 16px */
--icon-sm: 1.25rem; /* 20px */
--icon-md: 1.5rem;  /* 24px - default */
--icon-lg: 2rem;    /* 32px */
--icon-xl: 2.5rem;  /* 40px */
```

### Recommended Icon Library
- **Heroicons** (https://heroicons.com/) - Matches soft, friendly aesthetic
- **Lucide** (https://lucide.dev/) - Clean, minimal icons
- Alternative: **Feather Icons** (https://feathericons.com/)

---

## Usage Examples

### Button Variants
```html
<!-- Primary Button -->
<button class="btn btn-primary">
  Schedule Meeting
</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">
  Cancel
</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">
  View Details
</button>
```

```css
.btn {
  height: var(--btn-height-md);
  padding: var(--btn-padding-md);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--color-primary-400);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-500);
  box-shadow: var(--shadow-primary);
  transform: translateY(-2px);
}

.btn-primary:active {
  transform: scale(var(--btn-active-scale));
}
```

---

## Design Principles Summary

1. **Soft & Approachable**: Use soft color palette, rounded corners, gentle shadows
2. **Clear Hierarchy**: Strong typographic scale, consistent spacing
3. **Smooth Interactions**: Subtle animations, responsive hover states
4. **Accessible**: WCAG 2.1 AA compliant, keyboard-friendly, high contrast
5. **Performance-Conscious**: GPU-accelerated animations, optimized transitions
6. **Mobile-First**: Touch-friendly sizes (44px min), responsive scaling
7. **Consistent**: Use design tokens throughout, avoid magic numbers

---

**Next Steps:**
1. Apply design system to component library
2. Create Figma/Sketch design files
3. Build CSS custom properties stylesheet
4. Document component patterns

**Handoff Notes for Developers:**
- Import design tokens as CSS custom properties
- Use utility classes or CSS-in-JS for consistency
- Test with screen readers and keyboard navigation
- Validate color contrast ratios
