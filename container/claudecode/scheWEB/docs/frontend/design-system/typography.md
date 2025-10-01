# Typography System

## Font Families

```css
:root {
  /* Primary Font - Modern, Friendly Sans-Serif */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;

  /* Secondary Font - Rounded, Playful */
  --font-secondary: 'Nunito', 'Quicksand', sans-serif;

  /* Monospace - Code/Time Display */
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Courier New', monospace;
}
```

## Type Scale

```css
:root {
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

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Font Weights */
  --weight-light: 300;
  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --weight-extrabold: 800;
}
```

## Typography Classes

```css
/* Headings */
.heading-1 {
  font-family: var(--font-secondary);
  font-size: var(--text-4xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.heading-2 {
  font-family: var(--font-secondary);
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
}

.heading-3 {
  font-family: var(--font-primary);
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-snug);
  color: var(--text-primary);
}

.heading-4 {
  font-family: var(--font-primary);
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-snug);
  color: var(--text-primary);
}

/* Body Text */
.body-large {
  font-family: var(--font-primary);
  font-size: var(--text-lg);
  font-weight: var(--weight-normal);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
}

.body-base {
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--weight-normal);
  line-height: var(--leading-normal);
  color: var(--text-secondary);
}

.body-small {
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: var(--weight-normal);
  line-height: var(--leading-normal);
  color: var(--text-secondary);
}

/* Labels & UI Text */
.label {
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.caption {
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  font-weight: var(--weight-normal);
  line-height: var(--leading-normal);
  color: var(--text-tertiary);
}

/* Special Text */
.time-display {
  font-family: var(--font-mono);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  letter-spacing: 0.02em;
}

.badge-text {
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
```

## Usage Guidelines

### Page Titles
- Use `heading-1` with `font-secondary` for main page headers
- Add subtle gradient text for special sections

### Section Headers
- Use `heading-2` or `heading-3` based on hierarchy
- Add emoji icons for friendly touch (optional)

### Cards & Components
- Card titles: `heading-4`
- Card content: `body-base`
- Metadata/timestamps: `caption`

### Forms
- Field labels: `label`
- Input text: `body-base`
- Helper text: `caption`
- Error messages: `body-small` in `--error-500`

### Time Display
- Use `time-display` for all time-related text
- Ensures consistency and readability

### Responsive Typography

```css
@media (max-width: 768px) {
  .heading-1 { font-size: var(--text-3xl); }
  .heading-2 { font-size: var(--text-2xl); }
  .heading-3 { font-size: var(--text-xl); }
  .body-large { font-size: var(--text-base); }
}

@media (max-width: 480px) {
  .heading-1 { font-size: var(--text-2xl); }
  .heading-2 { font-size: var(--text-xl); }
}
```

## Font Loading

```html
<!-- In HTML head -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Nunito:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```
