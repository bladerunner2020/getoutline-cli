# GetOutline CLI

**getoutline-cli** is an unofficial command-line interface for publishing markdown files to [Outline](https://getoutline.com/).
The primary goal of this project is to automate the process of publishing markdown files to Outline in CI/CD pipelines.

It allows to publish **CHANGELOG.md**, **README.md**, or any other markdown file to an Outline wiki.

The list of files to publish is defined in the configuration file `.outline-cli.yml`.
Alternatively, you can specify configuration file using `--config` option.

## Installation and usage

```bash
pip install getoutline-cli
```

To publish markdown files to Outline, run the following command:

```bash
getoutline-cli
```

To specify the configuration file, use the `--config` option:

```bash
getoutline-cli --config some_config.yml
```

To preview the changes without publishing, use the `--preview` option:

```bash
getoutline-cli --preview
```

## Environment Variables

- `OUTLINE_API_TOKEN` - Outline API token (required if not specified in the configuration file)
- `OUTLINE_URL` - Outline URL (e.g., `https://wiki.example.com`) (required if not specified in the configuration file)

## Configuration file

The configuration file is a YAML file containing the following fields:

- `token` - Outline API token (required if not specified in the environment variables)
- `url` - Outline URL (e.g., `https://wiki.example.com`) (required if not specified in the environment variables)
- `files` - List of files to publish (required)

The `files` field is a list of dictionaries with the following fields:

- `path` - Name or path to the markdown file (required)
- `id` - Outline document ID (required)
- `title` - Title of the document in Outline (optional)
- `append` - Append content to the existing document (optional, default is `False`)
- `publish` - Publish the document after updating (optional, default is `True`)
- `substitutions` - List of substitutions to apply to the content (optional)

The `substitutions` field is a list of dictionaries `regex: replacement value`,
applied to the content of the markdown file before publishing.

### Example Configuration File

```yaml
url: https://wiki.example.com
token: YOUR_OUTLINE_API_TOKEN
files:
  - path: CHANGELOG.md
    id: YOUR_ID_1
    substitutions:
      # Remove links to git commits
      - " ?\\(\\[[a-z0-9]+\\]\\(https://git\\.example\\.com/.+\\)\\)": ""
      # Remove commits without JIRA issues (DEV-XXXX)
      - "^\\* (?!.*\\(DEV-\\d+\\)).*$\\n": ""
      # Remove empty sections
      -  "### .+\\n+": ""
  - path: README.md
    id: YOUR_ID_2
    title: README
    append: false
    publish: true
```

## Keywords

- GetOutline
- CI/CD

## Authors

- Alexander Pivovarov

## License

License under the MIT License.
