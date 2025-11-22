/**
 * Dashboard Page Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!api.getToken()) {
        window.location.href = 'index.html';
        return;
    }

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', () => {
        api.clearToken();
        window.location.href = 'index.html';
    });

    // Load user info
    loadUserInfo();

    // Load dashboard data
    loadDashboardMetrics();
    loadRecentResumes();
});

async function loadUserInfo() {
    try {
        const user = await api.getCurrentUser();
        document.getElementById('userDisplay').textContent = `${user.username} (${user.role})`;
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

async function loadDashboardMetrics() {
    try {
        const metrics = await api.getOverview();

        // Update metric cards
        document.getElementById('totalResumes').textContent = metrics.total_resumes;
        document.getElementById('totalCandidates').textContent = metrics.total_candidates;
        document.getElementById('parsedResumes').textContent = metrics.parsed_resumes;
        document.getElementById('pendingResumes').textContent = metrics.pending_resumes;

        // Update success rate
        const successRate = metrics.success_rate;
        document.getElementById('successRate').textContent = `${successRate}%`;

        // Update progress circle
        const progressCircle = document.querySelector('.progress-circle');
        progressCircle.style.background = `conic-gradient(var(--secondary-color) ${successRate}%, var(--bg-color) ${successRate}%)`;

        // Update average experience
        document.getElementById('avgExperience').textContent = metrics.avg_experience_years.toFixed(1);

    } catch (error) {
        console.error('Failed to load metrics:', error);
    }
}

async function loadRecentResumes() {
    const container = document.getElementById('recentResumes');

    try {
        const resumes = await api.listResumes(0, 5);

        if (resumes.length === 0) {
            container.innerHTML = '<p class="loading">No resumes uploaded yet.</p>';
            return;
        }

        // Create table
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Type</th>
                    <th>Uploaded</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${resumes.map(resume => `
                    <tr>
                        <td>${resume.file_name}</td>
                        <td>${resume.file_type.toUpperCase()}</td>
                        <td>${new Date(resume.uploaded_at).toLocaleDateString()}</td>
                        <td>${getStatusBadge(resume.parsing_status)}</td>
                        <td>
                            ${resume.parsing_status === 'pending'
                ? `<button class="btn btn-sm btn-primary" onclick="parseResume(${resume.id})">Parse</button>`
                : `<a href="candidate-detail.html?id=${resume.id}" class="btn btn-sm">View</a>`
            }
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.innerHTML = '';
        container.appendChild(table);

    } catch (error) {
        console.error('Failed to load resumes:', error);
        container.innerHTML = '<p class="loading">Failed to load resumes.</p>';
    }
}

function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge badge-warning">Pending</span>',
        'processing': '<span class="badge badge-info">Processing</span>',
        'completed': '<span class="badge badge-success">Completed</span>',
        'failed': '<span class="badge badge-danger">Failed</span>'
    };
    return badges[status] || status;
}

async function parseResume(id) {
    try {
        await api.parseResume(id);
        alert('Resume parsing started!');
        loadRecentResumes();
        loadDashboardMetrics();
    } catch (error) {
        alert('Failed to parse resume: ' + error.message);
    }
}
