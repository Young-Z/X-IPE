# MCP Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Python FastMCP Tool with pytest

**Context:**
- tech_stack entry: "MCP/Python"
- source_code_path: `src/weather_mcp/`
- 2 AAA scenarios received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Get current weather for a city
        Arrange:
          - MCP server is running with weather API configured
          - City "London" exists in weather database
        Act:
          - Invoke tool "get_weather" with arguments { "city": "London", "units": "celsius" }
        Assert:
          - Response contains "temperature" field
          - Response contains "condition" field
          - Response "city" equals "London"
  - scenario_text: |
      @backend
      Test Scenario: Reject invalid city name
        Arrange:
          - MCP server is running
        Act:
          - Invoke tool "get_weather" with arguments { "city": "", "units": "celsius" }
        Assert:
          - Response is an MCP error
          - Error message contains "city is required"
```

### Execution Flow

```
1. LEARN existing code:
   - Found: pyproject.toml with "mcp" dependency
   - Detected: Python/FastMCP
   - Transport: stdio (default)

2. IMPLEMENT (built-in MCP practices, no protocol research):
   - Created: src/weather_mcp/server.py
   - Created: src/weather_mcp/tools.py
   - Applied: @mcp.tool(), Pydantic models, annotations

3. WRITE protocol-level tests:
   - Created: tests/test_weather_tools.py
