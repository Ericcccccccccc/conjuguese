-- Enable RLS and create permissive policies for 'results' table
ALTER TABLE public.results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all read access" ON public.results
FOR SELECT USING (true);

CREATE POLICY "Allow all write access" ON public.results
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access" ON public.results
FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow all delete access" ON public.results
FOR DELETE USING (true);
