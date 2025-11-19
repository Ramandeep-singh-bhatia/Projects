# FitTracker Pro - Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Adding New Features](#adding-new-features)
5. [Database Migrations](#database-migrations)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Contributing](#contributing)
9. [Best Practices](#best-practices)
10. [Common Development Tasks](#common-development-tasks)

---

## Development Environment Setup

### IDE Setup

**IntelliJ IDEA (Recommended):**

1. **Import Project:**
   ```
   File → Open → Select fittracker-pro directory
   ```

2. **Configure JDK:**
   ```
   File → Project Structure → Project SDK → Select Java 17
   ```

3. **Enable Lombok:**
   ```
   File → Settings → Plugins → Install "Lombok"
   File → Settings → Build, Execution, Deployment → Compiler → Annotation Processors → Enable annotation processing
   ```

4. **Code Style:**
   ```
   File → Settings → Editor → Code Style → Java
   - Use tab character: No
   - Tab size: 4
   - Indent: 4
   - Continuation indent: 8
   ```

5. **Install Plugins:**
   - Lombok
   - Spring Boot
   - Docker
   - Database Navigator
   - SonarLint (code quality)

**VS Code:**

1. **Install Extensions:**
   - Extension Pack for Java
   - Spring Boot Extension Pack
   - Lombok Annotations Support
   - Docker
   - REST Client

2. **settings.json:**
   ```json
   {
     "java.configuration.updateBuildConfiguration": "automatic",
     "java.compile.nullAnalysis.mode": "automatic",
     "spring-boot.ls.java.home": "/path/to/java17"
   }
   ```

### Local Development Setup

1. **Clone Repository:**
   ```bash
   git clone <repository-url>
   cd fittracker-pro
   ```

2. **Start Infrastructure:**
   ```bash
   docker-compose up -d
   ```

3. **Build Project:**
   ```bash
   mvn clean install
   ```

4. **Run Service (for development):**
   ```bash
   cd user-service
   mvn spring-boot:run
   ```

### Hot Reload with Spring DevTools

**Add to pom.xml:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

**In IntelliJ:**
```
File → Settings → Build, Execution, Deployment → Compiler → Build project automatically
File → Settings → Advanced Settings → Allow auto-make to start even if developed application is currently running
```

**In application.yml:**
```yaml
spring:
  devtools:
    restart:
      enabled: true
    livereload:
      enabled: true
```

---

## Project Structure

### Root Directory

```
fittracker-pro/
├── pom.xml                    # Parent POM (defines versions, plugins)
├── docker-compose.yml         # Development infrastructure
├── docker-compose.prod.yml    # Production configuration
├── .gitignore
├── README.md
├── GETTING_STARTED.md
├── ARCHITECTURE.md
├── API_REFERENCE.md
├── DEVELOPER_GUIDE.md         # This file
├── OPERATIONS_GUIDE.md
├── TROUBLESHOOTING.md
├── DEPLOYMENT.md
├── DEMO_SCENARIOS.md
├── .env.example
├── common/                    # Shared code module
├── eureka-server/             # Service discovery
├── config-server/             # Configuration management
├── api-gateway/               # API Gateway
├── user-service/              # User management microservice
├── nutrition-service/         # Nutrition tracking microservice
├── workout-service/           # Workout tracking microservice
├── analytics-service/         # Analytics microservice
├── docker/                    # Docker configs (Prometheus, Grafana)
└── sample-data/               # Sample SQL data
```

### Microservice Structure (Example: user-service)

```
user-service/
├── pom.xml
├── Dockerfile
├── src/
│   ├── main/
│   │   ├── java/com/fittracker/user/
│   │   │   ├── UserServiceApplication.java    # Main class
│   │   │   ├── config/                        # Configuration classes
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   ├── CacheConfig.java
│   │   │   │   └── OpenApiConfig.java
│   │   │   ├── controller/                    # REST controllers
│   │   │   │   └── UserController.java
│   │   │   ├── service/                       # Business logic
│   │   │   │   ├── UserService.java
│   │   │   │   └── AuthService.java
│   │   │   ├── repository/                    # Data access
│   │   │   │   ├── UserRepository.java
│   │   │   │   └── UserProfileRepository.java
│   │   │   ├── model/                         # Domain entities
│   │   │   │   ├── User.java
│   │   │   │   └── UserProfile.java
│   │   │   ├── dto/                           # Data transfer objects
│   │   │   │   ├── RegisterRequest.java
│   │   │   │   ├── LoginRequest.java
│   │   │   │   └── UserResponse.java
│   │   │   ├── exception/                     # Custom exceptions
│   │   │   │   ├── UserNotFoundException.java
│   │   │   │   └── GlobalExceptionHandler.java
│   │   │   └── util/                          # Utility classes
│   │   │       └── JwtUtil.java
│   │   └── resources/
│   │       ├── application.yml                # Application config
│   │       ├── application-dev.yml            # Dev profile
│   │       ├── application-prod.yml           # Prod profile
│   │       └── db/migration/                  # Flyway migrations
│   │           ├── V1__create_users_table.sql
│   │           └── V2__create_profiles_table.sql
│   └── test/
│       ├── java/com/fittracker/user/
│       │   ├── controller/                    # Controller tests
│       │   │   └── UserControllerTest.java
│       │   ├── service/                       # Service tests
│       │   │   └── UserServiceTest.java
│       │   └── integration/                   # Integration tests
│       │       └── UserServiceIntegrationTest.java
│       └── resources/
│           └── application-test.yml           # Test configuration
```

### Package Organization

**Layer-based packages:**
```
com.fittracker.{service}.controller    # REST endpoints
com.fittracker.{service}.service       # Business logic
com.fittracker.{service}.repository    # Data access
com.fittracker.{service}.model         # Domain entities
com.fittracker.{service}.dto           # DTOs
com.fittracker.{service}.config        # Configuration
com.fittracker.{service}.exception     # Exceptions
com.fittracker.{service}.util          # Utilities
```

---

## Coding Standards

### Java Code Style

**Naming Conventions:**

```java
// Classes: PascalCase
public class UserService { }

// Interfaces: PascalCase
public interface UserRepository extends JpaRepository<User, Long> { }

// Methods: camelCase
public User findUserById(Long id) { }

// Variables: camelCase
private String firstName;

// Constants: UPPER_SNAKE_CASE
public static final int MAX_LOGIN_ATTEMPTS = 5;

// Packages: lowercase
package com.fittracker.user.service;
```

**Class Structure Order:**

```java
public class Example {
    // 1. Static fields
    private static final Logger log = LoggerFactory.getLogger(Example.class);

    // 2. Instance fields
    private final DependencyService dependencyService;
    private String instanceField;

    // 3. Constructors
    public Example(DependencyService dependencyService) {
        this.dependencyService = dependencyService;
    }

    // 4. Public methods
    public void publicMethod() { }

    // 5. Protected methods
    protected void protectedMethod() { }

    // 6. Private methods
    private void privateMethod() { }

    // 7. Inner classes/enums
    private static class InnerClass { }
}
```

**Use Lombok to Reduce Boilerplate:**

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    // Lombok generates:
    // - Getters/setters
    // - toString()
    // - equals() and hashCode()
    // - Builder pattern
    // - Constructors
}
```

**Validation Annotations:**

```java
@Data
public class RegisterRequest {
    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, max = 100, message = "Password must be 8-100 characters")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
            message = "Password must contain uppercase, lowercase, number, and special character")
    private String password;

    @NotBlank(message = "First name is required")
    @Size(min = 2, max = 100)
    private String firstName;
}
```

**Comments and Documentation:**

```java
/**
 * Service for managing user authentication and authorization.
 *
 * <p>Provides methods for user registration, login, and token generation.
 * All passwords are hashed using BCrypt before storage.
 *
 * @author FitTracker Team
 * @version 1.0
 * @since 2024-01-01
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    /**
     * Authenticates a user with email and password.
     *
     * @param email the user's email address
     * @param password the user's plain-text password
     * @return JWT token if authentication successful
     * @throws AuthenticationException if credentials are invalid
     */
    public String authenticate(String email, String password) {
        // Method implementation
    }
}
```

### Controller Pattern

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<UserResponse>> register(
            @Valid @RequestBody RegisterRequest request) {

        log.info("Registering new user with email: {}", request.getEmail());

        UserResponse user = userService.register(request);

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("User registered successfully", user));
    }

    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<UserResponse>> getProfile(
            @AuthenticationPrincipal UserDetails userDetails) {

        log.info("Fetching profile for user: {}", userDetails.getUsername());

        UserResponse profile = userService.getProfile(userDetails.getUsername());

        return ResponseEntity.ok(
                ApiResponse.success("Profile retrieved successfully", profile));
    }
}
```

