#!/usr/bin/env python3

import argcomplete
import argparse
import os
import sys


def create_mat_command_line():
    def add(args):
        return (args.numberx + args.numbery, "addition")

    def sub(args):
        return (args.numbera - args.numberb, "subtraction")

    def mul(args):
        return (args.u * args.v, "multiplication")

    def div_int(args):
        return (args.i1 / args.i2, "division with integers")

    def div_flt(args):
        return (args.f1 / args.f2, "division with floats")

    parser = argparse.ArgumentParser(description="Amazing Math CLI", add_help=True)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("addition", aliases=["add"], help="Add two integers.", parents = [parser], add_help=False)
    parser_sub = subparsers.add_parser("subtraction", aliases=["sub"], help="Substracts two integers.", parents = [parser], add_help=False)
    parser_div = subparsers.add_parser("division", aliases=["div"], help="Divides two number.")
    parser_mul = subparsers.add_parser("multiplication", aliases=["mul"], help="Multiplies two integers.", parents = [parser], add_help=False)

    subparsers_div = parser_div.add_subparsers()
    parser_div_int = subparsers_div.add_parser("integer", aliases=["int"], help="Divides two integers.", parents = [parser], add_help=False)
    parser_div_flt = subparsers_div.add_parser("float", aliases=["flt"], help="Divides two floats.", parents = [parser], add_help=False)

    parser_add.add_argument("--numberx", "-x", type=float, help="Number X.")
    parser_add.add_argument("--numbery", "-y", type=float, help="Number Y.")

    parser_sub.add_argument("--numbera", "-a", type=float, help="Number A.")
    parser_sub.add_argument("--numberb", "-b", type=float, help="Number B.")

    parser_mul.add_argument("u", type=float, help="Number U.")
    parser_mul.add_argument("v", type=float, help="Number V.")

    parser_div_int.add_argument("i1", type=int, help="Integer 1.")
    parser_div_int.add_argument("i2", type=int, help="Integer 2.")

    parser_div_flt.add_argument("f1", type=float, help="Float 1.")
    parser_div_flt.add_argument("f2", type=float, help="Float 2.")

    parser_add.set_defaults(func=add)
    parser_sub.set_defaults(func=sub)
    parser_mul.set_defaults(func=mul)
    parser_div_int.set_defaults(func=div_int)
    parser_div_flt.set_defaults(func=div_flt)

    return parser


def execute_mat_operation(options, parser):
    if hasattr(options, 'func'):
        result = options.func(options)
    else:
        parser.print_help()
        sys.exit(1)

    if options.quiet:
        print(result[0])
    elif options.verbose:
        print("Operation '{1}' result is {0}.".format(*result))
    else:
        print("Result={0}".format(*result))


def main():
    # Create the command line parser
    parser = create_mat_command_line()

    # The argcomplete.autocomplete logic is slightly more complected now:
    # * Check for the environment variable which is set in the mat.complete.ps1 script
    # * If it is set, use stdout as output stream since PowerShell processes that one.
    # * Otherwise, just use the default settings
    output_stream=None
    if "_ARGCOMPLETE_POWERSHELL" in os.environ:
        output_stream = sys.stdout.buffer
    argcomplete.autocomplete(parser, output_stream=output_stream)

    # Do the parsing (after the completion!)
    options = parser.parse_args()

    # Just execut the operation
    execute_mat_operation(options, parser)
    sys.exit(0)


if __name__ == "__main__":
    main()
