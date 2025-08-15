# Changelog

All notable changes to this project will be documented in this file.

## [Recent Development] - 2025-08-15

### Added
- Emoji picker dialog with search functionality
- Emoji picker toolbar button with icon
- Emoji picker menu item with keyboard shortcut (Ctrl+Alt+E)
- Comprehensive emoji categories (Smileys & People, Animals & Nature, Food & Drink, Activities, Travel & Places, Objects, Symbols)
- Enhanced install script with colored output, error handling, and prerequisite checks
- Enhanced uninstall script with colored output and confirmation prompts
- Uninstall script
- Recent files menu option
- Screenshot

### Changed
- Converted LICENSE to markdown format (LICENSE.md)
- Updated copyright references
- Updated recent file modifiers
- Renamed project references
- Updated menu items, install script, and run script
- Updated README.md with emoji picker feature
- Corrected file paths and permissions
- Improved install/uninstall scripts with better user experience

### Fixed
- Fixed reference from rereremarkable to reremarkable

## [Recent Development] - 2025-08-14

### FORKED
- Forked from `jamiemcg/Remarkable`

### Added
- Virtual environment setup
- Requirements file
- Installation script improvements

### Changed
- Converted to virtual environment
- Clean-up of codebase
- Minor fixes and improvements

### Removed
- Removed pygtkspellcheck due to issues
- Removed AUR package
- Temporarily removed install script

## [Historical Updates] - 2024-04-18

### Fixed
- Updated self type comparison to use == instead of is

## [Historical Updates] - 2023-10-15

### Added
- Install script that copies Remarkable to /opt
- Updated .desktop file to point to new location

### Removed
- Removed snapcraft support
- Deleted FUNDING.yml

## [Historical Updates] - 2021-03-20

### Added
- Hide panel button for findbar panel
- Fixed issue with cancelling save operation when quitting

## [Historical Updates] - 2020-11-30 to 2020-07-01

### Added
- Keyboard shortcuts to README.md
- Various 2020 updates

### Fixed
- tree.getiterator - update for Python 3.9+

## [Historical Updates] - 2019-11-30 to 2019-10-28

### Added
- Snapcraft.yaml support
- Local highlightjs version
- Shortcuts for zoom-in/out

### Changed
- Updated to Webkit2
- Disabled markdown.extensions.nl2br extension
- Updated styles.py
- Properly implemented adding headings

### Fixed
- Copy to clipboard for Webkit2 WebView
- Zooming in/out functionality
- Various typos

### Removed
- Removed unused imports
- Removed feedback page

## [Historical Updates] - 2018-01-03 to 2018-01-06

### Added
- File chooser dialog opens in current file location

### Fixed
- Hide findbar properly when escape key is pressed
- Fixed menu labels

## [Historical Updates] - 2017-10-31 to 2017-11-29

### Changed
- Updated mathjax version
- Migrated mathjax from mathjax.org to cloudflare.com
- Updated README.md

## [Historical Updates] - 2017-02-10 to 2017-07-29

### Added
- Right-to-left (RTL) support under View menu
- Search & replace text functionality
- Hide/show find dialog
- Shortcuts for finding text
- Copy text from preview window
- Save zoom level and RTL settings
- Glade helper
- .gitignore file

### Changed
- Enable running from anywhere
- Easier local development from git repo

### Fixed
- CTRL+Arrow cursor control in RTL documents
- Pass arguments to remarkable
- Fix relative path image issues

## [Historical Updates] - 2016-08-05 to 2017-01-21

### Added
- GtkSourceView instead of GtkTextView
- Syntax highlighting in editor pane
- Line numbers display
- Join lines, sort lines functionality
- Horizontal layout option for editor/preview
- Image paste functionality
- Link alt-text using selected text
- Markdown tutorial

### Changed
- New launches new Remarkable process
- Open opens file in new process if file already loaded
- Updated LICENSE
- Updated desktop file

### Fixed
- Undo/redo bugs
- Saved settings being ignored
- PayPal donation page links

### Removed
- Deleted setup.py
- Deleted remarkable-1.87.egg-info

## [v1.75] - 2016-06-30

### Added
- Initial version 1.75 release

## [Initial Release] - 2016-06-11 to 2016-06-22

### Added
- Initial commit
- Created README.md
- Basic project structure