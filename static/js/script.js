// static/js/script.js

// 1. Initialize Dropdown on Load
document.addEventListener('DOMContentLoaded', fetchResumes);

async function fetchResumes() {
    const select = document.getElementById('resumeSelect');
    try {
        const response = await fetch('/api/resumes');
        const data = await response.json();
        
        if (data.resumes && data.resumes.length > 0) {
            select.innerHTML = '<option value="" disabled selected>Select a Candidate...</option>';
            data.resumes.forEach(filename => {
                const option = document.createElement('option');
                option.value = filename;
                option.innerText = filename;
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option value="" disabled selected>No resumes found. Upload one!</option>';
        }
    } catch (error) {
        console.error("Error fetching resumes:", error);
        select.innerHTML = '<option value="" disabled selected>⚠️ Error loading list</option>';
    }
}

// 2. Upload Logic
async function uploadResume() {
    const fileInput = document.getElementById('resumeUpload');
    const statusDiv = document.getElementById('uploadStatus');
    
    if (!fileInput.files[0]) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    statusDiv.innerText = "⏳ Uploading & Ingesting...";
    statusDiv.style.color = "blue";

    try {
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok) {
            statusDiv.innerText = "✅ Success! Resume added.";
            statusDiv.style.color = "green";
            fileInput.value = ""; 
            await fetchResumes(); // Refresh dropdown
            document.getElementById('resumeSelect').value = data.filename; // Auto-select
        } else {
            throw new Error(data.error || "Upload failed");
        }
    } catch (error) {
        statusDiv.innerText = "❌ Error: " + error.message;
        statusDiv.style.color = "red";
    }
}

// 3. Analysis Logic (THE FIX IS HERE)
async function analyzeJob() {
    const jdText = document.getElementById("jdInput").value;
    const resumeFilename = document.getElementById("resumeSelect").value;
    
    // Validation
    if (!resumeFilename) return alert("Please select a Candidate from the dropdown.");
    if (!jdText) return alert("Please paste a Job Description.");

    // UI Elements
    const btn = document.getElementById("analyzeBtn");
    const loader = document.getElementById("loader");
    const resultsContainer = document.getElementById("resultsContainer");
    const welcomeMessage = document.getElementById("welcomeMessage");

    // Set Loading State
    btn.disabled = true;
    loader.style.display = "block"; // Force show spinner

    try {
        console.log("Sending request..."); // Debug
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                jd_text: jdText,
                resume_filename: resumeFilename 
            })
        });
        
        const data = await response.json();
        console.log("Data received:", data); // Debug - Check F12 Console if issues persist

        if (data.error) throw new Error(data.error);
        
        // Render Data
        renderResults(data);

        // FORCE VISIBILITY TOGGLE (The Fix)
        // We use direct style manipulation to override any CSS conflicts
        welcomeMessage.style.display = "none";
        resultsContainer.style.display = "block"; 

    } catch (error) {
        console.error("Analysis Error:", error);
        alert("Analysis Failed: " + error.message);
    } finally {
        // Reset UI
        btn.disabled = false;
        loader.style.display = "none";
    }
}

function renderResults(data) {
    // Score Ring
    const ring = document.getElementById("scoreRing");
    const score = Math.round(data.match_score);
    ring.innerText = score + "%";
    
    // Color Logic
    if (score >= 80) ring.style.backgroundColor = "#059669";      // Green
    else if (score >= 50) ring.style.backgroundColor = "#D97706"; // Amber
    else ring.style.backgroundColor = "#DC2626";                  // Red

    // Text Info
    document.getElementById("candidateName").innerText = data.candidate_name || "Unknown Candidate";
    document.getElementById("summaryText").innerText = data.summary || "No summary available.";

    // Helper for Tags
    const createTags = (list, type) => {
        if (!list || list.length === 0) return '<span style="color:#999; font-style:italic;">None detected</span>';
        return list.map(item => `<span class="tag ${type}">${item}</span>`).join('');
    };

    document.getElementById("matchesList").innerHTML = createTags(data.key_matches, 'match');
    document.getElementById("missingList").innerHTML = createTags(data.missing_skills, 'missing');

    // Questions
    const qList = document.getElementById("questionsList");
    if (data.interview_questions && data.interview_questions.length > 0) {
        qList.innerHTML = data.interview_questions.map(q => `
            <li>
                <strong>${q.question}</strong>
                <span class="rationale">💡 ${q.rationale}</span>
            </li>
        `).join('');
    } else {
        qList.innerHTML = '<p>No specific questions generated.</p>';
    }
}