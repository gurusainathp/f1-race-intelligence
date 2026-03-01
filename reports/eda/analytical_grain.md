# Analytical Grain Decisions

## 1. Driver–Race Grain
One row per driver per race.
Used for race-level performance analysis and modeling.

Primary key:
- raceId
- driverId

## 2. Driver–Season Grain
One row per driver per season.
Used for consistency, form, and career progression analysis.

Primary key:
- year
- driverId

## 3. Constructor–Season Grain
One row per constructor per season.
Used for team performance and reliability analysis.

Primary key:
- year
- constructorId