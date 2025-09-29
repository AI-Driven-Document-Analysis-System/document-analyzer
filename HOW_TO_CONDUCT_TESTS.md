# HOW TO CONDUCT TESTS - STEP BY STEP PROCESS

## 3.1.1 DATA AND DATABASE INTEGRITY TESTING

### Using pgbench (PostgreSQL Load Testing Tool):
**What you do:**
1. Open command prompt
2. Initialize test database: `pgbench -i -s 10 document_analyzer_test`
3. Run concurrent connection test: `pgbench -c 20 -j 4 -T 60 document_analyzer_test`
4. Watch output showing transactions per second and latency

**What to look for:**
- TPS (transactions per second) should be consistent
- Average latency under 100ms
- No connection failures

### Using pg_prove (Database Unit Testing):
**What you do:**
1. Install pgTAP extension in your database
2. Write SQL test files for your tables
3. Run: `pg_prove -d document_analyzer_test tests/`
4. Check test results for each database function

**What to look for:**
- All database constraints working
- Triggers firing correctly
- Data validation rules enforced

### Using EXPLAIN ANALYZE (Query Performance):
**What you do:**
1. Connect to database with psql
2. Run: `EXPLAIN ANALYZE SELECT * FROM documents WHERE user_id = 123;`
3. Look at execution plan and timing
4. Check if indexes are being used

**What to look for:**
- No sequential scans on large tables
- Index scans being used
- Query execution time under 100ms

### Using pg_dump/pg_restore (Backup/Recovery Testing):
**What you do:**
1. Create backup: `pg_dump document_analyzer > backup.sql`
2. Intentionally corrupt some data
3. Restore: `psql document_analyzer < backup.sql`
4. Verify all data is restored correctly

**What to look for:**
- Complete data restoration
- No data corruption
- Foreign key relationships intact

### Using MinIO Performance Testing (mc admin):
**What you do:**
1. Install MinIO client: `mc`
2. Configure alias: `mc alias set myminio http://localhost:9000 minioadmin minioadmin`
3. Test upload speed: `mc cp large_file.pdf myminio/documents/`
4. Test download speed: `mc cp myminio/documents/large_file.pdf ./downloaded.pdf`
5. Run concurrent uploads: `for i in {1..10}; do mc cp file$i.pdf myminio/documents/ & done`

**What to look for:**
- Upload throughput > 10MB/s
- Download throughput > 15MB/s
- No failed uploads under concurrent load
- Consistent performance across multiple files

### Using ChromaDB Performance Testing:
**What you do:**
1. Create test script to insert 1000 documents with embeddings
2. Measure insertion time: `time python insert_test_docs.py`
3. Test query performance: measure time for similarity search with different k values
4. Test collection size scaling: insert 10k, 100k, 1M documents and measure query time
5. Monitor memory usage during large batch operations

**What to look for:**
- Insertion rate > 100 documents/minute
- Query time < 100ms for collections up to 100k documents
- Memory usage scales linearly with collection size
- No performance degradation with concurrent queries

---

## 3.1.2 FUNCTION TESTING

### Using Test Script Automation Tool (Selenium/Playwright):
**What you do:**
1. Install Selenium WebDriver or Playwright
2. Create automated test scripts for each use case:
   - User registration with valid/invalid data
   - Document upload with different file types
   - Chat functionality with various queries
   - Summary generation with different options
3. Execute scripts to test all business functions
4. Verify expected results vs actual results

**What to look for:**
- All use-case scenarios execute successfully
- Valid data produces expected results
- Invalid data shows appropriate error messages
- Business rules are properly applied

### Using Data Generation Tools:
**What you do:**
1. Use tools like Faker or custom scripts to generate test data
2. Create datasets with boundary values (min/max file sizes, text lengths)
3. Generate edge cases (special characters, unicode, empty fields)
4. Test with realistic production-like data volumes

**What to look for:**
- System handles all data types correctly
- Boundary conditions work properly
- Edge cases don't break functionality
- Performance remains acceptable with large datasets

### Using Base Configuration Imager and Restorer:
**What you do:**
1. Create system snapshots before testing
2. Run function tests that modify system state
3. Restore to clean state between test runs
4. Ensure consistent test environment

**What to look for:**
- Tests run consistently across multiple executions
- No test interference from previous runs
- Clean state restoration works properly

### Using Installation Monitoring Tools:
**What you do:**
1. Monitor system resources (CPU, memory, disk) during function tests
2. Track registry changes (Windows) or system files (Linux)
3. Monitor network usage during API calls
4. Check for memory leaks during long-running tests

**What to look for:**
- Resource usage within acceptable limits
- No memory leaks during extended testing
- System remains stable during all functions
- Network usage patterns are normal

---

## 3.1.3 USER INTERFACE TESTING

