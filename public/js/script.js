let CSV_FILE = 'gmapsdata/8896242f-ea71-4a85-8bf4-e7ed210dddbb.csv';

// Check if there's a jobId provided in the URL query string
const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get('jobId');

if (jobId) {
    // Read the generated CSV directly from the mapped volume
    CSV_FILE = `gmapsdata/${jobId}.csv`;
}
let allData = [];
let headers = [];

const PREFERRED_ORDER = ['link', 'title', 'category', 'address', 'phone', 'website', 'emails'];

function orderHeaders(fields) {
    const ordered = [];
    const others = [];

    PREFERRED_ORDER.forEach(col => {
        if (fields.includes(col)) {
            ordered.push(col);
        }
    });

    fields.forEach(f => {
        if (!ordered.includes(f)) {
            others.push(f);
        }
    });

    return [...ordered, ...others];
}

document.addEventListener('DOMContentLoaded', () => {
    loadCSV();

    document.getElementById('searchInput').addEventListener('input', (e) => {
        filterData(e.target.value);
    });
});

function loadCSV() {
    const statsEl = document.getElementById('stats');
    statsEl.textContent = 'Loading and parsing CSV...';

    Papa.parse(CSV_FILE, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function (results) {
            headers = orderHeaders(results.meta.fields);
            allData = results.data;
            renderTable(allData);
            updateStats(allData.length, allData.length);
        },
        error: function (err) {
            statsEl.textContent = 'Error loading CSV. Make sure you are running a local server.';
            statsEl.style.color = '#ef4444';
            console.error(err);
        }
    });
}

function renderTable(data) {
    const thead = document.getElementById('tableHead');
    const tbody = document.getElementById('tableBody');

    // Render headers
    thead.innerHTML = '';
    headers.forEach(h => {
        const th = document.createElement('th');
        const div = document.createElement('div');
        div.className = 'resizable-header';
        div.textContent = formatHeader(h);
        th.appendChild(div);
        thead.appendChild(th);
    });

    const actionTh = document.createElement('th');
    const actionDiv = document.createElement('div');
    actionDiv.className = 'resizable-header';
    actionDiv.textContent = 'Actions';
    actionTh.appendChild(actionDiv);
    thead.appendChild(actionTh);

    // Render rows
    tbody.innerHTML = '';

    const displayData = data.slice(0, 1000);

    displayData.forEach((row, index) => {
        const tr = document.createElement('tr');
        // Animation stagger fallback for JS created rows
        tr.style.animationDelay = `${Math.min(index * 0.05, 0.5)}s`;

        headers.forEach(h => {
            const td = document.createElement('td');
            const val = row[h] || '';

            if ((h === 'link' || h === 'website' || h === 'reviews_link') && val && val.startsWith('http')) {
                const a = document.createElement('a');
                a.href = val;
                a.target = '_blank';
                a.textContent = 'Open Link';
                a.className = 'link-btn';
                td.appendChild(a);
            } else if (h === 'address' || h === 'complete_address' || h === 'descriptions' || h === 'about' || h === 'open_hours' || h === 'popular_times' || h === 'user_reviews') {
                const div = document.createElement('div');
                div.className = 'scrollable-content';
                if (val) {
                    try {
                        const parsed = JSON.parse(val);
                        if (typeof parsed === 'object' && parsed !== null) {
                            div.textContent = JSON.stringify(parsed, null, 2);
                            div.classList.add('json-content');
                        } else {
                            div.textContent = val;
                        }
                    } catch (e) {
                        div.textContent = val;
                    }
                }
                td.appendChild(div);
            } else if (h === 'thumbnail' || h === 'images') {
                if (val && val.startsWith('http')) {
                    const img = document.createElement('img');
                    img.src = val;
                    img.style.height = '64px';
                    img.style.border = '2px solid #111';
                    img.style.boxShadow = '4px 4px 0 #111';
                    td.appendChild(img);
                } else if (val && val.includes('http') && h === 'images') {
                    // Quick parsing of images JSON array if valid
                    try {
                        const parsed = JSON.parse(val);
                        if (Array.isArray(parsed) && parsed[0] && parsed[0].image) {
                            const img = document.createElement('img');
                            img.src = parsed[0].image;
                            img.style.height = '64px';
                            img.style.border = '2px solid #111';
                            img.style.boxShadow = '4px 4px 0 #111';
                            td.appendChild(img);
                        } else {
                            td.textContent = val;
                            td.className = 'td-truncate';
                            td.title = val;
                        }
                    } catch (e) {
                        td.textContent = val;
                        td.className = 'td-truncate';
                        td.title = val;
                    }
                } else {
                    td.textContent = val;
                    td.className = 'td-truncate';
                    td.title = val;
                }
            } else if (h === 'review_rating') {
                td.textContent = Number(val) ? Number(val).toFixed(1) : val;
                if (Number(val)) {
                    td.className = 'rating';
                } else {
                    td.className = 'td-truncate';
                }
            } else {
                td.textContent = val;
                td.className = 'td-truncate';
                td.title = val;
            }

            tr.appendChild(td);
        });

        const actionTd = document.createElement('td');
        const sheetBtn = document.createElement('button');
        sheetBtn.textContent = 'Add to Sheet';
        sheetBtn.className = 'link-btn';
        sheetBtn.style.cursor = 'pointer';
        sheetBtn.style.whiteSpace = 'nowrap';
        sheetBtn.style.border = 'none';
        sheetBtn.style.fontSize = '0.75rem';
        sheetBtn.onclick = () => fillGoogleSheet(row, sheetBtn);
        actionTd.appendChild(sheetBtn);
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
    });
}

async function fillGoogleSheet(row, btn) {
    btn.textContent = 'Sending...';
    btn.disabled = true;

    try {
        let date = new Date().toLocaleDateString('en-GB').replace(/\//g, '-');
        
        let emails = row['emails'] || '';
        if (emails && typeof emails === 'string' && emails.startsWith('[')) {
            try {
                const parsed = JSON.parse(emails);
                emails = Array.isArray(parsed) && parsed.length > 0 ? parsed.join(', ') : emails;
            } catch (e) {}
        }

        const payload = {
            date: date,
            companyName: row['title'] || '',
            pic: '',
            position: '',
            phone: row['phone'] || '',
            email: emails || '',
            country: row['country'] || row['state'] || '',
            city: row['city'] || '',
            address: row['address'] || '',
            accountExecutive: '',
            noted: row['link'] || ''
        };

        const response = await fetch('/api/sheets/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to send data to Google Sheets.');
        }

        btn.textContent = 'Added \u2713';
        btn.style.backgroundColor = '#10b981';
        btn.style.color = '#111';
    } catch (error) {
        console.error('Error:', error);
        btn.textContent = 'Error';
        btn.disabled = false;
        alert(error.message);
    }
}

function formatHeader(header) {
    if (!header) return '';
    return header.toString().replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function filterData(query) {
    if (!query) {
        renderTable(allData);
        updateStats(allData.length, allData.length);
        return;
    }

    const lowerQuery = query.toLowerCase();
    const filtered = allData.filter(row => {
        return Object.values(row).some(val =>
            String(val).toLowerCase().includes(lowerQuery)
        );
    });

    renderTable(filtered);
    updateStats(filtered.length, allData.length);
}

function updateStats(filteredCount, totalCount) {
    const statsEl = document.getElementById('stats');
    if (filteredCount === totalCount) {
        statsEl.textContent = `Showing all ${totalCount} records`;
    } else {
        statsEl.textContent = `Found ${filteredCount} matches out of ${totalCount}`;
    }
}
