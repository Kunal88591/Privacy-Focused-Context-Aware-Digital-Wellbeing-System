# Contributing to Privacy-Focused Digital Wellbeing System

Thank you for your interest in contributing to this project! This guide will help you get started.

## 🎯 Project Vision

We're building a system that:
- Protects user privacy without compromise
- Reduces digital distractions intelligently
- Adapts to environmental context
- Respects user autonomy and wellbeing

## 🛠️ Development Setup

1. **Fork and clone** the repository
2. **Run setup script**: `./setup.sh`
3. **Read documentation**: Check `docs/setup/QUICK_START.md`
4. **Start coding!**

## 📁 Project Structure

```
├── backend-api/        # FastAPI backend server
├── mobile-app/         # React Native mobile app
├── iot-device/         # Raspberry Pi code
├── ai-models/          # ML training and models
├── shared/             # Shared utilities
└── docs/               # Documentation
```

## 🔧 Development Workflow

### 1. Pick an Issue
- Browse open issues or create a new one
- Comment to let others know you're working on it
- Get clarification if needed before starting

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes
- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 4. Test Your Changes
```bash
# Backend
cd backend-api
source venv/bin/activate
pytest

# Mobile App
cd mobile-app
npm test

# IoT Device
cd iot-device
source venv/bin/activate
pytest
```

### 5. Commit
```bash
git add .
git commit -m "feat: add notification batching feature"
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python (Backend & IoT)
- Follow PEP 8
- Use type hints
- Docstrings for all functions/classes
- Max line length: 100 characters

Example:
```python
def classify_notification(text: str, sender: str) -> dict:
    """
    Classify a notification as urgent or non-urgent.
    
    Args:
        text: Notification text content
        sender: Sender identifier
        
    Returns:
        dict: Classification result with confidence score
    """
    # Implementation
    pass
```

### JavaScript/TypeScript (Mobile App)
- Use ES6+ features
- Functional components with hooks
- Props validation with PropTypes or TypeScript
- Max line length: 100 characters

Example:
```javascript
/**
 * Notification card component
 * @param {Object} props
 * @param {string} props.title - Notification title
 * @param {boolean} props.isUrgent - Urgency flag
 */
const NotificationCard = ({ title, isUrgent }) => {
  // Implementation
};
```

## 🧪 Testing Requirements

### Unit Tests
- Write tests for all business logic
- Aim for >80% code coverage
- Mock external dependencies

### Integration Tests
- Test API endpoints
- Test MQTT communication
- Test component interactions

### Manual Testing
- Test on actual devices when possible
- Verify privacy features work correctly
- Check performance under load

## 🔒 Security Guidelines

1. **Never commit secrets**: No API keys, passwords, or tokens
2. **Validate all input**: Sanitize user input and API data
3. **Use encryption**: For sensitive data storage and transmission
4. **Privacy first**: Minimize data collection, maximize user control
5. **Report vulnerabilities**: Email security issues privately

## 📚 Documentation

When adding features, update:
- Code comments
- API documentation
- Architecture diagrams (if applicable)
- README.md (for major features)
- User guides

## 🐛 Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots/logs if applicable
- Environment (OS, device, versions)

## 💡 Feature Requests

Include:
- Problem being solved
- Proposed solution
- Alternative approaches considered
- Potential impact on existing features

## 🎨 Design Contributions

- Follow minimalist design principles
- Prioritize clarity and functionality
- Consider accessibility (color contrast, font sizes)
- Provide mockups/wireframes when possible

## 🤝 Code Review Process

1. Maintainers review within 48 hours
2. Address feedback and requested changes
3. Once approved, PR will be merged
4. Your contribution will be credited in release notes

## 📊 Priority Areas

We especially need help with:
- 🧠 **ML Model Improvement**: Better training data, model optimization
- 🔒 **Privacy Features**: Enhanced VPN integration, caller ID masking
- 📱 **Mobile UI/UX**: Interface design, user experience
- 🤖 **IoT Automation**: Smart home integration, additional sensors
- 📖 **Documentation**: Tutorials, guides, examples
- 🧪 **Testing**: Test coverage, edge cases

## 🌟 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in academic papers (if applicable)

## 📞 Getting Help

- **Documentation**: Check `docs/` directory first
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create an issue for bugs or feature requests
- **Direct Contact**: For sensitive matters, create a private issue

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making digital wellbeing better for everyone!** 🙏
