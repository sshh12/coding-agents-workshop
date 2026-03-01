"""
tags_v2.py - Alternative tag implementation using CSV-on-experiment approach
============================================================================

This module implements the "v2" tagging system where tags are stored as a
comma-separated string directly on the experiment row (tags_csv column)
instead of in the separate experiment_tags join table.

Motivation: The original experiment_tags table approach has performance issues
when querying experiments by tag (requires JOIN). Storing tags as CSV on the
experiment row makes tag-filtered queries much simpler and faster.

See TAGS_MIGRATION_PLAN.md for the migration strategy.
See config.py ENABLE_TAGS flag to activate this module.

Status: ON HOLD - waiting for approval from product team (see Slack #ml-tools)
"""

# from fastapi import APIRouter, HTTPException, Request
# from fastapi.responses import JSONResponse
#
# # NOTE: this router uses /labels not /tags to avoid collision with v1 routes
# # in app.py. Once migration is complete, v1 routes will be removed and these
# # will be renamed to /tags.
# router = APIRouter(prefix="/api/experiments/{experiment_id}/labels", tags=["labels"])

import json
from datetime import datetime


# --- Data model helpers for CSV-based tags ---

def parse_tags_csv(tags_csv_value):
    """Parse the tags_csv column value into a list of tag strings.

    The tags_csv column stores tags as: "tag1,tag2,tag3"
    Empty string or None means no tags.
    """
    if not tags_csv_value:
        return []
    return [t.strip() for t in tags_csv_value.split(",") if t.strip()]


def serialize_tags_csv(tag_list):
    """Convert a list of tag strings back to CSV format for storage."""
    if not tag_list:
        return ""
    # deduplicate while preserving order
    seen = set()
    unique = []
    for t in tag_list:
        normalized = t.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return ",".join(unique)


def add_tag_csv(existing_csv, new_tag):
    """Add a tag to an existing CSV string. Returns updated CSV string.

    Raises ValueError if tag already exists or is invalid.
    """
    tags = parse_tags_csv(existing_csv)
    normalized = new_tag.strip().lower()
    if not normalized:
        raise ValueError("Tag cannot be empty")
    if len(normalized) > 50:
        raise ValueError("Tag too long (max 50 chars)")
    if normalized in [t.lower() for t in tags]:
        raise ValueError(f"Tag '{normalized}' already exists")
    tags.append(normalized)
    return serialize_tags_csv(tags)


def remove_tag_csv(existing_csv, tag_to_remove):
    """Remove a tag from a CSV string. Returns updated CSV string."""
    tags = parse_tags_csv(existing_csv)
    normalized = tag_to_remove.strip().lower()
    tags = [t for t in tags if t.lower() != normalized]
    return serialize_tags_csv(tags)


# --- Commented-out route handlers (to be enabled after migration) ---

# @router.post("")
# async def add_label(experiment_id: int, request: Request):
#     """Add a label (tag) to an experiment using CSV storage.
#
#     This replaces the old /tags endpoint from app.py which uses the
#     experiment_tags table. See TAGS_MIGRATION_PLAN.md step 3.
#     """
#     db = get_db()
#     try:
#         exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
#         if not exp:
#             return JSONResponse({"error": "not found"}, status_code=404)
#         body = await request.json()
#         name = body.get("name", body.get("label", body.get("tag", "")))
#         try:
#             exp.tags_csv = add_tag_csv(exp.tags_csv, name)
#         except ValueError as e:
#             return JSONResponse({"error": str(e)}, status_code=400)
#         db.commit()
#         return {"labels": parse_tags_csv(exp.tags_csv)}
#     finally:
#         db.close()

# @router.get("")
# async def get_labels(experiment_id: int):
#     """Get all labels (tags) for an experiment from CSV column.
#
#     Response format differs from v1 /tags endpoint:
#       v1 returns: [{"id": 1, "name": "foo"}, ...]
#       v2 returns: {"labels": ["foo", "bar"]}
#
#     See api_stuff/exp_helpers.py validate_tag_data() for validation logic.
#     """
#     db = get_db()
#     try:
#         exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
#         if not exp:
#             return JSONResponse({"error": "not found"}, status_code=404)
#         return {"labels": parse_tags_csv(exp.tags_csv)}
#     finally:
#         db.close()

# @router.delete("/{label_name}")
# async def remove_label(experiment_id: int, label_name: str):
#     """Remove a label from an experiment."""
#     db = get_db()
#     try:
#         exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
#         if not exp:
#             return JSONResponse({"error": "not found"}, status_code=404)
#         exp.tags_csv = remove_tag_csv(exp.tags_csv, label_name)
#         db.commit()
#         return {"labels": parse_tags_csv(exp.tags_csv)}
#     finally:
#         db.close()
