# misc api stuff that didn't fit in app.py

# NOTE: these are registered as routes in app.py via include_router
# but some of them might not be hooked up yet

from fastapi import APIRouter

router = APIRouter()

# this was going to be the experiments batch endpoint but we never finished it
# @router.post("/api/experiments/batch")
# async def batch_create():
#     pass

# placeholder for future tag endpoint
# @router.post("/api/experiments/{id}/tags")
# async def add_tags():
#     pass

# also wanted to add export but ran out of time
# @router.get("/api/experiments/{id}/export")
# async def export_experiment():
#     pass
