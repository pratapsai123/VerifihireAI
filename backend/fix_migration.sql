-- Fix migration history inconsistency
-- Migration 0101 was applied but its dependency 0100_merge_20260427_1430 doesn't exist

-- Option 1: Delete the problematic migration record and re-apply
DELETE FROM django_migrations WHERE app = 'api' AND name = '0101_contactsubmission_assessment_assessment_mode';

-- Then run: python manage.py migrate

-- Option 2: Insert the missing dependency if it should exist
-- INSERT INTO django_migrations (app, name, applied) VALUES ('api', '0100_merge_20260427_1430', NOW());
