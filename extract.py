#!/usr/bin/env python3

import argparse
import collections
import logging
from pathlib import Path
import re
import shlex
import sys
import textwrap
import typing as T

import marko.parser
import marko.block
import marko.inline

import yaml

__version__ = "0.1.0"

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger("extract")


def parse_markdown_doc(markdown_path: Path) -> marko.block.Document:
    parser = marko.parser.Parser()
    md_text = markdown_path.read_text()
    doc = parser.parse(md_text)
    return doc


def yaml_dump(data: T.Any, *, explicit_start=True) -> str:
    return yaml.dump(
        data,
        Dumper=yaml.Dumper,
        indent=2,
        explicit_start=explicit_start,
        sort_keys=False,
    )


def stripped(lines: T.Iterable[str]) -> T.List[str]:
    return [line.strip() for line in lines]


def backslash_newline(s: str) -> str:
    return re.sub(r"\\\s*\n\s*", " ", s)


def raw_text_lines(raw_text: str) -> T.List[str]:
    lines = stripped(backslash_newline(raw_text).splitlines())
    return lines


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


MarkoCode = T.Union[marko.block.CodeBlock, marko.block.FencedCode]


def code_text(marko_code: MarkoCode) -> str:
    return marko_code.children[0].children


Tag = str
TagMap = T.Dict[Tag, T.List[str]]
Keyword = str


def split_tag(text: str) -> T.Tuple[Tag, str]:
    m = re.search(r"^(:[-a-zA-Z]+:)(.*)$", text)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def is_keyword(text: str) -> bool:
    return re.search(r"^[-a-zA-Z]+$", text) is not None


def para_tags(para: marko.block.Paragraph) -> TagMap:
    """Return {':tag1:' : ['suffix1', 's2'], ':tag2:': ['']] for paragraph.

    Empty suffixes are included in the list.

    Example:
            Paragraph
                RawText: 'text '
                CodeSpan: ':tag1:suffix1'
                RawText: ' more text '
                CodeSpan: ':tag2:'
                RawText: ' even more text '
                CodeSpan: ':tag1:s2'
                RawText: ':'
    """
    tags: T.Dict[Tag, T.List[str]] = {}
    for child in para.children:
        if isinstance(child, marko.inline.CodeSpan):
            code_span = child.children
            tag, suffix = split_tag(code_span)
            if tag:
                tags.setdefault(tag, []).append(suffix)
    return tags


def para_keywords(para: marko.block.Paragraph) -> T.List[Keyword]:
    """Return ['keyword1', 'keyword2'] for paragraph.

    Example:
            Paragraph
                RawText: 'keyword1 '
                CodeSpan: ':span1:'
                RawText: ' keyword2 more text '
                CodeSpan: ':span2:'
                RawText: ':'
    """
    keywords = []
    for child in para.children:
        if isinstance(child, marko.inline.RawText):
            for text in child.children.split():
                if is_keyword(text):
                    keywords.append(text)
    return keywords


def extract_tagged_code(
    node: marko.block.Element,
) -> T.Generator[
    T.Tuple[TagMap, T.List[Keyword], marko.block.Paragraph, MarkoCode],
    None,
    None,
]:
    children = getattr(node, "children", None)
    if not isinstance(children, list):
        return

    para_pos = 0
    while para_pos < len(children):
        para = children[para_pos]
        if isinstance(para, marko.block.Paragraph):
            tags = para_tags(para)
            code_pos = para_pos + 1

            while code_pos < len(children) and isinstance(
                children[code_pos], marko.block.BlankLine
            ):
                code_pos += 1

            if tags and code_pos < len(children):
                code = children[code_pos]
                if isinstance(
                    code, (marko.block.CodeBlock, marko.block.FencedCode)
                ):
                    para_pos = code_pos + 1
                    yield tags, para_keywords(para), para, code
                    continue

            if tags:
                logger.warning(
                    f"paragraph with tags {tags} lacks code (try --verbose)"
                )

        yield from extract_tagged_code(children[para_pos])
        para_pos += 1


def extract_into_files(node: marko.block.Element) -> None:
    for tags, keywords, para, code in extract_tagged_code(node):
        for dest in tags.get(":extract:", []):
            write_text(Path(dest), code_text(code))
        for dest in tags.get(":extract-echod:", []):
            # Remove leading `echod` and trailing quote line:
            # E.g.:
            #   echod -o output_file '
            #     This is the first line
            #     This is the last line
            #   '
            lines = code_text(code).splitlines()[1:-1]
            text = "\n".join(lines) + "\n"
            write_text(Path(dest), textwrap.dedent(text))


