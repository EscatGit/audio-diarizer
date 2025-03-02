document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadForm = document.getElementById('upload-form');
    const audioFileInput = document.getElementById('audio-file');
    const fileNameDisplay = document.getElementById('file-name');
    const uploadSection = document.querySelector('.upload-section');
    const processingSection = document.getElementById('processing');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const transcriptContainer = document.getElementById('transcript');
    const downloadBtn = document.getElementById('download-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');
    
    // Current job info
    let currentJobId = null;
    
    // Update file name display when file is selected
    audioFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileNameDisplay.textContent = this.files[0].name;
        } else {
            fileNameDisplay.textContent = 'Seleccionar archivo...';
        }
    });
    
    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show processing section
        uploadSection.classList.add('hidden');
        processingSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        // Create form data
        const formData = new FormData(uploadForm);
        
        try {
            // Upload file
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Error al subir el archivo');
            }
            
            const data = await response.json();
            currentJobId = data.job_id;
            
            // Start polling for status
            pollJobStatus(currentJobId);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        }
    });
    
    // Poll job status
    async function pollJobStatus(jobId) {
        try {
            const response = await fetch(`/api/status/${jobId}`);
            
            if (!response.ok) {
                throw new Error('Error al obtener el estado del trabajo');
            }
            
            const data = await response.json();
            
            if (data.status === 'completed') {
                // Job completed
                showResults(data);
            } else if (data.status === 'error') {
                // Job failed
                showError(data.error || 'Error desconocido durante el procesamiento');
            } else {
                // Job still processing, poll again in 2 seconds
                setTimeout(() => pollJobStatus(jobId), 2000);
            }
            
        } catch (error) {
            console.error('Error polling status:', error);
            showError(error.message);
        }
    }
    
    // Show results
    function showResults(data) {
        processingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Format and display transcript
        const segments = data.segments || [];
        let formattedTranscript = '';
        let currentSpeaker = '';
        
        segments.forEach((segment, index) => {
            if (index === 0 || segments[index - 1].speaker !== segment.speaker) {
                formattedTranscript += `\n${segment.speaker} [${formatTime(segment.start)}]\n`;
                currentSpeaker = segment.speaker;
            }
            formattedTranscript += segment.text.trim() + ' ';
        });
        
        transcriptContainer.textContent = formattedTranscript.trim();
    }
    
    // Show error
    function showError(message) {
        processingSection.classList.add('hidden');
        errorSection.classList.remove('hidden');
        errorMessage.textContent = message;
    }
    
    // Format time in HH:MM:SS
    function formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        
        return [
            h,
            m.toString().padStart(2, '0'),
            s.toString().padStart(2, '0')
        ].filter((v, i) => v > 0 || i > 0).join(':');
    }
    
    // Download transcript
    downloadBtn.addEventListener('click', function() {
        if (currentJobId) {
            window.location.href = `/api/transcript/${currentJobId}`;
        }
    });
    
    // Try again button
    tryAgainBtn.addEventListener('click', function() {
        // Reset form
        uploadForm.reset();
        fileNameDisplay.textContent = 'Seleccionar archivo...';
        
        // Show upload section
        uploadSection.classList.remove('hidden');
        errorSection.classList.add('hidden');
    });
});
