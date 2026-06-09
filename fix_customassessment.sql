-- Fix missing columns in api_customassessment table
-- Run this in your PostgreSQL database

-- Check if columns exist and add them if missing
DO $$
BEGIN
    -- Add first_name if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='api_customassessment' AND column_name='first_name'
    ) THEN
        ALTER TABLE api_customassessment ADD COLUMN first_name VARCHAR(100) NULL;
        RAISE NOTICE 'Added first_name column';
    ELSE
        RAISE NOTICE 'first_name column already exists';
    END IF;

    -- Add last_name if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='api_customassessment' AND column_name='last_name'
    ) THEN
        ALTER TABLE api_customassessment ADD COLUMN last_name VARCHAR(100) NULL;
        RAISE NOTICE 'Added last_name column';
    ELSE
        RAISE NOTICE 'last_name column already exists';
    END IF;
END $$;
