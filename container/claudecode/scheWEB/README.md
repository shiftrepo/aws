# Team Schedule Management System

A comprehensive team schedule management system with shift tracking, conflict detection, and reporting capabilities. Built with Express.js, SQLite, and optimized for teams up to 30 users.

## Features

- **Team Management**: Create and manage multiple teams with color coding
- **Schedule Management**: Track shifts (morning, afternoon, evening, night) with location support
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **Reporting**: Generate schedule reports by date range and team
- **Security**: HTTP Basic Authentication with session management
- **Performance**: Optimized for 30 concurrent users with sub-500ms response times
- **DevOps**: Complete Docker deployment with automated backups and monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Node.js 18+ and npm 9+ (for local development)

### Deploy with Docker (5 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd schedule-system

# 2. Configure environment
cp config/environments/.env.production .env
nano .env  # Change credentials!

# 3. Deploy
docker-compose up -d

# 4. Verify
curl http://localhost:3000/health
```

**Access**: http://localhost:3000 (Default: admin/changeme)

### Local Development

```bash
# Install dependencies
npm install

# Configure environment
cp config/environments/.env.development .env

# Run migrations
npm run db:migrate

# Start development server
npm run dev
```

## Configuration

### Critical Environment Variables

**MUST CHANGE in production:**

```bash
BASIC_AUTH_USERNAME=your_admin_username
BASIC_AUTH_PASSWORD=your_strong_password
SESSION_SECRET=generate_32_char_random_string
```

Generate secure credentials:

```bash
# Generate password
openssl rand -base64 32

# Generate session secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Architecture

```
├── src/
│   ├── server.js           # Application entry point
│   ├── database.js         # SQLite database layer
│   ├── routes/             # API route handlers
│   ├── middleware/         # Express middleware
│   └── utils/              # Utility functions
├── devops/
│   ├── docker/             # Docker configurations
│   ├── scripts/            # Operational scripts
│   └── monitoring/         # Prometheus configs
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── performance/        # Load tests
├── config/
│   └── environments/       # Environment configs
└── docs/                   # Documentation
```

## API Endpoints

### Teams

- `GET /api/teams` - List all teams
- `POST /api/teams` - Create team
- `PUT /api/teams/:id` - Update team
- `DELETE /api/teams/:id` - Delete team

### Schedules

- `GET /api/schedules` - List schedules (with filters)
- `POST /api/schedules` - Create schedule
- `PUT /api/schedules/:id` - Update schedule
- `DELETE /api/schedules/:id` - Delete schedule
- `GET /api/schedules/conflicts` - Detect conflicts
- `GET /api/schedules/report` - Generate report

### Health

- `GET /health` - Application health check

## Testing

```bash
# Run all tests
npm test

# Unit tests only
npm run test:unit

# Integration tests
npm run test:integration

# Performance tests (requires k6)
npm run test:performance
```

### Test Coverage

- Unit Tests: 80%+ coverage
- Integration Tests: 70%+ coverage
- Performance: Validated for 30 concurrent users

## Deployment

### Production Deployment

```bash
# Start with SSL and backups
docker-compose --profile production up -d

# With monitoring
docker-compose --profile monitoring up -d
```

### Backup & Recovery

```bash
# Manual backup
docker-compose exec app /backup/backup.sh

# Restore from backup
docker-compose exec app /backup/restore.sh <backup-file>

# List backups
docker-compose exec app ls /app/backups/
```

### Monitoring

**Prometheus**: http://localhost:9090  
**Grafana**: http://localhost:3001 (admin/admin)

## Security

### Built-in Security Features

- ✅ HTTP Basic Authentication
- ✅ Session management with secure cookies
- ✅ Rate limiting (100 req/15min)
- ✅ Security headers (HSTS, XSS Protection, etc.)
- ✅ Input validation and sanitization
- ✅ SQL injection protection (parameterized queries)
- ✅ HTTPS/TLS support via Nginx

### Security Best Practices

1. **Change default credentials immediately**
2. Use strong passwords (12+ characters)
3. Enable HTTPS in production
4. Regular security updates
5. Monitor logs for suspicious activity
6. Enable automated backups

See [Security Guide](./docs/SECURITY.md) for details.

## Performance

### Specifications

- **Max Users**: 30 concurrent
- **Response Time (p95)**: < 500ms
- **Response Time (p99)**: < 1000ms
- **Error Rate**: < 1%
- **Database**: SQLite (optimized)
- **Resource Usage**: 512MB RAM, 1 CPU

### Optimization

- Database indexing on frequently queried fields
- Connection pooling
- Gzip compression
- Static asset caching
- Rate limiting

## Documentation

Comprehensive documentation available:

- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Step-by-step deployment
- **[DevOps Guide](./docs/DEVOPS_GUIDE.md)** - Operations and maintenance
- **[Security Guide](./docs/SECURITY.md)** - Security best practices
- **[Testing Strategy](./docs/TESTING_STRATEGY.md)** - Testing methodology
- **[API Documentation](./docs/API.md)** - API reference (if available)

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
docker-compose logs app
```

**Database locked:**
```bash
docker-compose restart app
```

**Can't access application:**
```bash
# Check if running
docker-compose ps

# Check firewall
sudo ufw status
```

See [DevOps Guide](./docs/DEVOPS_GUIDE.md#troubleshooting) for more.

## CI/CD

GitHub Actions workflow included:

- ✅ Lint and format checks
- ✅ Unit and integration tests
- ✅ Security scanning
- ✅ Docker image build
- ✅ Performance testing
- ✅ Automated deployment

## Development

### Project Setup

```bash
# Install dependencies
npm install

# Set up git hooks
npx husky install

# Run migrations
npm run db:migrate
```

### Code Quality

```bash
# Lint
npm run lint

# Format
npm run format

# Type check (if using TypeScript)
npm run typecheck
```

## Technology Stack

- **Backend**: Node.js 18+, Express.js
- **Database**: SQLite with better-sqlite3
- **Security**: Helmet, express-rate-limit, bcrypt
- **Testing**: Jest, Supertest, k6, Artillery
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Monitoring**: Prometheus, Grafana (optional)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure all tests pass (`npm test`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Security**: security@example.com

## Roadmap

- [ ] Multi-factor authentication
- [ ] Real-time notifications
- [ ] Mobile app
- [ ] Advanced reporting with charts
- [ ] Calendar integration (Google, Outlook)
- [ ] Shift swap requests
- [ ] Time-off management
- [ ] Role-based access control (RBAC)

## Acknowledgments

Built with industry best practices for security, performance, and maintainability.

---

**Quick Links:**
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Security Guide](./docs/SECURITY.md)
- [API Documentation](./docs/API.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
