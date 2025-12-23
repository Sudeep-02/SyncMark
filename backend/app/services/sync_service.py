# from typing import List, Dict, Any, Optional
# from datetime import datetime, timezone
# from uuid import UUID

# from sqlmodel import Session, select
# from fastapi import HTTPException

# from app.schemas.sync_schema import SyncRequest, SyncResponse, BookmarkDelta, ConflictItem, FieldConflict, ServerChange
# from backend.app.models.user_model import Bookmark  # your existing model
# from app.services.bookmark_service import get_user_bookmark, validate_folder  # reuse helpers
# from app.services.tag_service import validate_tag_ids_exist, add_tags_to_bookmark, remove_tags_from_bookmark  # optional reuse


# def _now() -> datetime:
#     return datetime.now(timezone.utc)


# def _bookmark_to_dict(b: Bookmark) -> Dict[str, Any]:
#     # Return fields the client needs; exclude internal-only fields if required
#     return {
#         "id": b.id,
#         "url": b.url,
#         "title": b.title,
#         "description": b.description,
#         "favicon_url": b.favicon_url,
#         "folder_id": b.folder_id,
#         "tag_ids": [],  # we'll fetch tag ids below or if Bookmark has relationship, populate it
#         "version": b.version,
#         "last_modified_at": b.updated_at,
#         "last_modified_device": b.last_modified_device,
#         "deleted_at": b.deleted_at,
#     }


# def _get_bookmark_tag_ids(db: Session, bookmark_id: UUID) -> List[UUID]:
#     stmt = select(selectable for selectable in [])  # placeholder; implement fetch per your model
#     # Simpler: query BookmarkTagLink where bookmark_id==bookmark_id and return tag_id list
#     from app.models.tag_models import BookmarkTagLink
#     rows = db.exec(select(BookmarkTagLink.tag_id).where(BookmarkTagLink.bookmark_id == bookmark_id)).all()
#     return [r for r in rows]


# def _get_server_bookmark(db: Session, bookmark_id: UUID) -> Optional[Bookmark]:
#     return db.get(Bookmark, bookmark_id)


# def process_sync(db: Session, user_id: UUID, req: SyncRequest) -> SyncResponse:
#     """
#     Main sync workflow:
#      - Process client deltas
#      - For each delta, apply per-field merge or create new
#      - Collect accepted changes and conflicts
#      - Compute server_changes since client.last_sync_at
#     """
#     accepted = []
#     conflicts = []
#     device_id = req.device_id
#     server_time = _now()

#     # 1) Process each client delta
#     for delta in req.deltas:
#         # If tag_ids present, validate they belong to user
#         if getattr(delta, "tag_ids", None):
#             validate_tag_ids_exist(db, user_id, delta.tag_ids)

#         if delta.id is None:
#             # create new bookmark
#             bm_data = delta.dict()
#             # sanitize: remove sync-only fields
#             bm_data.pop("local_id", None)
#             bm_data.pop("version", None)
#             bm_data.pop("last_modified_at", None)
#             bm_data.pop("device_id", None)
#             bm_data.pop("deleted", None)

#             # validate folder
#             if "folder_id" in bm_data:
#                 validate_folder(db, user_id, bm_data.get("folder_id"))

#             # create
#             from app.crud.bookmark import create_bookmark as create_bookmark_crud
#             new_bm = create_bookmark_crud(db, user_id, payload=delta_to_create_payload(delta), device_id=device_id)  # helper below
#             # ensure version and last_modified fields are set
#             new_bm.version = 1
#             new_bm.last_modified_at = server_time
#             new_bm.last_modified_device = device_id
#             db.add(new_bm)
#             db.commit()
#             db.refresh(new_bm)

#             # link tags if provided
#             if delta.tag_ids:
#                 # use add_tags_to_bookmark to avoid duplicates
#                 add_tags_to_bookmark(db, user_id, new_bm.id, delta.tag_ids)

#             accepted.append({
#                 "bookmark_id": new_bm.id,
#                 "local_id": delta.local_id,
#                 "bookmark": _bookmark_to_dict(new_bm)
#             })
#             continue

