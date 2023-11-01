from functools import cmp_to_key
import math
import random
import re
from locale import (atof, str as locale_str)

import sublime
import sublime_plugin


def mean(numbers, *more):
    if more:
        return mean([numbers] + list(more))
    return sum(numbers) / len(numbers)

def is_number(view, sel):
    try:
        substr = view.substr(sel)
        atof(substr)
        return True
    except ValueError:
        return False

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

class CalculateCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)
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

    def run(self, edit, **kwargs):
        self.dict['i'] = 0
        for region in self.view.sel():
            try:
                error = self.run_each(edit, region, **kwargs)
            except Exception as exception:
                error = str(exception)

            self.dict['i'] = self.dict['i'] + 1
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
    def run(self, edit):
        insert_region = None
        numbers = []
        for region in self.view.sel():
            if not region:
                insert_region = region
            else:
                try:
                    number = atof(self.view.substr(region))
                except ValueError:
                    pass
                numbers.append(number)

        if insert_region is None:
            self.view.show_popup('Select an empty region where the output will be inserted')
            return

        self.view.replace(edit, insert_region, repr(self.operation(numbers)))

    def operation(self, numbers):
        raise Exception("Implement 'def operation(self, numbers)' in {}".format(type(self).__name__))

class CalculateAddCommand(CalculateMathCommand):
    def operation(self, numbers):
        return sum(numbers)

class CalculateMeanCommand(CalculateMathCommand):
    def operation(self, numbers):
        return mean(numbers)


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
