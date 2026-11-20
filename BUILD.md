## Building and running MAVProxy from source with uv

These instructions use [uv](https://docs.astral.sh/uv/) to run MAVProxy
from a git checkout. uv manages the Python interpreter and dependencies
for you, so nothing is installed into your system Python.

### Install uv

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or on MacOS with Homebrew:

```
brew install uv
```

### Install MAVProxy as a command available everywhere

From the root of the MAVProxy checkout run:

```
uv tool install -e '.[recommended,cesium]' --python 3.13
uv tool update-shell
```

then open a new terminal. `uv tool update-shell` only needs to be run
once; it adds `~/.local/bin` to your PATH.

This creates an isolated virtualenv for MAVProxy (in
`~/.local/share/uv/tools/mavproxy`) and links the MAVProxy commands
into `~/.local/bin`:

 - mavproxy.py
 - MAVExplorer.py
 - mavflightview.py
 - mavpicviewer.py
 - mavvidplay.py
 - mp_slipmap.py
 - mp_tile.py

so they can be run from any directory, for example:

```
mavproxy.py --master=udp:127.0.0.1:14550 --console --map
```

Notes:

 - `-e` makes this an editable install: the commands run the code in
   your checkout, so changes to the source take effect the next time
   MAVProxy is started, without reinstalling.
 - The `recommended` extra brings in the packages used by the optional
   modules (joystick, chat, restserver, video and so on), and `cesium`
   brings in tornado for the cesium module. On MacOS the base install
   already includes wxPython, matplotlib and opencv for the console,
   map and graphs.
 - `--python 3.13` is needed because pygame (part of `recommended`)
   does not publish wheels for Python 3.14 yet. uv downloads Python
   3.13 if it is not already installed.

If you want a shorter name, add an alias to your shell startup file
(e.g. `~/.zshrc`):

```
alias mavproxy='mavproxy.py'
```

### Reinstalling and updating

Source changes need no reinstall. If the dependencies in `setup.py`
change, or the environment breaks, reinstall with:

```
uv tool install -e '.[recommended,cesium]' --python 3.13 --reinstall
```

For a completely clean reinstall:

```
uv tool uninstall mavproxy
uv tool install -e '.[recommended,cesium]' --python 3.13
```

To see what is installed and where:

```
uv tool list --show-paths
```
