# genesynth
This library is used to synthetically generate structured data based on configuration to be used for testing as well as structured data training purposes. The approach of the library is to leverage as much as C-level python packages such as numpy and scipy to generate data at field level, one type at a time, and use graph approach to piece together the complex dependency as well as de-normalization/sampling from each fields to construct data in a scalable manner fast.

For most of the text generation, genesynth currently leverage Mimesis to handle text generation. Eventually the library will include extensions that support text generation from LLM so that can be plugged into the model for more custom dataset.


## Configuration

The main interface to the library is a YAML configuration file that follows a JSON Schema-like format. The configuration defines the structure and characteristics of the data to be generated.

### Basic Structure

```yaml
version: 2
type: "json|table|object"  # Top-level output format
description: "Description of the dataset"
metadata:
    size: 1000  # Number of records to generate
    sep: ","    # Separator for tabular data (optional)
properties:
    table_name:  # Name of the table/object
        type: "json|table|object"
        metadata:
            namespace: "schema_name"  # Database schema namespace (optional)
            size: 500  # Override global size for this table
            sep: "|"   # Override separator for this table
            weight: 10 # Sampling weight for relationships
        constraints:
            - "notnull"  # Table-level constraints
            - "unique: [column1, column2]"  # Composite constraints
        properties:
            column1:
                type: "integer|string|timestamp|etc"
                metadata:
                    min: 0        # Numeric range
                    max: 100
                    length: 50    # String length
                    precision: 2  # Decimal precision
                    scale: 1      # Decimal scale
                    dist:         # Statistical distribution
                        normal:
                            loc: 0
                            scale: 1
                    foreign:      # Foreign key reference
                        name: "other_table.id"
                constraints:
                    - "unique"    # Column constraints
                    - "incremental"
                    - "nullable: 0.1"  # 10% null values
```

### Supported Types

#### Basic Types
- `integer`: Whole numbers
- `serial`: Auto-incrementing integers
- `float/double`: Floating point numbers
- `decimal/numeric`: Fixed-precision decimals
- `boolean`: True/False values
- `string`: Text data with optional Mimesis providers
- `text`: Random string data
- `timestamp/datetime`: Date and time values
- `date`: Date only
- `time`: Time only
- `password`: Bcrypt password hashes
- `enum`: Selection from predefined options

#### Structural Types
- `array/list/tuple`: Ordered collections
- `map/struct`: Key-value structures
- `foreign`: References to other fields

#### Container Types
- `object/table`: 2D tabular data
- `json`: Nested data structures
- `[json]`: Array of JSON objects

#### LLM Types
- `llama/gemma`: Local Ollama models
- `chatgpt`: OpenAI GPT models
- `google`: Google AI models

### Constraints

- `unique`: Ensures unique values
- `notnull`: No null values allowed
- `nullable: float`: Percentage of null values
- `incremental`: Auto-incrementing values
- `sorted`: Sort values
- Composite constraints using arrays

### Statistical Distributions

Support for various statistical distributions via scipy.stats:
```yaml
metadata:
    dist:
        normal:
            loc: 0
            scale: 1
        # Other supported distributions:
        # uniform, beta, gamma, exponential, etc.
```

### Example Configurations

Here are some focused examples demonstrating specific use cases:

#### Basic Types Example
```yaml
type: json
metadata:
    size: 5  # Generate 5 records
properties:
    basic_types:
        type: table
        properties:
            id:
                type: serial
                metadata:
                    start: 1
            number:
                type: integer
                metadata:
                    min: 0
                    max: 100
            text:
                type: string
                metadata:
                    subtype: text
                    field: word
```

#### Statistical Distribution Example
```yaml
type: json
metadata:
    size: 1000
properties:
    normal_distribution:
        type: table
        properties:
            value:
                type: float
                metadata:
                    dist:
                        normal:
                            loc: 50    # mean
                            scale: 10  # standard deviation
```

#### Foreign Key Relationship Example
```yaml
type: json
metadata:
    size: 10
properties:
    parents:
        type: table
        properties:
            parent_id:
                type: serial
                constraints:
                    - unique
    children:
        type: table
        metadata:
            size: 20  # More children than parents
        properties:
            child_id:
                type: serial
            parent_id:
                type: integer
                metadata:
                    foreign:
                        name: parents.parent_id
```

#### Text Generation Example
```yaml
type: json
metadata:
    size: 3
properties:
    people:
        type: table
        properties:
            name:
                type: string
                metadata:
                    subtype: person
                    field: full_name
            email:
                type: string
                metadata:
                    subtype: person
                    field: email
```

#### LLM Integration Example
```yaml
type: json
metadata:
    size: 2
properties:
    content:
        type: table
        properties:
            title:
                type: ollama
                metadata:
                    prompt: "Generate a blog post title about AI"
                    model: "gemma:2b"
```
Use tests/test.yaml as an example.

## datatype definitions
There are a few datatypes that are supported. Here are the configuration parameters for each types that will go into metadata attributes at each level of the configuraiton yaml.

