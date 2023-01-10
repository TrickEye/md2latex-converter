from md2latex_converter.cmd_parser import parse_command, Cmd


def main() -> None:
    cmd: Cmd = parse_command()

    cmd.handler()


if __name__ == "__main__":
    main()
