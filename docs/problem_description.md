# IHTP — Problem Description

Competition: [Integrated Healthcare Timetabling Competition 2024](https://ihtc2024.github.io/)

## Overview

The Integrated Healthcare Timetabling Problem (IHTP) combines three subproblems:

1. **Surgical Case Planning (SCP)** — assign each patient a surgery day, operating theater.
2. **Patient Admission Scheduling (PAS)** — assign each admitted patient to a room for their length of stay.
3. **Nurse-to-Room Assignment (NRA)** — assign a nurse to each occupied room in each shift.

The three subproblems share resources (rooms, nurses, theaters) and must be solved simultaneously.

## Instance JSON Format

```
{
  "days": <int>,                    // planning horizon length
  "skill_levels": <int>,            // number of nurse skill tiers (0 = lowest)
  "shift_types": ["early","late","night"],
  "age_groups": ["infant","adult","elderly"],
  "weights": { ... },               // soft-constraint weights (see below)
  "occupants": [...],               // pre-admitted patients (fixed room, no surgery)
  "patients": [...],                // patients to schedule
  "surgeons": [...],
  "operating_theaters": [...],
  "rooms": [...],
  "nurses": [...]
}
```

### Occupant
```json
{
  "id": "a0",
  "gender": "A",             // "A" or "B"
  "age_group": "elderly",
  "length_of_stay": 4,
  "workload_produced": [3,3,1,...],   // length_of_stay * shifts_per_day values
  "skill_level_required": [1,0,0,...],
  "room_id": "r4"
}
```

### Patient
```json
{
  "id": "p00",
  "mandatory": false,
  "gender": "A",
  "age_group": "elderly",
  "length_of_stay": 3,
  "surgery_release_day": 3,     // earliest admission day
  "surgery_due_day": 7,         // mandatory patients only: latest admission day
  "surgery_duration": 120,      // minutes
  "surgeon_id": "s0",
  "incompatible_room_ids": [],  // rooms patient cannot be assigned to
  "workload_produced": [...],   // length_of_stay * shifts_per_day
  "skill_level_required": [...]
}
```
`workload_produced` and `skill_level_required` are indexed relative to admission day (shift 0 = first shift of admission day).

### Surgeon
```json
{ "id": "s0", "max_surgery_time": [0,480,0,...] }  // minutes per day (0 = unavailable)
```

### Operating Theater
```json
{ "id": "t0", "availability": [480,480,...] }  // minutes per day
```

### Room
```json
{ "id": "r0", "capacity": 2 }
```

### Nurse
```json
{
  "id": "n00",
  "skill_level": 1,
  "working_shifts": [
    { "day": 0, "shift": "early", "max_load": 12 },
    ...
  ]
}
```
A nurse is only available during listed shifts; `max_load` is the soft workload cap.

## Solution JSON Format

```json
{
  "patients": [
    { "id": "p00", "admission_day": 3, "room": "r3", "operating_theater": "t1" },
    { "id": "p01", "admission_day": "none" }   // unscheduled optional patient
  ],
  "nurses": [
    {
      "id": "n00",
      "assignments": [
        { "day": 4, "shift": "night", "rooms": ["r3"] },
        { "day": 5, "shift": "night", "rooms": [] }   // working but no room
      ]
    }
  ]
}
```

Nurses not assigned to any room in a shift can have `"rooms": []` or be omitted entirely. Unscheduled patients should have `"admission_day": "none"` (or be omitted). The optional `"costs"` key in reference solutions is informational; the validator ignores it.

## Constraints

### Hard Constraints (violations — must be zero for feasibility)

| Name | Description |
|------|-------------|
| `RoomGenderMix` | Patients of both genders in same room on same day; penalises `min(#A, #B)` per room-day |
| `PatientRoomCompatibility` | Patient assigned to an incompatible room |
| `SurgeonOvertime` | Surgeon's total surgery time exceeds `max_surgery_time` on a day |
| `OperatingTheaterOvertime` | Theater's total surgery time exceeds `availability` on a day |
| `MandatoryUnscheduledPatients` | A mandatory patient is not scheduled |
| `AdmissionDay` | Patient admitted before `surgery_release_day` or after last possible day |
| `RoomCapacity` | More patients in room than `capacity` on a day |
| `NursePresence` | Nurse assigned to a shift they are not working |
| `UncoveredRoom` | Occupied room has no assigned nurse in a shift |

### Soft Constraints (weighted costs — minimise)

| Weight key | Cost name | Description |
|------------|-----------|-------------|
| `room_mixed_age` | `RoomAgeMix` | Max age-group index difference among patients in room per day |
| `room_nurse_skill` | `RoomSkillLevel` | Sum of skill deficit (`required − nurse_skill`) per patient-shift |
| `continuity_of_care` | `ContinuityOfCare` | Number of distinct nurses per patient over stay |
| `nurse_eccessive_workload` | `ExcessiveNurseWorkload` | Workload above `max_load` per nurse per shift |
| `open_operating_theater` | `OpenOperatingTheater` | Number of (theater, day) pairs where the theater is used |
| `surgeon_transfer` | `SurgeonTransfer` | `(theaters_used − 1)` per surgeon per day when > 1 theater |
| `patient_delay` | `PatientDelay` | Days between `surgery_release_day` and actual admission |
| `unscheduled_optional` | `ElectiveUnscheduledPatients` | Count of optional patients not admitted |

## Scoring

Total score = Σ (weight × cost). Zero violations is required for a feasible solution; lower total cost is better among feasible solutions.

## Instance Scale (public dataset)

- 30 competition instances (i01–i30) + 10 test instances (test01–test10)
- Planning horizons: 2–4 weeks (14–28 days)
- 50–500 patients per instance
- 3 shift types: early, late, night

## Reference Scores (test instances)

Run `./validator/IHTP_Validator data/instances/testNN.json data/solutions/sol_testNN.json` for each reference solution. Example: test01 reference = **3177**.
