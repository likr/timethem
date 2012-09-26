import timeit
import unittest


def _new_method(testcase_class, method_name, param, number, plotparams):
    def test_method(self):
        self._classname = testcase_class.__name__
        self._plotparams = plotparams
        self._param = param

        self._setUp(param)
        method = testcase_class.__getattribute__(testcase_class, method_name)
        f = lambda: method(self)
        self._result = timeit.Timer(f).timeit(number) / number
        self._tearDown(param)
    return test_method


def timethem(parameters, number, plotparams=None):
    def _timethem(testcase_class):
        from inspect import getargspec

        attrs = {}
        if hasattr(testcase_class, 'setUp') \
           and len(getargspec(testcase_class.setUp).args) > 1:
            attrs['_setUp'] = testcase_class.setUp
        else:
            attrs['_setUp'] = lambda self, *args: None
        if hasattr(testcase_class, 'tearDown') \
           and len(getargspec(testcase_class.tearDown).args) > 1:
            attrs['_tearDown'] = testcase_class.tearDown
        else:
            attrs['_tearDown'] = lambda self, *args: None

        loader = unittest.TestLoader()
        for test_method in loader.loadTestsFromTestCase(testcase_class)._tests:
            test_method_name = test_method._testMethodName
            inner_test_method_name = '_' + test_method_name
            attrs[inner_test_method_name] = test_method
            for i, param in enumerate(parameters):
                new_method = _new_method(testcase_class, test_method_name,
                                         param, number, plotparams)
                new_method.__name__ = '{0}_{1}'.format(test_method_name, i)
                attrs[new_method.__name__] = new_method
        return type(testcase_class.__name__, testcase_class.__bases__, attrs)
    return _timethem


class TestResult(unittest._TextTestResult):
    def __init__(self, *args, **kwargs):
        super(TestResult, self).__init__(*args, **kwargs)
        self.results = {}
        self.plotparams = {}
        self.params = {}

    def addSuccess(self, test):
        class_name = test._classname
        method_name, index = self._parse_method_name(test._testMethodName)
        self.results.setdefault(class_name, {}). \
                setdefault(method_name, {})[index] = test._result
        self.plotparams[class_name] = test._plotparams
        self.params.setdefault(class_name, {})[index] = test._param

    def stopTestRun(self):
        for class_name, records in self.results.items():
            self._report_results(class_name, records, self.params[class_name])

            if self.plotparams[class_name]:
                plotparams = self.plotparams[class_name]
                try:
                    self._plot(records, self.params[class_name], plotparams)
                    self.stream.writeln(
                            '{0} saved'.format(plotparams['filename']))
                except Exception as e:
                    print(e)
                    self.stream.writeln('error occured')
            self.stream.writeln('')

    def _parse_method_name(self, method_name):
        return method_name[:-2], method_name[-1]

    def _report_results(self, class_name, records, params):
        method_names = sorted(records.keys())

        param_header_width = \
                max(len(str(param))
                    for param in params.values()) + 1
        param_header_template = '{{0:>{0}}}'.format(param_header_width)
        self.stream.writeln(class_name)

        header = param_header_template.format('')
        for method_name in method_names:
            width = max(len(method_name) + 1, 12)
            header += '{{0:>{0}}}'.format(width).format(method_name)
        self.stream.writeln(header)

        for index, param in sorted(params.items()):
            line = param_header_template.format(param)
            for method_name in method_names:
                width = max(len(method_name) + 1, 12)
                result = records[method_name][index]
                line += '{{0:{0}.6f}}'.format(width).format(result)
            self.stream.writeln(line)

    def _plot(self, records, params, plotparams):
        from matplotlib import pyplot

        plot_line = all(str(p).isdigit() for p in params.values())

        indices = sorted(params.keys())
        if plot_line:
            x = [int(str(p)) for _, p in sorted(params.items())]
            if plotparams.get('xlog', False):
                pyplot.xscale('log')
        else:
            x = [int(x) for x in indices]
            labels = [str(params[k]) for k in indices]
            pyplot.xticks(x, labels)

        if plotparams.get('ylog', False):
            pyplot.yscale('log')

        for method_name, results in records.items():
            y = [results[k] for k in indices]
            if plot_line:
                pyplot.plot(x, y)
            else:
                pyplot.bar(x, y)

        legends = records.keys()
        pyplot.legend(legends, loc=2)

        pyplot.savefig(plotparams['filename'])
        pyplot.close()

    def _plot_line(self, records):
        pass

    def _plot_bar(self, records):
        pass


class TestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return TestResult(self.stream, self.descriptions,
                          self.verbosity)


def main():
    unittest.main(testRunner=TestRunner(), verbosity=2)
