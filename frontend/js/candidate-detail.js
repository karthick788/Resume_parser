/**
 * Candidate Detail Page Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!api.getToken()) {
        window.location.href = 'index.html';
        return;
    }

    // Get candidate ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const candidateId = urlParams.get('id');

    if (!candidateId) {
        showError('No candidate ID provided');
        return;
    }

    // Load candidate details
    await loadCandidateDetails(candidateId);

    // Setup event listeners
    setupEventListeners(candidateId);
});

/**
 * Load candidate details from API
 */
async function loadCandidateDetails(candidateId) {
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const candidateDetails = document.getElementById('candidateDetails');

    try {
        loadingState.style.display = 'block';
        errorState.style.display = 'none';
        candidateDetails.style.display = 'none';

        // Fetch candidate data
        const candidate = await api.getCandidate(candidateId);

        // Display candidate details
        displayCandidateDetails(candidate);

        loadingState.style.display = 'none';
        candidateDetails.style.display = 'block';

    } catch (error) {
        console.error('Error loading candidate:', error);
        showError(error.message || 'Failed to load candidate details');
        loadingState.style.display = 'none';
    }
}

/**
 * Display candidate details in the UI
 */
function displayCandidateDetails(candidate) {
    // Personal Information
    document.getElementById('candidateName').textContent = candidate.name || '-';
    document.getElementById('candidateEmail').textContent = candidate.email || '-';
    document.getElementById('candidatePhone').textContent = candidate.phone || '-';
    document.getElementById('candidateLocation').textContent = candidate.location || '-';

    // Professional Summary
    const summary = candidate.summary || candidate.professional_summary || '-';
    document.getElementById('candidateSummary').textContent = summary;

    // Skills
    displaySkills(candidate.skills || []);

    // Experience
    displayExperience(candidate.experience || []);

    // Education
    displayEducation(candidate.education || []);

    // Certifications
    displayCertifications(candidate.certifications || []);

    // Resume Score
    const score = candidate.resume_score || candidate.score || 0;
    document.getElementById('resumeScore').textContent = score;
}

/**
 * Display skills as badges
 */
function displaySkills(skills) {
    const container = document.getElementById('candidateSkills');

    if (!skills || skills.length === 0) {
        container.innerHTML = '<p>No skills found</p>';
        return;
    }

    container.innerHTML = skills.map(skill => {
        const skillName = typeof skill === 'string' ? skill : skill.name;
        return `<span class="badge badge-info">${skillName}</span>`;
    }).join(' ');
}

/**
 * Display work experience
 */
function displayExperience(experience) {
    const container = document.getElementById('candidateExperience');

    if (!experience || experience.length === 0) {
        container.innerHTML = '<p>No experience found</p>';
        return;
    }

    container.innerHTML = experience.map(exp => `
        <div class="experience-item">
            <h3>${exp.title || exp.position || 'Position'}</h3>
            <p class="company">${exp.company || 'Company'}</p>
            <p class="duration">${exp.duration || exp.start_date + ' - ' + (exp.end_date || 'Present')}</p>
            ${exp.description ? `<p class="description">${exp.description}</p>` : ''}
        </div>
    `).join('');
}

/**
 * Display education
 */
function displayEducation(education) {
    const container = document.getElementById('candidateEducation');

    if (!education || education.length === 0) {
        container.innerHTML = '<p>No education found</p>';
        return;
    }

    container.innerHTML = education.map(edu => `
        <div class="education-item">
            <h3>${edu.degree || 'Degree'}</h3>
            <p class="institution">${edu.institution || edu.school || 'Institution'}</p>
            <p class="year">${edu.year || edu.graduation_year || ''}</p>
            ${edu.gpa ? `<p class="gpa">GPA: ${edu.gpa}</p>` : ''}
        </div>
    `).join('');
}

/**
 * Display certifications
 */
function displayCertifications(certifications) {
    const container = document.getElementById('candidateCertifications');

    if (!certifications || certifications.length === 0) {
        container.innerHTML = '<p>No certifications found</p>';
        return;
    }

    container.innerHTML = certifications.map(cert => {
        const certName = typeof cert === 'string' ? cert : cert.name;
        const certIssuer = typeof cert === 'object' ? cert.issuer : '';
        const certYear = typeof cert === 'object' ? cert.year : '';

        return `
            <div class="certification-item">
                <h4>${certName}</h4>
                ${certIssuer ? `<p class="issuer">${certIssuer}</p>` : ''}
                ${certYear ? `<p class="year">${certYear}</p>` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Setup event listeners
 */
function setupEventListeners(candidateId) {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        try {
            await api.logout();
        } catch (error) {
            console.error('Logout error:', error);
        }
        api.clearToken();
        window.location.href = 'index.html';
    });

    // Edit button
    document.getElementById('editBtn').addEventListener('click', () => {
        // TODO: Implement edit functionality
        alert('Edit functionality coming soon!');
    });

    // Delete button
    document.getElementById('deleteBtn').addEventListener('click', async () => {
        if (!confirm('Are you sure you want to delete this candidate?')) {
            return;
        }

        try {
            await api.deleteCandidate(candidateId);
            alert('Candidate deleted successfully!');
            window.location.href = 'candidates.html';
        } catch (error) {
            alert('Failed to delete candidate: ' + error.message);
        }
    });
}

/**
 * Show error message
 */
function showError(message) {
    const errorState = document.getElementById('errorState');
    errorState.textContent = message;
    errorState.style.display = 'block';
}
