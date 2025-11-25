/**
 * Registration Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    // Check if already logged in
    if (api.getToken()) {
        window.location.href = 'dashboard.html';
        return;
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const role = document.getElementById('role').value;

        // Hide previous messages
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        // Validate passwords match
        if (password !== confirmPassword) {
            errorMessage.textContent = 'Passwords do not match!';
            errorMessage.style.display = 'block';
            return;
        }

        // Validate password length
        if (password.length < 6) {
            errorMessage.textContent = 'Password must be at least 6 characters long!';
            errorMessage.style.display = 'block';
            return;
        }

        try {
            // Show loading state
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Registering...';
            submitBtn.disabled = true;

            // Register
            const response = await api.register(username, email, password, role);

            // Show success message
            successMessage.textContent = 'Registration successful! Redirecting to login...';
            successMessage.style.display = 'block';

            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);

        } catch (error) {
            // Show error
            errorMessage.textContent = error.message || 'Registration failed. Please try again.';
            errorMessage.style.display = 'block';

            // Reset button
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Register';
            submitBtn.disabled = false;
        }
    });
});
