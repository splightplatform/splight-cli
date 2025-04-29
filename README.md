# Splight CLI

---

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

You can enable auto completions by running

```bash
splight --install-completion <SHELL>
```

where SHELL is either bash, zsh, fish, powershell, pwsh.

This will add commands at the bottom of your shell's dotfile (zsh example):

```bash
autoload -Uz compinit
zstyle ':completion:*' menu select
fpath+=~/.zfunc
```

If these do not work after restarting the shell, you can try adding

```bash
compinit -D
```

to the bottom of your shell's dotfile, in order to recreate the autocompletions file, and restarting again.

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
  splight component create <name> -v <version> -p <path>
  ```

  The parameters `<name>` and
  `<version>` are the name and version of the component to be created,
  while the `<path>` parameter is the path of the directory where the
  component will be created.
  The three commands parameters `<name>` and `<version>` are
  commong between all the sub-commands.

  If no `<path>` is specified, you will find some
  files that defines the basic structure of the component source
  code in the same directory where the command was executed. If `<path>`
  is specified, then the files will be located in the specified path.

- Create component Readme

  As a component developer, you can generate a README.md file automatically using the
  command

  ```bash
  splight component readme <path> [-f]
  ```

  This way, based on the `spec.json` file the readme is generated and you don't need
  to care about basic descriptions like input, output, custom types and more.

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

#### Component

- List component

  You can list all the components with the command

  ```bash
  splight hub component list
  ```

- Pull or download a component

  For downloading an existing component in _Splight Hub_ you can use

  ```bash
  splight hub component pull <name> <version>
  ```

  This will download the component source code to your machine.

- Push a component

  For pushing a new component or component version to _Splight Hub_ the command is

  ```bash
  splight hub component push <path>
  ```

  Where `<path>` is the path (relative or absolute) for the source code of the
  component to be uploded.

- List component versions

  You can also list all the version of given component with

  ```bash
  splight hub component versions <name>
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

- `create <name>` to create a new workspace. After the creation of a new worskpace you need to configure _Splight CLI_ with `splight configure`.
- `delete <name>` to delete an existing workspace.
- `list` to list all workspaces. Current workspace displays a '\*' to the left.
- `select <name>` to switch between different configured workspaces.
- `show <name>` to display the contents of an existing workspace.

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
│   main.py
│   Initialization
│   spec.json
│   README.md
```

- `main.py` : The main file to contian the component's code.
- `Initialization` : Execute instructions for the component to be initialized.
- `spec.json` : JSON file where the component metadata is set.
- `README.md` : Text that describes the component and how it works

#### Component Core

When creating a component, inside `main.py` you will find a component template 
already written in python for you, in order to make it easier to write the component code.

For example, when you create an algorithm component, in `main.py` will have the following:

```python
import random
from typing import Optional, Type

import typer
from splight_lib.component import SplightBaseComponent
from splight_lib.execution import Task
from splight_lib.logging import getLogger
from splight_lib.models import Number

app = typer.Typer(pretty_exceptions_enable=False)


class ExampleComponent(SplightBaseComponent):
    def __init__(self, component_id: str):
        super().__init__(component_id)
        self._logger = getLogger("MyComponent")

    def start(self):
        self.execution_engine.start(
            Task(
                handler=self._run,
                args=(self.input.min, self.input.max),
                period=self.input.period,
            )
        )

    def _run(self, min_value: float, max_value: float):
        value = self._give_a_random_value(
            self.input.lower_bound, self.input.upper_bound
        )
        preds = Number(
            value=value,
        )
        preds.save()
        self._logger.info(f"\nValue = {value}\n")

    def _give_a_random_value(self, min: float, max: float) -> float:
        return (max - min) * random.random() + min


@app.command()
def main(
    component_id: str = typer.Option(...),
    input: Optional[str] = typer.Option(None),
):
    logger = getLogger("MyComponent")
    component = ExampleComponent(component_id=component_id)
    try:
        component.start()
    except Exception as exc:
        logger.exception(exc, tags="EXCEPTION")
        component.stop()


if __name__ == "__main__":
    app()
```

The component class must always be called `Main` and must inherit from one of
`splight_lib` abstract component classes. Also, super() init must be called. The
execution of the component starts when the method `start()` is called, so the method
should be implemented by the developer that is writting the component. Also, we
provide you a lot of useful functions in our package so you can use them to interact
with the platform and make better components