```

### Implementation Output (snippet)

```python
# src/weather_mcp/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def get_weather(city: str, units: str = "celsius") -> dict:
    """Get current weather for a city.

    Args:
        city: Name of the city to get weather for.
        units: Temperature units - 'celsius' or 'fahrenheit'.

    Returns:
        Weather data including temperature, condition, and city name.
    """
    if not city.strip():
        raise ValueError("city is required")

    weather_data = await fetch_weather(city, units)
    return {
        "city": city,
        "temperature": weather_data.temperature,
        "condition": weather_data.condition,
        "units": units,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Test Output (snippet)

```python
# tests/test_weather_tools.py
import pytest
from unittest.mock import AsyncMock, patch

from weather_mcp.server import get_weather


@pytest.mark.asyncio
class TestGetWeather:
    """Get current weather for a city."""

    @patch("weather_mcp.server.fetch_weather")
    async def test_response_contains_temperature(self, mock_fetch):
        """Assert: Response contains temperature field."""
        # Arrange
        mock_fetch.return_value = AsyncMock(temperature=15.0, condition="Cloudy")

        # Act
        result = await get_weather(city="London", units="celsius")

        # Assert
        assert "temperature" in result

    @patch("weather_mcp.server.fetch_weather")
    async def test_response_contains_condition(self, mock_fetch):
        """Assert: Response contains condition field."""
        # Arrange
        mock_fetch.return_value = AsyncMock(temperature=15.0, condition="Cloudy")

        # Act
        result = await get_weather(city="London", units="celsius")

        # Assert
        assert "condition" in result

    @patch("weather_mcp.server.fetch_weather")
    async def test_response_city_equals_london(self, mock_fetch):
        """Assert: Response city equals London."""
        # Arrange
        mock_fetch.return_value = AsyncMock(temperature=15.0, condition="Cloudy")

        # Act
        result = await get_weather(city="London", units="celsius")

        # Assert
        assert result["city"] == "London"


class TestGetWeatherValidation:
    """Reject invalid city name."""

    @pytest.mark.asyncio
    async def test_empty_city_returns_error(self):
        """Assert: Response is an MCP error."""
        # Arrange — no setup needed

        # Act & Assert
        with pytest.raises(ValueError):
            await get_weather(city="", units="celsius")

    @pytest.mark.asyncio
    async def test_error_message_contains_city_required(self):
        """Assert: Error message contains city is required."""
        # Arrange — no setup needed

        # Act & Assert
        with pytest.raises(ValueError, match="city is required"):
            await get_weather(city="", units="celsius")
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/weather_mcp/server.py"
      - "src/weather_mcp/tools.py"
    test_files:
      - "tests/test_weather_tools.py"
    test_results:
      - scenario: "Get current weather for a city"
        assert_clause: "Response contains temperature field"
        status: "pass"
      - scenario: "Get current weather for a city"
        assert_clause: "Response contains condition field"
        status: "pass"
      - scenario: "Get current weather for a city"
        assert_clause: "Response city equals London"
        status: "pass"
      - scenario: "Reject invalid city name"
        assert_clause: "Response is an MCP error"
        status: "pass"
      - scenario: "Reject invalid city name"
        assert_clause: "Error message contains city is required"
        status: "pass"
    lint_status: "pass"
    stack_identified: "MCP/Python"
  errors: []
```

---

## Example 2: TypeScript MCP SDK Tool

**Context:**
- tech_stack entry: "MCP/TypeScript"
- source_code_path: `src/`
- 1 AAA scenario received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: List files in a directory
        Arrange:
          - MCP server is running with filesystem access configured
          - Directory "/tmp/test" contains files "a.txt" and "b.txt"
        Act:
          - Invoke tool "list_files" with arguments { "directory": "/tmp/test" }
        Assert:
          - Response contains array of file entries
          - Array length is 2
          - Each entry contains "name" and "size" fields
```

### Execution Flow

```
1. LEARN: Found package.json with @modelcontextprotocol/sdk → TypeScript/MCP SDK
2. IMPLEMENT: Created server with registerTool, Zod schemas, stdio transport
3. WRITE: vitest tests with MCP client test utilities
4. RUN tests: npx vitest run → 3/3 pass
5. RUN lint: eslint + tsc --noEmit → pass
```

### Implementation Output (snippet)

```typescript
// src/server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readdir, stat } from "fs/promises";
import { join } from "path";

const server = new McpServer({
  name: "filesystem-server",
  version: "1.0.0",
});

server.registerTool(
  "list_files",
  {
    description: "List files in a directory with name and size",
    inputSchema: {
      directory: z.string().describe("Absolute path to the directory to list"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ directory }) => {
    const entries = await readdir(directory);
    const files = await Promise.all(
      entries.map(async (name) => {
        const stats = await stat(join(directory, name));
        return { name, size: stats.size };
      })
    );
    return {
      structuredContent: { files },
      content: [{ type: "text", text: JSON.stringify(files, null, 2) }],
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

### Test Output (snippet)

```typescript
// tests/list-files.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { mkdirSync, writeFileSync, rmSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";

// Assuming a test helper that invokes tools via MCP protocol
import { createTestClient } from "./helpers/mcp-test-client.js";

describe("List files in a directory", () => {
  const testDir = join(tmpdir(), "mcp-test-files");
  let client: Awaited<ReturnType<typeof createTestClient>>;

  beforeAll(async () => {
    mkdirSync(testDir, { recursive: true });
    writeFileSync(join(testDir, "a.txt"), "hello");
    writeFileSync(join(testDir, "b.txt"), "world");
    client = await createTestClient();
  });

  afterAll(() => {
    rmSync(testDir, { recursive: true, force: true });
  });

  it("Response contains array of file entries", async () => {
    // Act
    const result = await client.callTool("list_files", { directory: testDir });

    // Assert
    expect(result.structuredContent.files).toBeInstanceOf(Array);
  });

  it("Array length is 2", async () => {
    // Act
    const result = await client.callTool("list_files", { directory: testDir });

    // Assert
    expect(result.structuredContent.files).toHaveLength(2);
  });

  it("Each entry contains name and size fields", async () => {
    // Act
    const result = await client.callTool("list_files", { directory: testDir });

    // Assert
    for (const entry of result.structuredContent.files) {
      expect(entry).toHaveProperty("name");
      expect(entry).toHaveProperty("size");
    }
  });
});
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/server.ts"
    test_files:
      - "tests/list-files.test.ts"
      - "tests/helpers/mcp-test-client.ts"
    test_results:
      - scenario: "List files in a directory"
        assert_clause: "Response contains array of file entries"
        status: "pass"
      - scenario: "List files in a directory"
        assert_clause: "Array length is 2"
        status: "pass"
      - scenario: "List files in a directory"
        assert_clause: "Each entry contains name and size fields"
        status: "pass"
    lint_status: "pass"
    stack_identified: "MCP/TypeScript"
  errors: []
```