### Service Pattern

```java
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public UserResponse register(RegisterRequest request) {
        // Validate email not already in use
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new EmailAlreadyExistsException("Email already in use");
        }

        // Create user entity
        User user = User.builder()
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .firstName(request.getFirstName())
                .lastName(request.getLastName())
                .dateOfBirth(request.getDateOfBirth())
                .gender(request.getGender())
                .build();

        // Save to database
        User savedUser = userRepository.save(user);

        // Generate JWT token
        String token = jwtUtil.generateToken(savedUser.getEmail(), savedUser.getId());

        // Map to response DTO
        return UserResponse.from(savedUser, token);
    }

    @Transactional(readOnly = true)
    public UserResponse getProfile(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User not found"));

        return UserResponse.from(user);
    }
}
```

### Repository Pattern

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.createdAt > :date")
    List<User> findUsersCreatedAfter(@Param("date") LocalDateTime date);

    @Query(value = "SELECT * FROM users WHERE last_name LIKE :pattern",
           nativeQuery = true)
    List<User> findByLastNamePattern(@Param("pattern") String pattern);
}
```

### Exception Handling

```java
// Custom exception
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}

// Global exception handler
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ApiResponse<?>> handleUserNotFound(
            UserNotFoundException ex) {

        log.error("User not found: {}", ex.getMessage());

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error(ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<?>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.toList());

        log.error("Validation errors: {}", errors);

        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error("Validation failed", errors));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<?>> handleGenericException(Exception ex) {
        log.error("Unexpected error", ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("An unexpected error occurred"));
    }
}
```

---

## Adding New Features

### Example: Adding a New Endpoint

**Scenario:** Add an endpoint to get user's recent activity.

**Step 1: Create DTO**

```java
// user-service/src/main/java/com/fittracker/user/dto/UserActivityResponse.java
@Data
@Builder
public class UserActivityResponse {
    private Long userId;
    private LocalDateTime lastLogin;
    private Integer totalMeals;
    private Integer totalWorkouts;
    private LocalDate memberSince;
}
```

**Step 2: Add Repository Method**

```java
// user-service/src/main/java/com/fittracker/user/repository/UserRepository.java
public interface UserRepository extends JpaRepository<User, Long> {
    // Existing methods...

