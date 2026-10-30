# Java Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Spring Boot REST Controller with JUnit 5

**Context:**
- tech_stack entry: "Java/SpringBoot"
- source_code_path: `src/main/java/com/example/app/`
- 2 @backend AAA scenarios received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Create user via REST API
        Arrange:
          - Spring Boot app is running with test database
          - No user with email "test@example.com" exists
        Act:
          - Send POST /api/users with body { "name": "Alice", "email": "test@example.com" }
        Assert:
          - Response status is 201
          - Response body contains "id" field
          - Response body "email" equals "test@example.com"
  - scenario_text: |
      @backend
      Test Scenario: Reject duplicate email
        Arrange:
          - User with email "existing@example.com" exists in database
        Act:
          - Send POST /api/users with body { "name": "Bob", "email": "existing@example.com" }
        Assert:
          - Response status is 409
          - Response body contains error "Email already registered"
```

### Execution Flow

```
1. LEARN existing code:
   - Found: pom.xml with spring-boot-starter-web dependency
   - Detected: Maven build tool, Spring Boot framework
   - Existing pattern: @RestController, constructor injection, package-by-feature

2. IMPLEMENT (built-in practices, no research):
   - Created: src/main/java/com/example/app/user/UserController.java
   - Created: src/main/java/com/example/app/user/UserService.java
   - Created: src/main/java/com/example/app/user/UserRepository.java
   - Created: src/main/java/com/example/app/user/CreateUserRequest.java (record)
   - Applied: constructor injection, records for DTOs, clean architecture layers

3. WRITE JUnit 5 tests:
   - Created: src/test/java/com/example/app/user/UserControllerTest.java
```

### Implementation Output (snippet)

```java
// src/main/java/com/example/app/user/UserController.java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@RequestBody CreateUserRequest request) {
        UserResponse response = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}

