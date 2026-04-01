# Application RE — Java Language Mixin

> Apply this mixin when the target codebase contains Java (or Kotlin) source code.
> Merge these into the base playbook and collection templates when mixin_key: java.
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

### For Section 2 (Design Pattern Detection)
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

### For Section 3 (API Contracts)
<!-- ADDITIONAL PROMPTS:
- Extract Spring MVC: @RestController, @RequestMapping, @GetMapping, @PostMapping
- Extract Spring WebFlux: @RouterFunction, RouterFunctions.route()
- Extract JAX-RS: @Path, @GET, @POST, @Produces, @Consumes
- Parse Java records / POJOs for request/response models
- Check for OpenAPI annotations: @Operation, @ApiResponse, @Schema
- Extract interface definitions that serve as API contracts between modules
-->

### For Section 5 (Code Structure)
<!-- ADDITIONAL PROMPTS:
- Identify Maven/Gradle standard layout: src/main/java, src/test/java, src/main/resources
- Map Java package hierarchy to module structure
- Note Spring component scanning base packages
- Identify convention-over-configuration patterns
-->

### For Section 7 (Technology Stack)
<!-- ADDITIONAL PROMPTS:
- Parse pom.xml dependencies and dependency management
- Parse build.gradle dependencies blocks
- Detect Java version from source/target compatibility settings
- Identify Spring Boot version from parent POM or plugin
- Detect ORM: Hibernate, JPA, MyBatis, jOOQ
- Detect build plugins: Maven plugins, Gradle plugins
-->

### For Section 8 (Source Code Tests)
<!-- ADDITIONAL PROMPTS:
- Detect JUnit 5: @Test, @BeforeEach, @AfterEach, @ParameterizedTest
- Detect JUnit 4: @Test, @Before, @After, @RunWith
- Detect Mockito: @Mock, @InjectMocks, when().thenReturn()
- Detect Spring Test: @SpringBootTest, @WebMvcTest, @DataJpaTest
- Check for test containers: @Testcontainers, @Container
- Identify test coverage tool: JaCoCo, Cobertura
-->
