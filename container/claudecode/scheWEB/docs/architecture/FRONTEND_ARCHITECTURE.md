# Frontend Architecture - Team Schedule Management System

## Component Hierarchy

```
App
├── Providers
│   ├── AuthProvider (Context)
│   ├── ScheduleProvider (Context)
│   ├── NotificationProvider (Context)
│   └── ThemeProvider (Context)
│
├── Layout
│   ├── AppShell
│   │   ├── Header
│   │   │   ├── Logo
│   │   │   ├── Navigation
│   │   │   ├── UserMenu
│   │   │   └── NotificationBell
│   │   ├── Sidebar (Optional)
│   │   │   └── QuickActions
│   │   ├── MainContent
│   │   └── Footer
│   │
│   └── AuthLayout (Login/Register)
│       ├── AuthCard
│       └── BackgroundAnimation
│
├── Pages
│   ├── LoginPage
│   ├── DashboardPage
│   ├── SchedulePage
│   ├── TeamMembersPage
│   ├── ShiftManagementPage
│   ├── TimeOffPage
│   ├── ProfilePage
│   └── SettingsPage
│
├── Features
│   ├── Schedule
│   │   ├── CalendarView
│   │   │   ├── WeekView
│   │   │   ├── MonthView
│   │   │   └── DayView
│   │   ├── ShiftCard
│   │   ├── ShiftAssignmentModal
│   │   ├── DragDropInterface
│   │   ├── FilterBar
│   │   └── ConflictIndicator
│   │
│   ├── Team
│   │   ├── TeamMemberList
│   │   ├── MemberCard
│   │   ├── MemberDetailModal
│   │   └── AddMemberForm
│   │
│   ├── Shifts
│   │   ├── ShiftTemplateList
│   │   ├── ShiftTemplateForm
│   │   ├── ShiftSwapList
│   │   ├── ShiftSwapCard
│   │   └── SwapRequestModal
│   │
│   ├── TimeOff
│   │   ├── TimeOffCalendar
│   │   ├── TimeOffRequestForm
│   │   ├── RequestApprovalCard
│   │   └── ApprovalModal
│   │
│   └── Notifications
│       ├── NotificationCenter
│       ├── NotificationList
│       ├── NotificationItem
│       └── NotificationPreferences
│
└── Shared Components
    ├── UI
    │   ├── Button
    │   ├── Input
    │   ├── Select
    │   ├── Checkbox
    │   ├── Radio
    │   ├── DatePicker
    │   ├── TimePicker
    │   ├── Card
    │   ├── Badge
    │   ├── Avatar
    │   ├── Modal
    │   ├── Drawer
    │   ├── Toast
    │   ├── Tooltip
    │   ├── Dropdown
    │   └── Tabs
    │
    ├── Layout
    │   ├── Container
    │   ├── Grid
    │   ├── Flex
    │   └── Stack
    │
    ├── Feedback
    │   ├── LoadingSpinner
    │   ├── SkeletonLoader
    │   ├── ErrorBoundary
    │   ├── EmptyState
    │   └── ProgressBar
    │
    └── Data Display
        ├── Table
        ├── List
        ├── Timeline
        └── StatCard
```

## Directory Structure

```
frontend/
├── src/
│   ├── api/                      # API client and services
│   │   ├── client.js             # Axios instance with interceptors
│   │   ├── auth.js               # Authentication API calls
│   │   ├── users.js              # User management API
│   │   ├── shifts.js             # Shift management API
│   │   ├── schedule.js           # Schedule API
│   │   ├── timeoff.js            # Time-off API
│   │   └── notifications.js      # Notifications API
│   │
│   ├── components/               # Reusable components
│   │   ├── ui/                   # Base UI components
│   │   ├── layout/               # Layout components
│   │   ├── feedback/             # Feedback components
│   │   └── data-display/         # Data display components
│   │
│   ├── features/                 # Feature-specific components
│   │   ├── auth/
│   │   ├── schedule/
│   │   ├── team/
│   │   ├── shifts/
│   │   ├── timeoff/
│   │   └── notifications/
│   │
│   ├── contexts/                 # React Context providers
│   │   ├── AuthContext.jsx
│   │   ├── ScheduleContext.jsx
│   │   ├── NotificationContext.jsx
│   │   └── ThemeContext.jsx
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useSchedule.js
│   │   ├── useNotifications.js
│   │   ├── useDebounce.js
│   │   ├── useLocalStorage.js
│   │   └── useMediaQuery.js
│   │
│   ├── pages/                    # Page components
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── SchedulePage.jsx
│   │   ├── TeamMembersPage.jsx
│   │   ├── ShiftManagementPage.jsx
│   │   ├── TimeOffPage.jsx
│   │   ├── ProfilePage.jsx
│   │   └── NotFoundPage.jsx
│   │
│   ├── utils/                    # Utility functions
│   │   ├── date.js               # Date formatting/parsing
│   │   ├── validation.js         # Form validation
│   │   ├── formatting.js         # Text formatting
│   │   ├── storage.js            # LocalStorage helpers
│   │   └── constants.js          # App constants
│   │
│   ├── styles/                   # Global styles
│   │   ├── globals.css           # Global CSS
│   │   ├── animations.css        # Animation definitions
│   │   └── themes.css            # Theme variables
│   │
│   ├── assets/                   # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   │
│   ├── App.jsx                   # Root component
│   ├── main.jsx                  # Entry point
│   └── router.jsx                # Route definitions
│
├── public/                       # Public assets
│   ├── favicon.ico
│   └── manifest.json
│
├── tests/                        # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## Component Design Patterns

### 1. Container/Presentational Pattern

**Container Components (Smart):**
- Handle data fetching and state management
- Connect to context/state
- Pass data to presentational components

**Presentational Components (Dumb):**
- Focus on UI rendering
- Receive data via props
- Emit events via callbacks

Example:
```jsx
// Container
const ShiftListContainer = () => {
  const { shifts, loading, error } = useSchedule();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <ShiftList shifts={shifts} onShiftClick={handleClick} />;
};

