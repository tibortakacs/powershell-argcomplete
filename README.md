# PowerShell with `argcomplete`

## Introduction

[`argcomplete`](https://github.com/kislyuk/argcomplete) is a great Python package for
tab completion, however, it only works with bash as your shell (and with zsh, fish and
tcsh with limited support).  [`PowerShell`](https://github.com/PowerShell/PowerShell)
has also a great command-line interface, but the `argcomplete`-based applications cannot
use its tab completion functionality.

**This project provides a straightforward solution how to use `argcomplete` tab completion
functionality in `PowerShell`.**

## Content

* **`mat.py`**.  Example script with `argcomplete`.
* **`mat.complete.ps1`**.  Script to register `mat` command for tab completion.
* **`mat.complete.psm1`**.  Module to register `mat` command for tab completion.

## How to use the example?

* Start a new PowerShell window.
* Clone this project.
* Create and activate your Python3 virtual environment as you like.
* Enter into this project's directory (`cd powershell-argcomplete`)
* Install `argparse` and `argcomplete`.
* Test `mat.py` by calling `python .\mat.py`
* Activate PowerShell tab completion with either of the scripts:
    * Dot-sourcing: `. .\mat.complete.ps1`
    * Import module: `Import-Module .\mat.complete.psm1`
* Run `mat`
* Play with `Tab` or `Ctrl+Space` auto-completion of `mat`.

## Background

`Register-ArgumentCompleter` ([link](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/register-argumentcompleter?view=powershell-7))
"*registers a custom argument completer.  An argument completer allows you to provide*
*dynamic tab completion, at run time for any command that you specify.*"  The main idea
is that using this cmdlete we register a script to complete arguments of an alias
function which wraps the original command:

1. A PowerShell function is defined which is a simple alias of the original command:

```powershell
$MatPythonCommand = "&'python .\mat.py'"
$MatCommandAlias = "mat"

Function mat {
    Invoke-Expression "$MatPythonCommand $args"
}
```

2. Using `Register-ArgumentCompleter`, the command alias is registered for argument
completion:

```powershell
Register-ArgumentCompleter -Native -CommandName $MatCommandAlias -ScriptBlock $MatArgCompleteScriptBlock
```

`$MatArgCompleteScriptBlock` script block is called by activating argument completion
(by pressing `Tab` or `Ctrl+Space`)

3. `$MatArgCompleteScriptBlock` script block mimics bash by setting up special environment
variables on a similiar way:

```powershell
New-Item -Path Env: -Name _ARGCOMPLETE -Value 1 | Out-Null # Enables tab completion in argcomplete
New-Item -Path Env: -Name COMP_TYPE -Value 9 | Out-Null # Constant
New-Item -Path Env: -Name _ARGCOMPLETE_IFS -Value " " | Out-Null # Separator of the items
New-Item -Path Env: -Name _ARGCOMPLETE_SUPPRESS_SPACE -Value 1 | Out-Null # Constant
New-Item -Path Env: -Name _ARGCOMPLETE_COMP_WORDBREAKS -Value "" | Out-Null # Constant
New-Item -Path Env: -Name COMP_POINT -Value $cursorPosition | Out-Null # Refers to the last character of the current line
New-Item -Path Env: -Name COMP_LINE -Value $line | Out-Null # Current line
```

`argcomplete` uses these variables as input to determine the completion suggestions.

4. `argcomplete` writes the result into an output stream.  Per default, it uses file
descriptor `8` which is not supported by Powershell.  In order to fill this gap, the
new `_ARGCOMPLETE_OSTREAM_FD` has been introduced [here](https://github.com/tibortakacs/argcomplete/blob/f51a8efcfbe58fda54f70216e978d9043daac458/argcomplete/__init__.py#L188).  If this variable exists, it specifies the file descriptor of the
output stream used by `argcomplete`.  The PowerShell script sets up this variable for
`stdout`, while bash does not touch it, so the original behaviour is also kept:

```powershell
New-Item -Path Env: -Name _ARGCOMPLETE_OSTREAM_FD -Value 1 | Out-Null
```

5. Finally, the script just executes the original command.  Due to the set environment
variables, `argcomplete` will execute the `autocomplete` function and writes the result
back to `stdout` which is redirected into a variable.  Splitting this result into
separated lines are the results of argument completion which are presented by the
command-line window to the user:

```powershell
Invoke-Expression $MatPythonCommand -OutVariable completionResult -ErrorVariable errorOut -ErrorAction SilentlyContinue | Out-Null
...
$items = $completionResult.Split()
if ($items -eq $completionResult) {
    "$items "
}
else {
    $items
}
```

6. There are a few minor tricks in the pre- and post-processing parts to mimic the bash
experience as much as possible.  These can be freely modified to adapt the behaviour
to specific needs.
