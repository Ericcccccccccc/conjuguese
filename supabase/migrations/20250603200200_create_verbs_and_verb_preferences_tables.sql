-- Create verbs table
CREATE TABLE public.verbs (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    infinitive TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS and create permissive policies for 'verbs' table
ALTER TABLE public.verbs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all read access to verbs" ON public.verbs
FOR SELECT USING (true);

CREATE POLICY "Allow all write access to verbs" ON public.verbs
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access to verbs" ON public.verbs
FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow all delete access to verbs" ON public.verbs
FOR DELETE USING (true);

-- Create verb_preferences table
CREATE TABLE public.verb_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    verb_id INT REFERENCES public.verbs(id) ON DELETE CASCADE,
    preference_type TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS and create permissive policies for 'verb_preferences' table
ALTER TABLE public.verb_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all read access to verb_preferences" ON public.verb_preferences
FOR SELECT USING (true);

CREATE POLICY "Allow all write access to verb_preferences" ON public.verb_preferences
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access to verb_preferences" ON public.verb_preferences
FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow all delete access to verb_preferences" ON public.verb_preferences
FOR DELETE USING (true);
