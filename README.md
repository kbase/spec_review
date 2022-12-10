# KBase type spec review repo

This repo's purpose is to facilitate changes to a KBase type spec, mainly via stakeholder
change review and version checking.

## Folder contents

* The spec to be altered, pulled from the KBase production workspace
* A `notes.md` file containing, at least, the time the spec was retrieved and the version of
  the spec (a timestamp)
* A `specversions.txt` file containing the output of `spec_versions/check_versions.py` for the
  module (see below for instructions)

## Spec versions script

`spec_versions/check_versions.py` is a quick, dirty, and unittestless type verison checking
script that compares type versions across the KBase `prod`, `appdev`, and `ci` environments.
Assuming it runs correctly, it will flag when environments have diverged from each other for
a particular type spec. To run it, python 3.7+ is required. Example:

```
PYTHONPATH=spec_versions python spec_versions/check_versions.py KBaseGenomes
```
