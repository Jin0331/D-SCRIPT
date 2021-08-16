"""
D-SCRIPT: Structure Aware PPI Prediction
"""
import argparse
import os
import sys

from omegaconf import OmegaConf


class CitationAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(CitationAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import dscript

        print(dscript.__citation__)
        setattr(namespace, self.dest, values)
        sys.exit(0)


def main():
    import dscript

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="D-SCRIPT " + dscript.__version__,
    )
    parser.add_argument(
        "-c",
        "--citation",
        action=CitationAction,
        nargs=0,
        help="show program's citation and exit",
    )

    subparsers = parser.add_subparsers(title="D-SCRIPT Commands", dest="cmd")
    subparsers.required = True

    from .commands import embed, evaluate, predict, train

    modules = {
        "train": train,
        "eval": evaluate,
        "embed": embed,
        "predict": predict,
    }

    for name, module in modules.items():
        sp = subparsers.add_parser(name, description=module.__doc__)
        module.add_args(sp)
        sp.set_defaults(cmd=name)

    args = parser.parse_args()
    oc = OmegaConf.create(vars(args))
    modules[args.cmd].main(oc)


if __name__ == "__main__":
    main()
