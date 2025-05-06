# Portuguese Verb Conjugation Practice App

A web application to practice Portuguese verb conjugations in various tenses.

## Features

- Practice conjugating Portuguese verbs in different tenses
- Track your progress with a history of results
- Practice sentence creation with verbs you've had difficulty with
- Customize which verbs and tenses you want to practice

## Supported Verb Tenses

- Presente
- Pretérito Perfeito
- Pretérito Imperfeito
- Subjuntivo Presente
- Subjuntivo Pretérito
- Subjuntivo Futuro

## Initial Verbs

- falar
- cantar
- comprar
- andar
- comer
- beber

## How to Run

1. Make sure you have Python installed (Python 3.6 or higher recommended)
2. Install Flask:
   ```
   pip install flask
   ```
3. Navigate to the project directory:
   ```
   cd portuguese_conjugation_app
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and go to:
   ```
   http://localhost:53210
   ```

## How to Use

1. Click "Iniciar 5 Exercícios" on the home page to start practicing
2. For each exercise, fill in the correct conjugation for each pronoun
3. Press Enter to move between fields (if the "ele/ela/você" field is empty and you press Enter, it will copy from the "eu" field)
4. After completing all exercises, you'll be prompted to create sentences with any verbs you had difficulty with
5. View your progress in the "Registros de Verbos" section
6. View your practice sentences in the "Frases Registradas" section

## Extending the App

To add more verbs, edit the `data/verbs.py` file and add new entries to the `VERBS` dictionary following the same format as the existing entries.