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
The component's input parameters are:

{% for input in inputs -%}
  - {{input.name}} [{{input.type}}]: (Default: {{input.value}}) {{input.description}}
{% endfor -%}
{%- else -%}
This component does not have any input parameter.
{%- endif %}

### Custom Types

{% if custom_types is not none -%}
The custom types defined by the component are:

{% for item in custom_types -%}
  - {{item.name}}
     {% for p in item.fields -%}
      - {{p.name}} [{{p.type}}]: (Default: {{p.value}}) {{p.description}}
     {% endfor %}
{% endfor -%}
{%- else -%}
This component does not have any custom type.
{%- endif -%}

### Output

{% if output is not none -%}
The component's output are:

{% for out in output -%}
  - {{out.name}}:
    {% for field in out.fields -%}
      - {{field.name}} [{{field.type}}]
    {% endfor %}
{% endfor %}
{%- else -%}
This component does not have any output.
{%- endif -%}

### Bindings

{% if bindings -%}
{% for val in bindings -%}
  {{loop.index}}. {{val.name}}: The binding **{{val.name}}** is executed when the action **{{val.object_action}}** is applied on a **{{val.object_type}}**.
{% endfor %}
{%- else -%}
This component does not have any binding.
{%- endif %}

### Commands

{% if commands -%}
The component commands are the following:

{% for val in commands -%}
  {{loop.index}}. {{val.name}}: 
    {% for field in val.fields -%}
      {{field.name}} [{{field.type}}]
    {% endfor %}
{% endfor %}
{%- else -%}
This component does not have any command.
{%- endif -%}

### Endpoints

{% if endpoints -%}
The component's endpoints are:

{% for val in endpoints -%}
  {{loop.index}}. Endpoint **{{val.name}}** on port {{val.port}}.
{% endfor %}
{%- else -%}
This component does not have any endpoint
{%- endif -%}
