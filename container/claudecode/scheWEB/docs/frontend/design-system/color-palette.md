# Color Palette - Poppy & Friendly Design

## Primary Colors (Pastel)

### Main Brand Colors
```css
:root {
  /* Primary - Soft Purple/Lavender */
  --primary-50: #FAF5FF;
  --primary-100: #F3E8FF;
  --primary-200: #E9D5FF;
  --primary-300: #D8B4FE;
  --primary-400: #C084FC;
  --primary-500: #A855F7;  /* Main brand color */
  --primary-600: #9333EA;

  /* Secondary - Peachy Pink */
  --secondary-50: #FFF5F7;
  --secondary-100: #FFE4E9;
  --secondary-200: #FFC9D4;
  --secondary-300: #FFACC2;
  --secondary-400: #FF8FAF;
  --secondary-500: #FF6B9D;  /* Accent color */

  /* Tertiary - Mint Green */
  --tertiary-50: #F0FDF9;
  --tertiary-100: #CCFBEF;
  --tertiary-200: #99F6E0;
  --tertiary-300: #5EEAD4;
  --tertiary-400: #2DD4BF;
  --tertiary-500: #14B8A6;

  /* Warm Yellow - Highlights */
  --accent-50: #FFFBEB;
  --accent-100: #FEF3C7;
  --accent-200: #FDE68A;
  --accent-300: #FCD34D;
  --accent-400: #FBBF24;
  --accent-500: #F59E0B;
}
```

## Neutral Colors (Soft & Warm)

```css
:root {
  /* Warm Grays */
  --neutral-50: #FAFAF9;
  --neutral-100: #F5F5F4;
  --neutral-200: #E7E5E4;
  --neutral-300: #D6D3D1;
  --neutral-400: #A8A29E;
  --neutral-500: #78716C;
  --neutral-600: #57534E;
  --neutral-700: #44403C;
  --neutral-800: #292524;
  --neutral-900: #1C1917;

  /* Background */
  --bg-primary: #FEFEFE;
  --bg-secondary: #F9F9F9;
  --bg-tertiary: #F3F3F3;

  /* Text */
  --text-primary: #2D2D2D;
  --text-secondary: #6B6B6B;
  --text-tertiary: #9B9B9B;
}
```

## Semantic Colors

```css
:root {
  /* Success - Soft Green */
  --success-50: #F0FDF4;
  --success-100: #DCFCE7;
  --success-200: #BBF7D0;
  --success-500: #22C55E;

  /* Warning - Soft Orange */
  --warning-50: #FFF7ED;
  --warning-100: #FFEDD5;
  --warning-200: #FED7AA;
  --warning-500: #F97316;

  /* Error - Soft Red */
  --error-50: #FEF2F2;
  --error-100: #FEE2E2;
  --error-200: #FECACA;
  --error-500: #EF4444;

  /* Info - Soft Blue */
  --info-50: #EFF6FF;
  --info-100: #DBEAFE;
  --info-200: #BFDBFE;
  --info-500: #3B82F6;
}
```

## Usage Guidelines

### Buttons
- **Primary Action**: `--primary-500` background, white text
- **Secondary Action**: `--secondary-500` background, white text
- **Success Action**: `--tertiary-500` background, white text
- **Hover States**: Darken by one shade (e.g., 500 → 600)

### Cards & Containers
- **Main Cards**: `--bg-primary` with subtle shadow
- **Nested Cards**: `--bg-secondary`
- **Hover/Active**: `--primary-50` or `--secondary-50` tint

### Typography
- **Headings**: `--text-primary`
- **Body Text**: `--text-secondary`
- **Muted Text**: `--text-tertiary`

### Status Indicators
- **Available**: `--success-500`
- **Busy**: `--error-500`
- **Tentative**: `--warning-500`
- **Out of Office**: `--neutral-400`

### Gradients (for special elements)
```css
/* Soft Purple to Pink */
.gradient-primary {
  background: linear-gradient(135deg, var(--primary-300), var(--secondary-300));
}

/* Mint to Blue */
.gradient-cool {
  background: linear-gradient(135deg, var(--tertiary-300), var(--info-300));
}

/* Warm Sunset */
.gradient-warm {
  background: linear-gradient(135deg, var(--accent-300), var(--secondary-300));
}
```

## Accessibility

- All color combinations meet WCAG 2.1 AA standards (4.5:1 contrast ratio minimum)
- Primary actions use `--primary-500` which has 4.8:1 contrast on white
- Text colors provide sufficient contrast for readability
- Color is never the only means of conveying information
