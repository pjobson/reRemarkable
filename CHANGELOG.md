# Changelog

All notable changes to this project will be documented in this file.

## 2025-08-17

### Changed
- Updated emoji picker to use `emoji` pip package instead of hardcoded emoji list
- Improved emoji search functionality with better name matching using emoji package's demojize function
- Enhanced emoji tooltips with more descriptive names
- Increased emoji picker dialog height for better browsing experience
- Set minimum height for emoji container to display more emojis without scrolling
- Removed emoji categorization for simplified single-grid display
- Added emoji package to requirements.txt

### Fixed
- Better emoji name resolution for search functionality
- Improved performance with filtered emoji list (limited to 500 emojis)
- Added fallback emoji set if emoji package fails to load

## 2025-08-16

### Added
- Updated project icon (reremarkable icon)
- Enhanced README.md documentation

### Changed
- Icon updates and improvements

## 2025-08-15

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

## 2025-08-14

### Forked
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

## 2024-04-18 [Remarkable Historical Updates]

### Fixed
- Updated self type comparison to use == instead of is

## 2023-10-15 [Remarkable Historical Updates]

### Added
- Install script that copies Remarkable to /opt
- Updated .desktop file to point to new location

### Removed
- Removed snapcraft support
- Deleted FUNDING.yml

## 2021-03-20 [Remarkable Historical Updates]

### Added
- Hide panel button for findbar panel
- Fixed issue with cancelling save operation when quitting

## 2020-11-30 to 2020-07-01 [Remarkable Historical Updates]

### Added
- Keyboard shortcuts to README.md
- Various 2020 updates

### Fixed
- tree.getiterator - update for Python 3.9+

## 2019-11-30 to 2019-10-28 [Remarkable Historical Updates] 

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

## 2018-01-03 to 2018-01-06 [Remarkable Historical Updates]

### Added
- File chooser dialog opens in current file location

### Fixed
- Hide findbar properly when escape key is pressed
- Fixed menu labels

## 2017-10-31 to 2017-11-29 [Remarkable Historical Updates]

### Changed
- Updated mathjax version
- Migrated mathjax from mathjax.org to cloudflare.com
- Updated README.md

## 2017-02-10 to 2017-07-29 [Remarkable Historical Updates]

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

## 2016-08-05 to 2017-01-21 [Remarkable Historical Updates]

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

## 2016-06-30 [v1.75]

### Added
- Initial version 1.75 release

## 2016-06-11 to 2016-06-22 [Initial Release]

### Added
- Initial commit
- Created README.md
- Basic project structure