// Presentational
const ShiftList = ({ shifts, onShiftClick }) => (
  <div className="shift-list">
    {shifts.map(shift => (
      <ShiftCard key={shift.id} shift={shift} onClick={onShiftClick} />
    ))}
  </div>
);
```

### 2. Compound Components Pattern

For complex components with shared state:

```jsx
const Calendar = ({ children }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());

  return (
    <CalendarContext.Provider value={{ selectedDate, setSelectedDate }}>
      <div className="calendar">{children}</div>
    </CalendarContext.Provider>
  );
};

Calendar.Header = ({ children }) => {
  const { selectedDate } = useContext(CalendarContext);
  return <div className="calendar-header">{children}</div>;
};

Calendar.Grid = ({ children }) => {
  return <div className="calendar-grid">{children}</div>;
};

// Usage
<Calendar>
  <Calendar.Header />
  <Calendar.Grid />
</Calendar>
```

### 3. Render Props Pattern

For sharing logic between components:

```jsx
const DataFetcher = ({ url, render }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, [url]);

  return render({ data, loading });
};

// Usage
<DataFetcher
  url="/api/shifts"
  render={({ data, loading }) => (
    loading ? <Spinner /> : <ShiftList shifts={data} />
  )}
/>
```

## State Management Strategy

### Context API Structure

#### 1. AuthContext
```jsx
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = async (credentials) => {
    const response = await authAPI.login(credentials);
    setUser(response.data.user);
    setIsAuthenticated(true);
    localStorage.setItem('token', response.data.token);
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    authAPI.logout();
  };

  const checkAuth = async () => {
    try {
      const response = await authAPI.me();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch {
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loading,
      login,
      logout,
      hasPermission: (permission) => user?.role?.permissions?.includes(permission)
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

#### 2. ScheduleContext
```jsx
const ScheduleContext = createContext();

export const ScheduleProvider = ({ children }) => {
  const [shifts, setShifts] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('week'); // week, month, day
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchShifts = async (startDate, endDate) => {
    setLoading(true);
    try {
      const response = await scheduleAPI.getShifts({ startDate, endDate, ...filters });
      setShifts(response.data);
    } finally {
      setLoading(false);
    }
  };

  const assignShift = async (shiftData) => {
    const response = await scheduleAPI.createShift(shiftData);
    setShifts([...shifts, response.data]);
    return response.data;
  };

  const updateShift = async (id, updates) => {
    const response = await scheduleAPI.updateShift(id, updates);
    setShifts(shifts.map(s => s.id === id ? response.data : s));
  };

  return (
    <ScheduleContext.Provider value={{
      shifts,
      selectedDate,
      setSelectedDate,
      viewMode,
      setViewMode,
      filters,
      setFilters,
      loading,
      fetchShifts,
      assignShift,
      updateShift
    }}>
      {children}
    </ScheduleContext.Provider>
  );
};
```

#### 3. NotificationContext
```jsx
const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = async () => {
    const response = await notificationAPI.getNotifications();
    setNotifications(response.data);
    setUnreadCount(response.data.filter(n => !n.isRead).length);
  };

  const markAsRead = async (id) => {
    await notificationAPI.markAsRead(id);
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, isRead: true } : n
    ));
    setUnreadCount(prev => prev - 1);
  };

  const addNotification = (notification) => {
    setNotifications([notification, ...notifications]);
    setUnreadCount(prev => prev + 1);
  };

  // WebSocket connection for real-time notifications (future)
  useEffect(() => {
    fetchNotifications();
    // const ws = new WebSocket('ws://localhost:3001/notifications');
    // ws.onmessage = (event) => addNotification(JSON.parse(event.data));
    // return () => ws.close();
  }, []);

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      fetchNotifications,
      markAsRead,
      addNotification
    }}>
      {children}
    </NotificationContext.Provider>
  );
};
```

## Routing Configuration

```jsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <DashboardPage />
      },
      {
        path: 'schedule',
        element: <SchedulePage />,
        loader: scheduleLoader
      },
      {
        path: 'team',
        element: <TeamMembersPage />,
        loader: teamLoader
      },
      {
        path: 'shifts',
        children: [
          {
            index: true,
            element: <ShiftManagementPage />
          },
          {
            path: 'swaps',
            element: <ShiftSwapsPage />
          }
        ]
      },
      {
        path: 'timeoff',
        element: <TimeOffPage />
      },
      {
        path: 'profile',
        element: <ProfilePage />
      },
      {
        path: 'settings',
        element: <SettingsPage />,
        loader: requireAdmin
      }
    ]
  },
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/register',
    element: <RegisterPage />
  }
]);

// Protected route loader
const requireAuth = async () => {
  const isAuthenticated = await checkAuth();
  if (!isAuthenticated) {
    throw redirect('/login');
  }
  return null;
};

// Admin-only loader
const requireAdmin = async () => {
  const user = await getCurrentUser();
  if (user.role.name !== 'Admin') {
    throw new Response('Forbidden', { status: 403 });
  }
  return null;
};
```

## Animation Strategy

### Framer Motion Animations

```jsx
// Page transitions
const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

const PageWrapper = ({ children }) => (
  <motion.div
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    transition={{ duration: 0.3 }}
  >
    {children}
  </motion.div>
);

// Card hover effects
const cardVariants = {
  rest: { scale: 1 },
  hover: {
    scale: 1.02,
    boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
    transition: { duration: 0.2 }
  }
};

// List item stagger
const listVariants = {
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

<motion.ul variants={listVariants} initial="hidden" animate="show">
  {items.map(item => (
    <motion.li key={item.id} variants={itemVariants}>
      {item.content}
    </motion.li>
  ))}
</motion.ul>
```

## Responsive Design

### Breakpoints (Tailwind)
```javascript
module.exports = {
  theme: {
    screens: {
      'xs': '475px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px'
    }
  }
};
```

### Mobile-First Approach
```jsx
// Responsive calendar view
const CalendarView = () => {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(max-width: 1024px)');

  if (isMobile) return <DayView />;
  if (isTablet) return <WeekView />;
  return <MonthView />;
};
```

## Performance Optimization

### Code Splitting
```jsx
// Lazy load heavy components
const SchedulePage = lazy(() => import('./pages/SchedulePage'));
const TimeOffPage = lazy(() => import('./pages/TimeOffPage'));

// Usage with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/schedule" element={<SchedulePage />} />
    <Route path="/timeoff" element={<TimeOffPage />} />
  </Routes>
</Suspense>
```

### Memoization
```jsx
// Expensive computations
const MemoizedShiftList = React.memo(({ shifts }) => (
  <div>
    {shifts.map(shift => <ShiftCard key={shift.id} shift={shift} />)}
  </div>
), (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.shifts.length === nextProps.shifts.length;
});

// Memoized callbacks
const handleShiftClick = useCallback((shiftId) => {
  // Handle click
}, [/* dependencies */]);

// Memoized values
const sortedShifts = useMemo(() => {
  return shifts.sort((a, b) => a.startTime - b.startTime);
}, [shifts]);
```

### Virtual Scrolling
```jsx
import { FixedSizeList } from 'react-window';

const VirtualShiftList = ({ shifts }) => (
  <FixedSizeList
    height={600}
    itemCount={shifts.length}
    itemSize={80}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <ShiftCard shift={shifts[index]} />
      </div>
    )}
  </FixedSizeList>
);
```

## Error Handling

### Error Boundary
```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          resetError={() => this.setState({ hasError: false })}
        />
      );
    }

    return this.props.children;
  }
}
```

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)
```jsx
describe('ShiftCard', () => {
  it('renders shift information correctly', () => {
    const shift = {
      id: 1,
      date: '2025-10-01',
      startTime: '09:00',
      endTime: '17:00',
      user: { name: 'John Doe' }
    };

    render(<ShiftCard shift={shift} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('09:00 - 17:00')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = vi.fn();
    const shift = { id: 1, /* ... */ };

    render(<ShiftCard shift={shift} onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledWith(1);
  });
});
```

### Integration Tests
```jsx
describe('Schedule Page', () => {
  it('displays shifts for selected week', async () => {
    render(
      <ScheduleProvider>
        <SchedulePage />
      </ScheduleProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Week of Oct 1')).toBeInTheDocument();
    });

    expect(screen.getAllByTestId('shift-card')).toHaveLength(5);
  });
});
```

### E2E Tests (Playwright)
```javascript
test('user can assign a shift', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'manager@example.com');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');

  await page.goto('/schedule');
  await page.click('button:has-text("Assign Shift")');
  await page.selectOption('[name="user"]', '1');
  await page.fill('[name="date"]', '2025-10-01');
  await page.click('button:has-text("Save")');

  await expect(page.locator('.shift-card')).toContainText('John Doe');
});
```
