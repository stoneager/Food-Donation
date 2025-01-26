// script.js

document.addEventListener('DOMContentLoaded', () => {
    fetchDonations();
});

function fetchDonations() {
    fetch('/donations')
        .then(response => response.json())
        .then(data => {
            const donationsContainer = document.getElementById('donations-container');
            donationsContainer.innerHTML = '';
            data.forEach(donation => {
                const donationItem = document.createElement('div');
                donationItem.classList.add('donation-item');
                donationItem.innerHTML = `
                    <h3>${donation.title}</h3>
                    <p>${donation.description}</p>
                    <!-- Add more donation details here -->
                `;
                donationsContainer.appendChild(donationItem);
            });
        })
        .catch(error => console.error('Error fetching donations:', error));
}

// script.js

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const email = loginForm.email.value;
        const password = loginForm.password.value;

        // Validate email and password
        if (!email || !password) {
            errorMessage.textContent = 'Please enter both email and password.';
            return;
        }

        // Clear error message
        errorMessage.textContent = '';

        // Submit form data (dummy implementation)
        submitLoginForm(email, password);
    });
});

function submitLoginForm(email, password) {
    // Dummy implementation (replace with actual login logic)
    console.log('Email:', email);
    console.log('Password:', password);
    // Redirect to dashboard or display success message
}
