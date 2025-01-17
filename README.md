# ulauncher-browser-bookmarks

> [ulauncher](https://ulauncher.io/) Extension to quickly open browser bookmarks.

❗ This extension is heavily based on [this extension](https://github.com/nortmas/chrome-bookmarks). It's published as separate extension, because the original extension is hardly maintained anymore. Special thanks to Dmitry Antonenko for developing the original extension 👏

## Demo

https://github.com/pascalbe-dev/ulauncher-browser-bookmarks/assets/26909176/c39d9610-fe8d-4e1f-89e5-cff483bd1992

## Features

- search and open browser bookmarks
  - search by single text (must be contained in the bookmark title)
  - search by multiple texts split by space (all must be contained in the bookmark title)
- supports multiple browser profiles
- supports multiple browsers 
  - Google Chrome
  - Chromium
  - Brave
  - Vivaldi

## Requirements

- [ulauncher 5](https://ulauncher.io/)
- Python > 3

## Installation

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

`https://github.com/pascalbe-dev/ulauncher-browser-bookmarks.git`

## Contribution

Please refer to [the contribution guidelines](./CONTRIBUTING.md)

## Local development

### Requirements

- `less` package installed
- `inotify-tools` package installed

### Steps

1. Clone the repo `git clone https://github.com/pascalbe-dev/ulauncher-browser-bookmarks.git`
2. Cd into the folder `cd ulauncher-browser-bookmarks`
3. Watch and deploy your extension locally for simple developing and testing in parallel `./watch-and-deploy.sh` (this will restart ulauncher without extensions and deploy this extension at the beginning and each time a file in this directory changes)
4. Check the extension log `less /tmp/ulauncher-extension.log +F`
5. Check ulauncher dev log `less /tmp/ulauncher.log +F`
