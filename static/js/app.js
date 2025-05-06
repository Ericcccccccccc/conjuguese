/**
 * Portuguese Verb Conjugation Practice App
 * Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add any global event listeners or initialization code here
    
    // Example: Add fade-in animation to message boxes
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        message.style.opacity = '0';
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease-in-out';
            message.style.opacity = '1';
        }, 100);
        
        // Auto-hide messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
});