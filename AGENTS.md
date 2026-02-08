# Streamlit in Snowflake Demo Repo Overview

This repository contains a collection of Streamlit in Snowflake demos and tutorials. Each directory is an independent app with its own code, setup scripts, and sample data. 

## Repository Structure

- Each demo/app is in its own directory
- Main application file: `streamlit_app.py`
- Each app includes:
  - `README.md` - Setup instructions and description
  - `environment.yml` - Snowflake environment dependencies
  - `snowflake.yml` - Deployment configuration
  - `assets/` - Screenshots and static files
  - `data/` - Sample data and SQL creation scripts (when applicable)

## Technology Stack

- **Primary**: Python, Streamlit, Snowflake
- **Common Libraries**: pandas, plotly, altair, snowflake-snowpark-python
- **Visualization**: Plotly, Altair
- **Data**: CSV files, SQL scripts, Snowflake tables
- **Snowflake Deployment**: snowflake-cli

## Coding Conventions


### Snowflake Integration

Snowflake Sessions setup
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
```

or 

```python
session = st.connection('snowflake').session()
```

- Use parameterized queries or Snowpark DataFrame API to prevent SQL injection
- **Never use f-string interpolation for SQL queries with user input**
- Cache the results of queries using `st.cache_data`

### Environment Configuration (environment.yml)
- Use `snowflake` channel only (not `conda-forge`)
- Use Python 3.11
- Do not pin the `streamlit` library version

Example:
```yaml
name: app_environment
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
```

### Container Runtime Configuration (snowflake.yml)

Note: This is the preferred runtime

```yaml
definition_version: 2
entities:
  app_name:
    type: streamlit
    identifier:
      name: app_name
      database: DATABASE_NAME
      schema: SCHEMA_NAME
    query_warehouse: COMPUTE_WH
    compute_pool: SIS_COMPUTE_POOL
    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11
    external_access_integrations:
      - PYPI_ACCESS_INTEGRATION
    main_file: streamlit_app.py
    artifacts:
      - streamlit_app.py
      - pyproject.toml
```

### pyproject.toml (for container runtime)
```toml
[project]
name = "app-name"
requires-python = ">= 3.11"
version = "0.0.1"
description = "App description"
dependencies = [
    "streamlit[snowflake]",
    "pandas"
]
```

## Deployment

Deploy apps using Snowflake CLI:
```bash
cd "App Directory"
snow streamlit deploy --open
```

## Security Best Practices

- Never hardcode credentials
- Use Snowpark DataFrame API for database writes (prevents SQL injection)
- Use parameterized queries when raw SQL is necessary
- Validate user input at system boundaries

## When Making Changes

1. Maintain consistency with existing patterns
2. Update README files when adding new features
3. Include appropriate error handling
4. Test with sample data when possible
5. Follow established directory structure
6. Ensure all new dependencies are added to environment.yml
7. Use semantic commit messages