### Using Playwright Tool:
**What you do:**
1. Install Playwright: `npm install @playwright/test`
2. Install browsers: `npx playwright install`
3. Create test files for each UI flow (auth.spec.js, upload.spec.js, chat.spec.js)
4. Run tests: `npx playwright test` - automatically tests on Chrome, Firefox, Safari
5. Watch with UI mode: `npx playwright test --ui` to see tests running in real-time

**What to look for:**
- All tests pass on Chrome, Firefox, and Safari
- No JavaScript errors in browser console
- Pages load within reasonable time
- All interactive elements work across browsers

### Testing Specific UI Components with Playwright:
**What you do:**
1. **Authentication Flow**: Test login/register forms, token persistence, protected routes
2. **Document Upload**: Test drag-and-drop, file validation, progress bars, error handling
3. **Chat Interface**: Test message sending, streaming responses, conversation history
4. **Dashboard**: Test analytics charts, document lists, pagination, filters
5. **Responsive Design**: Test on different viewport sizes automatically

**What to look for:**
- Cross-browser consistency (Chrome, Firefox, Safari)
- Mobile responsiveness works correctly
- Streaming chat responses display properly
- File upload progress shows accurately
- Error states display appropriate messages

### Using Playwright Trace Viewer:
**What you do:**
1. Run tests with tracing: `npx playwright test --trace on`
2. When test fails, open trace: `npx playwright show-trace trace.zip`
3. Step through test execution to see exactly what happened
4. View network requests, console logs, screenshots at each step

**What to look for:**
- Identify exact point of failure
- Network request/response details
- Console errors and warnings
- Visual state at time of failure

---

## 3.1.4 PERFORMANCE PROFILING

### Using Apache Bench (ab) for API Performance:
**What you do:**
1. Install Apache Bench
2. Test single endpoint: `ab -n 1000 -c 10 http://localhost:8000/api/health`
3. Test with authentication: `ab -n 100 -c 5 -H "Authorization: Bearer TOKEN" http://localhost:8000/api/documents/list`
4. Review response time statistics

**What to look for:**
- Mean response time under 200ms
- No failed requests
- Consistent response times (low standard deviation)

### Using New Relic or Application Performance Monitoring (APM):
**What you do:**
1. Install New Relic agent in your Python app
2. Run normal operations (upload, chat, summarize)
3. Check New Relic dashboard for bottlenecks
4. Identify slowest database queries and API endpoints

**What to look for:**
- Database queries under 100ms
- API endpoints under 2 seconds
- Memory usage patterns
- Error rates

### Using cProfile (Python Profiler):
**What you do:**
1. Run your app with profiler: `python -m cProfile -o profile.stats run.py`
2. Analyze with: `python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"`
3. Identify functions taking most time

**What to look for:**
- Functions consuming most CPU time
- Excessive function calls
- Memory allocation patterns

---

## 3.1.5 LOAD TESTING

### Using Locust Tool:
**What you do:**
1. Open Locust web interface (usually http://localhost:8089)
2. Set number of users: start with 10
3. Set spawn rate: 1 user per second
4. Click Start Swarming
5. Watch the graphs showing response times and requests per second
6. Gradually increase users to 50, then 100

**What to look for:**
- Response times stay under 2 seconds
- Failure rate stays under 1%
- System doesn't crash
- Response times increase gradually, not suddenly spike

### Manual Load Testing:
**What you do:**
1. Get 10 friends/colleagues to use your app simultaneously
2. Everyone logs in and uploads documents at same time
3. Everyone asks questions in chat
4. Monitor server logs for errors

**What to look for:**
- No one gets error messages
- Everyone's uploads complete successfully
- Chat responses still come quickly

---

## 3.1.6 SECURITY AND ACCESS CONTROL TESTING

### Using OWASP ZAP (Zed Attack Proxy):
**What you do:**
1. Download and install OWASP ZAP
2. Configure browser proxy to point to ZAP (localhost:8080)
3. Browse your application normally to build site tree
4. Right-click on site → Attack → Active Scan
5. Review alerts in Alerts tab

**What to look for:**
- High/Medium risk vulnerabilities
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) issues
- Authentication bypass attempts

### Using Burp Suite Community:
**What you do:**
1. Download Burp Suite Community Edition
2. Configure browser proxy to Burp (127.0.0.1:8080)
3. Browse application with Intercept ON
4. Send requests to Repeater for manual testing
5. Use Intruder for automated attacks

**What to look for:**
- Parameter manipulation results
- Session token security
- Authorization bypass possibilities
- Input validation weaknesses

### Using Nmap for Network Security:
**What you do:**
1. Install Nmap
2. Scan your server: `nmap -sV -sC localhost`
3. Check for open ports: `nmap -p- localhost`
4. Test for common vulnerabilities: `nmap --script vuln localhost`