### core types
The following list are basic datatypes and should corresponds well to typical database datatypes.

#### text
text will generate random strings from Mimesis.
```
    length (optional): int/float - determine the length of the text to be generated
        defaults to None, which has no specific text length
```

#### timestamp/datetime
generate datetime
```
    min (optional): datetime - determine the starting point of the timestamp series
        defaults to POSIX 0 timestamp
    max (optional): datetime - determines the upper bound of timestamp
        defaults to current timestamp in local time
```

#### date
generate date cast from datetime object
```
    min (optional): datetime - determine the starting point of the timestamp series
        defaults to POSIX 0 timestamp
    max (optional): datetime - determines the upper bound of timestamp
        defaults to current timestamp in local time
```

#### time
generate python datetime's time objects
```
    min (optional): time - determine the starting point of time
        defaults to 0
    max (optional): time - determine the ending point of time
        defaults to 23:59:59
```

#### integer
generate integer data
```
    min: int - min value
    max: int - max value
    dist (optional): dict(str: dict(str, str)) - parameter for underlying statistical distribution
```

#### serial
generate incremental integers
```
    min (optinal): int - starting value
        default to 0
    step (optional): int - increment added from starting value
        default to 1
```

#### boolean
generate boolean values
```
```

#### float/double
generate python float
```
    min: int - minimum value
    max: int - maximum value
    dist (optional): dict(str: dict(str, str)) - parameter for underlying statistical distribution
```

#### decimal/numeric
generate decimal values
```
    precision: int - precision of the decimal
    scale: int - rounding scale of the decimal
    dist (optional): dict(str: dict(str, str)) - parameter for underlying statistical distribution
```

#### string
generate text data from Mimesis, which should refer the [Mimesis provider documentation](https://mimesis.name/en/master/providers.html#generic-provider) for detailed documentation
```
    subtype (optional): str - Mimesis provider selection
        defaults to text
    field (optional): str - Mimesis provider field
        defaults to sentence
```
Note that field must be supported by the provider configured in subtype.

#### password
generate fake bcrypt password hash
```
    rounds (optional): int - bcrypt rounding value
        default to 12
    prefix (optional): str - bcrypt prefix
        default to 2b
```

#### enum
generate random selection from enum array
```
    options: tuple - list of default values
    replace: bool - determine if the sample allows duplication
        default to True
```

### structure datatypes
The following list are types that either holds core datatypes or references them and generate expected structures based on the datatype.

#### array/list/tuple
generate repeated/array of data
```
    children: tuple(node) - wrapper around nodes that gets unpacked into an array
```

#### map/struct
generate nested structured data
```
    children: dict(node: node) - wrapper around nodes that gets reduced into key value format
```

#### foreign
reference or point to data generated in another field and replicate it
```
    foreign:
        name: str - full name (using OOP class reference ie table.column) of the referenced field
```

### container datatypes
The following list are container types that is used at the top level, or create nested structure for the generated data.

#### object/table
generate 2D tablular data
```
    metadata: dict - default metadata configuration
```

#### json
generate JSON like nested data structure
```
    metadata: dict - default metadata configuration
```

#### [json]
same as json type, but returns the data as an array of data; this may be deprecated in the future
```
    metadata: dict - default metadata configuration
```

#### llama/gemma
call local ollama server for prompt
```
    prompt: str - prompt used to generate text
    model (optional): str - default to llama2:7b/gemma:2b
```

#### chatgpt
call OpenAI's ChatGPT chat completion api with prompt
```
    prompt: str - prompt used to generate text
    model (optional): str - default to gpt-3.5-turbo
    env_var (optional): str - OpenAI api key environment variable name, default to OPENAI_API_KEY
    temperature (optional): float - default to 0.8
```

### more on mimesis provider
Here're the subset of Mimesis provider subtype and field that may be useful:
```
    subtype:
        - field

    person:
        - name
        - first_name
        - last_name
        - full_name
        - ssn
        - age
        - gender
        - email
        - username
        - password
        - telephone
        - occupation
        - natinality
    address:
        - address
        - city
        - country
        - state
        - street_name
        - postal_code
        - zip_code
    internet:
        - content_type
        - emoji
        - hashtags
        - hostname
        - http_status_code
        - ip_v4
        - uri
        - url
        - stock_image
    text:
        - alphabet
        - answer
        - quote
        - color
        - sentence
        - text
        - word
        - words
        - swear_word
    food:
        - dish
        - drink
        - fruit
        - vegetable
    file:
        - file_name
        - mime_type
    cryptographic:
        - uuid
        - token_hex
        - mnemonic_phrase
        - hash
    finance:
        - company
        - price
        - stock_name
        - stock_exchange
        - stock_ticket
    payment:
        - credit_card_network
        - credit_card_expiration_date
        - credit_card_number
        - paypal
        - cvv
        - credit_card_owner
    code:
        - ean
        - isbn
        - pin
        - issn
    transport:
        - car
        - airplane
        - manufacturer
        - truck
```
