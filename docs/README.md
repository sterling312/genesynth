# Genesynth

A powerful library for generating synthetic data with complex relationships and constraints. Genesynth leverages high-performance Python packages like NumPy and SciPy for efficient data generation at the field level, while using a graph-based approach to handle dependencies and relationships between fields.

## Overview

Genesynth provides:
- Rich set of data types matching common database types
- Support for complex relationships and constraints
- Integration with LLMs for text generation
- Efficient handling of large datasets
- Flexible output formats (CSV, JSON, etc.)

## Configuration

The main interface is a YAML configuration file following a JSON Schema-like format. Here's the basic structure:

```yaml
version: 2
type: "top level datatype (json|table|object)"
description: "description of the dataset"
metadata:
    size: 1000  # number of records to generate
    sep: ","    # separator for CSV output
properties:
    table_name:
        type: "table|object|json" 
        metadata:
            namespace: "optional db namespace"
            size: 500  # override top-level size
        constraints: []  # table-level constraints
        properties:
            column_name:
                type: "data type"
                metadata: {}  # type-specific config
                constraints: []  # column constraints
```

## Data Types

### Core Types

#### Numeric Types

- **integer**
  ```yaml
  type: integer
  metadata:
    min: 0
    max: 100
    dist:  # optional statistical distribution
      normal:
        loc: 50
        scale: 10
  ```

- **serial**
  ```yaml
  type: serial
  metadata:
    min: 1  # starting value
    step: 1 # increment
  ```

- **float/double**
  ```yaml
  type: float
  metadata:
    min: -1.0
    max: 1.0
    dist:
      uniform: {}
  ```

- **decimal/numeric**
  ```yaml
  type: decimal
  metadata:
    precision: 16
    scale: 3
    min: 0
    max: 1000
  ```

#### Text Types

- **text**
  ```yaml
  type: text
  metadata:
    length: 100  # optional max length
  ```

- **string** (Mimesis-powered)
  ```yaml
  type: string
  metadata:
    subtype: person  # Mimesis provider
    field: full_name # provider field
  ```

- **password** (bcrypt format)
  ```yaml
  type: password
  metadata:
    rounds: 12
    prefix: "2b"
  ```

- **enum**
  ```yaml
  type: enum
  metadata:
    options: ["A", "B", "C"]
    replace: true  # allow duplicates
  ```

#### Temporal Types

- **timestamp/datetime**
  ```yaml
  type: timestamp
  metadata:
    min: "2024-01-01T00:00:00"
    max: "2024-12-31T23:59:59"
  ```

- **date**
  ```yaml
  type: date
  metadata:
    min: "2024-01-01"
    max: "2024-12-31"
  ```

- **time**
  ```yaml
  type: time
  metadata:
    min: "00:00:00"
    max: "23:59:59"
  ```

### Structure Types

- **array/list/tuple**
  ```yaml
  type: array
  properties:
    - type: integer
      metadata: {}
  ```

- **map/struct**
  ```yaml
  type: map
  properties:
    key1:
      type: string
    key2:
      type: integer
  ```

- **foreign** (references)
  ```yaml
  type: foreign
  metadata:
    foreign:
      name: "table1.id"  # references table1.id field
  ```

### Container Types

- **table/object**
  ```yaml
  type: table
  metadata:
    sep: ","
    header: true
  properties:
    id:
      type: serial
    name:
      type: string
  ```

- **json**
  ```yaml
  type: json
  metadata:
    full_key: false  # use short keys
  properties:
    user:
      type: map
      properties:
        id: 
          type: serial
  ```

### LLM Integration

#### OpenAI Integration
```yaml
type: openai
metadata:
  prompt: "Generate a product description"
  model: "gpt-4"  # optional
  env_var: "OPENAI_API_KEY"  # optional
```

#### Ollama Integration
```yaml
type: ollama
metadata:
  prompt: "Write a short story"
  model: "llama2:7b"  # optional
```

#### Google AI Integration
```yaml
type: google
metadata:
  prompt: "Generate a news headline"
  model: "gemini-1.5-flash-001"  # optional
```

## Constraints

Constraints can be applied at both table and column levels:

- **notnull**: Ensures no null values
- **unique**: Ensures unique values
- **nullable**: Allows null values with specified percentage
- **sorted**: Sorts the generated values

Example:
```yaml
constraints:
  - notnull
  - unique
  - nullable: 0.1  # 10% null values
```

## Example Configuration

Here's a complete example:

```yaml
type: json
metadata:
  size: 1000
properties:
  users:
    type: table
    metadata:
      sep: ","
    properties:
      id:
        type: serial
        constraints:
          - unique
          - notnull
      name:
        type: string
        metadata:
          subtype: person
          field: full_name
      bio:
        type: openai
        metadata:
          prompt: "Write a short bio"
          model: "gpt-4"
    constraints:
      - notnull
```

## Advanced Features

### Statistical Distributions

Support for various statistical distributions via SciPy:

```yaml
type: float
metadata:
  dist:
    normal:
      loc: 0
      scale: 1
    # or
    uniform:
      low: 0
      high: 1
    # or
    beta:
      a: 2
      b: 5
```

### Caching

Generated data can be cached for reuse:

```yaml
metadata:
  cache: true
  cache_dir: "./cache"
```

### Output Formats

Supports multiple output formats:
- CSV (with custom separators)
- JSON (nested structures)
- JSON Lines
- Compressed formats (gzip)

## Best Practices

1. Start with small sizes during development
2. Use appropriate constraints to ensure data quality
3. Consider using statistical distributions for realistic data
4. Leverage LLM integration for complex text generation
5. Use caching for large datasets
6. Structure your configuration files logically

## Contributing

Contributions are welcome! Please check our contribution guidelines and feel free to submit pull requests.
