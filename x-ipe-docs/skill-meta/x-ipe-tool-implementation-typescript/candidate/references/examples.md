# TypeScript Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: React Component with TypeScript

**Context:**
- tech_stack entry: "TypeScript/React"
- source_code_path: `src/components/`
- 2 @frontend AAA scenarios received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @frontend
      Test Scenario: Render user profile card
        Arrange:
          - User data with name "Alice" and role "Admin" is provided as props
        Act:
          - Render the UserProfileCard component
        Assert:
          - User name "Alice" is displayed
          - Role badge shows "Admin"
  - scenario_text: |
      @frontend
      Test Scenario: Handle missing avatar gracefully
        Arrange:
          - User data without avatarUrl is provided as props
        Act:
          - Render the UserProfileCard component
        Assert:
          - Default avatar placeholder is displayed
          - No image error is thrown
```

### Execution Flow

```
1. LEARN existing code:
   - Found: tsconfig.json with strict: true, jsx: "react-jsx"
   - Found: package.json with react, @testing-library/react
   - Detected: React framework
   - Existing pattern: FC with Props interfaces, named exports

2. IMPLEMENT (built-in practices, no research):
   - Created: src/components/UserProfileCard/UserProfileCard.tsx
   - Created: src/components/UserProfileCard/index.ts (barrel)
   - Applied: Props interface, strict types, named export

3. WRITE vitest tests:
   - Created: src/components/UserProfileCard/__tests__/UserProfileCard.test.tsx
```

### Implementation Output (snippet)

```typescript
// src/components/UserProfileCard/UserProfileCard.tsx
import type { ReactElement } from 'react';

export interface UserProfileCardProps {
  name: string;
  role: string;
  avatarUrl?: string;
}

export function UserProfileCard({
  name,
  role,
  avatarUrl,
}: UserProfileCardProps): ReactElement {
  return (
    <div className="profile-card">
      {avatarUrl ? (
        <img src={avatarUrl} alt={`${name}'s avatar`} className="avatar" />
      ) : (
        <div className="avatar-placeholder" aria-label="Default avatar" />
      )}
      <h2>{name}</h2>
      <span className="role-badge">{role}</span>
    </div>
  );
}
```

### Test Output (snippet)

```typescript
// src/components/UserProfileCard/__tests__/UserProfileCard.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';

import { UserProfileCard } from '../UserProfileCard';

describe('UserProfileCard', () => {
  test('renders user profile card with name and role', () => {
    // Arrange
    const props = { name: 'Alice', role: 'Admin' };

    // Act
    render(<UserProfileCard {...props} />);

    // Assert
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
  });

  test('handles missing avatar gracefully', () => {
    // Arrange
    const props = { name: 'Alice', role: 'Admin' };

    // Act
    render(<UserProfileCard {...props} />);

    // Assert
    expect(screen.getByLabelText('Default avatar')).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });
});
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/components/UserProfileCard/UserProfileCard.tsx"
      - "src/components/UserProfileCard/index.ts"
    test_files:
      - "src/components/UserProfileCard/__tests__/UserProfileCard.test.tsx"
    test_results:
      - scenario: "Render user profile card"
        assert_clause: "User name Alice is displayed"
        status: "pass"
      - scenario: "Render user profile card"
        assert_clause: "Role badge shows Admin"
        status: "pass"
      - scenario: "Handle missing avatar gracefully"
        assert_clause: "Default avatar placeholder is displayed"
        status: "pass"
      - scenario: "Handle missing avatar gracefully"
        assert_clause: "No image error is thrown"
        status: "pass"
    lint_status: "pass"
    stack_identified: "TypeScript/React"
  errors: []
```

---

## Example 2: Express API Endpoint with Interfaces

**Context:**
- tech_stack entry: "TypeScript/Express"
- source_code_path: `src/api/`
- 2 @backend AAA scenarios

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Create a new task
        Arrange:
          - Database is empty
          - Valid task payload with title "Buy groceries"
        Act:
          - Send POST /api/tasks with body { "title": "Buy groceries", "priority": "high" }
        Assert:
          - Response status is 201
          - Response body contains "id" field
          - Response body "title" equals "Buy groceries"
  - scenario_text: |
      @backend
      Test Scenario: Reject task without title
        Arrange:
          - No preconditions
        Act:
          - Send POST /api/tasks with body { "priority": "high" }
        Assert:
          - Response status is 400
          - Response body contains error "title is required"
```

### Implementation Output (snippet)

```typescript
// src/api/types/task.ts
export interface CreateTaskRequest {
  title: string;
  priority: 'low' | 'medium' | 'high';
}

export interface TaskResponse {
  id: string;
  title: string;
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field: string,
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

```typescript
// src/api/routes/tasks.ts
import { Router } from 'express';
import type { Request, Response } from 'express';

import type { CreateTaskRequest, TaskResponse } from '../types/task';
import { ValidationError } from '../types/task';
import { TaskService } from '../services/task-service';

