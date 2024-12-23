document.addEventListener('DOMContentLoaded', () => {
    const manualPartNumberInput = document.getElementById('part-number');
    const manualCheckbox = document.getElementById('manual-checkbox');
    const manualPartNumberGroup = document.getElementById('manual-part-number-group');
    const dropdownPartNumberGroup = document.getElementById('dropdown-part-number-group');
    const partNumberSelect = document.getElementById('part-number-select');
    const refreshPartsButton = document.getElementById('refresh-parts');
    const leftWeldInput = document.getElementById('expected-left-welds');
    const rightWeldInput = document.getElementById('expected-right-welds');
    const totalWeldDisplay = document.getElementById('total-welds');
    var url_prefix = document.getElementById('index-form').action

    const toggleManualEntry = () => {
        if (manualCheckbox.checked) {
            manualPartNumberInput.name = 'part_number';
            partNumberSelect.removeAttribute('name');
            manualPartNumberGroup.classList.remove('hidden');
            dropdownPartNumberGroup.classList.add('hidden');
        } else {
            partNumberSelect.name = 'part_number';
            manualPartNumberInput.removeAttribute('name');
            manualPartNumberGroup.classList.add('hidden');
            dropdownPartNumberGroup.classList.remove('hidden');
        }
    };

    const fetchParts = () => {
        fetch(url_prefix + '/api/parts')
            .then(response => response.json())
            .then(data => {
                partNumberSelect.innerHTML = '<option value="" disabled selected>-- Select Part Number --</option>';
                Object.keys(data).forEach(partNumber => {
                    const option = document.createElement('option');
                    option.value = partNumber;
                    option.textContent = partNumber;
                    option.dataset.leftWelds = data[partNumber]['Left Weld Count'];
                    option.dataset.rightWelds = data[partNumber]['Right Weld Count'];
                    partNumberSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching part numbers:', error));
    };

    const updateTotalWelds = () => {
        const leftWelds = parseInt(leftWeldInput.value, 10) || 0;
        const rightWelds = parseInt(rightWeldInput.value, 10) || 0;
        totalWeldDisplay.textContent = leftWelds + rightWelds;
    };

    partNumberSelect.addEventListener('change', (event) => {
        const selectedOption = event.target.selectedOptions[0];
        if (selectedOption) {
            leftWeldInput.value = selectedOption.dataset.leftWelds || 0;
            rightWeldInput.value = selectedOption.dataset.rightWelds || 0;
            updateTotalWelds();
        }
    });

    refreshPartsButton.addEventListener('click', fetchParts);

    document.querySelectorAll('.increment, .decrement').forEach(button => {
        button.addEventListener('click', (event) => {
            const input = event.target.dataset.target === 'left' ? leftWeldInput : rightWeldInput;
            let currentValue = parseInt(input.value, 10) || 0;

            if (event.target.classList.contains('increment')) {
                if (currentValue < 200) currentValue++;
            } else if (event.target.classList.contains('decrement')) {
                if (currentValue > 0) currentValue--;
            }

            input.value = currentValue;
            updateTotalWelds();
            event.preventDefault();
        });
    });

    manualCheckbox.addEventListener('change', toggleManualEntry);
    leftWeldInput.addEventListener('input', updateTotalWelds);
    rightWeldInput.addEventListener('input', updateTotalWelds);

    // Initial setup
    toggleManualEntry();
    fetchParts();
    updateTotalWelds();
});
