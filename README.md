# whereisthis
> a human language based file finder with a tui using textual!

## installation
currently, there is a macos homebrew release, and a pip version for windows and linux!

### macos
make sure you have homebrew installed (install at https://brew.sh)!

then, simple tap into the repo and install!
```sh
brew tap divpreeet/whereisthis
brew install whereisthis
```

then just type ```whereisthis``` to run!

### windows and linux
currently, the only 'easy' way to install on windows and linux is using `pip`, so make sure you have python installed!

#### create a venv 
windows - 
```sh
python -m venv venv
venv\Scripts\Activate.ps1
```

linux - 
```sh
python3 -m venv venv
source venv/bin/activate
```

then install using -
```sh
pip install whereisthis
```
and just run using ```whereisthis```!

## usage
```bash
whereisthis [query] [options]
```
both, the query and options are optional, it just helps you kickstart!

### options
- `--dir [path]` - specify the directory to search in  - `whereisthis --dir ~/Documents`, the default directory is the current directory.
- `--hidden` - search through hidden files, by default hidden files are ignored!