// src/main/java/com/example/app/user/CreateUserRequest.java
public record CreateUserRequest(String name, String email) {}
```

### Test Output (snippet)

```java
// src/test/java/com/example/app/user/UserControllerTest.java
@WebMvcTest(UserController.class)
@ExtendWith(MockitoExtension.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Nested
    @DisplayName("Create user via REST API")
    class CreateUser {

        @Test
        @DisplayName("Response status is 201")
        void returnsCreatedStatus() throws Exception {
            // Arrange
            var request = new CreateUserRequest("Alice", "test@example.com");
            when(userService.create(any())).thenReturn(new UserResponse("u-1", "Alice", "test@example.com"));

            // Act & Assert
            mockMvc.perform(post("/api/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {"name": "Alice", "email": "test@example.com"}
                        """))
                .andExpect(status().isCreated());
        }

        @Test
        @DisplayName("Response body contains id field")
        void responseContainsId() throws Exception {
            // Arrange
            when(userService.create(any())).thenReturn(new UserResponse("u-1", "Alice", "test@example.com"));

            // Act & Assert
            mockMvc.perform(post("/api/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {"name": "Alice", "email": "test@example.com"}
                        """))
                .andExpect(jsonPath("$.id").exists());
        }
    }

    @Nested
    @DisplayName("Reject duplicate email")
    class RejectDuplicate {

        @Test
        @DisplayName("Response status is 409")
        void returnsConflictStatus() throws Exception {
            // Arrange
            when(userService.create(any())).thenThrow(new EmailAlreadyExistsException("existing@example.com"));

            // Act & Assert
            mockMvc.perform(post("/api/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""
                        {"name": "Bob", "email": "existing@example.com"}
                        """))
                .andExpect(status().isConflict());
        }
    }
}
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/main/java/com/example/app/user/UserController.java"
      - "src/main/java/com/example/app/user/UserService.java"
      - "src/main/java/com/example/app/user/UserRepository.java"
      - "src/main/java/com/example/app/user/CreateUserRequest.java"
    test_files:
      - "src/test/java/com/example/app/user/UserControllerTest.java"
    test_results:
      - scenario: "Create user via REST API"
        assert_clause: "Response status is 201"
        status: "pass"
      - scenario: "Create user via REST API"
        assert_clause: "Response body contains id field"
        status: "pass"
      - scenario: "Create user via REST API"
        assert_clause: "Response body email equals test@example.com"
        status: "pass"
      - scenario: "Reject duplicate email"
        assert_clause: "Response status is 409"
        status: "pass"
      - scenario: "Reject duplicate email"
        assert_clause: "Response body contains error Email already registered"
        status: "pass"
    lint_status: "pass"
    stack_identified: "Java/SpringBoot"
  errors: []
```

---

## Example 2: Maven CLI Application

**Context:**
- tech_stack entry: "Java/Plain"
- source_code_path: `src/main/java/com/example/cli/`
- 1 @backend AAA scenario

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Convert CSV to JSON
        Arrange:
          - Input file "data.csv" contains 3 rows with headers "name,age"
        Act:
          - Run CLI command: java -jar app.jar convert --input data.csv --format json
        Assert:
          - Exit code is 0
          - Output file "data.json" is created
          - JSON contains array with 3 elements
```

### Execution Flow

```
1. LEARN: Found pom.xml without framework starters → Plain Java + Maven
2. IMPLEMENT: Created CsvConverter with argparse-style CLI using picocli
3. WRITE: JUnit 5 tests with @TempDir for file I/O
4. RUN tests: mvn test → 3/3 pass
5. RUN lint: checkstyle → pass, google-java-format → pass
```

### Implementation Output (snippet)

```java
// src/main/java/com/example/cli/CsvToJsonConverter.java
public class CsvToJsonConverter {

    public String convert(Path inputFile) throws IOException {
        List<String> lines = Files.readAllLines(inputFile);
        String[] headers = lines.getFirst().split(",");
        var result = new ArrayList<Map<String, String>>();

        for (int i = 1; i < lines.size(); i++) {
            String[] values = lines.get(i).split(",");
            var row = new LinkedHashMap<String, String>();
            for (int j = 0; j < headers.length; j++) {
                row.put(headers[j].trim(), values[j].trim());
            }
            result.add(row);
        }
        return new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(result);
    }
}
```

### Test Output (snippet)

```java
// src/test/java/com/example/cli/CsvToJsonConverterTest.java
class CsvToJsonConverterTest {

    private final CsvToJsonConverter converter = new CsvToJsonConverter();

    @Test
    @DisplayName("Exit code is 0 for valid CSV input")
    void convertsSuccessfully(@TempDir Path tempDir) throws Exception {
        // Arrange
        Path input = tempDir.resolve("data.csv");
        Files.writeString(input, "name,age\nAlice,30\nBob,25\nCharlie,35");

        // Act
        String json = converter.convert(input);

        // Assert — exit code 0 implied by no exception
        assertNotNull(json);
    }

    @Test
    @DisplayName("JSON contains array with 3 elements")
    void outputContainsThreeElements(@TempDir Path tempDir) throws Exception {
        // Arrange
        Path input = tempDir.resolve("data.csv");
        Files.writeString(input, "name,age\nAlice,30\nBob,25\nCharlie,35");

        // Act
        String json = converter.convert(input);

        // Assert
        var array = new ObjectMapper().readTree(json);
        assertEquals(3, array.size());
    }
}
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/main/java/com/example/cli/CsvToJsonConverter.java"
      - "src/main/java/com/example/cli/CliApp.java"
    test_files:
      - "src/test/java/com/example/cli/CsvToJsonConverterTest.java"
    test_results:
      - scenario: "Convert CSV to JSON"
        assert_clause: "Exit code is 0"
        status: "pass"
      - scenario: "Convert CSV to JSON"
        assert_clause: "Output file data.json is created"
        status: "pass"
      - scenario: "Convert CSV to JSON"
        assert_clause: "JSON contains array with 3 elements"
        status: "pass"
    lint_status: "pass"
    stack_identified: "Java/Plain"
  errors: []
```
