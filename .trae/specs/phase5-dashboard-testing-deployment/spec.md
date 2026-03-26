# Phase 5: Dashboard, Testing & Deployment Spec

## Why
Phase 5 completes the MVP by adding real-time capabilities through WebSocket, enhancing the dashboard with role-based views and live data, adding comprehensive test coverage, and ensuring production-ready deployment configuration.

## What Changes
- WebSocket endpoint for real-time updates (delivery, alerts, trust scores, grievances)
- Enhanced Dashboard with role-based views and API data integration
- Backend test suite with unit and integration tests
- Frontend test setup with component tests
- Documentation (README.md, API usage guide)
- Verify and enhance Docker configuration for production

## Impact
- Affected specs: Dashboard, WebSocket, Testing infrastructure
- Affected code: 
  - Backend: main.py, new websocket.py, tests/
  - Frontend: Dashboard.tsx, hooks/useWebSocket.ts, __tests__/

## ADDED Requirements

### Requirement: WebSocket Real-Time Updates
The system SHALL provide WebSocket support for real-time data updates.

#### Scenario: Connection established
- **WHEN** client connects to `/ws` endpoint
- **THEN** connection is established and client receives connection confirmation

#### Scenario: Real-time delivery update
- **WHEN** delivery status changes
- **THEN** connected clients receive `delivery_update` event with new status

#### Scenario: Alert notification
- **WHEN** new alert is generated
- **THEN** connected clients receive `alert_new` event

### Requirement: Role-Based Dashboard Views
The system SHALL display dashboard content based on user role.

#### Scenario: State Admin views dashboard
- **WHEN** user with STATE_ADMIN role views dashboard
- **THEN** state-wide metrics and district breakdowns are displayed

#### Scenario: District Admin views dashboard
- **WHEN** user with DISTRICT_ADMIN role views dashboard
- **THEN** district-specific metrics and block breakdowns are displayed

#### Scenario: AWW views dashboard
- **WHEN** user with AWW role views dashboard
- **THEN** center-specific delivery schedule and stock levels are displayed

### Requirement: Backend Test Suite
The system SHALL have comprehensive backend tests.

#### Scenario: Unit tests pass
- **WHEN** pytest runs
- **THEN** all unit tests for agents, services, and utils pass

#### Scenario: Integration tests pass
- **WHEN** pytest runs integration tests
- **THEN** API endpoints and database operations are verified

### Requirement: Frontend Test Setup
The system SHALL have frontend testing infrastructure.

#### Scenario: Component tests run
- **WHEN** vitest runs
- **THEN** component tests execute and pass

### Requirement: Documentation
The system SHALL have complete documentation.

#### Scenario: README exists
- **WHEN** developer reads README.md
- **THEN** project setup and run instructions are clear

#### Scenario: API documentation accessible
- **WHEN** developer accesses /docs endpoint
- **THEN** OpenAPI documentation is available

## MODIFIED Requirements

### Requirement: Enhanced Dashboard
The existing Dashboard SHALL be enhanced with:
- Real API data from backend endpoints
- Role-based content filtering
- Real-time updates via WebSocket
- Widgets for recommendations, compliance, and forecasts

## REMOVED Requirements
None - all additions are incremental.
