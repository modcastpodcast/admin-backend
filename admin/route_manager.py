"""
Module to take in a directory, iterate through it and create a Starlette routing map.
"""

import importlib
import inspect
from pathlib import Path
from typing import Union

from starlette.routing import Route as StarletteRoute, Mount
from nested_dict import nested_dict

from admin.route import Route

def construct_route_map_from_dict(route_dict: dict):
    route_map = []
    for mount, item in route_dict.items():
        if inspect.isclass(item):
            route_map.append(StarletteRoute(mount, item))
        else:
            route_map.append(Mount(mount, routes=construct_route_map_from_dict(item)))

    return route_map

def create_route_map():
    routes_directory = Path("admin") / "routes"

    route_dict = nested_dict()
    
    for file in routes_directory.rglob("*.py"):
        import_name = f"{str(file.parent).replace('/', '.')}.{file.stem}"
        
        route = importlib.import_module(import_name)
        
        for _member_name, member in inspect.getmembers(route):
            if inspect.isclass(member):
                if issubclass(member, Route) and member != Route:
                    member.check_parameters()

                    levels = str(file.parent).split("/")[2:]
                    
                    current_level = None
                    for level in levels:
                        if current_level is None:
                            current_level = route_dict[f"/{level}"]
                        else:
                            current_level = current_level[f"/{level}"]

                    if current_level is not None:
                        current_level[member.path] = member
                    else:
                        route_dict[member.path] = member

    route_map = construct_route_map_from_dict(route_dict.to_dict())

    return route_map