**What to look for:**
- Unnecessary open ports
- Outdated service versions
- Known CVE vulnerabilities
- Weak SSL/TLS configurations

### Using SQLMap for SQL Injection Testing:
**What you do:**
1. Install SQLMap
2. Test login endpoint: `sqlmap -u "http://localhost:8000/api/auth/login" --data="username=test&password=test"`
3. Test search parameters: `sqlmap -u "http://localhost:8000/api/search?q=test"`
4. Check for database enumeration possibilities

**What to look for:**
- SQL injection vulnerabilities
- Database information disclosure
- Privilege escalation possibilities

---

## 3.1.7 FAILOVER AND RECOVERY TESTING

### Using Chaos Monkey/Chaos Engineering Tools:
**What you do:**
1. Install Chaos Monkey or similar tool
2. Configure it to randomly kill services (database, API server)
3. Run normal user operations while chaos is happening
4. Monitor system recovery time and data integrity

**What to look for:**
- System auto-recovers within defined RTO (Recovery Time Objective)
- No data loss beyond defined RPO (Recovery Point Objective)
- User experience degrades gracefully

### Using Network Simulation Tools (tc, netem):
**What you do:**
1. Install network simulation tools
2. Simulate network latency: `tc qdisc add dev eth0 root netem delay 100ms`
3. Simulate packet loss: `tc qdisc add dev eth0 root netem loss 5%`
4. Test application behavior under poor network conditions

**What to look for:**
- Application handles network issues gracefully
- Retry mechanisms work properly
- Timeouts are appropriate

### Using Database Failover Testing:
**What you do:**
1. Set up PostgreSQL primary-replica configuration
2. Simulate primary database failure
3. Test automatic failover to replica
4. Verify application continues working with replica

**What to look for:**
- Automatic failover within 30 seconds
- No data loss during failover
- Application reconnects to new primary

### Using Circuit Breaker Pattern Testing:
**What you do:**
1. Configure circuit breakers for external APIs (Groq, DeepSeek)
2. Simulate API failures by blocking network access
3. Verify circuit breaker opens and prevents cascading failures
4. Test circuit breaker reset when service recovers

**What to look for:**
- Circuit breaker opens after defined failure threshold
- Fallback mechanisms activate
- Circuit breaker closes when service recovers

---

## 3.1.8 CONFIGURATION TESTING

### Using Playwright for Cross-Browser Testing:
**What you do:**
1. Configure playwright.config.js with multiple browser projects (chromium, firefox, webkit)
2. Run tests across all browsers: `npx playwright test`
3. Run specific browser: `npx playwright test --project=firefox`
4. Compare test results and screenshots across browsers

**What to look for:**
- Consistent behavior across Chrome, Firefox, and Safari
- No browser-specific JavaScript errors
- CSS rendering differences between browsers
- Performance variations between browsers
- Mobile Safari vs desktop Safari differences

### Using Docker for Environment Testing:
**What you do:**
1. Create Docker containers with different Python versions (3.9, 3.10, 3.11)
2. Build your application in each container
3. Run test suite in each environment
4. Test with different dependency versions

**What to look for:**
- Application works on all supported Python versions
- No version-specific compatibility issues
- Dependencies resolve correctly
- Performance consistency across versions

### Using BrowserStack/Sauce Labs for Device Testing:
**What you do:**
1. Sign up for BrowserStack or Sauce Labs
2. Configure tests to run on different devices/OS combinations
3. Test on real mobile devices and desktop browsers
4. Check responsive design on various screen sizes

**What to look for:**
- Mobile responsiveness works correctly
- Touch interactions function properly
- Different screen resolutions supported
- OS-specific behavior differences

### Using Configuration Management Tools (Ansible/Chef):
**What you do:**
1. Create different server configurations (different OS, database versions)
2. Deploy your application to each configuration
3. Run integration tests on each deployment
4. Verify application behavior is consistent

**What to look for:**
- Application deploys successfully on all configurations
- No configuration-specific bugs
- Performance remains within acceptable ranges
- All integrations work correctly

---

## WHAT EACH TOOL ACTUALLY DOES:

**pytest** = Automatically runs your test functions and tells you pass/fail
**Postman** = Lets you send API requests manually and see responses
**Cypress** = Robot that uses your website automatically while you watch
**Locust** = Simulates many users using your app at once
**OWASP ZAP** = Scans your website for security vulnerabilities
**Browser Dev Tools** = Shows you performance data and errors
**pgAdmin** = GUI for viewing and managing your database

## THE TESTING PROCESS:

1. **Start small** - Test basic functions first
2. **Document results** - Keep notes of what passed/failed
3. **Fix issues** - Address problems before moving to next test
4. **Increase complexity** - Add more users, larger files, etc.
5. **Repeat** - Test again after fixes to ensure they work
