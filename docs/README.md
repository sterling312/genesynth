# genesynth
This library is used to synthetically generate structured data based on configuration to be used for testing as well as structured data training purposes. The approach of the library is to leverage as much as C-level python packages such as numpy and scipy to generate data at field level, one type at a time, and use graph approach to piece together the complex dependency as well as de-normalization/sampling from each fields to construct data in a scalable manner fast.

For most of the text generation, genesynth currently leverage Mimesis to handle text generation. Eventually the library will include extensions that support text generation from LLM so that can be plugged into the model for more custom dataset.


## configuration`
Currently the main interface to the library is a YAML file that largely follow JSON Schema format, with a few minor differences. The intent is to eventually support to full JSON Schema spec, as well as other input format, which is configurable. 

The main structure supported today follows the schema below:
```
version: 2
type: "supoorted top level datatype for the data being generated"
description: "brief description of the generated data"
metadata:
    size: "integer value of number of records to generate"
    sep: "separator for tabular data output format"
properties:
    table_name/object_name:
        type: "table|object|json"
        metadata: 
            namespace: "optional namespace used to define database table namespace"
            size: "optinal but overwrites the top level size"
            {keys}: "other datatype specific metadata"
        constraints: [constraints added at the table/object level]
        properties:
            column_name/field_name:
                type: "column/field level type"
                metadata: {other datatype specific metadata}
                constraints: [column/field level constraints]
                properties: {repeat properties if there are JSON or nested types}
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
```

#### decimal/numeric
generate decimal values
```
    precision: int - precision of the decimal
    scale: int - rounding scale of the decimal
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

#### json_array
same as json type, but returns the data as an array of data; this may be deprecated in the future
```
    metadata: dict - default metadata configuration
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
