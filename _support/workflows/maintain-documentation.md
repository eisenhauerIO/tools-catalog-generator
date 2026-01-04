# Documentation Maintenance Workflow

This guide ensures documentation stays organized, accurate, and free from redundancy.

## Content Ownership Matrix

Each piece of content has a single source of truth. When updating documentation, always update the primary location first, then update cross-references if needed.

| Content | Primary Location | Cross-references Allowed |
|---------|------------------|--------------------------|
| Installation | [user-guide.md#installation](../../docs/user-guide.md#installation) | [README.md](../../README.md) (summary only), [index.rst](../../docs/index.rst) (link only) |
| User stories & use cases | [user-guide.md#who-should-use-this](../../docs/user-guide.md#who-should-use-this) | [README.md](../../README.md) (4-line summary) |
| Basic usage examples | [user-guide.md#getting-started](../../docs/user-guide.md#getting-started) | [README.md](../../README.md) (1 minimal example) |
| Configuration examples | [configuration.md](../../docs/configuration.md) | [user-guide.md](../../docs/user-guide.md) (context-specific tutorials) |
| Data schemas | [user-guide.md#understanding-output](../../docs/user-guide.md#understanding-output) | None - link only from other files |
| API patterns | [user-guide.md#tutorials](../../docs/user-guide.md#tutorials) | [README.md](../../README.md) (quick reference only) |
| Architecture & design | [design.md](../../docs/design.md) | None - technical reference only |
| Impact functions | [configuration.md](../../docs/configuration.md) | [user-guide.md](../../docs/user-guide.md) (usage examples only) |
| Product details | [configuration.md](../../docs/configuration.md) | [user-guide.md](../../docs/user-guide.md) (Tutorial 6) |

## Update Workflow

When updating documentation, follow these steps:

### 1. Identify Content Owner

Check the matrix above to find where content should be updated.

### 2. Update Primary Location

Make your changes in the primary location first.

### 3. Verify Against Actual Code

**CRITICAL**: Before finalizing documentation changes, verify all examples match the actual codebase:

**For API Documentation**:
- Check API signatures in `online_retail_simulator/__init__.py` for public API
- Verify function parameters match actual implementation
- Test code examples actually run without errors
- Verify data schemas match actual DataFrame outputs

**For Configuration Documentation** (configuration.md):
- **Primary source**: `online_retail_simulator/config_defaults.yaml` - all default values
- **Validation logic**: `online_retail_simulator/config_processor.py` - structure and validation
- Verify all parameter names match defaults file exactly
- Verify default values match defaults file exactly
- Check that CHARACTERISTICS/METRICS structure is correct
- Verify function names (e.g., `simulate_characteristics_rule_based`)
- Test configuration examples with actual config processor

**Common verification points**:
- `simulate()` returns `JobInfo`, not `DataFrame`
- `enrich()` takes `(config_path, job_info)` not `(config, dataframe)`
- Use `load_job_results(job_info)` to get DataFrames
- Config uses `STORAGE.PATH` not `OUTPUT.DIR`
- Rule config has nested `CHARACTERISTICS` and `METRICS` sections
- Parameter names are case-sensitive (e.g., `sale_prob` not `SALE_PROB`)

### 4. Update Cross-References

If content is cross-referenced elsewhere:
- Use links, not duplication
- Keep summaries brief (1-4 lines maximum)
- Always point to the primary location for details

### 5. Verify Changes

Before committing documentation updates:
- Build Sphinx docs locally (from docs/): `cd docs && hatch run make html`
- Check for broken links (manually review)
- Verify all code examples work
- Review against this workflow

## Prohibited Patterns

To prevent documentation drift, **DO NOT**:

❌ Duplicate code examples across files
- **Wrong**: Copy/paste same example to multiple files
- **Right**: Put complete example in user-guide.md, link from others

❌ Duplicate configuration blocks
- **Wrong**: Same YAML config in README.md and examples.md
- **Right**: Full configs in configuration.md, tutorials in user-guide.md

❌ Duplicate schema tables
- **Wrong**: Same data schema table in multiple files
- **Right**: Schema in user-guide.md#understanding-output, link from elsewhere

❌ Duplicate user stories
- **Wrong**: Full user story in README.md and use_cases.md
- **Right**: Full story in user-guide.md, brief summary in README.md

## Best Practices

✅ **DO** use these patterns:

### Link Instead of Duplicate

```markdown
<!-- Good: In README.md -->
For complete configuration options, see the [Configuration Reference](https://eisenhauerio.github.io/tools-catalog-generator/configuration.html).

<!-- Bad: In README.md -->
Here's all the configuration options... [300 lines of duplication]
```

### Summary + Link Pattern

```markdown
<!-- Good: In README.md -->
- **Data Scientists**: Generate realistic e-commerce data for ML model training

[See complete user stories →](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html#who-should-use-this)

<!-- Bad: In README.md -->
[Full detailed user story with code examples duplicated from user-guide.md]
```

### One Example, Link for More

```markdown
<!-- Good: In README.md -->
```python
from online_retail_simulator import simulate, load_job_results
job_info = simulate("config.yaml")
sales_df = load_job_results(job_info)["sales"]
```

For more examples, see the [User Guide](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html).

<!-- Bad: In README.md -->
[10 different code examples all duplicated from user-guide.md]
```

## Review Checklist

Before committing documentation changes, verify:

### Content Review
- [ ] No duplicate code examples across files
- [ ] No duplicate configuration blocks
- [ ] No duplicate schema definitions
- [ ] Cross-references use links, not duplication
- [ ] New content follows the Content Ownership Matrix

### Technical Review
- [ ] **Code verified against actual implementation** (see Step 3 above)
- [ ] API signatures match `online_retail_simulator/__init__.py`
- [ ] Function parameters match actual implementations
- [ ] Configuration keys match actual config processor
- [ ] All code examples are tested and work
- [ ] Configuration examples match actual schema
- [ ] Data schemas match actual DataFrame outputs
- [ ] Version numbers are current (if applicable)

### Link Validation
- [ ] All internal links resolve correctly
- [ ] All external links are valid
- [ ] Links point to canonical sources (per matrix)
- [ ] No broken links in local rendering
- [ ] No broken links in GitHub Pages

### Build Validation
- [ ] `cd docs && hatch run make html` succeeds with no warnings
- [ ] Generated HTML renders correctly
- [ ] Navigation works in built docs

### User Experience
- [ ] Information is easy to find
- [ ] Examples progress from simple to complex
- [ ] Cross-references help rather than confuse
- [ ] No dead-end pages (all pages link somewhere)

## When to Update This Workflow

Update this workflow when:
- Adding new documentation files
- Changing documentation structure
- Adding new content types
- Modifying the single source of truth for any content

## Integration with Project Integrity

This workflow integrates with [confirm-project-integrity.md](confirm-project-integrity.md). Documentation integrity checks are part of the standard project validation workflow.