    @Query("SELECT u FROM User u WHERE u.id = :userId")
    Optional<User> findUserActivity(@Param("userId") Long userId);
}
```

**Step 3: Add Service Method**

```java
// user-service/src/main/java/com/fittracker/user/service/UserService.java
@Service
@RequiredArgsConstructor
public class UserService {
    // Existing fields...

    public UserActivityResponse getUserActivity(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found"));

        // You would fetch totalMeals and totalWorkouts from analytics service
        // or through Kafka events

        return UserActivityResponse.builder()
                .userId(user.getId())
                .lastLogin(user.getLastLoginAt())
                .memberSince(user.getCreatedAt().toLocalDate())
                .build();
    }
}
```

**Step 4: Add Controller Endpoint**

```java
// user-service/src/main/java/com/fittracker/user/controller/UserController.java
@RestController
@RequestMapping("/api/users")
public class UserController {
    // Existing methods...

    @GetMapping("/activity")
    public ResponseEntity<ApiResponse<UserActivityResponse>> getUserActivity(
            @AuthenticationPrincipal UserDetails userDetails) {

        User user = userService.findByEmail(userDetails.getUsername());
        UserActivityResponse activity = userService.getUserActivity(user.getId());

        return ResponseEntity.ok(
                ApiResponse.success("User activity retrieved", activity));
    }
}
```

**Step 5: Add Tests**

```java
// user-service/src/test/java/com/fittracker/user/service/UserServiceTest.java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void getUserActivity_ShouldReturnActivity_WhenUserExists() {
        // Arrange
        Long userId = 1L;
        User user = User.builder()
                .id(userId)
                .email("test@example.com")
                .createdAt(LocalDateTime.now().minusDays(30))
                .build();

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        // Act
        UserActivityResponse activity = userService.getUserActivity(userId);

        // Assert
        assertNotNull(activity);
        assertEquals(userId, activity.getUserId());
        verify(userRepository).findById(userId);
    }

    @Test
    void getUserActivity_ShouldThrowException_WhenUserNotFound() {
        // Arrange
        Long userId = 999L;
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(UserNotFoundException.class,
                () -> userService.getUserActivity(userId));
    }
}
```

**Step 6: Update Swagger Documentation**

```java
@Operation(summary = "Get user activity",
           description = "Retrieve user's recent activity summary")
