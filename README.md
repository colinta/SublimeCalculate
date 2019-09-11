Calculate
=========

Select a formula and run `calculate` to evaluate it using python.  The result can be appended to the selection (`1+1` => `1+1 = 2`) or replace the selection (`1+1` => `2`).  Using the `replace: true` option replaces the selected text with the result.  Empty selections are treated as operating on lines, like most sublime commands.  When the line under the caret is not a formula, you will be prompted for one, and the result will be inserted.  

Any function from `math` and `random` libraries can be used ([math][] and [random][] documentation).

You can generate passwords using `pwd(len)` (or `password(len)`).
You can calculate averages (mean) using `avg([values])` (or `average([values])`).
If you need to use a counter, you can use the `i` variable.  Every selection will increase the counter, and it starts at 0.

    i  =>  0        i*i  =>  0        (i+1)*10  =>  10
    i  =>  1        i*i  =>  1        (i+1)*10  =>  20
    i  =>  2        i*i  =>  4        (i+1)*10  =>  30

There is also a `calculate_count` command, used to count from 1 (or another index, see below) and incrementing at every cursor.

[math]: http://docs.python.org/2/library/math.html
[random]: http://docs.python.org/2/library/random.html

Installation
------------

1. Using Package Control, install "Calculate"

Or:

1. Open the Sublime Text Packages folder
    - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
    - Windows: %APPDATA%/Sublime Text 3/Packages/
    - Linux: ~/.Sublime Text 3/Packages/ or ~/.config/sublime-text-3/Packages

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

Commands
--------

* `calculate`: Calculates the selection(s), or prompts for a formula.  The `replace` argument (default: `false`) can be used to format the result (see above).  The `prompt` argument (default: `true`) controls whether to prompt for a formula or not (see above as well). 
* `calculate_count`: Counts, adding 1 to the initial index, over each selection.
  - If the first selection is a number, it is used as the initial index.
  - Hexadecimal (`0xNNNN`) and octal (`0NNNN`) are matched, too.
  - If it is a letter, the alphabet is used.
  - Otherwise 1 is used, or it can be passed in as an argument (`index`) to the command.
* `calculate_add`: Add all the selected numbers and put the summation in the last empty cursor.
* `calculate_increment`: Increment the selected numbers by 1 (or number that the cursor is on).
* `calculate_decrement`: Decrement the selected numbers by 1 (or number that the cursor is on).

Keybindings
-----------

Open your key bindings file and add the bindings you want.  For example:

###### Example.sublime-keymap
```json
[
    { "keys": ["ctrl+shift+="], "command": "calculate", "args": {"replace": false} },
    { "keys": ["ctrl+shift+c"], "command": "calculate", "args": {"replace": true} },
    { "keys": ["ctrl+up"], "command": "calculate_increment" },
    { "keys": ["ctrl+down"], "command": "calculate_decrement" },
    { "keys": ["ctrl+shift+alt+1"], "command": "calculate_count" }
]
```
