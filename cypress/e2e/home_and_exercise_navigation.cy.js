describe('Homepage and Exercise Navigation', () => {
  it('should display the homepage correctly and navigate to the exercise page', () => {
    // 1. Navigate to Homepage
    cy.visit('/');

    // Expected Outcome: Page title
    cy.title().should('eq', 'Prática de Conjugação Portuguesa');

    // Expected Outcome: Main heading
    cy.get('h2').should('contain', 'Bem-vindo à Prática de Conjugação Portuguesa');

    // Expected Outcome: "Iniciar 5 Exercícios" button
    cy.get('a.btn.primary-btn')
      .should('be.visible')
      .and('have.text', 'Iniciar 5 Exercícios')
      .and('have.attr', 'href', '/start_exercises');

    // 2. Navigate to Exercise Page
    cy.get('a.btn.primary-btn').click();

    // Expected Outcome: URL change
    cy.url().should('include', '/exercise');

    // Expected Outcome: Exercise page content
    cy.get('.exercise-section h3').should('contain', 'Verbo:');
  });
});
