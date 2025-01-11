#!/usr/bin/env python3
import yaml
import re
import requests
import argparse


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
        print(f'HTTP error occurred: {status_code} - {text}')
        exit(1)


def main():
    """
    Main function to parse arguments and publish files to Outline wiki.
    """
    parser = argparse.ArgumentParser(
        description='Publish markdown files to Outline wiki.')
    parser.add_argument('--config',
                        help='Path to the configuration yaml file.',
                        default='.outline-cli.yml')
    args = parser.parse_args()

    config = load_config(args.config)

    # Required parameters
    url = config.get('url')
    if not url:
        raise ValueError('Missing URL in configuration.')
    token = config.get('token')
    if not token:
        raise ValueError('Missing token in configuration.')

    files = config.get('files')
    if not files:
        raise ValueError('Missing files in configuration.')

    for file_config in files:
        # Required parameters
        path = file_config.get('path')
        document_id = file_config.get('id')

        if not path:
            raise ValueError('Missing name in configuration.')
        if not document_id:
            raise ValueError('Missing id in configuration for file: ' + path)

        # Optional parameters
        title = config.get('title')
        append = config.get('append', False)
        publish = config.get('publish', True)
        substitutions = file_config.get('substitutions', [])

        with open(path, 'r') as file:
            content = file.read()

        # Apply substitutions if any
        content = apply_substitutions(content, substitutions)

        # Publish the file to the Outline wiki
        publish_file(url, token, document_id, title, content, append, publish)
        print(f'Published: {path} => {url}/doc/{document_id}')


if __name__ == '__main__':
    main()
