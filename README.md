# Calculate

Select a formula and run `calculate` to evaluate it using python. The result can be appended to the selection (`1+1` => `1+1 = 2`) or replace the selection (`1+1` => `2`). Using the `replace: true` option replaces the selected text with the result. Empty selections are treated as operating on lines, like most sublime commands. When the line under the caret is not a formula, you will be prompted for one, and the result will be inserted.

Because this plugin uses python to evaluate the selection, we cannot support countries/locales that use `,` as the decimal separator. We tried this for a long time, but realized it broke support for doing calculations on python lists, which is a very convenient feature. So in the interest of more calculator operations you will need to use English-style decimal (`.`) separators. And no `,` support in numbers, either, that applies the same for everyone!

Any function from `math` and `random` libraries can be used ([math][] and [random][] documentation).

You can generate passwords using `pwd(len)` (or `password(len)`).

Examples:

```
min(1,2,4)+max(9.8,9.11) = 10.8
round(1.23)+int(3.14)+ceil(3.6)+floor(3.4) = 11
oct(10) = 0o12
seed(42) = None
uniform(0,1)+randint(1,10) = 1.6394267984578836
choice(['a','b','c']) = c
sqrt(2)+pow(2,2) = 5.414213562373095
pi+e = 5.859874482048838
cos(pi/4)-sqrt(2)/2 = 0
pwd(16) = RPOIvGrv5iFlbCBF
```

You can calculate averages (mean) using `avg([values])` (or `average([values])`).
If you need to use a counter, you can use the `i` variable. Every selection will increase the counter, and it starts at 0. The `n` variable presents the total regions you've selected.

```
    i  =>  0        n-i-1 => 2        i*i  =>  0        (i+1)*10  =>  10
    i  =>  1        n-i-1 => 1        i*i  =>  1        (i+1)*10  =>  20
    i  =>  2        n-i-1 => 0        i*i  =>  4        (i+1)*10  =>  30
```

By typing command `Calculate: Run command for each regions`, you can run a python eval command for each regions, the region values are marked as `x`. 

For instance, type `x+1` will do an increment, and `x-1` is a decrement.

```
    x+1           x**x            x-n-1         x+1
    1 => 2        1 => 1          1 => -4       1+1 => 3
    2 => 3        2 => 4          2 => -3       2+1 => 4
    3 => 4        3 => 27         3 => -2       3+1 => 5
    4 => 5        4 => 256        4 => -1       4+1 => 6
```

There is also a `calculate_count` command, used to count from 1 (or another index, see below) and incrementing at every cursor.

[math]: http://docs.python.org/2/library/math.html
[random]: http://docs.python.org/2/library/random.html

## Installation

1. Using Package Control, install "Calculate"

Or:

1. Open the Sublime Text Packages folder

   - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
   - Windows: %APPDATA%/Sublime Text 3/Packages/
   - Linux: ~/.Sublime Text 3/Packages/ or ~/.config/sublime-text-3/Packages

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

## Commands

- `calculate`: Calculates the selection(s), or prompts for a formula. The `replace` argument (default: `false`) can be used to format the result (see above). The `prompt` argument (default: `true`) controls when to prompt for a formula, `true` for default behavior (see above), `false` for never and `"always"` whenever the selection is empty.
- `calculate_replace`: `calculate` command with replacement.
- `calculate_count`: Counts, adding 1 to the initial index, over each selection.
  - If the first selection is a number, it is used as the initial index.
  - Hexadecimal (`0xNNNN`) and octal (`0NNNN`) are matched, too.
  - If it is a letter, the alphabet is used.
  - Otherwise 1 is used, or it can be passed in as an argument (`index`) to the command.
- `calculate_add`: Add all the selected numbers and put the summation in the last empty cursor.
- `calculate_increment`: Increment the selected numbers by 1 (or number that the cursor is on).
- `calculate_decrement`: Decrement the selected numbers by 1 (or number that the cursor is on).
- `calculate_each_region`: Calculate each regions according to the command, the regions value are marked as `x`.

## Options & Settings

- `copy_to_clipboard`: Default is `False`. When enabled, the result will be put into the clipboard after calculation.
- `index_symbol`: Default is `'i'`. It presents the index of selections.
- `total_count_symbol`: Default is `'n'`. It presents the total count of regions.
- `region_symbol`: Default is `'x'`. It presents each region's value.

## Keybindings

Open your key bindings file and add the bindings you want. For example:

###### Example.sublime-keymap

```json
[
  { "keys": ["ctrl+shift+="], "command": "calculate", "args": { "replace": false } },
  { "keys": ["ctrl+shift+c"], "command": "calculate", "args": { "replace": true } },
  { "keys": ["ctrl+up"], "command": "calculate_increment" },
  { "keys": ["ctrl+down"], "command": "calculate_decrement" },
  { "keys": ["ctrl+shift+alt+1"], "command": "calculate_count" }
]
```
