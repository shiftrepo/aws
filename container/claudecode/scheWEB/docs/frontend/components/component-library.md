# Component Library - Schedule Management System

## Core Components

### 1. Button Component

```jsx
// Button.jsx
import { motion } from 'framer-motion';

export const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  disabled = false,
  onClick,
  type = 'button',
  ...props
}) => {
  const variants = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600',
    secondary: 'bg-secondary-500 text-white hover:bg-secondary-600',
    success: 'bg-tertiary-500 text-white hover:bg-tertiary-600',
    outline: 'border-2 border-primary-500 text-primary-500 hover:bg-primary-50',
    ghost: 'text-primary-500 hover:bg-primary-50',
  };

  const sizes = {
    small: 'px-4 py-2 text-sm',
    medium: 'px-6 py-3 text-base',
    large: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={`
        ${variants[variant]}
        ${sizes[size]}
        rounded-lg font-medium
        transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
      `}
      disabled={disabled || isLoading}
      onClick={onClick}
      type={type}
      {...props}
    >
      {isLoading ? (
        <>
          <Spinner size="small" />
          <span>Loading...</span>
        </>
      ) : children}
    </motion.button>
  );
};
```

### 2. Card Component

```jsx
// Card.jsx
import { motion } from 'framer-motion';

export const Card = ({
  children,
  variant = 'default',
  hoverable = true,
  className = '',
  ...props
}) => {
  const variants = {
    default: 'bg-white border border-neutral-200',
    elevated: 'bg-white shadow-md',
    gradient: 'bg-gradient-to-br from-primary-50 to-secondary-50',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hoverable ? {
        y: -4,
        boxShadow: '0 16px 24px -4px rgba(0, 0, 0, 0.12)'
      } : {}}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className={`
        ${variants[variant]}
        rounded-xl p-6
        transition-shadow duration-200
        ${className}
      `}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-xl font-semibold text-neutral-800 ${className}`}>
    {children}
  </h3>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={`${className}`}>
    {children}
  </div>
);
```

### 3. Form Components

```jsx
// Input.jsx
export const Input = ({
  label,
  error,
  helperText,
  required = false,
  ...props
}) => {
  return (
    <div className="form-group">
      {label && (
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-3
          rounded-lg border-2
          ${error
            ? 'border-error-500 focus:border-error-500'
            : 'border-neutral-200 focus:border-primary-500'
          }
          focus:outline-none focus:ring-2 focus:ring-primary-200
          transition-colors duration-200
          bg-white text-neutral-800
          placeholder:text-neutral-400
        `}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-error-500">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1 text-sm text-neutral-500">{helperText}</p>
      )}
    </div>
  );
};

// Select.jsx
export const Select = ({
  label,
  options,
  error,
  required = false,
  ...props
}) => {
  return (
    <div className="form-group">
      {label && (
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      <select
        className={`
          w-full px-4 py-3
          rounded-lg border-2
          ${error
            ? 'border-error-500 focus:border-error-500'
            : 'border-neutral-200 focus:border-primary-500'
          }
          focus:outline-none focus:ring-2 focus:ring-primary-200
          transition-colors duration-200
          bg-white text-neutral-800
          cursor-pointer
        `}
        {...props}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-sm text-error-500">{error}</p>
      )}
    </div>
  );
};

// TimePicker.jsx
export const TimePicker = ({
  label,
  value,
  onChange,
  error,
  required = false
}) => {
  return (
    <Input
      type="time"
      label={label}
      value={value}
      onChange={onChange}
      error={error}
      required={required}
    />
  );
};

// DatePicker.jsx
export const DatePicker = ({
  label,
  value,
  onChange,
  error,
  required = false,
  min,
  max
}) => {
  return (
    <Input
      type="date"
      label={label}
      value={value}
      onChange={onChange}
      error={error}
      required={required}
      min={min}
      max={max}
    />
  );
};
```

### 4. Badge Component

```jsx
// Badge.jsx
export const Badge = ({
  children,
  variant = 'default',
  size = 'medium',
  dot = false
}) => {
  const variants = {
    default: 'bg-neutral-100 text-neutral-700',
    success: 'bg-success-100 text-success-700',
    warning: 'bg-warning-100 text-warning-700',
    error: 'bg-error-100 text-error-700',
    info: 'bg-info-100 text-info-700',
    primary: 'bg-primary-100 text-primary-700',
  };

  const sizes = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-1 text-sm',
    large: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`
        ${variants[variant]}
        ${sizes[size]}
        inline-flex items-center gap-1.5
        rounded-full font-medium
      `}
    >
      {dot && (
        <span className={`
          w-2 h-2 rounded-full
          ${variant === 'success' && 'bg-success-500'}
          ${variant === 'warning' && 'bg-warning-500'}
          ${variant === 'error' && 'bg-error-500'}
          ${variant === 'info' && 'bg-info-500'}
        `} />
      )}
      {children}
    </span>
  );
};
```

### 5. Avatar Component

```jsx
// Avatar.jsx
export const Avatar = ({
  src,
  alt,
  name,
  size = 'medium',
  status
}) => {
  const sizes = {
    small: 'w-8 h-8 text-xs',
    medium: 'w-12 h-12 text-sm',
    large: 'w-16 h-16 text-lg',
    xlarge: 'w-24 h-24 text-2xl',
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="relative inline-block">
      <div
        className={`
          ${sizes[size]}
          rounded-full
          flex items-center justify-center
          font-medium
          ${src
            ? 'bg-neutral-200'
            : 'bg-gradient-to-br from-primary-400 to-secondary-400 text-white'
          }
        `}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name}
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          <span>{getInitials(name)}</span>
        )}
      </div>
      {status && (
        <span
          className={`
            absolute bottom-0 right-0
            w-3 h-3 rounded-full border-2 border-white
            ${status === 'online' && 'bg-success-500'}
            ${status === 'busy' && 'bg-error-500'}
            ${status === 'away' && 'bg-warning-500'}
            ${status === 'offline' && 'bg-neutral-400'}
          `}
        />
      )}
    </div>
  );
};
```

### 6. Modal Component

```jsx
// Modal.jsx
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect } from 'react';

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  showCloseButton = true
}) => {
  const sizes = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    xlarge: 'max-w-4xl',
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className={`
                ${sizes[size]}
                w-full bg-white rounded-2xl shadow-xl
                overflow-hidden
              `}
            >
              {/* Header */}
              <div className="px-6 py-4 border-b border-neutral-200 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-neutral-800">
                  {title}
                </h2>
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="text-neutral-400 hover:text-neutral-600 transition-colors"
                  >
                    <CloseIcon />
                  </button>
                )}
              </div>

              {/* Content */}
              <div className="px-6 py-6 max-h-[70vh] overflow-y-auto">
                {children}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
```

### 7. Loading & Status Components

```jsx
// Spinner.jsx
import { motion } from 'framer-motion';

export const Spinner = ({ size = 'medium', color = 'primary' }) => {
  const sizes = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  const colors = {
    primary: 'border-primary-500',
    secondary: 'border-secondary-500',
    white: 'border-white',
  };

  return (
    <motion.div
      className={`
        ${sizes[size]}
        border-2 ${colors[color]} border-t-transparent
        rounded-full
      `}
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    />
  );
};

// EmptyState.jsx
export const EmptyState = ({
  icon,
  title,
  description,
  action
}) => {
  return (
    <div className="text-center py-12">
      {icon && (
        <div className="mb-4 flex justify-center">
          {icon}
        </div>
      )}
      <h3 className="text-xl font-semibold text-neutral-800 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-neutral-600 mb-6 max-w-md mx-auto">
          {description}
        </p>
      )}
      {action}
    </div>
  );
};

// Alert.jsx
export const Alert = ({
  variant = 'info',
  title,
  children,
  onClose
}) => {
  const variants = {
    success: 'bg-success-50 border-success-200 text-success-800',
    warning: 'bg-warning-50 border-warning-200 text-warning-800',
    error: 'bg-error-50 border-error-200 text-error-800',
    info: 'bg-info-50 border-info-200 text-info-800',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        ${variants[variant]}
        border-2 rounded-lg p-4
        flex items-start gap-3
      `}
    >
      <div className="flex-1">
        {title && (
          <h4 className="font-semibold mb-1">{title}</h4>
        )}
        <div className="text-sm">{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-current opacity-70 hover:opacity-100 transition-opacity"
        >
          <CloseIcon size={20} />
        </button>
      )}
    </motion.div>
  );
};
```

## Component Usage Examples

```jsx
// Example: Schedule Form
<Card>
  <CardHeader>
    <CardTitle>Add New Schedule</CardTitle>
  </CardHeader>
  <CardContent>
    <form>
      <Input
        label="Title"
        placeholder="Meeting with team"
        required
      />
      <DatePicker
        label="Date"
        required
      />
      <TimePicker
        label="Start Time"
        required
      />
      <TimePicker
        label="End Time"
        required
      />
      <Select
        label="Status"
        options={[
          { value: 'available', label: 'Available' },
          { value: 'busy', label: 'Busy' },
          { value: 'tentative', label: 'Tentative' }
        ]}
      />
      <Button type="submit" variant="primary" size="large">
        Save Schedule
      </Button>
    </form>
  </CardContent>
</Card>
```
