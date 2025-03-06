from functools import cmp_to_key
import math
import random
import re
from locale import (atof, str as locale_str)
import os
import sublime
import sublime_plugin
import json

def load_settings():
    return sublime.load_settings("SublimeCalculate.sublime-settings")

def mean(numbers, *more):
    if more:
        return mean([numbers] + list(more))
    if len(numbers) == 0:
        return
    return sum(numbers) / len(numbers)

"""
This func calculate the standard varience of numbers.
`ddof` is `Delta Degrees of Freedom`, chosen from Numpy's API.
The default `ddof` is 0.
"""
def std(numbers, *more, ddof = 0):
    if more:
        return std([numbers] + list(more))
    if len(numbers) == 0:
        return
    variance = sum((x - mean(numbers)) ** 2 for x in numbers) / (len(numbers) - ddof)
    return math.sqrt(variance)

def is_number(view, sel):
    try:
        substr = view.substr(sel)
        atof(substr)
        return True
    except ValueError:
        return False

def to_clipboard(res):
    sublime.set_clipboard(str(res))
    sublime.status_message("Result " + str(res) + " copied to clipboard!")

class SelectionListener(sublime_plugin.EventListener):
    """
    If all selections are numbers, show sum and average in status bar
    """
    def on_selection_modified_async(self, view):
        number_selections = list(filter(lambda sel: is_number(view, sel), view.sel()))
        if len(number_selections) <= 1:
            return
        numbers = [atof(view.substr(sel)) for sel in number_selections]
        sublime.status_message("Sum: {:n}\tAverage: {:n}".format(sum(numbers), mean(numbers)))

# add replace command for convenience
class CalculateReplaceCommand(CalculateCommand):
    def run(self, edit):
        self.view.run_command("calculate", {"replace": True})

class CalculateCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)
        self.settings = load_settings()
        self.dict = {}
        for key in dir(random):
            self.dict[key] = getattr(random, key)
        for key in dir(math):
            self.dict[key] = getattr(math, key)

        def average(nums):
            return sum(nums) / len(nums)

        self.dict['avg'] = average
        self.dict['average'] = average

        def password(length=20):
            pwdchrs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            return ''.join(random.choice(pwdchrs) for _ in range(length))

        self.dict['pwd'] = password
        self.dict['password'] = password
        self.dict['mean'] = mean

        builtins = {}
        for key in [
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'compile', 'complex', 'dict', 'dir', 'divmod', 'enumerate',
            'filter', 'float', 'format', 'frozenset', 'getattr', 'hasattr', 'hash',
            'hex', 'id', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'map',
            'max', 'memoryview', 'min', 'next', 'object', 'oct', 'ord', 'pow', 'range',
            'repr', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple',
            'type', 'vars', 'zip'
        ]:
            try:
                builtins[key] = __builtins__[key]
            except KeyError:
                pass

        self.dict['__builtins__'] = builtins
        self.index_symbol = self.settings.get('index_symbol', 'i')
        self.total_count_symbol = self.settings.get('total_count_symbol', 'n')
        self.region_symbol = self.settings.get('region_symbol', 'x')

    def run(self, edit, **kwargs):
        self.dict[self.index_symbol] = 0
        # sometimes `n` is quite useful
        self.dict[self.total_count_symbol] = len(self.view.sel())

        for region in self.view.sel():
            try:
                error = self.run_each(edit, region, **kwargs)
            except Exception as exception:
                error = str(exception)

            self.dict[self.index_symbol] = self.dict[self.index_symbol] + 1
            if error:
                self.view.show_popup(error)

    def calculate(self, formula):
        # remove newlines
        formula = formula.replace('\n',' ').replace('\r',' ')
        # replace × by * and ÷ by /
        formula = formula.replace('×', '*').replace('÷', '/')

        # remove preceding 0s (preserve hex digits)
        formula = re.sub(r'\b(?<![\d\.])0*(\d+)\b', r'\1', formula)
        # finally evaluate it
        result = eval(formula, self.dict, {})

        # convert result to string if needed
        if not isinstance(result, str):
            result = str(result)
        # if result is integer
        if result[-2:] == '.0':
            result = result[:-2]

        return result

    def run_each(self, edit, region, replace=False, prompt=True):
        if not region.empty():
            formula = self.view.substr(region)
            value = self.calculate(formula)
            if not replace:
                value = "%s = %s" % (formula, value)
            self.view.replace(edit, region, value)
        elif prompt == 'always':
            self.get_formula()
        else:
            line = self.view.line(region.a)
            formula = self.view.substr(line)

            try:
                value = self.calculate(formula)
            except SyntaxError as ex:
                if prompt and len(self.view.sel()) == 1:
                    self.get_formula()
                else:
                    raise ex
            else:
                self.view.sel().subtract(region)
                if not replace:
                    value = " = %s" % (value)
                    self.view.replace(edit, sublime.Region(line.b, line.b), value)
                else:
                    self.view.replace(edit, line, value)
                line = self.view.line(line.a)
                self.view.sel().add(sublime.Region(line.b, line.b))

    def get_formula(self):
        self.view.window().show_input_panel('Calculate:', '', self.on_calculate, None, None)

    def on_calculate(self, formula):
        value = self.calculate(formula)
        self.view.run_command('insert_snippet', {'contents': '${0:%s}' % value})


