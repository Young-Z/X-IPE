# Application RE — Java Language Mixin

> Apply this mixin when the target codebase contains Java (or Kotlin) source code.
> Merge these overlays into the base playbook when language: java.
> This is an additive overlay — it does NOT replace repo-type mixin content.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Java files | `*.java` files present | high |
| Maven POM | `pom.xml` at root or in modules | high |
| Gradle build | `build.gradle` or `build.gradle.kts` | high |
| Kotlin files | `*.kt` or `*.kts` files | medium |
| Spring Boot | `@SpringBootApplication` annotation | medium |
| Java packages | `src/main/java/` directory structure | medium |

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Identify Maven/Gradle standard layout: src/main/java, src/test/java, src/main/resources
- Map Java package hierarchy to module structure
- Note Spring component scanning base packages
- Identify convention-over-configuration patterns
-->

### For Section 2 (API Contract Extraction)
<!-- ADDITIONAL PROMPTS:
- Extract Spring MVC: @RestController, @RequestMapping, @GetMapping, @PostMapping
- Extract Spring WebFlux: @RouterFunction, RouterFunctions.route()
- Extract JAX-RS: @Path, @GET, @POST, @Produces, @Consumes
- Parse Java records / POJOs for request/response models
- Check for OpenAPI annotations: @Operation, @ApiResponse, @Schema
- Extract interface definitions that serve as API contracts between modules
-->

### For Section 3 (Business Logic Mapping)
<!-- ADDITIONAL PROMPTS:
- Detect GoF patterns in Java idioms:
  Factory: static factory methods, *Factory classes, create*() methods
  Singleton: private constructor + static getInstance(), Spring @Bean
  Builder: fluent API with build() method, @Builder (Lombok)
  Observer: EventListener, ApplicationEvent, @EventListener
  Strategy: interface implementations with context injection
  Template Method: abstract class with final method calling abstract steps
- Detect Spring patterns: DI via @Autowired/@Inject, AOP aspects, @Configuration
- Detect Java EE patterns: DAO, DTO, Service layer, Repository
- Check for Lombok annotations: @Data, @Builder, @Getter/@Setter
-->

### For Section 5 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Parse pom.xml dependencies and dependency management
- Parse build.gradle dependencies blocks
- Detect Java version from source/target compatibility settings
- Identify Spring Boot version from parent POM or plugin
- Detect ORM: Hibernate, JPA, MyBatis, jOOQ
- Detect build plugins: Maven plugins, Gradle plugins
-->

### For Section 7 (Security & Auth Patterns)
<!-- ADDITIONAL PROMPTS:
- Detect Spring Security configuration: SecurityFilterChain, @EnableWebSecurity
- Check for JWT libraries (jjwt, java-jwt, nimbus-jose-jwt)
- Identify role-based annotations: @Secured, @RolesAllowed, @PreAuthorize
- Check for CORS configuration: CorsFilter, @CrossOrigin
-->

### For Section 8 (Testing Strategy)
<!-- ADDITIONAL PROMPTS:
- Detect JUnit 5: @Test, @BeforeEach, @AfterEach, @ParameterizedTest
- Detect JUnit 4: @Test, @Before, @After, @RunWith
- Detect Mockito: @Mock, @InjectMocks, when().thenReturn()
- Detect Spring Test: @SpringBootTest, @WebMvcTest, @DataJpaTest
- Check for test containers: @Testcontainers, @Container
- Identify test coverage tool: JaCoCo, Cobertura
-->
