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
    - [Database](#database)
    - [Datalake](#datalake)
    - [Deployment](#deployment)
    - [Storage](#storage)
    - [Workspace](#workspace)
  - [Developing Components](#developing-components)


## Introduction

The Splight Command Line Interface is a unified tool to interact with *Splight 
Platform*. It contains different features that a user can use for creating, deloping, 
publishing components.

## Getting Started

### Installation

*SplightCLI* is a Python package that can be installed using `pip`
```bash
pip install splight-cli
```

At this date, the package is stored in a private repository so in order to 
install it you need to configure `pip` to download packages from JFROG. With your 
JFROG username and pasword you can run the following command so that `pip` is able 
to look for packages stored there

```sh
pip config set global.extra-index-url https://<your JFROG username>:<your JFROG password>@splight.jfrog.io/artifactory/api/pypi/splight/simple
```

Once you have installed `splight-cli` you can check the installation with 
```bash
splightcli 
```
You should see something like
```bash
$ splightcli

Usage: splightcli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
...
```

### Configuration

Before using the *Splight CLI*, you need to configure it. In order to do it you need 
to create your *User credentials* from the platform and then you will be able to 
configure *Splight CLI*.

#### Create Developer Credentials

Go to the [Splight Platform](https://app.splight-ae.com), and in your *User Configuration > Account*, in the right side pannel you will find the section *Developers* and the subsection *Credentials*. Under the *Credentials* subsection select “**New access key”.** This will generate a Client Access ID and Secret Key which are 
the credentials you will use for configuring *Splight CLI*. These credentials should 
not be share with other users.

Also, you need to keep in mind that the Secret Key is only shown once, if you loose the 
Key you will need to create a new set of Access Credentials.

#### Configure Splight CLI

The fastest and easiest way for configuring *Splight CLI* is running on your terminal 
the following command

```bash
splightcli configure
```

After entering the above command will ask you for the credentials you have created before.

## Commands

This section introduce you to many of the common features and options provided by 
*Splight CLI*.

The tool contains a set of commands that can be used for different purposes. 
In the following subsections, we will go through each of the commands that can be 
used.

The basic usage is 
```bash
splightcli <command> [--help]
```

where `<command>` is the command you want to use, and optionally you can add the flag 
`--help` to each one of the commands to get more information about the given command.

### Component

This is probably the most important command and the one you will use most. The command `component` allow you to operate over components, this mean you can create components, test locally components, push private or public components to *Splight HUB*, download 
existing component in *Splight HUB* and delete them.

In the following section we will cover in details the development process of a 
component, here we will only cover the different sub-commands you can use

* Create a new component
 
  To create a new component the command is
  ```bash
  splightcli component create <component_type> <name> <version>
  ```
  where `<component_type>` is the type of component to be created, can be one of
  `algorithm`, `connector`, `network` or `system`. The parameters `<name>` and 
  `<version>` are the name and version of the component to be created.
  The three commands parameters `<component_type>`, `<name>` and `<version>` are 
  commong between all the sub-commands.
  
  The command creates a new folder with the name `<name>-<version>` in the same 
  directory where the command was executed. Inside the new folder, you will find some
  files that defines the basic structure of the component source code.

* Delete a component

  You can delete an existing component with the command 
  ```bash
  splightcli component delete <component_type> <name> <version>
  ```
  This command deletes the component in *Splight HUB* so it can't be used any more.
  
* Install component locally

  The command
  ```bash
  splightcli component install-requirements <component_type> <path>
  ```
  Where the parameter `<path>` is the path to the component that will be installed 
  locally.

  This command is useful for running locally a component for testing and development.

* List component

  You can list all the component of given type with the command
  ```bash
  splightcli component list <component_type>
  ```

* Pull or download a component
  
  For downloading an existing component in *Splight HUB* you can use
  ```bash
  splightcli component pull <component_type> <name> <version>
  ```

  This will download the component source code to your machine.

* Push a component
  
  For pushing a new component or component version to *Splight HUB* the command is
  ```bash
  splightcli component push <component_type> <path>
  ```
  Where `<path>` is the path (relative or absolute) for the source code of the 
  component to be uploded.

* Run locally a component
  
  You can run locally a component, this is quite usefull for testing a comoponent
  before push it and for development a new component. The command is the following

  ```bash
  splightcli component run <component_type> <path> [-r] [-rs]
  ```
  This command will run a component locally. Optionally you can use the flag 
  `-r/--reset-input`, so you will be asked to configure some parameters for the 
  component. If it is the first time you run a component, you will see some messages in 
  the terminal for input some parameters values that are needed for running correctly 
  the component. Also, you can use the flag `-rs/--run-spec` for using a custom 
  configuration different to the one defined in the `spec.json` file. In the following 
  section we will dive in in the usage of the file `spec.json`.

* List component versions
  
  You can also list all the version of given component with 
  ```bash
  splightcli component versions <component_type> <name>
  ```
  
### Configure
This command is used for configuring Splight CLI and can be used as many times as you 
want.

The command is
```bash
splightcli configure
```

And it will prompt you to enter some pieces of information that needed by Splight CLI.
This command is quite useful when is used along with `workspace` command.

### Database
The `database` command is used for listing different resources from the Splight Platform.
The command is

```bash
splightcli database list <resource>
```

Where `<resource>` is the type of the resource to be listed. For example, can be 
`Algorithm`, `Connector`, `Network`, `Asset`, `Attribute` and many more.

### Datalake

You can interact with the datalake service using the `datalake` command as follow
```bash
splightcli datalake <sub-command>
```

The sub-commands are

* `dump` for getting data from datalake.
* `list` for listing the different collections.
* `load` for loading new data to the datalake.

Each sub-command contain it's own parameters. the information can be retrieved using the
`--help` flag:

```bash
splightcli datalake <sub-command> --help
```

### Deployment

The `deployment` command is used for listing the running component in the platform

```bash
splightcli deployment list
```

### Storage

The command `storage` allows the user to use the storage service. The command basics is
```bash
splgithcli storage <subcommand>
```
The sub-commands are

* `delete` for removing a file.
* `download` for downloaing a file.
* `list` for listing all the stored files.
* `load` for saving a new file.

### Workspace

This command allows you to manage different workspaces in the same computer. This can 
be useful for managing different environments of different users that share the same 
computer.

The command is
```bash
splightcli workspace <sub-command>
```

The available subcommands are
* `create` for creating new workspace. After the creation of a new worskpace you need to configure *Splight CLI* with `splightcli configure`.
* `delete` for deleting an existing workspace.
* `list` for listing the differents configured workspaces and showing the workspace in use.
* `select` for switching between the different configured workspaces.

## Developing Components

