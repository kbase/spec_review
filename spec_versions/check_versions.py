"""
Q&D Script to compare versions of a spec across the different KBase environments. You should
probably spot check (or completely check) the results.

Given a spec name, it prints out the current types in each environment and which verisons, if any,
they match in the other environments.
"""

import datetime
import math
import sys
import time

from collections import defaultdict
from workspace_client import Workspace

_URL_SUFFIX = "kbase.us/services/ws"

CI = "ci"
# don't bother with next, just devops land, way behind everything else
APPDEV = "appdev"
PROD = "prod"

URLS = {
    PROD: "https://" + _URL_SUFFIX,
    APPDEV: "https://appdev." + _URL_SUFFIX,
    CI: "https://ci." + _URL_SUFFIX,
}


def dt_from_ms_epoch(msepoch: int):
    return datetime.datetime.fromtimestamp(msepoch / 1000, datetime.timezone.utc)


def get_spec_info(mod: str, url: str):
    ws = Workspace(url)
    spec = ws.get_module_info({"mod": mod})
    typemap = ws.translate_to_MD5_types(list(spec['types'].keys()))
    return {'ver': spec['ver'], 'types': typemap}
    

def get_equivalent_types(types: dict[str, str], url: str):
    ws = Workspace(url)
    typemap = ws.translate_from_MD5_types(list(types.values()))
    return {t:  typemap[types[t]] for t in types}


def get_current_type_vers(types: list):
    ret = {}
    for t in types:
        ty, ver = t.split('-')
        ret[ty] = ver
    return ret


def no_mod(type_: str):
    return type_.split('.', 1)[1]


def pull_data(mod: str):
    ts = defaultdict(dict)
    for env in URLS:
        ts[env][env] = get_spec_info(mod, URLS[env])
    for env in URLS:
        # could merge the 2 requests into one to slightly speed things up... meh
        for env2 in (set(URLS.keys()) - set([env])):
            ts[env][env2] = get_equivalent_types(ts[env][env]['types'], URLS[env2])
    return ts


def print_data(ts):
    for env in URLS:
        ver = ts[env][env]['ver']
        print(f"{env}\tmod ver: {ver} ({dt_from_ms_epoch(ver)})")
        for env2 in (set(URLS.keys()) - set([env])):
            print(f"\tvs {env2}:")
            env2currentvers = get_current_type_vers(ts[env2][env2]['types'].keys())
            for t in ts[env][env]['types']:
                print(f"\t\t{no_mod(t)}:")
                env2vers = [x.split('-')[1] for x in ts[env][env2][t]]
                if not env2vers:
                    print(f"\t\t\t*** NO EQUIVALENT TYPES, {env} has diverged from {env2} ***")
                else:
                    suffix = ""
                    # if a type has been released and then removed (either by deleting it from
                    # the spec or using the remove_types argument when registering) there may
                    # be types returned from the translate MD5 type -> regular type step
                    # but no current type version
                    env2currentver = env2currentvers.get(t.split('-')[0])
                    if env2currentver not in env2vers:
                        suffix = (" *** NO MATCH TO CURRENT VER: "
                            + f"{env2currentver or 'No current version'} ***")
                    else:
                        env2vers = [x + "*" if x == env2currentver else x for x in env2vers]
                    print(f"\t\t\t{' '.join(env2vers)}{suffix}")
        print()


def main():
    mod = sys.argv[1]
    tstmp = math.floor(time.time() * 1000)
    print(f"Pulling data for module {mod} at {tstmp} ({dt_from_ms_epoch(tstmp)})")
    ts = pull_data(mod)
    print_data(ts)
    print("* = current version")


if __name__ == "__main__":
    main()