#         # Existing bookmark — merge
#         bookmark = _get_server_bookmark(db, delta.id)
#         if not bookmark:
#             # server doesn't know this id — client may be confused; respond as conflict
#             conflicts.append(ConflictItem(
#                 bookmark_id=delta.id,
#                 local_id=delta.local_id,
#                 conflicts=[FieldConflict(
#                     field="__bookmark__",
#                     client_value=delta.dict(),
#                     server_value=None,
#                     server_last_modified_at=None,
#                     server_last_modified_device=None
#                 )]
#             ))
#             continue

#         # Access control
#         if bookmark.user_id != user_id:
#             conflicts.append(ConflictItem(
#                 bookmark_id=delta.id,
#                 local_id=delta.local_id,
#                 conflicts=[FieldConflict(field="__bookmark__", client_value=None, server_value="belongs_to_other_user",
#                                          server_last_modified_at=bookmark.last_modified_at,
#                                          server_last_modified_device=bookmark.last_modified_device)]
#             ))
#             continue

#         # If client sent deleted=True -> treat as delete request
#         if delta.deleted:
#             # If server has a newer change than client's last_modified_at, conflict
#             client_ts = delta.last_modified_at
#             if client_ts and bookmark.last_modified_at and bookmark.last_modified_at > client_ts:
#                 # server changed after client; create conflict so client can decide
#                 conflicts.append(ConflictItem(
#                     bookmark_id=bookmark.id,
#                     local_id=delta.local_id,
#                     conflicts=[FieldConflict(
#                         field="deleted",
#                         client_value=True,
#                         server_value=bookmark.deleted_at is not None,
#                         server_last_modified_at=bookmark.last_modified_at,
#                         server_last_modified_device=bookmark.last_modified_device
#                     )]
#                 ))
#             else:
#                 # accept delete
#                 bookmark.deleted_at = server_time
#                 bookmark.deleted_by_device = device_id
#                 bookmark.version = (bookmark.version or 0) + 1
#                 bookmark.last_modified_at = server_time
#                 bookmark.last_modified_device = device_id
#                 db.add(bookmark)
#                 db.commit()
#                 db.refresh(bookmark)
#                 accepted.append({"bookmark_id": bookmark.id, "local_id": delta.local_id, "bookmark": _bookmark_to_dict(bookmark)})
#             continue

#         # For updates: per-field compare
#         field_conflicts = []
#         applied_any = False

#         # We'll compare these fields; if changed in client, check timestamps
#         candidate_fields = ["url", "title", "description", "favicon_url", "folder_id"]
#         for field in candidate_fields:
#             client_value = getattr(delta, field)
#             if client_value is None and field not in delta.__fields_set__:
#                 # client didn't send this field -> skip
#                 continue

#             # server's last_modified_at is the bookmark-level timestamp; we might store field-level timestamps for more precise merging
#             client_ts = delta.last_modified_at
#             # Simple rule:
#             # - If server.last_modified_at > client_ts -> conflict for the field
#             # - else apply client value
#             if client_ts and bookmark.last_modified_at and bookmark.last_modified_at > client_ts:
#                 # But if the existing server value equals client value, no conflict
#                 server_value = getattr(bookmark, field)
#                 if server_value != client_value:
#                     field_conflicts.append(FieldConflict(
#                         field=field,
#                         client_value=client_value,
#                         server_value=server_value,
#                         server_last_modified_at=bookmark.last_modified_at,
#                         server_last_modified_device=bookmark.last_modified_device
#                     ))
#                 # else no change needed
#             else:
#                 # Accept client change
#                 setattr(bookmark, field, client_value)
#                 applied_any = True

