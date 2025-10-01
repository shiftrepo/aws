# Spacing & Layout System

## Spacing Scale

```css
:root {
  /* Base Unit: 4px */
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
  --space-24: 6rem;     /* 96px */

  /* Semantic Spacing */
  --space-xs: var(--space-2);
  --space-sm: var(--space-3);
  --space-md: var(--space-4);
  --space-lg: var(--space-6);
  --space-xl: var(--space-8);
  --space-2xl: var(--space-12);
}
```

## Border Radius

```css
:root {
  --radius-sm: 0.375rem;   /* 6px - Subtle rounding */
  --radius-base: 0.5rem;   /* 8px - Default */
  --radius-md: 0.75rem;    /* 12px - Cards */
  --radius-lg: 1rem;       /* 16px - Modals */
  --radius-xl: 1.5rem;     /* 24px - Large cards */
  --radius-2xl: 2rem;      /* 32px - Hero sections */
  --radius-full: 9999px;   /* Full circle */
}
```

## Shadows

```css
:root {
  /* Soft, Elevated Shadows */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 2px 4px 0 rgba(0, 0, 0, 0.06),
               0 1px 2px 0 rgba(0, 0, 0, 0.03);
  --shadow-base: 0 4px 6px -1px rgba(0, 0, 0, 0.08),
                 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 8px 12px -2px rgba(0, 0, 0, 0.1),
               0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 16px 24px -4px rgba(0, 0, 0, 0.12),
               0 8px 12px -4px rgba(0, 0, 0, 0.06);
  --shadow-xl: 0 24px 48px -8px rgba(0, 0, 0, 0.15),
               0 12px 24px -8px rgba(0, 0, 0, 0.08);

  /* Colored Shadows (for hover states) */
  --shadow-primary: 0 8px 16px -4px rgba(168, 85, 247, 0.2);
  --shadow-secondary: 0 8px 16px -4px rgba(255, 107, 157, 0.2);
  --shadow-tertiary: 0 8px 16px -4px rgba(20, 184, 166, 0.2);
}
```

## Layout Grid

```css
:root {
  /* Container Widths */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;

  /* Grid Gaps */
  --gap-sm: var(--space-4);
  --gap-md: var(--space-6);
  --gap-lg: var(--space-8);
}

/* Responsive Container */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

@media (min-width: 640px) {
  .container { max-width: var(--container-sm); }
}
@media (min-width: 768px) {
  .container {
    max-width: var(--container-md);
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}
@media (min-width: 1024px) {
  .container {
    max-width: var(--container-lg);
    padding-left: var(--space-8);
    padding-right: var(--space-8);
  }
}
@media (min-width: 1280px) {
  .container { max-width: var(--container-xl); }
}
```

## Component Spacing

### Cards
```css
.card {
  padding: var(--space-6);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.card-compact {
  padding: var(--space-4);
}

.card-spacious {
  padding: var(--space-8);
}
```

### Forms
```css
.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  margin-bottom: var(--space-2);
}

.form-input {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-base);
}

.form-input-large {
  padding: var(--space-4) var(--space-5);
}
```

### Buttons
```css
.button {
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-base);
}

.button-sm {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
}

.button-lg {
  padding: var(--space-4) var(--space-8);
  border-radius: var(--radius-md);
}
```

### Sections
```css
.section {
  padding-top: var(--space-12);
  padding-bottom: var(--space-12);
}

@media (min-width: 768px) {
  .section {
    padding-top: var(--space-16);
    padding-bottom: var(--space-16);
  }
}
```

## Z-Index Scale

```css
:root {
  --z-0: 0;
  --z-10: 10;
  --z-20: 20;
  --z-30: 30;
  --z-40: 40;
  --z-50: 50;

  /* Semantic Z-Index */
  --z-base: var(--z-0);
  --z-dropdown: var(--z-10);
  --z-sticky: var(--z-20);
  --z-fixed: var(--z-30);
  --z-modal-backdrop: var(--z-40);
  --z-modal: var(--z-50);
  --z-popover: var(--z-50);
  --z-tooltip: var(--z-50);
}
```

## Responsive Breakpoints

```css
:root {
  --breakpoint-sm: 640px;   /* Small devices */
  --breakpoint-md: 768px;   /* Tablets */
  --breakpoint-lg: 1024px;  /* Laptops */
  --breakpoint-xl: 1280px;  /* Desktops */
  --breakpoint-2xl: 1536px; /* Large desktops */
}
```

## Usage Guidelines

### Consistent Spacing
- Use spacing scale for all margins and padding
- Maintain vertical rhythm with consistent spacing
- Use larger spacing between sections, smaller within components

### Elevation & Depth
- Base layer: `--shadow-xs` or none
- Cards/panels: `--shadow-sm` to `--shadow-md`
- Dropdowns/popovers: `--shadow-lg`
- Modals: `--shadow-xl`
- Hover states: Increase shadow by one level

### Border Radius
- Small interactive elements: `--radius-sm` to `--radius-base`
- Cards: `--radius-md`
- Large sections: `--radius-lg` to `--radius-xl`
- Avatars/pills: `--radius-full`

### Responsive Design
- Mobile-first approach
- Use container classes for consistent max-widths
- Adjust spacing at different breakpoints
- Stack columns on mobile, grid on desktop
