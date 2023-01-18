from md2latex_converter.core.cmd_parser import parse_command, Cmd


def main() -> None:
    # ext = SentExt('Code', r'```(?P<lang>.*)')

    cmd: Cmd = parse_command()

    cmd.handler()


if __name__ == "__main__":
    main()
