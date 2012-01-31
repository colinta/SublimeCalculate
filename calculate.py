import sublime
import sublime_plugin

import math
import re


class CalculateCommand(sublime_plugin.TextCommand):
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
        dict = {}
        for key in dir(math):
            dict[key] = getattr(math, key)

        def average(nums):
            return sum(nums) / len(nums)

        dict['avg'] = average
        dict['average'] = average

        return unicode(eval(formula, dict, {}))

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

        def generate_counter(initial):
            def count():
                offset = initial
                while True:
                    yield offset
                    offset += 1
            return iter(count()).next

        is_first = True
        subs = []
        for region in regions:
            if is_first:
                print region
                # see if the region is a number or alphanumerics
                content = self.view.substr(region)
                if re.match('[0-9]+$', content):
                    counter = generate_counter(int(content))
                else:
                    counter = generate_counter(index)

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
