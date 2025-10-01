# Animation Framework - Poppy & Delightful

## Technology Stack

### Primary: Framer Motion (React)
**Why Framer Motion:**
- Declarative, easy-to-use API
- Excellent performance with hardware acceleration
- Built-in gesture support
- Layout animations
- SVG animations
- Extensive spring physics
- Server-side rendering support

### Alternative: CSS Animations + GSAP
For vanilla JS or Vue.js implementations

## Animation Principles

### 1. **Speed & Timing**
```javascript
const springConfig = {
  type: "spring",
  stiffness: 260,
  damping: 20,
  mass: 1
};

const easeConfig = {
  duration: 0.3,
  ease: [0.4, 0, 0.2, 1] // Custom easing curve
};
```

### 2. **Animation Types**

#### Entrance Animations
```javascript
// Fade In + Scale
const fadeInScale = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
};

// Slide In
const slideInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
};

// Bounce In
const bounceIn = {
  initial: { opacity: 0, scale: 0.3 },
  animate: { opacity: 1, scale: 1 },
  transition: {
    type: "spring",
    stiffness: 260,
    damping: 15
  }
};
```

#### Hover Animations
```javascript
// Lift & Shadow
const hoverLift = {
  rest: {
    y: 0,
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.08)"
  },
  hover: {
    y: -4,
    boxShadow: "0 16px 24px -4px rgba(0, 0, 0, 0.12)",
    transition: { duration: 0.2 }
  }
};

// Scale & Glow
const hoverGlow = {
  rest: { scale: 1 },
  hover: {
    scale: 1.05,
    boxShadow: "0 8px 16px -4px rgba(168, 85, 247, 0.2)",
    transition: { duration: 0.2 }
  }
};
```

#### Micro-interactions
```javascript
// Button Press
const buttonPress = {
  tap: { scale: 0.95 },
  transition: { duration: 0.1 }
};

// Toggle Switch
const toggleSwitch = {
  on: { x: 20, backgroundColor: "#A855F7" },
  off: { x: 0, backgroundColor: "#D6D3D1" },
  transition: { type: "spring", stiffness: 500, damping: 30 }
};

// Checkbox Check
const checkboxCheck = {
  checked: {
    pathLength: 1,
    opacity: 1,
    transition: { duration: 0.2 }
  },
  unchecked: {
    pathLength: 0,
    opacity: 0,
    transition: { duration: 0.1 }
  }
};
```

## Implementation Examples

### Framer Motion (React)

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Card Component with Entrance Animation
export const ScheduleCard = ({ schedule }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{
        y: -4,
        boxShadow: "0 16px 24px -4px rgba(0, 0, 0, 0.12)"
      }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="schedule-card"
    >
      {/* Card content */}
    </motion.div>
  );
};

// Staggered List Animation
export const ScheduleList = ({ schedules }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {schedules.map(schedule => (
        <motion.div
          key={schedule.id}
          variants={itemVariants}
        >
          <ScheduleCard schedule={schedule} />
        </motion.div>
      ))}
    </motion.div>
  );
};

// Modal with Backdrop Animation
export const Modal = ({ isOpen, children }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-backdrop"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="modal-content"
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// Loading Spinner
export const LoadingSpinner = () => {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}
      className="spinner"
    />
  );
};

// Success Checkmark Animation
export const SuccessCheck = () => {
  return (
    <motion.svg width="60" height="60" viewBox="0 0 60 60">
      <motion.circle
        cx="30"
        cy="30"
        r="28"
        stroke="#22C55E"
        strokeWidth="3"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      />
      <motion.path
        d="M15 30 L25 40 L45 20"
        stroke="#22C55E"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.4, delay: 0.3, ease: "easeInOut" }}
      />
    </motion.svg>
  );
};
```

### CSS Animations (Alternative)

```css
/* Entrance Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.98);
  }
  100% {
    transform: scale(1);
  }
}

/* Apply Animations */
.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.animate-scale-in {
  animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.animate-bounce-in {
  animation: bounceIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hover Transitions */
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 24px -4px rgba(0, 0, 0, 0.12);
}

/* Loading Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Pulse Animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

## Animation Library

### Installation
```bash
# Framer Motion (React)
npm install framer-motion

# GSAP (Alternative)
npm install gsap

# Lottie (for complex animations)
npm install lottie-web
```

### Performance Tips

1. **Use `transform` and `opacity`** - Hardware accelerated
2. **Avoid animating `width`, `height`, `top`, `left`** - Triggers layout
3. **Use `will-change` sparingly** - Only for frequently animated elements
4. **Reduce motion for accessibility**:
```javascript
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const transition = reducedMotion.matches
  ? { duration: 0 }
  : { duration: 0.3, ease: "easeOut" };
```

## Animation Schedule

### Page Load
1. Hero section: Fade in (0s)
2. Navigation: Slide down (0.1s)
3. Dashboard cards: Stagger up (0.2s, 0.1s intervals)
4. User list: Stagger (0.4s, 0.08s intervals)

### User Interactions
- Button click: Immediate feedback (<100ms)
- Form submission: Show loading state (0-300ms)
- Success message: Fade in with checkmark animation (300ms)
- Error message: Shake + fade in (200ms)

### Transitions
- Route changes: Fade out/in (300ms)
- Modal open/close: Scale + fade (250ms)
- Dropdown: Slide down (200ms)
- Tooltip: Fade (150ms)
