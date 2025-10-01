# Dashboard Design - Team Schedule Management

## Layout Structure

### 1. Main Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  HEADER (Fixed Top)                                 │
│  - Logo                                             │
│  - Navigation Links                                 │
│  - User Profile                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌──────────────────────────────┐ │
│  │             │  │                              │ │
│  │  SIDEBAR    │  │   MAIN CONTENT AREA          │ │
│  │  (Optional) │  │                              │ │
│  │             │  │  - Dashboard Stats           │ │
│  │  - Home     │  │  - Team Availability Grid    │ │
│  │  - Schedule │  │  - Quick Actions             │ │
│  │  - Team     │  │  - Recent Activity           │ │
│  │  - Settings │  │                              │ │
│  │             │  │                              │ │
│  └─────────────┘  └──────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. Responsive Breakpoints

```javascript
// Mobile: < 768px
// - Hide sidebar, show hamburger menu
// - Stack dashboard cards vertically
// - Single column layout

// Tablet: 768px - 1024px
// - Collapsible sidebar
// - 2-column grid for cards
// - Bottom navigation (optional)

// Desktop: > 1024px
// - Full sidebar visible
// - 3-4 column grid
// - Multi-panel layouts
```

## Dashboard Views

### View 1: Overview Dashboard (Home)

```jsx
// DashboardOverview.jsx
export const DashboardOverview = () => {
  return (
    <div className="dashboard-container p-6 max-w-7xl mx-auto">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-neutral-800 mb-2">
          Welcome back, Sarah! 👋
        </h1>
        <p className="text-lg text-neutral-600">
          Here's what's happening with your team today
        </p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Available Now"
          value="8"
          subtitle="out of 12 team members"
          icon={<UsersIcon />}
          color="success"
        />
        <StatCard
          title="Upcoming Meetings"
          value="3"
          subtitle="in the next 2 hours"
          icon={<CalendarIcon />}
          color="info"
        />
        <StatCard
          title="Free Slots Today"
          value="15"
          subtitle="total available slots"
          icon={<ClockIcon />}
          color="primary"
        />
        <StatCard
          title="Out of Office"
          value="2"
          subtitle="team members"
          icon={<UserXIcon />}
          color="warning"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Team Availability - Takes 2 columns on desktop */}
        <div className="lg:col-span-2">
          <TeamAvailabilityWidget />
        </div>

        {/* Quick Actions Sidebar */}
        <div className="space-y-6">
          <QuickActionsCard />
          <UpcomingMeetingsCard />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <RecentActivityFeed />
      </div>
    </div>
  );
};
```

### View 2: Team Availability Grid

```jsx
// TeamAvailabilityGrid.jsx
export const TeamAvailabilityGrid = () => {
  return (
    <Card className="p-6">
      <CardHeader className="flex items-center justify-between mb-6">
        <CardTitle>Team Availability</CardTitle>
        <div className="flex gap-2">
          <Button variant="outline" size="small">
            Today
          </Button>
          <Button variant="ghost" size="small">
            This Week
          </Button>
          <Button variant="ghost" size="small">
            <FilterIcon />
          </Button>
        </div>
      </CardHeader>

      {/* Time Slots Header */}
      <div className="overflow-x-auto">
        <div className="min-w-[800px]">
          {/* Header Row with Time Slots */}
          <div className="grid grid-cols-13 gap-2 mb-4">
            <div className="col-span-2 font-medium text-sm text-neutral-600">
              Team Member
            </div>
            {timeSlots.map(slot => (
              <div key={slot} className="text-center text-xs text-neutral-500">
                {slot}
              </div>
            ))}
          </div>

          {/* Team Member Rows */}
          {teamMembers.map((member, idx) => (
            <motion.div
              key={member.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="grid grid-cols-13 gap-2 mb-3 items-center"
            >
              {/* Member Info */}
              <div className="col-span-2 flex items-center gap-3">
                <Avatar
                  src={member.avatar}
                  name={member.name}
                  size="small"
                  status={member.status}
                />
                <div>
                  <p className="text-sm font-medium text-neutral-800">
                    {member.name}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {member.role}
                  </p>
                </div>
              </div>

              {/* Availability Slots */}
              {member.schedule.map((slot, slotIdx) => (
                <TimeSlot
                  key={slotIdx}
                  status={slot.status}
                  tooltip={slot.title}
                />
              ))}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-success-200" />
          <span>Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-error-200" />
          <span>Busy</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-warning-200" />
          <span>Tentative</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-neutral-200" />
          <span>Out of Office</span>
        </div>
      </div>
    </Card>
  );
};

// TimeSlot Component
const TimeSlot = ({ status, tooltip }) => {
  const statusColors = {
    available: 'bg-success-200 hover:bg-success-300 border-success-400',
    busy: 'bg-error-200 hover:bg-error-300 border-error-400',
    tentative: 'bg-warning-200 hover:bg-warning-300 border-warning-400',
    out: 'bg-neutral-200 hover:bg-neutral-300 border-neutral-400',
  };

  return (
    <Tooltip content={tooltip}>
      <motion.div
        whileHover={{ scale: 1.1, y: -2 }}
        className={`
          h-8 rounded-md border-2 cursor-pointer
          transition-colors duration-200
          ${statusColors[status]}
        `}
      />
    </Tooltip>
  );
};
```

