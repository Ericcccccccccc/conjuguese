-- Create the 'results' table
CREATE TABLE public.results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    verb text NOT NULL,
    tense text NOT NULL,
    pronoun text NOT NULL,
    user_answer text,
    is_correct boolean,
    timestamp timestamp with time zone DEFAULT now()
);

-- Create the 'sentences' table
CREATE TABLE public.sentences (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    verb text NOT NULL,
    tense text NOT NULL,
    pronoun text NOT NULL,
    correct_form text NOT NULL,
    sentence text NOT NULL,
    is_correct boolean,
    timestamp timestamp with time zone DEFAULT now()
);

-- Create the 'preferences' table
CREATE TABLE public.preferences (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    verb text NOT NULL,
    tense text NOT NULL,
    never_show boolean DEFAULT FALSE,
    always_show boolean DEFAULT FALSE,
    show_primarily boolean DEFAULT FALSE,
    UNIQUE (user_id, verb, tense)
);
