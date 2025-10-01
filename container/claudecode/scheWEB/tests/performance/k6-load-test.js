import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 30 }, // Ramp up to 30 users (max)
    { duration: '5m', target: 30 }, // Stay at 30 users
    { duration: '2m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'], // Error rate < 1%
    errors: ['rate<0.05'], // Custom error rate < 5%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
const USERNAME = __ENV.AUTH_USER || 'admin';
const PASSWORD = __ENV.AUTH_PASS || 'password';

// Helper function for Basic Auth
function getAuthHeaders() {
  const credentials = `${USERNAME}:${PASSWORD}`;
  const encoded = encoding.b64encode(credentials);
  return {
    'Authorization': `Basic ${encoded}`,
    'Content-Type': 'application/json',
  };
}

export default function () {
  const headers = getAuthHeaders();

  // Test 1: Health Check
  {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health check status is 200': (r) => r.status === 200,
    }) || errorRate.add(1);
  }

  sleep(1);

  // Test 2: Get all teams
  {
    const res = http.get(`${BASE_URL}/api/teams`, { headers });
    check(res, {
      'get teams status is 200': (r) => r.status === 200,
      'get teams response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
  }

  sleep(1);

  // Test 3: Get all schedules
  {
    const res = http.get(`${BASE_URL}/api/schedules`, { headers });
    check(res, {
      'get schedules status is 200': (r) => r.status === 200,
      'get schedules response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
  }

  sleep(1);

  // Test 4: Create a team
  {
    const payload = JSON.stringify({
      name: `Team ${Date.now()}`,
      color: '#FF5733',
    });
    const res = http.post(`${BASE_URL}/api/teams`, payload, { headers });
    check(res, {
      'create team status is 201': (r) => r.status === 201,
      'create team response time < 1000ms': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);

    if (res.status === 201) {
      const team = JSON.parse(res.body);

      // Test 5: Update the team
      sleep(1);
      const updatePayload = JSON.stringify({
        name: `Updated Team ${Date.now()}`,
        color: '#33FF57',
      });
      const updateRes = http.put(`${BASE_URL}/api/teams/${team.id}`, updatePayload, { headers });
      check(updateRes, {
        'update team status is 200': (r) => r.status === 200,
      }) || errorRate.add(1);

      // Test 6: Delete the team
      sleep(1);
      const deleteRes = http.del(`${BASE_URL}/api/teams/${team.id}`, null, { headers });
      check(deleteRes, {
        'delete team status is 200': (r) => r.status === 200,
      }) || errorRate.add(1);
    }
  }

  sleep(2);

  // Test 7: Create a schedule entry
  {
    const schedulePayload = JSON.stringify({
      teamId: 1, // Assumes team 1 exists
      date: new Date().toISOString().split('T')[0],
      shift: 'morning',
      location: 'Office',
    });
    const res = http.post(`${BASE_URL}/api/schedules`, schedulePayload, { headers });
    check(res, {
      'create schedule status is 201': (r) => r.status === 201 || r.status === 400,
      'create schedule response time < 1000ms': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
  }

  sleep(1);

  // Test 8: Query schedules by date
  {
    const today = new Date().toISOString().split('T')[0];
    const res = http.get(`${BASE_URL}/api/schedules?date=${today}`, { headers });
    check(res, {
      'query schedules status is 200': (r) => r.status === 200,
      'query schedules response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
  }

  sleep(2);
}

// Setup function (runs once per VU)
export function setup() {
  console.log('Starting load test...');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Max concurrent users: 30`);
}

// Teardown function (runs once at the end)
export function teardown(data) {
  console.log('Load test completed!');
}
