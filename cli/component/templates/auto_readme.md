# {{component_name}} {{component_type}}

## Version: {{version}}

## Table of Contents  
1. [Description](#description)
2. [Input](#Input)
3. [Output](#Output)
4. [Bindings](#Bindings)

### Description

{% if description is not none %}{{description}}{% else %}COMPLETE COMPONENT DESCRIPTION{% endif %}

### Input

{% if inputs is not none -%}
{% for input in inputs -%}
  - {{input.name}} [{{input.type}}]: (Default: {{input.value}}) {{input.description}}
{% endfor -%}
{%- else -%}
This component does not have any input parameter
{%- endif %}

### Custom Types

{% if custom_types is not none -%}
{% for item in custom_types -%}
  - {{item.name}}
     {% for p in item.fields -%}
       {{p.name}} [{{p.type}}]: (Default: {{p.value}}) {{p.description}}
     {% endfor %}
{% endfor -%}
{%- else -%}
This component does not have any custom type
{%- endif -%}

### Output

{% if output is not none -%}
{% for out in output -%}
  - {{out.name}}: {{out.type}} value 
{% endfor %}
{%- else -%}
This component does not have any output
{%- endif %}

### Bindings

{% if bindings -%}
{% for val in bindings -%}
  {{loop.index}}. {{val.name}}: {{val.object_type}} value 
{% endfor %}
{%- else -%}
This component does not have any binding
{%- endif -%}
