/**
 * Rockfall Early Warning and Response Coordination System
 * Client-Side Interactivity Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss flash alert messages after 6 seconds
    const flashBanners = document.querySelectorAll('.alert-banner');
    flashBanners.forEach(banner => {
        setTimeout(() => {
            banner.style.transition = 'opacity 0.5s ease';
            banner.style.opacity = '0';
            setTimeout(() => banner.remove(), 500);
        }, 6000);
    });

    // 2. Table search filtering helper
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            const targetTableId = input.getAttribute('data-table-search');
            const table = document.getElementById(targetTableId);
            if (!table) return;

            const filter = e.target.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });
});

/**
 * Quick scenario loaders for academic demonstration and viva presentations.
 * Allows instant population of sensor fields with realistic geotechnical scenarios.
 */
function loadScenario(type) {
    const rainfallInput = document.getElementById('rainfall_mm');
    const slopeInput = document.getElementById('slope_angle_deg');
    const vibrationInput = document.getElementById('vibration_intensity');
    const moistureInput = document.getElementById('soil_moisture_pct');
    const dispInput = document.getElementById('displacement_rate_mm_day');
    const rockInput = document.getElementById('rock_movement_mm');
    const geoInput = document.getElementById('geological_condition');

    if (!rainfallInput) return;

    if (type === 'normal') {
        rainfallInput.value = 14.5;
        slopeInput.value = 45.0;
        vibrationInput.value = 0.6;
        moistureInput.value = 24.0;
        dispInput.value = 0.4;
        rockInput.value = 1.1;
        geoInput.value = 'Stable Bedrock';
    } else if (type === 'medium') {
        rainfallInput.value = 72.0;
        slopeInput.value = 62.0;
        vibrationInput.value = 4.2;
        moistureInput.value = 65.0;
        dispInput.value = 6.8;
        rockInput.value = 11.5;
        geoInput.value = 'Weathered Sandstone';
    } else if (type === 'high') {
        rainfallInput.value = 148.0;
        slopeInput.value = 74.0;
        vibrationInput.value = 8.5;
        moistureInput.value = 86.0;
        dispInput.value = 22.4;
        rockInput.value = 34.0;
        geoInput.value = 'Loose Shale & Siltstone';
    } else if (type === 'extreme_rule_only') {
        // Special case: moderate general values but EXTREME vibration spike > 9 mm/s
        // Demonstrates independent rule-based backstop kicking in!
        rainfallInput.value = 25.0;
        slopeInput.value = 48.0;
        vibrationInput.value = 11.8; // critical breach
        moistureInput.value = 35.0;
        dispInput.value = 1.5;
        rockInput.value = 3.0;
        geoInput.value = 'Jointed Basalt';
    }
}
