document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scraperForm');
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('jobStatus');
    const viewResultsBtn = document.getElementById('viewResultsBtn');
    const jobsTbody = document.getElementById('jobsTbody');

    // Load initial jobs
    fetchJobs();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset UI
        submitBtn.disabled = true;
        submitBtn.textContent = 'DISPATCHING...';
        viewResultsBtn.style.display = 'none';

        // Build payload
        const payload = {
            name: document.getElementById('name').value,
            keywords: document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k),
            lang: document.getElementById('lang').value || 'en',
            zoom: parseInt(document.getElementById('zoom').value) || 15,
            depth: parseInt(document.getElementById('depth').value) || 1,
            max_time: parseInt(document.getElementById('max_time').value) || 3600
        };

        const lat = document.getElementById('lat').value;
        if (lat) payload.lat = lat;

        const lon = document.getElementById('lon').value;
        if (lon) payload.lon = lon;

        const radius = document.getElementById('radius').value;
        if (radius) payload.radius = parseInt(radius);

        payload.fast_mode = document.getElementById('fast_mode').checked;
        payload.email = document.getElementById('email').checked;

        try {
            statusDiv.textContent = `[SYSTEM] Submitting payload:\n${JSON.stringify(payload, null, 2)}\n\n[SYSTEM] Connecting to API...`;

            const response = await fetch('/api/v1/jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            const jobId = data.id;

            statusDiv.textContent += `\n[SUCCESS] Job dispatched. ID: ${jobId}\n[SYSTEM] Initializing polling sequence...`;

            pollJobStatus(jobId);

        } catch (error) {
            statusDiv.textContent += `\n[ERROR] ${error.message}\n[SYSTEM] Dispatch failed. Ready for retry.`;
            submitBtn.disabled = false;
            submitBtn.textContent = 'RETRY DISPATCH';
        }
    });

    async function pollJobStatus(jobId) {
        let isPolling = true;

        // Provide standard feedback during polling
        let tick = 0;
        const tickInterval = setInterval(() => {
            const dots = '.'.repeat((tick % 4) + 1);
            if (statusDiv.textContent.includes('[SYSTEM] Polling')) {
                statusDiv.textContent = statusDiv.textContent.replace(/\[SYSTEM\] Polling.*/, `[SYSTEM] Polling${dots}`);
            } else {
                statusDiv.textContent += `\n[SYSTEM] Polling${dots}`;
            }
            tick++;
        }, 1000);

        while (isPolling) {
            try {
                // Wait 5 seconds between polls
                await new Promise(r => setTimeout(r, 5000));

                const response = await fetch(`/api/v1/jobs/${jobId}`);
                if (!response.ok) throw new Error('Failed to fetch job status');

                const job = await response.json();

                if (job.status === 'completed' || job.status === 'finished') {
                    clearInterval(tickInterval);
                    isPolling = false;
                    statusDiv.textContent += `\n\n[SUCCESS] JOB COMPLETED.\n[SYSTEM] Data is ready for rendering via Viewer module.`;

                    // Show viewer button
                    viewResultsBtn.href = `viewer.html?jobId=${jobId}`;
                    viewResultsBtn.style.display = 'block';

                    // Reset form button
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'DISPATCH NEW JOB';

                    // Refresh jobs list
                    fetchJobs();
                    break;
                } else if (job.status === 'error' || job.status === 'failed') {
                    clearInterval(tickInterval);
                    isPolling = false;
                    statusDiv.textContent += `\n\n[ERROR] JOB FAILED.\n[SYSTEM] Check backend logs.`;
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'RETRY DISPATCH';

                    // Refresh jobs list anyway
                    fetchJobs();
                    break;
                }

                // If still running/pending, loop continues.

            } catch (error) {
                console.error("Polling error:", error);
                // Continue polling despite temporary network errors
            }
        }
    }

    async function fetchJobs() {
        try {
            const response = await fetch('/api/v1/jobs');
            if (!response.ok) throw new Error('Failed to fetch jobs');

            const jobs = await response.json();

            // Sort by descending date if needed, or assume API does it

            jobsTbody.innerHTML = '';

            if (!jobs || jobs.length === 0) {
                jobsTbody.innerHTML = '<tr><td colspan="6">No jobs found in the archive.</td></tr>';
                return;
            }

            jobs.forEach(job => {
                const tr = document.createElement('tr');

                const jobId = job.ID || job.id || '';
                const jobName = job.Name || job.name || 'Unnamed';
                const jobStatus = (job.Status || job.status || 'unknown').toLowerCase();
                const jobDate = job.Date || job.date;
                const jobData = job.Data || job.data || {};

                const idTd = document.createElement('td');
                idTd.textContent = jobId.substring(0, 8) + '...';
                idTd.title = jobId;

                const nameTd = document.createElement('td');
                nameTd.textContent = jobName;

                const kwTd = document.createElement('td');
                kwTd.textContent = (jobData.keywords) ? jobData.keywords.join(', ') : '';

                const dateTd = document.createElement('td');
                dateTd.textContent = jobDate ? new Date(jobDate).toLocaleString() : '';

                const statusTd = document.createElement('td');
                const span = document.createElement('span');
                span.className = `badge ${jobStatus}`;
                span.textContent = jobStatus;
                statusTd.appendChild(span);

                const actionTd = document.createElement('td');
                if (jobStatus === 'completed' || jobStatus === 'finished' || jobStatus === 'ok') {
                    const a = document.createElement('a');
                    a.href = `viewer.html?jobId=${jobId}`;
                    a.target = '_blank';
                    a.className = 'link-btn btn-sm';
                    a.textContent = 'VIEW';
                    actionTd.appendChild(a);
                } else {
                    actionTd.textContent = '-';
                }

                tr.appendChild(idTd);
                tr.appendChild(nameTd);
                tr.appendChild(kwTd);
                tr.appendChild(dateTd);
                tr.appendChild(statusTd);
                tr.appendChild(actionTd);

                jobsTbody.appendChild(tr);
            });

        } catch (error) {
            console.error("Error fetching jobs:", error);
            jobsTbody.innerHTML = '<tr><td colspan="6" style="color: red;">[SYSTEM] Error pulling archive logs. Check connection.</td></tr>';
        }
    }
});
