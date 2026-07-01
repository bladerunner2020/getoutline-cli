#!/usr/bin/env python3
import os
import sys
import yaml
import re
import requests
import argparse
from importlib.metadata import version, PackageNotFoundError

_RESET = '\033[0m'
_GREEN = '\033[32m'
_YELLOW = '\033[33m'
_RED = '\033[31m'
_CYAN = '\033[36m'
_WHITE = '\033[97m'
_BOLD = '\033[1m'


def _color(text, *codes):
    if not sys.stdout.isatty():
        return text
    return ''.join(codes) + text + _RESET


def load_config(config_path):
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration YAML file.

    Returns:
        dict: Configuration data.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def apply_substitutions(content, substitutions):
    """
    Apply a series of regex substitutions to the content.

    Args:
        content (str): The original content.
        substitutions (list): A list of dictionaries where keys are regex
        patterns and values are the replacements.

    Returns:
        str: The content after substitutions.
    """
    for item in substitutions:
        for pattern, replacement in item.items():
            regex = re.compile(pattern, re.MULTILINE)
            content = regex.sub(replacement, content)
    return content


TRANSLIT_MAP = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'yo',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'j',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '',
    'ы': 'y',
    'ь': '',
    'э': 'e',
    'ю': 'yu',
    'я': 'ya',
}


def transliterate_anchor(raw_fragment):
    if not raw_fragment or raw_fragment.isascii():
        return raw_fragment
    result = ''.join(TRANSLIT_MAP.get(ch, ch) for ch in raw_fragment.lower())
    return 'h-' + result


def fetch_document_url(base_url, token, document_id, cache):
    if document_id in cache:
        return cache[document_id]
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{base_url}/api/documents.info',
                             headers=headers,
                             json={'id': document_id})
    response.raise_for_status()
    doc_url = base_url.rstrip('/') + response.json()['data']['url']
    cache[document_id] = doc_url
    return doc_url


def resolve_internal_links(content, file_path, path_to_id, base_url, token,
                           url_cache):
    file_dir = os.path.dirname(file_path)

    def replace_link(match):
        original = match.group(0)
        link_path = match.group(2)
        if link_path.startswith(('http://', 'https://', '//')):
            return original
        raw_fragment = ''
        if '#' in link_path:
            link_path, raw_fragment = link_path.split('#', 1)
        fragment = transliterate_anchor(raw_fragment)
        fragment_str = f'#{fragment}' if fragment else ''
        if not link_path:
            return f'[{match.group(1)}]({fragment_str})'
        resolved = os.path.normpath(os.path.join(file_dir, link_path))
        document_id = path_to_id.get(resolved)
        if document_id is None:
            print(
                _color('Warning: no document configured', _YELLOW, _BOLD) +
                '\n' + _color(f'  link: {resolved}', _YELLOW) + '\n' +
                _color(f'  referenced in: {file_path}', _YELLOW))
            return match.group(1)
        try:
            doc_url = fetch_document_url(base_url, token, document_id,
                                         url_cache)
            return f'[{match.group(1)}]({doc_url}{fragment_str})'
        except Exception as e:
            print(
                _color(f'Warning: failed to resolve link {resolved}: {e}',
                       _YELLOW, _BOLD))
            return original

    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)


def publish_file(url, token, document_id, title, content, append, publish):
    """
    Publish the content to the Outline wiki.

    Args:
        url (str): The base URL of the Outline wiki.
        token (str): The authorization token.
        document_id (str): The ID of the document to update.
        content (str): The content to publish.

    Raises:
        requests.exceptions.HTTPError: If the HTTP request returned an
        unsuccessful status code.
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'text': content,
        'id': document_id,
        'append': append,
        'publish': publish,
        'done': True
    }
    if title:
        data['title'] = title

    response = requests.post(f'{url}/api/documents.update',
                             headers=headers,
                             json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        text = err.response.text
        print(_color(f'Error: {status_code} - {text}', _RED, _BOLD))
        exit(1)


def main():
    """
    Main function to parse arguments and publish files to Outline wiki.
    """
    try:
        pkg_version = version('getoutline-cli')
    except PackageNotFoundError:
        pkg_version = 'dev'

    parser = argparse.ArgumentParser(
        description='Publish markdown files to Outline wiki.')
    parser.add_argument('--version',
                        action='version',
                        version=f'getoutline-cli v{pkg_version}')
    parser.add_argument('--config',
                        help='Path to the configuration yaml file.',
                        default='.outline-cli.yml')
    parser.add_argument('--file',
                        help='Publish only the document with this path.',
                        metavar='PATH')
    parser.add_argument('--id',
                        help='Publish only the document with this id.',
                        metavar='ID')
    parser.add_argument('--dry-run',
                        help='Process files without publishing.',
                        action='store_true')
    parser.add_argument('--preview',
                        help='Print processed content (requires --file or --id).',
                        action='store_true')

    args = parser.parse_args()

    if args.preview and not args.file and not args.id:
        parser.error('--preview requires --file or --id')

    print(_color(f'getoutline-cli v{pkg_version}', _CYAN, _BOLD))

    config = load_config(args.config)

    url = config.get('url') or os.getenv('OUTLINE_URL')
    if not url:
        raise ValueError('Outline URL is required either in the configuration '
                         'file (field `url`) or as an environment variable '
                         '`OUTLINE_URL`.')

    token = config.get('token') or os.getenv('OUTLINE_API_TOKEN')
    if not token:
        raise ValueError(
            'Outline API token is required either in the configuration file '
            '(field `token`) or as an environment variable '
            '`OUTLINE_API_TOKEN.`')

    files = config.get('files')
    if not files:
        raise ValueError('Missing files in configuration.')

    if args.file:
        files = [fc for fc in files if fc.get('path') == args.file]
        if not files:
            raise ValueError(f'No document configured for path: {args.file}')
    elif args.id:
        files = [fc for fc in files if fc.get('id') == args.id]
        if not files:
            raise ValueError(f'No document configured for id: {args.id}')

    global_substitutions = config.get('substitutions', [])

    path_to_id = {
        os.path.normpath(fc['path']): fc['id']
        for fc in config.get('files', []) if fc.get('path') and fc.get('id')
    }
    url_cache = {}

    for file_config in files:
        path = file_config.get('path')
        document_id = file_config.get('id')

        if not path:
            raise ValueError('Missing name in configuration.')
        if not document_id:
            raise ValueError('Missing id in configuration for file: ' + path)

        title = config.get('title')
        append = config.get('append', False)
        publish = config.get('publish', True)
        substitutions = global_substitutions + file_config.get(
            'substitutions', [])

        try:
            with open(path, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            print(_color(f'Error: file not found — {path}', _RED, _BOLD))
            continue

        content = resolve_internal_links(content, path, path_to_id, url, token,
                                         url_cache)
        content = apply_substitutions(content, substitutions)

        if args.preview:
            print(_color(f'Preview: ', _CYAN, _BOLD) + _color(path, _WHITE) +
                  f' => {url}/doc/{document_id}')
            print(content)
        elif args.dry_run:
            print(
                _color('Dry run: ', _CYAN, _BOLD) + _color(path, _WHITE) +
                f' => {url}/doc/{document_id}')
        else:
            publish_file(url, token, document_id, title, content, append,
                         publish)
            print(
                _color('Published: ', _GREEN, _BOLD) + _color(path, _WHITE) +
                f' => {url}/doc/{document_id}')


if __name__ == '__main__':
    main()