@ApiResponses(value = {
    @ApiResponse(responseCode = "200", description = "Activity retrieved successfully"),
    @ApiResponse(responseCode = "401", description = "Unauthorized"),
    @ApiResponse(responseCode = "404", description = "User not found")
})
@GetMapping("/activity")
public ResponseEntity<ApiResponse<UserActivityResponse>> getUserActivity(
        @AuthenticationPrincipal UserDetails userDetails) {
    // Implementation
}
```

---

## Database Migrations

### Flyway Migrations

**Naming Convention:**
```
V{version}__{description}.sql

Examples:
V1__create_users_table.sql
V2__add_profile_columns.sql
V3__create_indexes.sql
V4__add_foreign_keys.sql
```

**Location:**
```
src/main/resources/db/migration/
```

**Example Migration:**

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Rollback Migration:**

Flyway doesn't support automatic rollback. For rollback, create a new forward migration:

```sql
-- V5__rollback_add_profile_columns.sql
ALTER TABLE users DROP COLUMN IF EXISTS new_column;
```

**Best Practices:**
- ✅ Never modify existing migrations
- ✅ Always test migrations locally first
- ✅ Keep migrations small and focused
- ✅ Add indexes for frequently queried columns
- ✅ Use transactions (Flyway does this by default)
- ✅ Include rollback plan in comments

**Run Migrations:**

Migrations run automatically on application startup. To run manually:

```bash
mvn flyway:migrate -pl user-service
```

**Migration Status:**

```bash
mvn flyway:info -pl user-service
```

---

## Testing

### Test Structure

```
src/test/java/com/fittracker/{service}/
├── controller/          # Controller tests (MockMvc)
├── service/             # Service tests (Mockito)
├── repository/          # Repository tests (TestContainers)
└── integration/         # Integration tests (full context)
```

### Unit Tests (Service Layer)

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @Test
    @DisplayName("Should register user successfully when valid request")
    void registerUser_Success() {
        // Arrange
        RegisterRequest request = RegisterRequest.builder()
                .email("test@example.com")
                .password("Password123!")
                .firstName("John")
                .lastName("Doe")
                .build();

        User savedUser = User.builder()
                .id(1L)
                .email(request.getEmail())
                .build();

        when(userRepository.existsByEmail(request.getEmail())).thenReturn(false);
        when(passwordEncoder.encode(request.getPassword())).thenReturn("hashed");
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        // Act
        UserResponse response = userService.register(request);

        // Assert
        assertNotNull(response);
        assertEquals("test@example.com", response.getEmail());
        verify(userRepository).save(any(User.class));
    }

    @Test
    @DisplayName("Should throw exception when email already exists")
    void registerUser_EmailExists_ThrowsException() {
        // Arrange
        RegisterRequest request = RegisterRequest.builder()
                .email("existing@example.com")
                .build();

        when(userRepository.existsByEmail(request.getEmail())).thenReturn(true);

        // Act & Assert
        assertThrows(EmailAlreadyExistsException.class,
                () -> userService.register(request));
        verify(userRepository, never()).save(any());
    }
}
```

