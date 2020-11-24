## MANIFESTO: a simple Python3 script to create manifest files
This Python3 script creates a tab-separated manifest file needed for data uploads to certain public repositories. The script mimics the functionality of this shell script [github.com/EMBL-EBI-GCA/gca-tools/tree/master/submissions](https://github.com/EMBL-EBI-GCA/gca-tools/tree/master/submissions)

with the following adaptations:
- multithreaded: `--jobs [JOBS]: Number of jobs to run in parallel. Default: 8`
  - note: traversing folder hierarchies and computing checksums is usually I/O limited, in particular on network file systems
- follow symbolic links pointing to directories: `--follow-linked-dirs: Follow sym linked directories. Default: False`
  - note: symbolic links pointing to files are always resolved
- self-awareness: by default, the current working directory is taken as entry point for creating the manifest file, but `make_manifest.py` will be ignored

### Usage
Place the `make_manifest.py` script in the directory that contains all files or symbolic links to files or symbolic links to other directories --- requires option `--follow-linked-dirs` --- that are part of the data upload, make it executable `chmod u+x make_manifest.py` and execute it `./make_manifest.py` (the script looks for the `python3` executable in your shell environment). By default, `make_manifest.py` is going to use the current directory name as output file name for the manifest file: `MANIFEST_ + DIR_NAME + .tsv`. You can specify an manifest file name via `--manifest`.

### Output
The output file is a tab-separated text file with three columns:
1. relative file path starting at the current working directory, or starting at the last component of the path specified via `--path`
2. file size in bytes
3. file MD5 checksum

### System requirements
1. Python3 (executable via calling `python3`)
2. `md5sum` command line tool
