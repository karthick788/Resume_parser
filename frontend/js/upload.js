/**
 * Upload Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
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

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const uploadBtn = document.getElementById('uploadBtn');
    const removeFileBtn = document.getElementById('removeFile');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadMessage = document.getElementById('uploadMessage');
    const parseResult = document.getElementById('parseResult');

    let selectedFile = null;

    // Click to browse
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Remove file
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        fileInput.value = '';
        dropZone.style.display = 'flex';
        filePreview.style.display = 'none';
        uploadBtn.disabled = true;
        uploadMessage.style.display = 'none';
        parseResult.style.display = 'none';
    });

    // Upload button
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        try {
            // Show progress
            uploadProgress.style.display = 'block';
            uploadMessage.style.display = 'none';
            uploadBtn.disabled = true;
            document.getElementById('progressText').textContent = 'Uploading...';
            document.getElementById('progressFill').style.width = '30%';

            // Upload file
            const uploadResult = await api.uploadResume(selectedFile);

            document.getElementById('progressFill').style.width = '60%';
            document.getElementById('progressText').textContent = 'Parsing resume...';

            // Parse resume
            const parseResponse = await api.parseResume(uploadResult.id);

            document.getElementById('progressFill').style.width = '100%';
            document.getElementById('progressText').textContent = 'Complete!';

            // Hide progress after delay
            setTimeout(() => {
                uploadProgress.style.display = 'none';
            }, 1000);

            // Show success message
            uploadMessage.className = 'message success';
            uploadMessage.textContent = 'Resume uploaded and parsed successfully!';
            uploadMessage.style.display = 'block';

            // Show result
            displayParseResult(parseResponse);

        } catch (error) {
            uploadProgress.style.display = 'none';
            uploadMessage.className = 'message error';
            uploadMessage.textContent = 'Upload failed: ' + error.message;
            uploadMessage.style.display = 'block';
            uploadBtn.disabled = false;
        }
    });

    // Upload another
    document.getElementById('uploadAnotherBtn').addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        dropZone.style.display = 'flex';
        filePreview.style.display = 'none';
        uploadBtn.disabled = true;
        uploadMessage.style.display = 'none';
        parseResult.style.display = 'none';
    });

    function handleFile(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        if (!allowedTypes.includes(file.type)) {
            alert('Invalid file type. Please upload PDF or DOCX files.');
            return;
        }

        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File too large. Maximum size is 5MB.');
            return;
        }

        selectedFile = file;

        // Show preview
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = formatFileSize(file.size);
        dropZone.style.display = 'none';
        filePreview.style.display = 'block';
        uploadBtn.disabled = false;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }

    function displayParseResult(result) {
        const resultContent = document.getElementById('resultContent');
        const data = result.data;

        resultContent.innerHTML = `
            <div class="result-info">
                <h3>✅ Parsing Successful</h3>
                <div class="result-details">
                    <p><strong>Name:</strong> ${data.personal_info.name || 'Not found'}</p>
                    <p><strong>Email:</strong> ${data.personal_info.email || 'Not found'}</p>
                    <p><strong>Phone:</strong> ${data.personal_info.phone || 'Not found'}</p>
                    <p><strong>Skills Found:</strong> ${data.skills_count}</p>
                    <p><strong>Overall Score:</strong> ${data.score.total_score} (${data.score.grade})</p>
                </div>
            </div>
        `;

        // Set view candidate link
        document.getElementById('viewCandidateBtn').href = `candidate-detail.html?id=${result.candidate_id}`;

        parseResult.style.display = 'block';
    }
});
