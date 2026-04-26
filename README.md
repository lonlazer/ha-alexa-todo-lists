# HA Alexa To-do Lists
[![Validate](https://github.com/lonlazer/ha-alexa-todo-lists/actions/workflows/validate.yml/badge.svg)](https://github.com/lonlazer/ha-alexa-todo-lists/actions/workflows/validate.yml)
[![GitHub release](https://img.shields.io/github/release/lonlazer/ha-alexa-todo-lists-test?include_prereleases=&sort=semver&color=blue)](https://github.com/lonlazer/ha-alexa-todo-lists/releases/)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue)](#license)
[![issues - ha-alexa-todo-lists-test](https://img.shields.io/github/issues/lonlazer/ha-alexa-todo-lists-test)](https://github.com/lonlazer/ha-alexa-todo-lists/issues)

<div align="center">
  <img width="60%" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/todo_lists_visible.png">
</div>

This custom component for Home Assistant allows you to synchronise your Alexa To-do and ShoppingLists with Home Assistant.
It directly uses the unoffical Alexas APIs (used by the Alexa mobile app) to access the services.

Changes from Home Assistant are reflected immediately in Home Assistant.
Changes initiated from the Alexa side (echo device, alexa app) are **only pulled periodically** from the Amazon servers.
Currenly the sync interval is set to 10 minutes.

The API was reverse-engineered by intercepting the Alexa mobile app's HTTP traffic.
The API client is implemented in a separate python library `pyalexatodo` ([GitHub](https://github.com/lonlazer/pyalexatodo), [PyPI](https://pypi.org/project/pyalexatodo/)).

__Disclaimer__: This is an unofficial integration and is not created, endorsed, or supported by Amazon.

## Installation

### HACS (Home Assistant Community Store)

Ensure that you have [HACS](https://hacs.xyz/) installed.

#### Add Integration via HACS:

After you have HACS installed, you can simply click this button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=lonlazer&repository=ha-alexa-todo-lists&category=integration)

1. Click **Add**.
2. Click **Download** button on the bottom right.
3. Restart Home Assistant.
4. Configure the integration via **Settings** -> **Devices & Services**.

Alternatively, you can follow these instructions to add it:

<details>
<summary>Manually add custom repository to HACS</summary>

1. Open HACS in Home Assistant.
2. Click on the `...` in the top right corner and select **Custom repositories**.
3. Add the URL `https://github.com/lonlazer/ha-alexa-todo-lists`.
4. Set the category to **Integration** and click .
5.Search for "Alexa To-do Lists" in the HACS Integrations.
6. Click **Download**.
7. Restart Home Assistant.
8. Configure the integration via **Settings** -> **Devices & Services**.
</details>

<details>
<summary>Manual Installation</summary>

1. Copy the `custom_components/alexa_todo_lists` directory from this repository into your Home Assistant `config/custom_components/` folder.
2. Restart Home Assistant.

</details>

## Configuration

1. In Home Assistant, go to **Settings** -> **Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right corner.
3. Search for **Alexa To-do Lists** and select it.

<img width="500px" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/add_integration.png">

4. Enter your Amazon account credentials and OTP token (only authenticator apps supported, not SMS)
5. Click **Submit**.

<img width="400px" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/integration_setup.png">

6. Once added, you will see your lists in Home Assistant.

<img width="400px" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/todo_lists_visible.png">

7. You can rename the lists or manage settings by clicking the configure button on the integration.

<img width="400px" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/settings_button.png">
<img width="400px" alt="image" src="https://github.com/lonlazer/ha-alexa-todo-lists/blob/main/img/rename_lists.png">

## Contributing

Contributions are welcome! Please follow the conventional commit format prepended by a [Gitmoji](https://gitmoji.dev/) for commit messages.
Make sure everything is formatted using ruff and pytest, ty, ruff checks are passing.

You can use them as command-line tools (see [scripts/lint.sh](scripts/lint.sh)) or via their VS Code extensions. 
These checks will be enforced by CI/CD as well.

## Development Setup

To set up the local development environment and run Home Assistant locally, make sure that uv is installed.

```bash
scripts/setup.sh
scripts/develop.sh
```

## Credits
- [Alexa Devices Integration](https://www.home-assistant.io/integrations/alexa_devices/): Some parts of the code (especcialy the configuration flow) were adapted from the Alexa Devices integration.
- [aioamazondevices](https://github.com/chemelli74/aioamazondevices): This library is used for logging in and making authentified API calls to Amazon.
- [pyalexatodo](https://github.com/lonlazer/pyalexatodo): This library is used for signing in and making authentified API calls to Amazon (developed by me for this integration)