class CalculateCountCommand(sublime_plugin.TextCommand):
    def run(self, edit, index=1):
        def generate_integer_counter(initial):
            def count():
                offset = initial
                while True:
                    yield str(offset)
                    offset += 1

            return iter(count()).__next__

        def generate_hexadecimal_counter(initial):
            def count():
                offset = initial
                while True:
                    yield u"0x%x" % offset
                    offset += 1

            return iter(count()).__next__

        def generate_octal_counter(initial):
            def count():
                offset = initial
                while True:
                    yield u"0%o" % offset
                    offset += 1

            return iter(count()).__next__

        def generate_string_counter(initial):
            if re.match('[a-z]+$', initial):
                maxord = ord('z')
                letter = 'a'
            else:
                maxord = ord('Z')
                letter = 'A'
            def count():
                offset = initial
                while True:
                    yield offset

                    up = 1  # increase last character
                    while True:
                        o = ord(offset[-up])
                        o += 1
                        tail = ''
                        if up > 1:
                            tail = offset[-up + 1:]

                        if o > maxord:
                            offset = offset[:-up] + letter + tail
                            up += 1
                            if len(offset) < up:
                                offset = letter + offset
                                break
                        else:
                            offset = offset[:-up] + chr(o) + tail
                            break

            return iter(count()).__next__

        def generate_plusminus_counter(initial):
            def count():
                offset = initial
                while True:
                    yield str(offset)
                    if offset == '-':
                        offset = '+'
                    else:
                        offset = '-'

            return iter(count()).__next__

        is_first = True
        subs = []
        for region in self.view.sel():
            if is_first:
                # see if the region is a number or alphanumerics
                content = self.view.substr(region)
                if re.match('0[xX][0-9a-fA-F]+$', content):
                    counter = generate_hexadecimal_counter(int(content[2:], 16))
                elif re.match('0[oO]?[0-7]+$', content):
                    if re.match('0[oO]', content):
                        start = 2
                    else:
                        start = 1
                    counter = generate_octal_counter(int(content[start:], 8))
                elif re.match('[+-]?[0-9]+$', content):
                    counter = generate_integer_counter(int(content))
                elif re.match('[A-Za-z]+$', content):
                    counter = generate_string_counter(content)
                elif re.match('[+-]+$', content):
                    counter = generate_plusminus_counter(content)
                else:
                    counter = generate_integer_counter(index)

            subs.append((region, str(counter())))

            is_first = False

        # any edits that are performed will happen in reverse; this makes it
        # easy to keep region.a and region.b pointing to the correct locations
        def get_end(region_tuple):
            return region_tuple[0].end()
        subs.sort(key=get_end, reverse=True)

        for sub in subs:
            self.view.sel().subtract(sub[0])
            self.view.replace(edit, sub[0], sub[1])
            self.view.sel().add(sublime.Region(sub[0].begin() + len(sub[1]), sub[0].begin() + len(sub[1])))


class CalculateMathCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        insert_region = None
        numbers = []
        for region in self.view.sel():
            if not region:
                insert_region = region
            else:
                try:
                    only_number = self.view.substr(region).replace('$', '')
                    number = atof(only_number)
                except ValueError:
                    pass
                numbers.append(number)

        result = repr(self.operation(numbers, **kwargs))

        # Get clipboard settings, by default clipboard is off.
        settings = load_settings()
        enable_clipboard = settings.get("copy_to_clipboard", False)
        if enable_clipboard:
            to_clipboard(result)

        if insert_region is None:
            # self.view.show_popup('Select an empty region where the output will be inserted')
            self.view.show_popup(result)
        else:
            self.view.replace(edit, insert_region, result)

    def operation(self, numbers, **kwargs):
        raise Exception("Implement 'def operation(self, numbers)' in {}".format(type(self).__name__))

class CalculateAddCommand(CalculateMathCommand):
    def operation(self, numbers):
        return sum(numbers)

class CalculateMeanCommand(CalculateMathCommand):
    def operation(self, numbers):
        return mean(numbers)

class CalculateStdCommand(CalculateMathCommand):
    def operation(self, numbers, **kwargs):
        return std(numbers, **kwargs)

class CalculateIncrementCommand(sublime_plugin.TextCommand):
    DELTA = 1

    def run(self, edit):
        for region in self.view.sel():
            if not region:
                start = end = region.a
                while is_number(self.view, sublime.Region(start - 1, start)):
                    start -= 1
                while is_number(self.view, sublime.Region(end, end + 1)):
                    end += 1
                region = sublime.Region(start, end)

            try:
                number = atof(self.view.substr(region))
            except ValueError:
                continue
            number += self.DELTA
            self.view.replace(edit, region, locale_str(number))


class CalculateDecrementCommand(CalculateIncrementCommand):
    DELTA = -1

class CalculateEachRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_input_panel("Enter command:", "", self.on_done, None, None)

    def on_done(self, input_string):
        self.view.run_command("apply_calculation", {"command": input_string})

class ApplyCalculationCommand(CalculateCommand):
    def run(self, edit, command):
        self.dict[self.index_symbol] = 0
        self.dict[self.total_count_symbol] = len(self.view.sel())

        selections = self.view.sel()
        for region in selections:
            try:
                formula = self.view.substr(region)
                self.dict[self.region_symbol] = eval(formula, self.dict, {})
                result = eval(command, self.dict, {})
                self.view.replace(edit, region, str(result))

            except Exception as exception:
                error = str(exception)
                self.view.show_popup(error)

            self.dict[self.index_symbol] = self.dict[self.index_symbol] + 1


class OpenSettingsCommand(sublime_plugin.WindowCommand):
    def run(self):
        setting_path = os.path.join(sublime.packages_path(), 'User', 'SublimeCalculate.sublime-settings')
        if not os.path.exists(setting_path):
            default_settings = {
                "copy_to_clipboard": False,
                "index_symbol": "i",
                "total_count_symbol": "n",
                "region_symbol": "x",
            }
            with open(setting_path, 'w') as f:
                json.dump(default_settings, f, indent=4)
        self.window.run_command("open_file", {"file": setting_path})
