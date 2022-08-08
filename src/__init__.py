""" created 9/9/2021
given a one root-folder dynamically import all
sub-folders & python files found (not recursively)
then attach each folder to a tag & use its "prefix route" as "http route"
creating a one final router including one router per folder
finally load METADATA from __init__.py & add to tags_metadata
"""


from importlib import import_module
from os import walk
from os.path import dirname, join
from pathlib import PosixPath

from fastapi import APIRouter

from .v1 import router as local_router

router = APIRouter()
tags_metadata = []

last_len = 0
for dir_path, dirs, files in walk(join(dirname(__file__), "v1")):
    if files := [i for i in files if i.endswith(".py") and i != "__init__.py"]:
        # router include & import
        for file in files:
            module_name = PosixPath(f"{dir_path}.{file}").stem
            import_module(f".v1.{module_name}", __package__)
        added_routes = len(local_router.routes) - last_len
        for added_route in local_router.routes[-added_routes:]:
            path = added_route.path
            path = path if path.startswith("/") else f"/{path}"
            added_route.path = f"/{PosixPath(dir_path).stem}{path}"
            added_route.tags = [PosixPath(dir_path).stem]
        last_len = len(local_router.routes)

        # tags metadata
        tag_route = f".v1.{PosixPath(dir_path).stem}"
        try:  # import METADATA attribute from __init__.py
            # noinspection PyUnresolvedReferences
            METADATA = import_module(tag_route, __package__).METADATA
            if type(METADATA) is not dict:
                raise AttributeError("metadata is not a dict")
            tags_metadata += [METADATA]
        except AttributeError:
            continue

# add an offset to each tag metadata
offset = "&nbsp;&nbsp;"
for tag in tags_metadata:
    tag["description"] = offset + tag["description"]

router.include_router(local_router)
