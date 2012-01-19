import sublime
import sublime_plugin

import math


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
