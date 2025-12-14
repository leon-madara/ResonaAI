# Test Coverage Reporting Guide

## Overview

This guide explains how to generate and interpret test coverage reports for the ResonaAI platform.

## Quick Start

### Generate Coverage Report

```bash
# Using the coverage script
python scripts/generate_coverage_report.py

# Or directly with pytest
pytest tests/ --cov=apps/backend --cov-report=html --cov-report=term-missing
```

### View Coverage Reports

1. **Terminal Report**: Displayed automatically when running tests with coverage
2. **HTML Report**: Open `htmlcov/index.html` in your browser
3. **JSON Report**: Available at `coverage.json` for CI/CD integration

## Coverage Configuration

### Coverage Settings (`.coveragerc`)

- **Source**: `apps/backend` - Only backend code is measured
- **Omitted**: Tests, migrations, cache files, virtual environments
- **Target**: 80% minimum coverage (configured in `pytest.ini`)

### Excluded Patterns

The following are excluded from coverage:
- Test files (`*/tests/*`, `*/test_*.py`)
- Cache directories (`*/__pycache__/*`)
- Virtual environments (`*/venv/*`, `*/env/*`)
- Database migrations (`*/migrations/*`)
- Abstract methods and protocols

## Coverage Reports

### Terminal Report

Shows:
- Overall coverage percentage
- Coverage by module/file
- Missing line numbers
- Files with low coverage

Example:
```
Name                                    Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
apps/backend/services/dissonance-detector/main.py      45      2    96%   23-24
apps/backend/services/baseline-tracker/main.py         52      5    90%   18-22
-------------------------------------------------------------------------
TOTAL                                                  1234    156    87%
```

### HTML Report

Interactive report showing:
- File-by-file coverage
- Line-by-line highlighting (green = covered, red = missing)
- Branch coverage
- Missing line numbers

### JSON Report

Machine-readable format for:
- CI/CD integration
- Automated coverage tracking
- Coverage trend analysis

## Running Coverage for Specific Services

```bash
# Single service
pytest tests/services/dissonance-detector/ --cov=apps/backend/services/dissonance-detector --cov-report=html

# Multiple services
pytest tests/services/{dissonance-detector,baseline-tracker}/ --cov=apps/backend/services --cov-report=html
```

## Coverage Goals

### Current Status

- **Overall**: ~60-70% (varies by service)
- **Target**: 80% minimum
- **Critical Services**: 90%+ (authentication, encryption, crisis detection)

### Service-Specific Targets

| Service | Current | Target | Priority |
|---------|---------|--------|----------|
| Dissonance Detector | 95%+ | 95%+ | High |
| Baseline Tracker | 90%+ | 90%+ | High |
| Crisis Detection | 90%+ | 90%+ | High |
| Safety Moderation | 85%+ | 85%+ | High |
| Cultural Context | 80%+ | 80%+ | Medium |
| Sync Service | 80%+ | 80%+ | Medium |
| Other Services | 70%+ | 80%+ | Medium |

## Improving Coverage

### Identify Gaps

1. Run coverage report
2. Review HTML report for missing lines
3. Check terminal output for files with low coverage

### Add Tests

1. Focus on uncovered code paths
2. Test error handling and edge cases
3. Test integration points
4. Verify all endpoints are tested

### Best Practices

- **Aim for 80%+ coverage** across all services
- **Focus on critical paths** (authentication, data processing, crisis detection)
- **Test edge cases** (invalid input, error conditions)
- **Maintain coverage** as code changes
- **Review coverage reports** before merging PRs

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=apps/backend --cov-report=xml --cov-report=html

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Coverage Badge

Add to README:
```markdown
[![Coverage](https://codecov.io/gh/your-org/resonaai/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/resonaai)
```

## Troubleshooting

### Coverage Not Showing

- Ensure `pytest-cov` is installed: `pip install pytest-cov`
- Check `.coveragerc` configuration
- Verify source paths in `pytest.ini`

### Low Coverage

- Review HTML report to identify gaps
- Add tests for uncovered code
- Check if code should be excluded (abstract methods, etc.)

### Coverage Decreasing

- Review recent changes
- Ensure new code has tests
- Check if tests are being skipped

## Resources

- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Test Execution Guide](TEST_EXECUTION_GUIDE.md)
- [Test Status Report](TEST_STATUS_REPORT.md)