def walk(tree: marko.block.Element, indent="") -> None:
    if isinstance(tree, marko.inline.RawText):
        print(f"{indent}RawText: {tree.children!r}")
    elif isinstance(tree, marko.inline.CodeSpan):
        print(f"{indent}CodeSpan: {tree.children!r}")
    # elif isinstance(tree, marko.block.CodeBlock):
    #     print(f"{indent}CodeBlock: {tree.children!r}")
    elif isinstance(tree, marko.block.FencedCode):
        raw_text = tree.children[0].children
        print(f"{indent}FencedCode({tree.lang}): {raw_text!r}")
    else:
        print(f"{indent}{tree.get_type()}")
        if getattr(tree, "children", None) is None:
            pass
            # print(f"{indent}no children")
        elif isinstance(tree.children, list):
            for i, child in enumerate(tree.children, 1):
                walk(child, indent + "    ")
        else:
            print(
                f"{indent}non-list children; "
                f"type {type(tree.children)}, {tree.children!r}"
            )


def extract_install_pipxg(
    cmd_args: T.List[str],
    roles: T.List[str],
    role_yaml_parts: T.DefaultDict[str, T.List[str]],
) -> None:
    if len(cmd_args) >= 3 and cmd_args[:2] == "pipxg install".split():
        name = cmd_args[-1]
        yaml_part = yaml_dump(
            [
                dict(
                    name=f"pipxg Install {name}",
                    command=" ".join(shlex.quote(arg) for arg in cmd_args),
                    args=dict(creates=f"/usr/local/bin/{name}"),
                )
            ],
            explicit_start=False,
        )

        for role in roles:
            role_yaml_parts[role].append(yaml_part)


def extract_install(
    code: MarkoCode,
    roles: T.List[str],
    role_yaml_parts: T.DefaultDict[str, T.List[str]],
    dist_role_packages: T.Dict[str, T.DefaultDict[str, T.List[str]]],
) -> None:
    if not isinstance(code, marko.block.CodeBlock):
        logger.warning("Install missing code block (try --verbose)")
        return

    for line in raw_text_lines(code_text(code)):
        if not line.strip():
            continue
        cmd_args = shlex.split(line)
        cmd, *args = cmd_args
        if cmd == "pipxg":
            extract_install_pipxg(cmd_args, roles, role_yaml_parts)
        elif cmd in ("agi", "yi"):
            packages = args
            if not packages:
                logger.warning(f"Empty '{cmd}' line {line!r} (try --verbose)")
            else:
                if cmd == "agi":
                    dist = "ubuntu"
                elif cmd == "yi":
                    dist = "fedora"
                else:
                    assert False
                for role in roles:
                    dist_role_packages[dist][role].extend(packages)
        else:
            logger.warning(f"Unknown 'Install' line {line!r} (try --verbose)")


def extract_ansible(
    code: MarkoCode,
    roles: T.List[str],
    role_yaml_parts: T.DefaultDict[str, T.List[str]],
) -> None:
    if not isinstance(code, marko.block.FencedCode) or code.lang != "yaml":
        logger.warning("Ansible missing yaml (try --verbose)")
        return
    yaml_part = code_text(code)
    for role in roles:
        role_yaml_parts[role].append(yaml_part)


def extract_general(doc: marko.block.Element) -> None:
    role_yaml_parts: T.DefaultDict[str, T.List[str]] = collections.defaultdict(
        list
    )
    dist_role_packages: T.Dict[str, T.DefaultDict[str, T.List[str]]] = {
        "ubuntu": collections.defaultdict(list),
        "fedora": collections.defaultdict(list),
    }

    for tag_map, keywords, para, code in extract_tagged_code(doc):
        roles = tag_map.get(":role:", [])
        if not roles:
            continue
        if "" in roles:
            print("Found empty `:role:` (try --verbose)")
            continue
        if "Ansible" in keywords:
            extract_ansible(code, roles, role_yaml_parts)
        elif "Install" in keywords:
            extract_install(
                code,
                roles,
                role_yaml_parts,
                dist_role_packages,
            )
        else:
            logger.warning(f"extract_general: bad keywords {keywords}")
    for role, yaml_parts in role_yaml_parts.items():
        yaml_path = Path(f"roles/{role}/tasks/extracted.yml")
        yaml_path.write_text("---\n" + "".join(yaml_parts))
    for dist, role_packages in dist_role_packages.items():
        for role, packages in role_packages.items():
            yaml_path = Path(f"roles/{role}/tasks/packages-{dist}.yml")
            package_step = dict(
                name=f"Install {dist} `:role:{role}` packages",
                package=dict(name=packages),
            )
            yaml_path.write_text(yaml_dump([package_step]))


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=__version__)

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="verbose",
        const=logging.DEBUG,
        help="""verbose output for debugging""",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="verbose",
        const=logging.WARNING,
        help="""suppress informational output""",
    )

    parser.add_argument("source", help="markdown source file")

    return parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()
    if args.verbose is None:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(args.verbose)

    doc = parse_markdown_doc(Path(args.source))

    if logger.isEnabledFor(logging.DEBUG):
        walk(doc)

    extract_into_files(doc)

    extract_general(doc)


if __name__ == "__main__":
    main()
