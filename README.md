# About

**fetchcommandwrapper** combines
download tool [aria2](https://aria2.github.io/)
with variable `GENTOO_MIRRORS`
to speed up distfile downloads of [Portage](https://wiki.gentoo.org/wiki/Portage)
by downloading from multiple mirrors at the same time.
**fetchcommandwrapper** integrates with Portage
through variables `FETCHCOMMAND` (and `RESUMECOMMAND`), hence the name.


# Installation

## System-wide installation in Gentoo

```console
# sudo emerge -av app-portage/fetchcommandwrapper
```
You can then append line `source /usr/share/fetchcommandwrapper/make.conf`
to file `/etc/portage/make.conf` to ease integration with Portage.


## Development from a Git clone

```console
# pip install --user --editable .
```