### Controller Tests

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void registerUser_ValidRequest_ReturnsCreated() throws Exception {
        // Arrange
        RegisterRequest request = RegisterRequest.builder()
                .email("test@example.com")
                .password("Password123!")
                .firstName("John")
                .lastName("Doe")
                .build();

        UserResponse response = UserResponse.builder()
                .id(1L)
                .email("test@example.com")
                .build();

        when(userService.register(any())).thenReturn(response);

        // Act & Assert
        mockMvc.perform(post("/api/users/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(new ObjectMapper().writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.email").value("test@example.com"));
    }
}
```

### Integration Tests (TestContainers)

```java
@SpringBootTest
@Testcontainers
@AutoConfigureMockMvc
class UserServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:14-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void setProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void fullUserRegistrationFlow() throws Exception {
        // Create user
        String registerJson = """
                {
                    "email": "integration@example.com",
                    "password": "Password123!",
                    "firstName": "Integration",
                    "lastName": "Test"
                }
                """;

        mockMvc.perform(post("/api/users/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(registerJson))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true));

        // Verify user in database
        Optional<User> user = userRepository.findByEmail("integration@example.com");
        assertTrue(user.isPresent());
        assertEquals("Integration", user.get().getFirstName());
    }
}
```

### Running Tests

```bash
# Run all tests
mvn test

# Run tests for specific service
mvn test -pl user-service

# Run specific test class
mvn test -Dtest=UserServiceTest

# Run with coverage
mvn test jacoco:report

# Skip tests during build
mvn clean install -DskipTests
```

---

## Debugging

### Logging

**LogBack Configuration (application.yml):**

```yaml
logging:
  level:
    root: INFO
    com.fittracker: DEBUG
    org.springframework.web: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
  pattern:
    console: "%d{yyyy-MM-DD HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/user-service.log
```

**In Code:**

```java
@Slf4j
public class UserService {