const router = Router();
const taskService = new TaskService();

router.post('/', (req: Request<unknown, TaskResponse, CreateTaskRequest>, res: Response) => {
  try {
    const { title, priority } = req.body;
    if (!title) {
      throw new ValidationError('title is required', 'title');
    }
    const task = taskService.create({ title, priority });
    res.status(201).json(task);
  } catch (error) {
    if (error instanceof ValidationError) {
      res.status(400).json({ error: error.message });
      return;
    }
    res.status(500).json({ error: 'Internal server error' });
  }
});

export { router as tasksRouter };
```

### Test Output (snippet)

```typescript
// tests/api/routes/tasks.test.ts
import request from 'supertest';
import { describe, test, expect, beforeEach } from 'vitest';

import { app } from '../../../src/api/app';

describe('POST /api/tasks', () => {
  test('creates a new task', async () => {
    // Arrange
    const payload = { title: 'Buy groceries', priority: 'high' as const };

    // Act
    const response = await request(app).post('/api/tasks').send(payload);

    // Assert
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.title).toBe('Buy groceries');
  });

  test('rejects task without title', async () => {
    // Arrange
    const payload = { priority: 'high' };

    // Act
    const response = await request(app).post('/api/tasks').send(payload);

    // Assert
    expect(response.status).toBe(400);
    expect(response.body.error).toBe('title is required');
  });
});
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/api/types/task.ts"
      - "src/api/routes/tasks.ts"
      - "src/api/services/task-service.ts"
    test_files:
      - "tests/api/routes/tasks.test.ts"
    test_results:
      - scenario: "Create a new task"
        assert_clause: "Response status is 201"
        status: "pass"
      - scenario: "Create a new task"
        assert_clause: "Response body contains id field"
        status: "pass"
      - scenario: "Create a new task"
        assert_clause: "Response body title equals Buy groceries"
        status: "pass"
      - scenario: "Reject task without title"
        assert_clause: "Response status is 400"
        status: "pass"
      - scenario: "Reject task without title"
        assert_clause: "Response body contains error title is required"
        status: "pass"
    lint_status: "pass"
    stack_identified: "TypeScript/Express"
  errors: []
```

---

## Example 3: Vue SFC with Composition API

**Context:**
- tech_stack entry: "TypeScript/Vue"
- source_code_path: `src/components/`
- 1 @frontend AAA scenario

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @frontend
      Test Scenario: Toggle dark mode
        Arrange:
          - ThemeToggle component is rendered
          - Current theme is "light"
        Act:
          - Click the toggle button
        Assert:
          - Theme switches to "dark"
          - Button label changes to "Switch to light mode"
          - Component emits "theme-change" event with value "dark"
```

### Implementation Output (snippet)

```vue
<!-- src/components/ThemeToggle.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue';

export interface ThemeToggleProps {
  initialTheme?: 'light' | 'dark';
}

export interface ThemeToggleEmits {
  (event: 'theme-change', theme: 'light' | 'dark'): void;
}

const props = withDefaults(defineProps<ThemeToggleProps>(), {
  initialTheme: 'light',
});
const emit = defineEmits<ThemeToggleEmits>();

const currentTheme = ref<'light' | 'dark'>(props.initialTheme);

const buttonLabel = computed(() =>
  currentTheme.value === 'light' ? 'Switch to dark mode' : 'Switch to light mode'
);

function toggleTheme(): void {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light';
  emit('theme-change', currentTheme.value);
}
</script>

<template>
  <button @click="toggleTheme" :aria-label="buttonLabel">
    {{ buttonLabel }}
  </button>
</template>
```

### Test Output (snippet)

```typescript
// src/components/__tests__/ThemeToggle.test.ts
import { mount } from '@vue/test-utils';
import { describe, test, expect } from 'vitest';

import ThemeToggle from '../ThemeToggle.vue';

describe('ThemeToggle', () => {
  test('toggles dark mode', async () => {
    // Arrange
    const wrapper = mount(ThemeToggle, {
      props: { initialTheme: 'light' },
    });

    // Act
    await wrapper.find('button').trigger('click');

    // Assert
    expect(wrapper.find('button').text()).toBe('Switch to light mode');
    expect(wrapper.emitted('theme-change')).toBeTruthy();
    expect(wrapper.emitted('theme-change')![0]).toEqual(['dark']);
  });
});
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/components/ThemeToggle.vue"
    test_files:
      - "src/components/__tests__/ThemeToggle.test.ts"
    test_results:
      - scenario: "Toggle dark mode"
        assert_clause: "Theme switches to dark"
        status: "pass"
      - scenario: "Toggle dark mode"
        assert_clause: "Button label changes to Switch to light mode"
        status: "pass"
      - scenario: "Toggle dark mode"
        assert_clause: "Component emits theme-change event with value dark"
        status: "pass"
    lint_status: "pass"
    stack_identified: "TypeScript/Vue"
  errors: []
```
