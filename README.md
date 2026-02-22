# SyncMark

**SyncMark** is a scalable, security-focused bookmark management system built as an MVP with production-oriented architectural decisions.

The project emphasizes stateless services, secure authentication, background processing, and infrastructure readiness for horizontal scaling.

---

## Architecture Overview

### Backend
- **FastAPI (ASGI)** – Stateless REST API
- **PostgreSQL** – Relational data integrity
- **SQLAlchemy + Alembic** – ORM & migrations
- **Redis** – Rate limiting & infrastructure layer
- **Celery** – Asynchronous background processing
- **JWT (Access + Refresh Rotation)** – Authentication
- **HTTP-only Cookies** – Secure token storage
- **Dockerized services**

### Frontend
- **React (TypeScript)**
- **Redux Toolkit**
- **RTK Query (injectEndpoints pattern)** for API & server-state management

---

## Core Engineering Decisions

- Stateless backend (horizontal scaling ready)
- JWT authentication with refresh token rotation
- HTTP-only cookies to reduce XSS token exposure
- Redis-backed rate limiting (atomic counters + TTL)
- Celery-based background job processing
- Explicit many-to-many modeling (bookmarks ↔ tags)
- Soft deletion + versioning for future sync handling
- Modular monolith structure with service layer separation

---

## Background Processing (Celery)

Used for:

- Asynchronous bookmark metadata extraction
- Decoupling external HTTP calls from request lifecycle
- Retry-enabled network operations

Infrastructure supports future:

- Periodic jobs
- Search indexing
- Analytics aggregation
- Device sync reconciliation
- Queue prioritization

---

## Redis Usage

Currently:

- Per-user rate limiting
- Atomic counters with expiration windows

Designed for future:

- Bookmark list caching
- Trending scoring via sorted sets
- Distributed locking
- Session/device state tracking

---

## Authentication Model

- Short-lived access tokens
- Long-lived refresh tokens with rotation
- Server-side refresh token revocation
- Device-aware token handling
- Stateless API layer

---

## System Design

```mermaid
graph TD
    Client --> API[FastAPI]
    API --> Service[Service Layer]
    Service --> DB[(PostgreSQL)]
    API --> Redis[(Redis)]
    API --> Queue[Task Queue]
    Queue --> Worker[Celery Worker]
