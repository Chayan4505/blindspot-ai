import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://cauhevaqfmqprdgfsikl.supabase.co';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNhdWhldmFxZm1xcHJkZ2ZzaWtsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1MDUxMzQsImV4cCI6MjA5MjA4MTEzNH0.lq5iWeZrqAv-KKF_Nu6IveEC9pQ7MrmR8vAGQSHfo7c';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
