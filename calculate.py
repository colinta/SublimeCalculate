import sublime
import sublime_plugin

import math
import random
import re


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

        def password(length):
            pwdchrs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            return ''.join(random.choice(pwdchrs) for _ in xrange(length))

        self.dict['pwd'] = password
        self.dict['password'] = password


    def run(self, edit, **kwargs):
        calculate_e = self.view.begin_edit('calculate')
        regions = [region for region in self.view.sel()]

        # any edits that are performed will happen in reverse; this makes it
        # easy to keep region.a and region.b pointing to the correct locations
        def compare(region_a, region_b):
            return cmp(region_b.end(), region_a.end())
        regions.sort(compare)

        for region in regions:
            try:
                error = self.run_each(edit, region, **kwargs)
            except Exception as exception:
                error = exception.message

            if error:
                sublime.status_message(error)
        self.view.end_edit(calculate_e)

    def calculate(self, formula):
        formula = re.sub(r'(?<![\d\.])0*(\d+)',r'\1',formula) # replace leading 0 to numbers
        formula = re.sub(r'\n',' ',formula)  # replace newlines by spaces
        return unicode(eval(formula, self.dict, {}))

    def run_each(self, edit, region, replace=False):
        if region.empty() and len(self.view.sel()):
            def on_done(formula):
                value = self.calculate(formula)
                self.view.insert(edit, region.begin(), value)
            self.view.window().show_input_panel('Formula', '', on_done, None, None)
        elif not region.empty():
            formula = self.view.substr(region)
            value = self.calculate(formula)
            if not replace:
                value = "%s = %s" % (formula, value)
            self.view.replace(edit, region, value)


class CalculateCountCommand(sublime_plugin.TextCommand):
    def run(self, edit, index=1):
        regions = [region for region in self.view.sel()]

        def generate_integer_counter(initial):
            def count():
                offset = initial
                while True:
                    yield unicode(offset)
                    offset += 1

            return iter(count()).next

        def generate_hexadecimal_counter(initial, length):
            def count():
                offset = initial
                while True:
                    yield u"0x%x" % offset
                    offset += 1

            return iter(count()).next

        def generate_octal_counter(initial, length):
            def count():
                offset = initial
                while True:
                    yield u"0%o" % offset
                    offset += 1

            return iter(count()).next

        def generate_string_counter(initial):
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

                        if o > ord('z'):
                            offset = offset[:-up] + u'a' + tail
                            up += 1
                            if len(offset) < up:
                                offset = u'a' + offset
                                break
                        else:
                            offset = offset[:-up] + unichr(o) + tail
                            break

            return iter(count()).next

        is_first = True
        subs = []
        for region in regions:
            if is_first:
                # see if the region is a number or alphanumerics
                content = self.view.substr(region)
                if re.match('0x[0-9a-fA-F]+$', content):
                    counter = generate_hexadecimal_counter(int(content[2:], 16), len(regions))
                elif re.match('0[0-7]+$', content):
                    counter = generate_octal_counter(int(content[1:], 8), len(regions))
                elif re.match('[0-9]+$', content):
                    counter = generate_integer_counter(int(content))
                elif re.match('[a-z]+$', content):
                    counter = generate_string_counter(content)
                else:
                    counter = generate_integer_counter(index)

            subs.append((region, str(counter())))

            is_first = False

        # any edits that are performed will happen in reverse; this makes it
        # easy to keep region.a and region.b pointing to the correct locations
        def compare(sub_a, sub_b):
            return cmp(sub_b[0].end(), sub_a[0].end())
        subs.sort(compare)

        calculate_e = self.view.begin_edit('calculate')
        for sub in subs:
            self.view.sel().subtract(sub[0])
            self.view.replace(edit, sub[0], sub[1])
            self.view.sel().add(sublime.Region(sub[0].begin() + len(sub[1]), sub[0].begin() + len(sub[1])))
        self.view.end_edit(calculate_e)
