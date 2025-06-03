describe('Exercise Submission Flow', () => {
    beforeEach(() => {
        // Start a new exercise session
        cy.visit('/start_exercises');
        // Ensure we are on the exercise page
        cy.url().should('include', '/exercise');

        // Access correct conjugations from the global JavaScript variable
        cy.window().then((win) => {
            const correctConjugations = win.correctConjugations;
            cy.wrap(correctConjugations).as('correctConjugations'); // Alias for use in tests
        });
    });

    it('Scenario 1: Successful Exercise Submission (All Correct)', () => {
        cy.get('@correctConjugations').then((answers) => {
            // Input correct conjugations
            cy.get('.conjugation-input').eq(0).type(answers[0]); // eu
            cy.get('.conjugation-input').eq(1).type(answers[1]); // ele
            cy.get('.conjugation-input').eq(2).type(answers[2]); // nós
            cy.get('.conjugation-input').eq(3).type(answers[3]); // eles

            // Click "Verificar"
            cy.get('.btn.primary-btn').contains('Verificar').click();

            // Assert URL change to results page
            cy.url().should('include', '/exercise_results');

            // Assert success message is visible
            cy.get('.success-message').should('be.visible').and('contain', 'Parabéns! Todas as conjugações estão corretas.');

            // Assert "Próximo Exercício" button is visible
            cy.get('.form-actions .primary-btn').should('be.visible').and('contain', 'Próximo Exercício');
        });
    });

    it('Scenario 2: Exercise Submission with Errors', () => {
        cy.get('@correctConjugations').then((answers) => {
            // Input some incorrect conjugations
            cy.get('.conjugation-input').eq(0).type('incorrecto'); // eu (incorrect)
            cy.get('.conjugation-input').eq(1).type(answers[1]); // ele (correct)
            cy.get('.conjugation-input').eq(2).type('errado'); // nós (incorrect)
            cy.get('.conjugation-input').eq(3).type(answers[3]); // eles (correct)

            // Click "Verificar"
            cy.get('.btn.primary-btn').contains('Verificar').click();

            // Assert URL change to results page
            cy.url().should('include', '/exercise_results');

            // Assert error message is visible
            cy.get('.error-message').should('be.visible').and('contain', 'Algumas conjugações precisam de correção. Revise os erros acima.');

            // Assert incorrect answers are marked and corrections are visible
            cy.get('.result-row').eq(0).find('.user-answer.incorrect').should('be.visible').and('contain', 'incorrecto');
            cy.get('.result-row').eq(0).find('.correction').should('be.visible').and('contain', `→ ${answers[0]}`);

            cy.get('.result-row').eq(2).find('.user-answer.incorrect').should('be.visible').and('contain', 'errado');
            cy.get('.result-row').eq(2).find('.correction').should('be.visible').and('contain', `→ ${answers[2]}`);

            // Assert correct answers are marked as correct
            cy.get('.result-row').eq(1).find('.user-answer.correct').should('be.visible').and('contain', answers[1]);
            cy.get('.result-row').eq(3).find('.user-answer.correct').should('be.visible').and('contain', answers[3]);

            // Assert "Próximo Exercício" button is visible
            cy.get('.form-actions .primary-btn').should('be.visible').and('contain', 'Próximo Exercício');
        });
    });
});
