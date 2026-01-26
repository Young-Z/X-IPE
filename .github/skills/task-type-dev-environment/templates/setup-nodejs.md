# Environment Setup - Node.js

## Tech Stack
- Node.js with npm package manager
- Package management: package.json

## Structure
```
project-root/
├── node_modules/       # Dependencies (auto-generated)
├── src/                # Source code
│   └── index.js
├── tests/              # Test files
│   └── index.test.js
├── package.json        # Project configuration
├── package-lock.json   # Dependency lock file
├── .gitignore          # Git ignore patterns
├── README.md           # Project documentation
└── x-ipe-docs/               # Documentation
    └── environment/
        └── setup.md    # This file
```

## Prerequisites
- Node.js 16+ (includes npm)
- Git
- Optional: yarn (alternative to npm)

## Setup Steps

### 1. Clone or navigate to project
```bash
cd /path/to/project
```

### 2. Install dependencies (when added)
```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### 3. Verify installation
```bash
node --version
npm --version
```

## Development Workflow

### Running the Application
```bash
# Run main entry point
node src/index.js

# Or use npm scripts (if defined in package.json)
npm start
npm run dev
```

### Running Tests
```bash
# Run tests (if test script defined)
npm test

# Or using yarn
yarn test

# Run specific test file
npm test -- tests/index.test.js
```

### Managing Dependencies

#### Add a package
```bash
# Production dependency
npm install <package-name>
# or
yarn add <package-name>

# Development dependency
npm install -D <package-name>
# or
yarn add -D <package-name>

# Global package
npm install -g <package-name>
```

#### Remove a package
```bash
npm uninstall <package-name>
# or
yarn remove <package-name>
```

#### Update packages
```bash
# Update all packages
npm update
# or
yarn upgrade

# Update specific package
npm update <package-name>
# or
yarn upgrade <package-name>
```

#### List installed packages
```bash
npm list
# or
yarn list
```

## Project Structure Guidelines

### Source Code (`src/`)
- Keep all application code here
- Use meaningful file and module names
- Follow consistent naming conventions

**Example:**
```
src/
├── index.js          # Entry point
├── config/
│   └── database.js
├── models/
│   └── user.js
├── services/
│   └── auth.js
├── routes/
│   └── api.js
└── utils/
    └── helpers.js
```

### Tests (`tests/`)
- Mirror source structure
- Name test files: `<module>.test.js` or `<module>.spec.js`
- Use descriptive test names

**Example:**
```
tests/
├── index.test.js
├── models/
│   └── user.test.js
└── services/
    └── auth.test.js
```

## Package.json Configuration

### Common Scripts
```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/",
    "format": "prettier --write \"src/**/*.js\""
  }
}
```

### Dependencies vs DevDependencies
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "nodemon": "^2.0.22",
    "jest": "^29.5.0",
    "eslint": "^8.40.0",
    "prettier": "^2.8.8"
  }
}
```

## Common Tasks

### Setting up development tools
```bash
# Install nodemon for auto-reload
npm install -D nodemon

# Install testing framework
npm install -D jest

# Install linting tools
npm install -D eslint prettier
```

### Using environment variables
Create a `.env` file:
```bash
# .env (excluded by .gitignore)
NODE_ENV=development
PORT=3000
DATABASE_URL=mongodb://localhost/mydb
API_KEY=your-api-key
```

Load in code:
```javascript
// Install dotenv
// npm install dotenv

require('dotenv').config();

const port = process.env.PORT || 3000;
const apiKey = process.env.API_KEY;
```

### Code Quality Tools
```bash
# Install ESLint
npm install -D eslint
npx eslint --init

# Install Prettier
npm install -D prettier
echo {} > .prettierrc

# Lint code
npm run lint

# Format code
npm run format
```

## Common npm Commands

### Package Management
```bash
npm init                    # Initialize new project
npm init -y                 # Initialize with defaults
npm install                 # Install all dependencies
npm install <package>       # Install package
npm install -D <package>    # Install dev dependency
npm uninstall <package>     # Remove package
npm update                  # Update packages
npm outdated                # Check for outdated packages
```

### Scripts
```bash
npm run <script-name>       # Run custom script
npm start                   # Run start script
npm test                    # Run test script
npm run dev                 # Run dev script
```

### Information
```bash
npm list                    # List installed packages
npm list --depth=0          # List top-level packages
npm view <package>          # View package info
npm outdated                # Show outdated packages
```

## Using Yarn (Alternative)

### Installation
```bash
npm install -g yarn
```

### Common Commands
```bash
yarn                        # Install dependencies
yarn add <package>          # Add package
yarn add -D <package>       # Add dev dependency
yarn remove <package>       # Remove package
yarn upgrade                # Update all packages
yarn upgrade <package>      # Update specific package
```

## Notes

- **node_modules/ is excluded** from git (in .gitignore)
- **Commit package.json and package-lock.json** to git
- **Use npm scripts** for common tasks
- **Keep dependencies updated** regularly
- **Use environment variables** for configuration
- **Document scripts** in package.json

## Troubleshooting

### Issue: `node: command not found`
**Solution:**
```bash
# Install Node.js from https://nodejs.org/
# Or use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
```

### Issue: Package installation fails
**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Permission errors
**Solution:**
```bash
# Don't use sudo with npm
# Instead, configure npm to use a different directory
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to ~/.bash_profile or ~/.zshrc:
export PATH=~/.npm-global/bin:$PATH
```

### Issue: Conflicting package versions
**Solution:**
```bash
# Check for conflicts
npm ls

# Update package-lock.json
rm package-lock.json
npm install

# Or use yarn for better dependency resolution
yarn install
```

### Issue: Module not found errors
**Solution:**
```bash
# Ensure package is installed
npm install <package-name>

# Check node_modules exists
ls node_modules/

# Reinstall all dependencies
rm -rf node_modules
npm install
```

## Additional Resources

- [Node.js Documentation](https://nodejs.org/x-ipe-docs/)
- [npm Documentation](https://docs.npmjs.com/)
- [Yarn Documentation](https://yarnpkg.com/)
- [Express.js](https://expressjs.com/) - Popular web framework
- [Jest](https://jestjs.io/) - Testing framework
- [ESLint](https://eslint.org/) - Linting tool
