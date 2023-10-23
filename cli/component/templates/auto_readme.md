# {{component_name}} {{component_type | capitalize}} - {{version}}

- [Description](#description)
- [Inputs](#inputs)
- [Routines](#routines)
{%- if routines != []-%}
{%- for routine in routines %}
  - [{{routine.name}}](#{{routine.name | lower}})
{%- endfor %}
{%- endif %}
- [Custom Types](#custom-types)
{%- if custom_types != []-%}
{%- for type in custom_types %}
  - [{{type.name}}](#{{type.name | lower}})
{%- endfor %}
{%- endif %}

### Description

{{description | default("COMPLETE COMPONENT DESCRIPTION", true)}}

### Inputs

{% if inputs != [] -%}
The component inputs are:

| name | type | default | required | description |
|------|------|---------|----------|-------------|
{% for input in inputs -%}
| {{input.name}} | {{input.type}} | {{input.value | default("-", true)}} | {{input.required | default("True")}} | {{input.description | default("-", true)}} |
{% endfor -%}
{%- else -%}
This component does not have any inputs.
{%- endif %}

### Routines

{% if routines != [] -%}
The component routines are:
{% for routine in routines %}
  - #### {{routine.name}}

    | section | name | type | default | required | description |
    |---------|------|------|---------|----------|-------------|
    {% for field in routine.config -%}
    | config | {{field.name}} | {{field.type}} | {{field.value | default("-", true)}} | {{field.required | default("True")}} | {{field.description | default("-", true)}} |
    {% endfor -%}
    {% for field in routine.input -%}
    | input | {{field.name}} | {{field.value_type}} | {{field.value | default("-", true)}} | {{field.required | default("True", true)}} | {{field.description | default("-", true)}} |
    {% endfor -%}
    {% for field in routine.output -%}
    | output | {{field.name}} | {{field.value_type}} | {{field.value | default("-", true)}} | {{field.required | default("True", true)}} | {{field.description | default("-", true)}} |
    {% endfor -%}
{% endfor -%}
{%- else -%}
This component does not have any routines.
{%- endif %}

### Custom Types

{% if custom_types != [] -%}
The component custom types are:
{% for type in custom_types %}
  - #### {{type.name}}

    | name | type | default | required | description |
    |------|------|---------|----------|-------------|
    {% for field in type.fields -%}
    | {{field.name}} | {{field.type}} | {{field.value | default("-", true)}} | {{field.required | default("True")}} | {{field.description | default("-", true)}} |
    {% endfor -%}

{% endfor -%}
{%- else -%}
This component does not have any custom types.
{%- endif %}


