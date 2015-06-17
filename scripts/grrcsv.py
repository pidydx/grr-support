import json
from collections import defaultdict
import time
import sys
import os

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: Input file %s was not found!' % sys.argv[1])

result_file = open(sys.argv[1], 'r')

results = json.loads(result_file.read())
result_file.close()

processed = defaultdict(list)

for item in results["items"]:
    source = item["source"]
    payload_type = item["payload_type"]
    payload = item["payload"]

    if payload_type == "FileFinderResult":
      try:
        md5 = payload["hash_entry"]["md5"]
      except KeyError:
        md5 = "" 

      try:
        stat_entry = payload["stat_entry"]
      except:
        stat_entry = {}

    if payload_type == "StatEntry":
      stat_entry = payload

    try:
      aff4path = stat_entry["aff4path"]
    except KeyError:
      aff4path = ""

    try:
      ospath = stat_entry["pathspec"]["path"]
    except KeyError:
      ospath = ""

    try:
      tskpath = stat_entry["pathspec"]["nested_path"]["path"]
    except KeyError:
      tskpath = ""

    try:
      mtime = stat_entry["st_mtime"]
    except KeyError:
      mtime = ""

    try:
      atime = stat_entry["st_atime"]
    except KeyError:
      atime = ""

    try:
      ctime = stat_entry["cr_ctime"]
    except KeyError:
      ctime = ""

    try:
      crtime = stat_entry["st_crtime"]
    except KeyError:
      crtime = ""
    
    try:
      registry_data = stat_entry["registry_data"]
    except KeyError:
      registry_data = ""  

    
    try:
      print ",".join([str(source), str(aff4path), str(ospath), str(tskpath), str(mtime), str(atime), str(ctime), str(crtime), str(registry_data)])
    except:
      print ",".join([str(source), "ERROR", "ERROR", "ERROR", str(mtime), str(atime), str(ctime), str(crtime), "ERROR"])

