# Contributing to Flux

Thank you for your interest in contributing to Flux! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/flux.git
   cd flux
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**
   ```bash
   pytest flux/tests/ -v
   ```

## 🧪 Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **mypy** for type checking

Run before committing:
```bash
black flux/
isort flux/
mypy flux/
```

### Testing

All new features must include tests. We use pytest with asyncio support.

```bash
# Run all tests
pytest flux/tests/ -v

# Run with coverage
pytest flux/tests/ --cov=flux --cov-report=term-missing

# Run specific test file
pytest flux/tests/test_engine.py -v
```

### Type Hints

All functions must include type hints:
```python
def download_file(url: str, output: Path) -> int:
    """Download a file."""
    ...
```

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Add tests for new features
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   black flux/
   isort flux/
   mypy flux/
   pytest flux/tests/ -v
   ```

4. **Commit with descriptive messages**
   ```bash
   git commit -m "feat: Add retry strategy for transient errors"
   ```

   Use conventional commit format:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Build/tooling changes

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

   Then open a Pull Request on GitHub with:
   - Clear description of changes
   - Screenshots for UI changes
   - Link to related issues

## 🎯 Contribution Areas

We welcome contributions in the following areas:

### Core Features
- Network protocol support (FTP, SFTP, etc.)
- Advanced retry strategies
- Bandwidth limiting
- Scheduling downloads

### TUI Enhancements
- Themes and color schemes
- Additional keyboard shortcuts
- Mouse support
- Configuration UI

### Intelligence
- New adaptive strategies
- Machine learning integration
- Predictive ETA algorithms
- Server capability detection

### Documentation
- Tutorials and guides
- Architecture documentation
- Code comments
- Example configurations

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Environment information**
   - OS and version
   - Python version
   - Flux version

2. **Steps to reproduce**
   - Clear, numbered steps
   - Sample URLs (if applicable)

3. **Expected vs actual behavior**

4. **Logs and screenshots**
   - Terminal output
   - Screenshots of TUI issues

Use the [Bug Report template](https://github.com/flux/flux/issues/new?template=bug_report.md) on GitHub.

## 💡 Suggesting Features

Feature requests are welcome! Please use the [Feature Request template](https://github.com/flux/flux/issues/new?template=feature_request.md).

Include:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered

## 📚 Documentation

Documentation improvements are always appreciated:

- Fix typos or unclear explanations
- Add examples and tutorials
- Improve code comments
- Translate documentation

## 🏗️ Architecture Guidelines

When making changes, follow these principles:

1. **UI-Agnostic Core**: The download engine must work independently of the TUI
2. **Event-Driven**: Use events for communication between layers
3. **No Blocking**: All I/O operations must be async
4. **Explainability**: Decisions must be logged and exportable

## 🤝 Code Review

All submissions require review. We'll provide constructive feedback on:

- Code quality and style
- Test coverage
- Documentation
- Architecture fit

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for making Flux better!
