from functools import cmp_to_key
import math
import random
import re

import sublime
import sublime_plugin


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

    def run(self, edit, **kwargs):
        self.dict['i'] = 0
        if len(self.view.sel()) == 1 and not self.view.sel()[0]:
            return self.get_formula()
        for region in self.view.sel():
            try:
                error = self.run_each(edit, region, **kwargs)
            except Exception as exception:
                error = str(exception)

            self.dict['i'] = self.dict['i'] + 1
            if error:
                sublime.status_message(error)

    def calculate(self, formula):
        # replace leading 0 to numbers
        formula = re.sub(r'(?<![\d\.])0*(\d+)', r'\1', formula)
        # replace newlines by spaces
        formula = re.sub(r'\n', ' ', formula)
        result = eval(formula, self.dict, {})

        if not isinstance(result, str):
            result = str(result)

        if result[-2:] == '.0':
            result = result[:-2]

        return result

    def run_each(self, edit, region, replace=False):
        if not region.empty():
            formula = self.view.substr(region)
            value = self.calculate(formula)
            if not replace:
                value = "%s = %s" % (formula, value)
            self.view.replace(edit, region, value)

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

        def generate_hexadecimal_counter(initial, length):
            def count():
                offset = initial
                while True:
                    yield u"0x%x" % offset
                    offset += 1

            return iter(count()).__next__

        def generate_octal_counter(initial, length):
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
                    counter = generate_hexadecimal_counter(int(content[2:], 16), len(regions))
                elif re.match('0[oO]?[0-7]+$', content):
                    counter = generate_octal_counter(int(content[1:], 8), len(regions))
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
