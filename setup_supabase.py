#!/usr/bin/env python3
"""
Supabase Database Setup Script
This script helps you set up your Supabase database to sync with your local Flask app.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header():
    print("=" * 70)
    print("SUPABASE DATABASE SETUP FOR SUSU APP")
    print("=" * 70)

def print_instructions():
    print("\n📋 SETUP INSTRUCTIONS:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL commands below")
    print("4. Run the SQL commands")
    print("5. Test the registration process")
    print("\n" + "=" * 70)

def get_supabase_sql():
    return """
-- ==================================================
-- SUSU APP DATABASE SCHEMA
-- ==================================================

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    supabase_id UUID UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create groups table
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    cycle_size INTEGER NOT NULL,
    weekly_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'forming',
    current_cycle INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create memberships table
CREATE TABLE IF NOT EXISTS memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    joined_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    UNIQUE(user_id, group_id)
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create group_invitations table
CREATE TABLE IF NOT EXISTS group_invitations (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id),
    invited_by INTEGER REFERENCES users(id),
    invited_email VARCHAR(120) NOT NULL,
    invited_phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

-- ==================================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- ==================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_invitations ENABLE ROW LEVEL SECURITY;

-- ==================================================
-- SECURITY POLICIES
-- ==================================================

-- Users table policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = supabase_id::text);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid()::text = supabase_id::text);

CREATE POLICY "Users can insert their own profile" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = supabase_id::text);

-- Groups table policies
CREATE POLICY "Users can view groups they are members of" ON groups
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM memberships 
            WHERE group_id = groups.id 
            AND user_id = (SELECT id FROM users WHERE supabase_id = auth.uid()::text)
        )
    );

CREATE POLICY "Group creators can manage their groups" ON groups
    FOR ALL USING (created_by = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- Memberships table policies
CREATE POLICY "Users can view their memberships" ON memberships
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can join groups" ON memberships
    FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- Transactions table policies
CREATE POLICY "Users can view their transactions" ON transactions
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can create transactions" ON transactions
    FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- Group invitations table policies
CREATE POLICY "Users can view invitations they sent" ON group_invitations
    FOR SELECT USING (invited_by = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can create invitations" ON group_invitations
    FOR INSERT WITH CHECK (invited_by = (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- ==================================================
-- INDEXES FOR BETTER PERFORMANCE
-- ==================================================

CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users(supabase_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_groups_created_by ON groups(created_by);
CREATE INDEX IF NOT EXISTS idx_memberships_user_id ON memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_group_id ON memberships(group_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_group_id ON transactions(group_id);

-- ==================================================
-- VERIFICATION QUERIES
-- ==================================================

-- Check if tables were created successfully
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'groups' as table_name, COUNT(*) as row_count FROM groups
UNION ALL
SELECT 'memberships' as table_name, COUNT(*) as row_count FROM memberships
UNION ALL
SELECT 'transactions' as table_name, COUNT(*) as row_count FROM transactions
UNION ALL
SELECT 'group_invitations' as table_name, COUNT(*) as row_count FROM group_invitations;
"""

def check_environment():
    """Check if environment variables are properly set"""
    print("\n🔍 CHECKING ENVIRONMENT VARIABLES:")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:30]}...")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    if not all_good:
        print("\n⚠️  Please check your .env file and ensure all Supabase variables are set.")
        return False
    
    return True

def main():
    print_header()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print_instructions()
    
    # Print SQL commands
    print(get_supabase_sql())
    
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("\nNext steps:")
    print("1. Run the SQL commands in your Supabase SQL Editor")
    print("2. Test user registration at http://localhost:5000/auth/register")
    print("3. Check that users are created in both local and Supabase databases")
    print("\nIf you encounter any issues:")
    print("- Check the Flask app logs for error messages")
    print("- Verify your Supabase credentials in the .env file")
    print("- Ensure the SQL commands executed successfully")
    print("=" * 70)

if __name__ == "__main__":
    main() 