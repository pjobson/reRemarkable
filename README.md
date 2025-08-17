# reRemarkable

## Notes

1. I **suck** at Python, like I'm so terrible that one time I told an interviewer to hire someone else, because I'm that bad at it. If you're reading the source and think "Why the F would anyone do something like that?!" Rember this note. That being said, put a merge request in and I'm more than happy to bow out to an expert. 
2. This is a very spare time effort for me. I will try to fix issues when I can. I would rather have contributors with merge requests than demands.
3. This is considered an early re-release; expect, better yet demand bugs.
4. I've only *tested* this on Linux Mint 22.1 kernel 6.8.0-59-generic w/ Python 3.12.3. I use the word tested as loosely as possible, as the software runs and behaves expectedly.
5. I have no idea how well if at all this will work with other operating systems. I don't have a lab setup with a bunch of VMs right now to do extensive testing and whatnot.

## Install / Uninstall

If I'm missing anything here, please make an issue and I'll update.

### Required Packages

**DEB**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-gi \
  gir1.2-gtk-3.0 gir1.2-gtksource-3.0 gir1.2-webkit2-4.1 \
  wkhtmltopdf glib-2.0-dev
```

**DNF**

```bash
sudo dnf install python3 python3-pip python3-gobject \
  gtk3-devel gtksourceview3-devel webkit2gtk4.1-devel \
  wkhtmltopdf glib2-devel
```

**PACMAN**

```bash
sudo pacman -S python python-pip python-gobject gtk3 \
  gtksourceview3 webkit2gtk wkhtmltopdf glib2
```

### Install

This will automatically copy the repo to your `/opt` directory
and add a menu item.

```bash
# Installation
git clone git@github.com:pjobson/reRemarkable.git
./install.sh

# Uninstall
/opt/reRemarkable/uninstall.sh
```

## About

**reRemarkable** is a fork of the unfortunately abandoned
[Remarkable](https://github.com/jamiemcg/Remarkable) project.

reRemarkable is a fully featured markdown editor for Linux

You can download the latest version from the [project site](https://github.com/pjobson/reRemarkable).

![Screen Shot](https://raw.githubusercontent.com/pjobson/reRemarkable/refs/heads/master/data/media/screenshot1.png)

## Features

reRemarkable has many features including:

- Live Preview with Synchronized Scrolling
- Syntax Highlighting
- GitHub Flavored Markdown Support
- HTML and PDF Export
- MathJax Support
- Dialogs for adding images, links and tables
- Emoji picker with search functionality
- Styles
- Custom CSS Support
- Keyboard Shortcuts

## Keyboard Shortcuts

### Formatting

| Syntax                 | Key            |
| --                     | --             |
| Bold                   | `CTRL+B`       |
| Heading 1              | `CTRL+1`       |
| Heading 2              | `CTRL+2`       |
| Heading 3              | `CTRL+3`       |
| Heading 4              | `CTRL+4`       |
| Highlight              | `CTRL+SHFT+H`  |
| Insert Horizontal Rule | `CTRL+H`       |
| Insert Image           | `CTRL+SHFT+I`  |
| Insert Link            | `CTRL+L`       |
| Insert Table           | `CTRL+SHFT+T`  |
| Insert Timestamp       | `CTRL+T`       |
| Insert Emoji           | `CTRL+ALT+E`   |
| Italic                 | `CTRL+I`       |
| Strikethrough          | `CTRL+D`       |

### Actions

| Action                 | Key            |
| --                     | --             |
| Copy                   | `CTRL+C`       |
| Cut                    | `CTRL+X`       |
| Export HTML            | `CTRL+SHFT+E`  |
| Export PDF             | `CTRL+E`       |
| Find                   | `CTRL+F`       |
| Fullscreen             | `F11`          |
| New File               | `CTRL+N`       |
| Open File              | `CTRL+O`       |
| Paste                  | `CTRL+V`       |
| Quit                   | `CTRL+Q`       |
| Redo                   | `CTRL+SHFT+Z`  |
| Save File              | `CTRL+S`       |
| Save File As           | `CTRL+SHFT+S`  |
| Undo                   | `CTRL+Z`       |
| Zoom In                | `CTRL+Plus`    |
| Zoom Out               | `CTRL+Minus`   |
| Open Recent File 1     | `CTRL+ALT+1`   |
| Open Recent File 2     | `CTRL+ALT+2`   |
| Open Recent File 3     | `CTRL+ALT+3`   |
| Open Recent File 4     | `CTRL+ALT+4`   |
| Open Recent File 5     | `CTRL+ALT+5`   |
| Open Recent File 6     | `CTRL+ALT+6`   |
| Open Recent File 7     | `CTRL+ALT+7`   |
| Open Recent File 8     | `CTRL+ALT+8`   |
| Open Recent File 9     | `CTRL+ALT+9`   |
