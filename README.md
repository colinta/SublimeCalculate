Calculate for Sublime Text 2
============================

Select a formula and press `ctrl+shift+c` to evaluate it using python.  Result is printed as " = *value*".  `ctrl+shift+=` does the same thing, but replaces the selection.  If you have zero selections, you will be prompted for a formula, and the result will be inserted.

There is also a counting command, used to count from 1 (or another index, see below) and incrementing for each region.


Installation
------------

1. Using Package Control, install "SublimeCalculate"

Or:

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

Commands
--------

* `calculate`: Calculates the selection(s), or prompts for a formula.  If `replace` is false it leaves the content.
* `calculate_count`: Counts, adding 1 to the initial index, over each selection.  If the first selection is a number, it is used as the initial index.  Otherwise 1 is used, or it can be passed in as an argument (`index`).