    public UserResponse register(RegisterRequest request) {
        log.info("Registering user with email: {}", request.getEmail());
        log.debug("Full registration request: {}", request);

        try {
            // Logic
            log.info("User registered successfully: {}", savedUser.getId());
        } catch (Exception e) {
            log.error("Error registering user", e);
            throw e;
        }
    }
}
```

### Remote Debugging

**1. Start service with debug port:**

```bash
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"
```

**2. In IntelliJ:**

```
Run → Edit Configurations → + → Remote JVM Debug
- Host: localhost
- Port: 5005
- Click Debug
```

**3. Set breakpoints and debug!**

### Database Debugging

**Enable SQL Logging:**

```yaml
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
```

**Example Output:**
```sql
Hibernate:
    /* insert com.fittracker.user.model.User */
    INSERT INTO users
        (email, password_hash, first_name, last_name, created_at)
    VALUES
        (?, ?, ?, ?, ?)
```

---

## Contributing

### Git Workflow

**1. Create Feature Branch:**

```bash
git checkout -b feature/add-user-activity-endpoint
```

**2. Make Changes and Commit:**

```bash
git add .
git commit -m "feat(user): add user activity endpoint

- Add UserActivityResponse DTO
- Add getUserActivity method to UserService
- Add /api/users/activity endpoint
- Add unit tests for new functionality"
```

**Commit Message Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**

```
feat(nutrition): add barcode scanning for food items

- Implement barcode lookup endpoint
- Add BarcodeService for external API integration
- Cache barcode results in Redis
- Add validation for barcode format

Closes #123
```

**3. Push Branch:**

```bash
git push origin feature/add-user-activity-endpoint
```

**4. Create Pull Request**

**5. Code Review and Merge**

---

## Best Practices

### 1. Keep Services Small and Focused

✅ **Good:**
```java
@Service
public class UserService {
    public UserResponse register(RegisterRequest request) { }
    public UserResponse getProfile(String email) { }
    public void updateProfile(UpdateProfileRequest request) { }
}
```

❌ **Bad:**
```java
@Service
public class UserService {
    // Too many responsibilities
    public void register() { }
    public void sendWelcomeEmail() { }
    public void logActivity() { }
    public void updateAnalytics() { }
    public void sendNotification() { }
}
```

### 2. Use DTOs for API Boundaries

✅ **Good:**
```java
@PostMapping("/register")
public ResponseEntity<ApiResponse<UserResponse>> register(
        @Valid @RequestBody RegisterRequest request) {
    // Convert request DTO to entity
    // Process
    // Convert entity to response DTO
    return ResponseEntity.ok(ApiResponse.success("Success", response));
}
```

❌ **Bad:**
```java
@PostMapping("/register")
public ResponseEntity<User> register(@RequestBody User user) {
    // Exposing entity directly
    return ResponseEntity.ok(userService.save(user));
}
```

### 3. Handle Errors Gracefully

✅ **Good:**
```java
@ExceptionHandler(UserNotFoundException.class)
public ResponseEntity<ApiResponse<?>> handleUserNotFound(UserNotFoundException ex) {
    log.error("User not found: {}", ex.getMessage());
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(ApiResponse.error(ex.getMessage()));
}
```

### 4. Use Caching Strategically

```java
@Cacheable(value = "foodItems", key = "#id")
public FoodItem getFoodItem(Long id) {
    return foodItemRepository.findById(id)
            .orElseThrow(() -> new FoodItemNotFoundException("Not found"));
}

@CacheEvict(value = "foodItems", key = "#id")
public void updateFoodItem(Long id, FoodItem updated) {
    // Update logic
}
```

### 5. Write Meaningful Tests

✅ **Good:**
```java
@Test
@DisplayName("Should throw EmailAlreadyExistsException when email is already registered")
void register_EmailExists_ThrowsException() {
    // Clear test name and intent
}
```

### 6. Use Transactions Appropriately

```java
@Transactional
public void completeWorkout(Long workoutId) {
    // All database operations in one transaction
    Workout workout = workoutRepository.findById(workoutId).orElseThrow();
    workout.setStatus(WorkoutStatus.COMPLETED);
    workoutRepository.save(workout);

    // Publish event after transaction commits
    eventPublisher.publishWorkoutCompleted(workout);
}
```

---

## Common Development Tasks

### Add New Microservice

1. **Copy existing service as template**
2. **Update pom.xml** with service name
3. **Create database** in docker/init-databases.sql
4. **Update docker-compose.yml** with datasource
5. **Create domain models and migrations**
6. **Implement services and controllers**
7. **Add to parent pom.xml** modules section
8. **Register with Eureka** (automatic with dependencies)

### Add Kafka Event

1. **Define event class** in common module
2. **Add topic constant** to KafkaTopics class
3. **Publish event** in producer service
4. **Create consumer** in consumer service with @KafkaListener
5. **Handle event** and update data

### Add Cache Configuration

1. **Enable caching** with @EnableCaching
2. **Add @Cacheable** to methods that should cache
3. **Add @CacheEvict** to methods that invalidate cache
4. **Configure TTL** in CacheConfig

### Update Swagger Documentation

1. **Add @Operation** to controller methods
2. **Add @ApiResponses** for different status codes
3. **Add @Schema** to DTOs for field descriptions
4. **View at** http://localhost:808X/swagger-ui.html

---

For architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md).
For API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
For operations guide, see [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