### View 3: Schedule Input Form

```jsx
// ScheduleForm.jsx
export const ScheduleForm = ({ onSubmit, initialData = null }) => {
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    startTime: '',
    endTime: '',
    status: 'busy',
    description: '',
    recurring: false,
    recurringPattern: 'daily',
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto p-6"
    >
      <Card>
        <CardHeader>
          <CardTitle>
            {initialData ? 'Edit Schedule' : 'Add New Schedule'}
          </CardTitle>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <Input
              label="Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Team Standup Meeting"
              required
            />

            {/* Date and Time Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <DatePicker
                label="Date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
              />
              <TimePicker
                label="Start Time"
                name="startTime"
                value={formData.startTime}
                onChange={handleChange}
                required
              />
              <TimePicker
                label="End Time"
                name="endTime"
                value={formData.endTime}
                onChange={handleChange}
                required
              />
            </div>

            {/* Status */}
            <Select
              label="Status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              options={[
                { value: 'available', label: '✅ Available' },
                { value: 'busy', label: '🔴 Busy' },
                { value: 'tentative', label: '⏳ Tentative' },
                { value: 'out', label: '🌴 Out of Office' },
              ]}
            />

            {/* Description */}
            <div className="form-group">
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Add notes or details about this schedule..."
                rows={4}
                className="w-full px-4 py-3 rounded-lg border-2 border-neutral-200
                         focus:border-primary-500 focus:outline-none focus:ring-2
                         focus:ring-primary-200 transition-colors duration-200"
              />
            </div>

            {/* Recurring Options */}
            <div className="form-group">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="recurring"
                  checked={formData.recurring}
                  onChange={handleChange}
                  className="w-5 h-5 rounded border-2 border-neutral-300
                           text-primary-500 focus:ring-2 focus:ring-primary-200"
                />
                <span className="text-sm font-medium text-neutral-700">
                  Recurring Event
                </span>
              </label>

              {formData.recurring && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4"
                >
                  <Select
                    label="Repeat"
                    name="recurringPattern"
                    value={formData.recurringPattern}
                    onChange={handleChange}
                    options={[
                      { value: 'daily', label: 'Daily' },
                      { value: 'weekly', label: 'Weekly' },
                      { value: 'monthly', label: 'Monthly' },
                    ]}
                  />
                </motion.div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end pt-4">
              <Button
                type="button"
                variant="ghost"
                onClick={() => window.history.back()}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="large"
              >
                {initialData ? 'Update Schedule' : 'Create Schedule'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
};
```

### View 4: User Profile Card

```jsx
// UserProfileCard.jsx
export const UserProfileCard = ({ user }) => {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-4 mb-6">
        <Avatar
          src={user.avatar}
          name={user.name}
          size="xlarge"
          status={user.status}
        />
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-neutral-800">
            {user.name}
          </h2>
          <p className="text-neutral-600">{user.role}</p>
          <div className="flex gap-2 mt-2">
            <Badge variant="primary" size="small">
              {user.department}
            </Badge>
            <Badge
              variant={user.status === 'online' ? 'success' : 'default'}
              size="small"
              dot
            >
              {user.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 py-4 border-t border-neutral-200">
        <div className="text-center">
          <p className="text-2xl font-bold text-primary-500">
            {user.stats.meetings}
          </p>
          <p className="text-xs text-neutral-600">Meetings</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-secondary-500">
            {user.stats.availability}%
          </p>
          <p className="text-xs text-neutral-600">Available</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-tertiary-500">
            {user.stats.responseTime}h
          </p>
          <p className="text-xs text-neutral-600">Response</p>
        </div>
      </div>

      {/* Contact Info */}
      <div className="space-y-3 pt-4 border-t border-neutral-200">
        <div className="flex items-center gap-3 text-sm">
          <EmailIcon className="text-neutral-400" />
          <span className="text-neutral-700">{user.email}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <PhoneIcon className="text-neutral-400" />
          <span className="text-neutral-700">{user.phone}</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 space-y-2">
        <Button variant="primary" className="w-full">
          Schedule Meeting
        </Button>
        <Button variant="outline" className="w-full">
          View Full Profile
        </Button>
      </div>
    </Card>
  );
};
```

## Responsive Design Patterns

### Mobile Navigation

```jsx
// MobileNav.jsx
export const MobileNav = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Hamburger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden p-2"
      >
        <MenuIcon />
      </button>

      {/* Slide-out Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-neutral-900/50 z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25 }}
              className="fixed left-0 top-0 bottom-0 w-80 bg-white shadow-xl z-50 lg:hidden"
            >
              {/* Navigation Content */}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
```

### Grid Responsiveness

```css
/* Mobile-first responsive grids */
.dashboard-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .dashboard-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```
