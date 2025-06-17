-- Enable RLS and create permissive policies for 'preferences' table
ALTER TABLE public.preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all read access" ON public.preferences
FOR SELECT USING (true);

CREATE POLICY "Allow all write access" ON public.preferences
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access" ON public.preferences
FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow all delete access" ON public.preferences
FOR DELETE USING (true);
