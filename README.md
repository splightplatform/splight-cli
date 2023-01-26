# Splight CLI

## Table of Content

- [Splight CLI](#splight-cli)
  - [Table of Content](#table-of-content)
  - [Introduction](#introduction)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Configuration](#configuration)
      - [Create Developer Credentials](#create-developer-credentials)
      - [Configure Splight CLI](#configure-splight-cli)
  - [Commands](#commands)
    - [Component](#component)
    - [Configure](#configure)
    - [Hub](#hub)
      - [Component](#component-1)
    - [Engine](#engine)
    - [Workspace](#workspace)
  - [Developing Components](#developing-components)
    - [What is a component?](#what-is-a-component)
    - [Creating a Component](#creating-a-component)
      - [Component Core](#component-core)
      - [Component Initialization](#component-initialization)
      - [Component Configuration](#component-configuration)
      - [Running Locally](#running-locally)

## Introduction

The Splight Command Line Interface is a unified tool to interact with _Splight
Platform_. It contains different features that a user can use for creating, deloping, and
publishing components.

## Getting Started

### Installation

_SplightCLI_ is a Python package that can be installed using `pip`

```bash
pip install splight-cli
```

Once you have installed `splight-cli` you can check the installation with 
```bash
splight --version
```

You should see something like

```bash
$ splight

Usage: splight [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
...
```

### Configuration

Before using the _Splight CLI_, you need to configure it. In order to do it you need
to create your _User credentials_ from the platform and then you will be able to
configure _Splight CLI_.

#### Create Developer Credentials

Go to the [Splight Platform](https://app.splight-ae.com), and in your _User Configuration > Account_, in the right side pannel you will find the section _Developers_ and the subsection _Credentials_. Under the _Credentials_ subsection select “**New access key”.** This will generate a Client Access ID and Secret Key which are
the credentials you will use for configuring _Splight CLI_. These credentials should
not be share with other users.

Also, you need to keep in mind that the Secret Key is only shown once, if you loose the
Key you will need to create a new set of Access Credentials.

#### Configure Splight CLI

The fastest and easiest way for configuring _Splight CLI_ is running on your terminal
the following command

```bash
splight configure
```

After entering the above command will ask you for the credentials you have created before.

## Commands

This section introduce you to many of the common features and options provided by
_Splight CLI_.

The tool contains a set of commands that can be used for different purposes.
In the following subsections, we will go through each of the commands that can be
used.

The basic usage is

```bash
splight <command> [--help]
```

where `<command>` is the command you want to use, and optionally you can add the flag
`--help` to each one of the commands to get more information about the given command.

### Component

This is probably the most important command and the one you will use most. The command `component` allow you to operate over components, this mean you can create components, test locally components, push private or public components to _Splight Hub_, download
existing component in _Splight Hub_ and delete them.

In the following section we will cover in details the development process of a
component, here we will only cover the different sub-commands you can use

- Create a new component

  To create a new component the command is

  ```bash
  splight component create <name> <version>
  ```

  The parameters `<name>` and
  `<version>` are the name and version of the component to be created.
  The three commands parameters `<name>` and `<version>` are
  commong between all the sub-commands.

  The command creates a new folder with the name `<name>-<version>` in the same
  directory where the command was executed. Inside the new folder, you will find some
  files that defines the basic structure of the component source code.

- Install component requirements

  The command

  ```bash
  splight component install-requirements <path>
  ```

  Where the parameter `<path>` is the path to the component that will be installed
  locally.

  This command is useful for running locally a component for testing and development.

- Run locally a component

  You can run locally a component, this is quite usefull for testing a comoponent
  before push it and for development a new component. The command is the following

  ```bash
  splight component run <path> [-r] [-rs]
  ```

  This command will run a component locally. Optionally you can use the flag
  `-r/--reset-input`, so you will be asked to configure some parameters for the
  component. If it is the first time you run a component, you will see some messages in
  the terminal for input some parameters values that are needed for running correctly
  the component. Also, you can use the flag `-rs/--run-spec` for using a custom
  configuration different to the one defined in the `spec.json` file. In the following
  section we will dive in in the usage of the file `spec.json`.

### Configure

This command is used for configuring Splight CLI and can be used as many times as you
want.

The command is

```bash
splight configure
```

And it will prompt you to enter some pieces of information that needed by Splight CLI.
This command is quite useful when is used along with `workspace` command.

You can also retrieve one of the parameters using the `get` command:

```bash
splight configure get <parameter>
```
for example for reading the `SPLIGHT_PLATFORM_API_HOST`:
```bash
splight configure get splight_platform_api_host
```

In the same way you can modify one parameter using the `set` command
```bash
splight configure set <parameter> <value>
```

### Hub

This command allows you to interact with the Splight HUB, places where you can find all the 
existing components that can be used in the platform. 

#### Component

- List component

  You can list all the components with the command

  ```bash
  splight component list
  ```

- Pull or download a component

  For downloading an existing component in _Splight Hub_ you can use

  ```bash
  splight component pull <name> <version>
  ```

  This will download the component source code to your machine.

- Push a component

  For pushing a new component or component version to _Splight Hub_ the command is

  ```bash
  splight component push <path>
  ```

  Where `<path>` is the path (relative or absolute) for the source code of the
  component to be uploded.

- List component versions

  You can also list all the version of given component with

  ```bash
  splight component versions <name>
  ```

### Engine

The `engine` command is used for interacting with the Splight Engine. So far, the available 
subcommands provide an interface for creating, reaading and deleting resources in the engine.

The command is
```bash
splight engine <subcommand> <action> [extra args]
```

depending on the which sub-command you use you can get different actions 
to perform

The valid sub-commands so far are:
- `asset`
- `attribute`
- `component`
- `datalake`
- `file`
- `graph`
- `query`
- `secret`

### Workspace

This command allows you to manage different workspaces in the same computer. This can
be useful for managing different environments of different users that share the same
computer.

The command is

```bash
splight workspace <sub-command>
```

The available subcommands are

- `create` for creating new workspace. After the creation of a new worskpace you need to configure _Splight CLI_ with `splightcli configure`.
- `delete` for deleting an existing workspace.
- `list` for listing the differents configured workspaces and showing the workspace in use.
- `select` for switching between the different configured workspaces.

## Developing Components

Now it's time to talk about the process for developing components.

### What is a component?

A component is a package of code that can be executed in the Splight platform. Splight
Hub is the space that manages all components that exist in Splight. You can upload your
own coded component for your usability or even allow other people in Splight to use it!

The expected flow for your component is the following:

- You create your component and code it locally
- Upload it to Splight Hub
- Use your component in Splight, where all your data is available

### Creating a Component

To create a component with the Splight Hub CLI, open a terminal and change the directory to the one where you want to work.

Execute the following command:

```bash
splight component create <name> <version>
```

This will create a directory with the following structure:

```
<name>-<version>
│   __init__.py
│   Initialization
│   spec.json
│   README
```

- `__init__.py` : The component is coded here.
- `Initialization` : Execute instructions for the component to be initialized.
- `spec.json` : JSON file where the component metadata is set.
- `README` : Text that describes the component and how it works

#### Component Core

When creating a component, inside `__init__.py` you will find a component template already written in python for you, in order to make it easier to write the component code.

For example, when you create an algorithm component, in `__init__.py` will have the following:

```python
import random

from splight_lib import logging
from splight_lib.component.abstract import AbstractComponent
from splight_lib.execution import Task

from splight_models import Variable


logger = logging.getLogger()


class Main(AbstractComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("It worked!")

    def start(self):
        # To start a periodic function uncomment this
        self.execution_client.start(
            Task(
                handler=self._my_periodic_function,
                args=tuple(),
                period=self.period
            )
        )

    def _my_periodic_function(self):
        logger.info("It worked!")
        # To ingest in datalake uncomment the following
        args = {
            "value": chosen_number,
        }
        self.datalake_client.save(
            Variable,
            instances=[Variable(args=args)],
            collection=self.collection_name
        )
```

The component class must always be called `Main` and must inherit from one of
`splight_lib` abstract component classes. Also, super() init must be called. The
execution of the component starts when the method `start()` is called, so the method
should be implemented by the developer that is writting the component. Also, we
provide you a lot of useful functions in our package so you can use them to interact
with the platform and make better components

#### Component Initialization

In the case you need some previous steps to be run before the component is executed,
you can use the file `Initialization`. When you create your component with Splight Hub,
`Initialization` will have the following:

```json
RUN pip install splight-lib==<some lib version>
```

This command will be run before the component is executed. You can add more lines like
this, or maybe even create a requirements.txt file in the component directory and just
leave `Initialization` as:

```json
RUN pip install -r requirements.txt
```

#### Component Configuration

The file `spec.json` defines all the specification for the component, in this file you
will find generic information about the component like the name and version but also
you will find the input and output parameters.

The structure of the file `spec.json` is the following

```json
{
  "name": "component_name",
  "version": "component_version",
  "tags": ["tag1", "tag2"],
  "custom_types": [],
  "input": [],
  "output": []
}
```

A component can have different inputs and outputs that are previously defined, these
parameters can any or primite Python types like `str`, `int`, `float`, `bool` or `file`,
can also take the value of any Splight parameter like `Asset`, `Attribute`,
`Component`, `Mapping`, `Query`, but also can be custom type defined in the
`"custom_types"` key.
A parameter have the structure

```json
{
  "name": <name>,
  "type": <type>,
  "required": <required>,
  "value": <value>
}
```

and also accepts the key `"multiple"` with `true` or `false` value to specify if the
parameter can take multiple value that is parsed as a list when the component is running.

A custom type is defined by the following format

```json
{
  "name": "<custom_type_name",
  "fields": [
    {
      "name": "<name>",
      "type": "<type>",
      "required": "<required>",
      "multiple": "<multiple>",
      "value": "<value>"
    }
  ]
}
```

Then the custom type can be used as input or output. For example, we create
a custom type:

```json
{
  "name": "AssetAttribute",
  "fields": [
    {
      "name": "asset",
      "type": "Asset",
      "required": true,
      "multiple": false
    },
    {
      "name": "attribute",
      "type": "Attribute",
      "depends_on": "asset",
      "required": true,
      "multiple": false
    }
  ]
}
```

So we can use it as follows

```json
{
    "name": "CustomTypeVar",
    "type": "AssetAttribute",
    "required": true,
    "multiple": false,
    "value": [
        {
            "name": "asset",
            "type": "Asset",
            "required": true,
            "multiple": false,
            "value": <asset_id>
        },
        {
            "name": "attribute",
            "type": "Attribute",
            "required": true,
            "multiple": false,
            "value": <attribute_id>
        }
    ]
}
```

This is just an example but you can create custom types as complex as you want,
the limit is your imagination.

#### Running Locally

You can run the component locally before pushing it to the platform

```bash
splight component run <component directory>
```
