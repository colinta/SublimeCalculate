Calculate for Sublime Text 2
============================

Select a formula and press `ctrl+shift+c` to evaluate it using python.  Result is printed as " = *value*".  `ctrl+shift+=` does the same thing, but replaces the selection.  If you have zero selections, you will be prompted for a formula, and the result will be inserted.

Installation
------------

1. Using Package Control, install "SublimeCalculate"

Or:

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo

Commands
--------

* `calculate`: Calculates the selection(s), or prompts for a formula.  If `replace` is false it leaves the content.
