#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from llm_ctf.challenge import get_canonical_name

ctf_db = Path(sys.argv[1]).resolve()
oci_dir = Path(sys.argv[2]).resolve()

for challenge_json in ctf_db.glob('*/*/*/*/challenge.json'):
    chaldir = challenge_json.parent
    chalname = get_canonical_name(chaldir)
    oci_link = (chaldir/chalname).with_suffix('.tar')
    oci_name = oci_link.name
    oci_matches = list(oci_dir.glob(f"**/{oci_name}"))
    if oci_matches and not oci_link.exists():
        print(f"FAIL {chaldir.relative_to(ctf_db)}: {oci_name} exists in {oci_matches} but not linked")
    elif not oci_link.exists():
        print(f"SKIP {chaldir.relative_to(ctf_db)/oci_name} not found and no matches found in OCI dir")
    else:
        print(f"PASS {chaldir.relative_to(ctf_db)}: {oci_name} -> {oci_link.resolve()}")

