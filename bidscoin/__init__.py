"""
BIDScoin is a toolkit to convert and organize raw data-sets according to the Brain Imaging Data Structure (BIDS)

The basic workflow is to run these two commandline tools:

  $ bidsmapper sourcefolder bidsfolder        # This produces a study bidsmap and launches a GUI
  $ bidscoiner sourcefolder bidsfolder        # This converts your data to BIDS according to the study bidsmap

The `bids` library module can be used to build plugins and interact with bidsmaps. The `bcoin` module can be
used as a library as well from the commandline to get help and perform generic management tasks.

For more documentation see: https://bidscoin.readthedocs.io
"""

# Imports from the standard library only (as these are imported during the cli/manpage build process)
import urllib.request
import json
from pathlib import Path
from importlib import metadata
from typing import Tuple, Union, List
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
try:
    from .due import due, Doi
except ImportError:
    from due import due, Doi

# Add license metadata
__license__    = 'GNU General Public License v3 or later (GPLv3+)'
__copyright__  = '2018-2023, Marcel Zwiers'
__disclaimer__ = """\
This module and all modules in this package are part of BIDScoin (https://github.com/Donders-Institute/bidscoin).

BIDScoin is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

BIDScoin is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
"""

# Define the default paths
tutorialurl      = 'https://surfdrive.surf.nl/files/index.php/s/HTxdUbykBZm2cYM/download'
bidscoinfolder   = Path(__file__).parent
schemafolder     = bidscoinfolder/'schema'
heuristicsfolder = bidscoinfolder/'heuristics'
pluginfolder     = bidscoinfolder/'plugins'
bidsmap_template = heuristicsfolder/'bidsmap_dccn.yaml'     # Default template bidsmap TODO: make it a user setting (in $HOME)?

# Register the BIDScoin citation
due.cite(Doi('10.3389/fninf.2021.770608'), description='A toolkit to convert source data to the Brain Imaging Data Structure (BIDS)', path='bidscoin')

# Get the BIDScoin version
try:
    __version__ = metadata.version('bidscoin')
except Exception:
    with open(Path(__file__).parents[1]/'pyproject.toml', 'rb') as fid:
        __version__ = tomllib.load(fid)['project']['version']


def check_version() -> Tuple[str, Union[bool, None], str]:
    """
    Compares the BIDSCOIN version from the local metadata to the remote pypi repository

    :return:    A `(pypi version number, up-to-date-boolean, checking message)` tuple
    """

    # Check pypi for the latest version number
    try:
        stream      = urllib.request.urlopen('https://pypi.org/pypi/bidscoin/json').read()
        pypiversion = json.loads(stream)['info']['version']
    except Exception as pypierror:
        print(pypierror)
        return '', None, '(Could not check https://pypi.org/pypi/bidscoin for new BIDScoin versions)'
    if __version__.split('+')[0] != pypiversion:
        return pypiversion, False, f"NB: Your BIDScoin version is NOT up-to-date: {__version__} -> {pypiversion}"
    else:
        return pypiversion, True, 'Your BIDScoin version is up-to-date :-)'


def bidsversion() -> str:
    """
    Reads the BIDS version from the BIDS_VERSION.TXT file

    :return:    The BIDS version number
    """

    return (schemafolder/'BIDS_VERSION').read_text().strip()


def is_hidden(path: Path) -> bool:
    """
    Checks if a path is or contains a hidden rootfolder.

    :param path:    The path to be checked
    :return:        True if a part of the path starts with a '.', otherwise False
    """

    if any([p.startswith('.') for p in path.parts]):
        return True
    else:
        return False


def lsdirs(folder: Path, wildcard: str='*') -> List[Path]:
    """
    Gets all directories in a folder, ignores files

    :param folder:      The full pathname of the folder
    :param wildcard:    Simple (glob.glob) shell-style wildcards. Foldernames starting with a dot are considered hidden and will be skipped. Use '**/wildcard for recursive search'
    :return:            A list with all directories in the folder
    """

    return sorted([fname for fname in sorted(folder.glob(wildcard)) if fname.is_dir() and not is_hidden(fname.relative_to(folder))])
