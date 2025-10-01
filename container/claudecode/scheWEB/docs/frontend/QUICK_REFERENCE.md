# Frontend Quick Reference Guide

## 🎨 Design Tokens

### Colors
```css
/* Primary Actions */
--primary-500: #A855F7    /* Purple */
--secondary-500: #FF6B9D  /* Pink */
--tertiary-500: #14B8A6   /* Mint */

/* Status Colors */
--success-500: #22C55E    /* ✅ Available */
--error-500: #EF4444      /* 🔴 Busy */
--warning-500: #F97316    /* ⏳ Tentative */
--neutral-400: #A8A29E    /* ⚪ Out of Office */
```

### Typography
```css
/* Fonts */
--font-primary: 'Inter'
--font-secondary: 'Nunito'
--font-mono: 'JetBrains Mono'

/* Sizes */
--text-xs: 0.75rem    /* 12px */
--text-sm: 0.875rem   /* 14px */
--text-base: 1rem     /* 16px */
--text-lg: 1.125rem   /* 18px */
--text-xl: 1.25rem    /* 20px */
--text-2xl: 1.5rem    /* 24px */
--text-3xl: 1.875rem  /* 30px */
--text-4xl: 2.25rem   /* 36px */
```

### Spacing
```css
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-12: 3rem     /* 48px */
```

### Animations
```javascript
// Standard timing
duration: 0.3
ease: [0.4, 0, 0.2, 1]

// Spring physics
stiffness: 260
damping: 20
```

## 🧩 Component Quick Reference

### Button
```jsx
<Button variant="primary" size="medium" onClick={handleClick}>
  Click Me
</Button>

// Variants: primary, secondary, success, outline, ghost
// Sizes: small, medium, large
```

### Card
```jsx
<Card variant="elevated" hoverable>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
</Card>

// Variants: default, elevated, gradient
```

### Input
```jsx
<Input
  label="Email"
  type="email"
  placeholder="your@email.com"
  error={errors.email}
  required
/>
```

### Badge
```jsx
<Badge variant="success" dot>
  Available
</Badge>

// Variants: default, success, warning, error, info, primary
```

### Modal
```jsx
<Modal isOpen={isOpen} onClose={handleClose} title="Modal Title">
  <p>Modal content</p>
</Modal>
```

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md - Tablet */ }
@media (min-width: 1024px) { /* lg - Laptop */ }
@media (min-width: 1280px) { /* xl - Desktop */ }
```

## 🎭 Animation Presets

### Entrance
```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

### Hover
```jsx
<motion.div
  whileHover={{ y: -4, scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
```

### List Stagger
```jsx
<motion.div
  variants={containerVariants}
  initial="hidden"
  animate="show"
>
  {items.map(item => (
    <motion.div key={item.id} variants={itemVariants}>
```

## 🔌 API Calls

### With TanStack Query
```typescript
// Fetch schedules
const { data, isLoading, error } = useQuery({
  queryKey: ['schedules'],
  queryFn: () => api.getSchedules()
});

// Create schedule
const mutation = useMutation({
  mutationFn: api.createSchedule,
  onSuccess: () => {
    queryClient.invalidateQueries(['schedules']);
  }
});
```

### With Axios
```typescript
// GET
const schedules = await apiClient.get('/schedules');

// POST
const newSchedule = await apiClient.post('/schedules', data);

// PUT
await apiClient.put(`/schedules/${id}`, data);

// DELETE
await apiClient.delete(`/schedules/${id}`);
```

## 🎯 Status Indicators

| Status | Color | Icon | Use Case |
|--------|-------|------|----------|
| Available | `success-200` | ✅ | Free time slots |
| Busy | `error-200` | 🔴 | Scheduled meetings |
| Tentative | `warning-200` | ⏳ | Unconfirmed plans |
| Out of Office | `neutral-200` | 🌴 | Away/vacation |

## 📂 File Locations

```
docs/frontend/
├── design-system/
│   ├── color-palette.md
│   ├── typography.md
│   └── spacing-layout.md
├── animations/
│   └── animation-framework.md
├── components/
│   └── component-library.md
├── layouts/
│   └── dashboard-design.md
├── interactions/
│   └── user-flows.md
├── tech-recommendations.md
├── implementation-roadmap.md
├── FRONTEND_PLAN_SUMMARY.md
└── QUICK_REFERENCE.md (this file)
```

## 🚀 Quick Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Production build
npm run preview          # Preview build

# Code Quality
npm run lint             # ESLint check
npm run format           # Prettier format
npm run type-check       # TypeScript check

# Testing
npm run test             # Run tests
npm run test:ui          # Vitest UI
npm run test:coverage    # Coverage report
```

## 🔑 Key Principles

1. **Mobile First**: Design for mobile, enhance for desktop
2. **Accessibility First**: WCAG AA compliance from the start
3. **Performance First**: < 200KB bundle, < 3.5s TTI
4. **Animation Delight**: Smooth 60fps, reduced motion support
5. **Type Safety**: TypeScript strict mode
6. **Component Reuse**: DRY principles, shared components
7. **Coordination**: Use memory hooks to share decisions

## 💾 Memory Keys (Coordination)

Retrieve backend coordination data:
```bash
# Design decisions
npx claude-flow@alpha hooks memory retrieve frontend/design-system

# Tech stack
npx claude-flow@alpha hooks memory retrieve frontend/tech-stack

# API requirements
npx claude-flow@alpha hooks memory retrieve frontend/api-requirements

# Implementation status
npx claude-flow@alpha hooks memory retrieve frontend/implementation-status
```

## 📞 Team Communication

**Questions for Backend?**
- API endpoints structure
- Authentication flow (JWT)
- Data model confirmation
- Real-time update strategy
- File upload requirements

**Share Progress:**
```bash
npx claude-flow@alpha hooks notify --message "Frontend milestone complete"
```

---

**Quick Start Checklist:**

- [ ] Read `FRONTEND_PLAN_SUMMARY.md` for full overview
- [ ] Review design system files for colors/typography
- [ ] Check `component-library.md` for component patterns
- [ ] Review `animation-framework.md` for motion design
- [ ] Check `dashboard-design.md` for layout structures
- [ ] Read `user-flows.md` for interaction patterns
- [ ] Review `tech-recommendations.md` for setup
- [ ] Follow `implementation-roadmap.md` for timeline

**Need Help?**
- Review full documentation in `/docs/frontend/`
- Check memory for backend coordination
- Ask backend team for API clarifications

---

✅ **Status**: Planning Complete - Ready for Implementation
