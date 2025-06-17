-- Enable RLS and create permissive policies for 'sentences' table
ALTER TABLE public.sentences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all read access" ON public.sentences
FOR SELECT USING (true);

CREATE POLICY "Allow all write access" ON public.sentences
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access" ON public.sentences
FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow all delete access" ON public.sentences
FOR DELETE USING (true);
