# Database structure

Full column-level reference for the HealthHub schema. Every table also carries
`created` / `modified` timestamps from the shared `TimeStampedModel`.

## `accounts`

| Table | Key columns | Notes |
|---|---|---|
| `accounts_user` | `id` PK, `email` **unique**, `full_name`, `role`, `is_staff`, `is_active`, `password` | Custom user; email is the login field; `role` indexed |
| `accounts_profile` | `id` PK, `user_id` **O2O→user**, `date_of_birth`, `sex`, `height_cm`, `activity_level`, `goal` | Auto-created per user via signal |
| `accounts_healthhistoryentry` | `id` PK, `user_id` FK, `kind`, `summary`, `details`, `recorded_on` | Append-only timeline |

## `fitness`

| Table | Key columns | Notes |
|---|---|---|
| `fitness_exercise` | `id` PK, `name` **unique**, `muscle_group`, `equipment`, `instructions` | Shared library |
| `fitness_routine` | `id` PK, `owner_id` FK (**nullable** = library), `name`, `is_ai_generated` | M2M to exercises via RoutineItem |
| `fitness_routineitem` | `id` PK, `routine_id` FK, `exercise_id` FK, `order`, `sets`, `reps` | **unique(routine, exercise)** |
| `fitness_workoutlog` | `id` PK, `user_id` FK, `exercise_id` FK, `performed_at`, `sets`, `reps`, `weight_kg` | `performed_at` indexed |
| `fitness_healthreading` | `id` PK, `user_id` FK, `metric`, `value`, `recorded_at` | Index `(user, metric, recorded_at)` |

## `nutrition`

| Table | Key columns | Notes |
|---|---|---|
| `nutrition_food` | `id` PK, `name` **unique**, `calories_per_100g`, `protein_g`, `carbs_g`, `fat_g` | Per-100g macros |
| `nutrition_meallog` | `id` PK, `user_id` FK, `food_id` FK, `meal_type`, `grams`, `eaten_at` | `calories` computed |
| `nutrition_dietplan` | `id` PK, `user_id` FK, `name`, `daily_calorie_target`, `is_ai_generated` | |

## `coach`

| Table | Key columns | Notes |
|---|---|---|
| `coach_conversation` | `id` PK, `user_id` FK, `title` | |
| `coach_message` | `id` PK, `conversation_id` FK, `role`, `content`, `was_blocked`, `block_reason` | Guardrail audit trail |

## `consultations`

| Table | Key columns | Notes |
|---|---|---|
| `consultations_doctorprofile` | `id` PK, `user_id` **O2O→user** (role=doctor), `specialty`, `consultation_fee`, `is_accepting` | |
| `consultations_availabilityslot` | `id` PK, `doctor_id` FK, `starts_at`, `ends_at`, `is_booked` | **unique(doctor, starts_at)** |
| `consultations_booking` | **`id` UUID PK**, `patient_id` FK, `doctor_id` FK, `slot_id` **O2O**, `status`, `reason` | UUID so ids aren't enumerable |
| `consultations_consultationmessage` | `id` PK, `booking_id` FK, `sender_id` FK, `body` | |

## `billing`

| Table | Key columns | Notes |
|---|---|---|
| `billing_plan` | `id` PK, `name` **unique**, `price_cents`, `currency`, `interval`, `stripe_price_id` | |
| `billing_subscription` | `id` PK, `user_id` **O2O**, `plan_id` FK, `status`, `stripe_*`, `current_period_end` | |
| `billing_payment` | **`id` UUID PK**, `user_id` FK, `amount_cents`, `status`, `stripe_payment_intent_id` | UUID PK |