#         # Tags are special: client may send tag_ids
#         if getattr(delta, "tag_ids", None) is not None:
#             # We choose to accept client's tag set if client's last_modified_at newer or equal,
#             # else mark conflict
#             client_ts = delta.last_modified_at
#             if client_ts and bookmark.last_modified_at and bookmark.last_modified_at > client_ts:
#                 # conflict: server tag set is authoritative
#                 server_tag_ids = _get_bookmark_tag_ids(db, bookmark.id)
#                 if set(server_tag_ids) != set(delta.tag_ids or []):
#                     field_conflicts.append(FieldConflict(
#                         field="tag_ids",
#                         client_value=delta.tag_ids,
#                         server_value=server_tag_ids,
#                         server_last_modified_at=bookmark.last_modified_at,
#                         server_last_modified_device=bookmark.last_modified_device
#                     ))
#             else:
#                 # apply tags: naive replace (we have separate endpoints to append/remove but for sync we accept client's full set)
#                 # Remove existing links and add new ones
#                 from app.models.tag_models import BookmarkTagLink
#                 existing_links = db.exec(select(BookmarkTagLink).where(BookmarkTagLink.bookmark_id == bookmark.id)).all()
#                 for l in existing_links:
#                     db.delete(l)
#                 for tag_id in delta.tag_ids or []:
#                     db.add(BookmarkTagLink(bookmark_id=bookmark.id, tag_id=tag_id))
#                 applied_any = True

#         # If conflicts found, collect them and do not apply bookmark-level version bump (client must resolve)
#         if field_conflicts:
#             conflicts.append(ConflictItem(bookmark_id=bookmark.id, local_id=delta.local_id, conflicts=field_conflicts))
#             # rollback any partial applied changes for this bookmark if needed (safer to refresh from DB)
#             db.rollback()
#             # reload bookmark
#             db.refresh(bookmark)
#             continue

#         # If any field applied -> bump version & timestamps
#         if applied_any:
#             bookmark.version = (bookmark.version or 0) + 1
#             bookmark.last_modified_at = server_time
#             bookmark.last_modified_device = device_id
#             db.add(bookmark)
#             db.commit()
#             db.refresh(bookmark)
#             accepted.append({"bookmark_id": bookmark.id, "local_id": delta.local_id, "bookmark": _bookmark_to_dict(bookmark)})
#         else:
#             # nothing changed; return server copy so client can sync metadata
#             accepted.append({"bookmark_id": bookmark.id, "local_id": delta.local_id, "bookmark": _bookmark_to_dict(bookmark)})

#     # 2) Finally, compute server-only changes since client.last_sync_at
#     server_changes = []
#     if req.last_sync_at:
#         # return bookmarks changed after last_sync_at for this user
#         # include created, updated, deleted items
#         stmt = select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.last_modified_at > req.last_sync_at)
#         rows = db.exec(stmt).all()
#         for r in rows:
#             bdict = _bookmark_to_dict(r)
#             # fetch tags
#             bdict["tag_ids"] = _get_bookmark_tag_ids(db, r.id)
#             server_changes.append({"bookmark_id": r.id, "bookmark": bdict})
#     else:
#         # If client never synced, optionally return all bookmarks (or none)
#         # We'll return all bookmarks for initial sync
#         stmt = select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.deleted_at.is_(None))
#         rows = db.exec(stmt).all()
#         for r in rows:
#             bdict = _bookmark_to_dict(r)
#             bdict["tag_ids"] = _get_bookmark_tag_ids(db, r.id)
#             server_changes.append({"bookmark_id": r.id, "bookmark": bdict})

#     return SyncResponse(
#         accepted=accepted,
#         conflicts=conflicts,
#         server_changes=server_changes,
#         server_time=server_time
#     )


# # helper to convert BookmarkDelta into a BookmarkCreate-like payload
# def delta_to_create_payload(delta: BookmarkDelta):
#     # avoid importing Pydantic into CRUD layer; produce a minimal object expected by create_bookmark CRUD
#     class _Tmp:
#         def __init__(self, **kwargs):
#             self.__dict__.update(kwargs)
#         def model_dump(self, exclude_unset=True):
#             # emulate Pydantic/SQLModel .model_dump used by your CRUD
#             return {
#                 k: v for k, v in self.__dict__.items() if v is not None
#             }
#     data = delta.dict()
#     # remove sync-only fields
#     data.pop("local_id", None)
#     data.pop("version", None)
#     data.pop("deleted", None)
#     data.pop("device_id", None)
#     data.pop("last_modified_at", None)
#     # This returns an object with model_dump method expected by create_bookmark
#     return _Tmp(**data)
