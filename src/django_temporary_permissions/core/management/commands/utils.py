import djclick as click


class VerbosityParamType(click.ParamType):
    name = "verbosity"

    def __init__(self) -> None:
        self.quiet = False
        self.total = 0

    def convert(self, value, param, ctx):
        self.total += value
        if param.name == "quiet":
            self.quiet = True
        if self.quiet:
            value = 0
        return int(value)


Verbosity = VerbosityParamType()

_global_options = [
    click.option("-v", "--verbosity", default=1, type=Verbosity, count=True),
    click.option("-q", "--quiet", default=0, is_flag=True, type=Verbosity),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func
