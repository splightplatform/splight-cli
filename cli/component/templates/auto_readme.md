# {{component_name}} {{component_type}}

## Version: {{version}}

## Table of Contents  
1. [Description](#description)  
2. [Input](#Input)  
3. [Output](#Output)  
4. [Bindings](#Bindings)  
5. [Example](#Example)

### Description

What does the component do?

### Input

{% for input in inputs %}
  - {{input.name}}: {{input.type}} value 
{% endfor %}

### Output

{% for out in output %}
  - {{out.name}}: {{out.type}} value 
{% endfor %}

### Bindings

{% for val in bindings %}
  {{loop.index}}. {{val.name}}: {{val.object_type}} value 
{% endfor %}

### Example

Provide a sample case for {{component_name}}