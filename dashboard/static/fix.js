// Auto-fix functionality for ORBIT-SEC Dashboard

async function fixVulnerability(vulnId, packageName) {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Fixing...';

    try {
        const response = await fetch(`/api/fix/${vulnId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            btn.textContent = '✓ Fixed!';
            btn.style.background = '#10b981';

            alert(`✅ Fixed ${packageName}!\n\n` +
                  `Updated: ${result.old_version} → ${result.new_version}\n` +
                  `File: ${result.file}\n` +
                  `Backup: ${result.backup}\n\n` +
                  `Refresh the page and re-scan to see updated results.`);

            // Refresh after 2 seconds
            setTimeout(() => window.location.reload(), 2000);
        } else {
            btn.textContent = 'Fix Failed';
            btn.style.background = '#dc2626';
            alert(`❌ Fix failed: ${result.error}`);
            btn.disabled = false;
        }
    } catch (error) {
        btn.textContent = 'Error';
        btn.style.background = '#dc2626';
        alert(`❌ Error: ${error.message}`);
        btn.disabled = false;
    }
}

async function fixAllVulnerabilities() {
    if (!confirm('Fix ALL vulnerabilities with available patches?\n\nThis will update your requirements files and create backups.')) {
        return;
    }

    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Fixing all...';

    try {
        const response = await fetch('/api/fix-all', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            btn.textContent = '✓ All Fixed!';
            btn.style.background = '#10b981';

            const details = result.files_updated.map(f =>
                `${f.file}: ${f.fixes_applied} fixes (backup: ${f.backup})`
            ).join('\n');

            alert(`✅ Fixed ${result.total_fixed} vulnerabilities!\n\n${details}\n\nRefresh and re-scan to see results.`);

            // Refresh after 3 seconds
            setTimeout(() => window.location.reload(), 3000);
        } else {
            btn.textContent = 'Fix Failed';
            btn.style.background = '#dc2626';
            alert(`❌ Fix failed: ${result.error}`);
            btn.disabled = false;
        }
    } catch (error) {
        btn.textContent = 'Error';
        btn.style.background = '#dc2626';
        alert(`❌ Error: ${error.message}`);
        btn.disabled = false;
    }
}
