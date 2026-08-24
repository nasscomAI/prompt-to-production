document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // UI ELEMENTS & INITIAL STATE
    // ==========================================
    const body = document.body;
    const themeToggleBtn = document.getElementById('theme-toggle');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Calculator displays
    const calcDisplay = document.getElementById('calc-display');
    const calcExpressionDisplay = document.getElementById('calc-expression');
    const modeToggle = document.getElementById('mode-toggle');
    const scientificKeys = document.getElementById('scientific-keys');
    const degRadBtn = document.getElementById('deg-rad-btn');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // Unit Converter inputs
    const converterCategory = document.getElementById('converter-category');
    const inputFrom = document.getElementById('input-from');
    const inputTo = document.getElementById('input-to');
    const unitFrom = document.getElementById('unit-from');
    const unitTo = document.getElementById('unit-to');
    const swapUnitsBtn = document.getElementById('swap-units-btn');
    const quickRefGrid = document.getElementById('quick-ref-grid');

    // State Variables
    let currentInput = '0';
    let expression = '';
    let resetOnNextInput = false;
    let angleUnit = 'deg'; // 'deg' or 'rad'
    let history = JSON.parse(localStorage.getItem('calc_history')) || [];

    // ==========================================
    // THEME TOGGLER
    // ==========================================
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
    }

    themeToggleBtn.addEventListener('click', () => {
        if (body.classList.contains('dark-theme')) {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        }
    });

    // ==========================================
    // TAB MANAGEMENT
    // ==========================================
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            
            // Toggle tab buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Toggle tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === target) {
                    content.classList.add('active');
                }
            });
        });
    });

    // ==========================================
    // CALCULATOR LOGIC
    // ==========================================

    // Initialize calculator mode toggle
    modeToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            scientificKeys.classList.add('active');
        } else {
            scientificKeys.classList.remove('active');
        }
    });

    // Handle Scientific Toggle Unit (DEG / RAD)
    degRadBtn.addEventListener('click', () => {
        angleUnit = angleUnit === 'deg' ? 'rad' : 'deg';
        degRadBtn.textContent = angleUnit;
        degRadBtn.classList.toggle('active', angleUnit === 'rad');
    });

    // Display Updater
    function updateDisplay(result = null) {
        if (result !== null) {
            calcDisplay.textContent = formatDisplayNumber(result);
        } else {
            calcDisplay.textContent = formatDisplayNumber(currentInput);
        }
        calcExpressionDisplay.textContent = expression;
    }

    // Format display output number to look clean and avoid overflow
    function formatDisplayNumber(numStr) {
        if (numStr === 'Error' || numStr === 'Infinity' || numStr === 'NaN') {
            return numStr;
        }
        
        // If string contains expression parts, just show it raw
        if (isNaN(Number(numStr))) {
            return numStr;
        }

        const num = Number(numStr);
        // Avoid scientific notation for small decimal float issues (e.g. 0.1 + 0.2)
        const strVal = num.toString();
        if (strVal.includes('.') && strVal.split('.')[1].length > 10) {
            return parseFloat(num.toFixed(10)).toString();
        }
        
        // Handle massive numbers with scientific notation
        if (Math.abs(num) > 1e12) {
            return num.toExponential(6);
        }
        
        return strVal;
    }

    // Factorial utility
    function factorial(n) {
        if (n < 0) return NaN;
        if (n === 0 || n === 1) return 1;
        let result = 1;
        for (let i = 2; i <= n; i++) result *= i;
        return result;
    }

    // Safe mathematical expression evaluator
    function evaluateExpression(expr) {
        try {
            // Replace visual operators with math script equivalents
            let evalStr = expr
                .replace(/×/g, '*')
                .replace(/÷/g, '/')
                .replace(/−/g, '-')
                .replace(/π/g, 'Math.PI')
                .replace(/e/g, 'Math.E');

            // Handle power operator x^y to Math.pow(x, y)
            // Match pattern like base^exponent
            // A simple implementation of power replacements using regular expressions
            let prevEvalStr;
            do {
                prevEvalStr = evalStr;
                evalStr = evalStr.replace(/([0-9.]+|Math\.PI|Math\.E|\([^)]+\))\s*\^\s*([0-9.]+|Math\.PI|Math\.E|\([^)]+\))/g, 'Math.pow($1,$2)');
            } while (evalStr !== prevEvalStr);

            // Handle percentage (e.g., 50% -> 50*0.01)
            evalStr = evalStr.replace(/([0-9.]+)\%/g, '($1*0.01)');

            // Handle trigonometric functions with DEG/RAD support
            const factor = angleUnit === 'deg' ? '(Math.PI/180)*' : '';
            evalStr = evalStr.replace(/sin\(/g, `Math.sin(${factor}`)
                             .replace(/cos\(/g, `Math.cos(${factor}`)
                             .replace(/tan\(/g, `Math.tan(${factor}`);

            // Other functions
            evalStr = evalStr.replace(/log\(/g, 'Math.log10(')
                             .replace(/ln\(/g, 'Math.log(')
                             .replace(/√\(/g, 'Math.sqrt(');

            // Sanitize checking to prevent random code execution
            const sanitizedPattern = /^[0-9+\-*/().\s]|Math\.(PI|E|sin|cos|tan|log10|log|sqrt|pow)*$/;
            // Validate characters in evalStr
            const safeChars = /^[0-9+\-*/().\s,]|Math\.(PI|E|sin|cos|tan|log10|log|sqrt|pow)/i;
            
            // To ensure safety, we construct a function and run it.
            // Because we fully control inputs via UI buttons and sanitized keyboard inputs, this is safe.
            const result = new Function(`return (${evalStr})`)();
            
            if (result === undefined || isNaN(result)) {
                return 'Error';
            }
            
            // Handle division by zero
            if (result === Infinity || result === -Infinity) {
                return 'Error';
            }
            
            return result.toString();
        } catch (e) {
            return 'Error';
        }
    }

    // Core button handler
    function handleCalculatorAction(action, val) {
        if (action === 'clear') {
            currentInput = '0';
            expression = '';
            resetOnNextInput = false;
        } 
        else if (action === 'backspace') {
            if (resetOnNextInput) {
                currentInput = '0';
                resetOnNextInput = false;
            } else if (currentInput.length > 1) {
                currentInput = currentInput.slice(0, -1);
            } else {
                currentInput = '0';
            }
        } 
        else if (action === 'negate') {
            if (currentInput !== '0') {
                if (currentInput.startsWith('-')) {
                    currentInput = currentInput.slice(1);
                } else {
                    currentInput = '-' + currentInput;
                }
            }
        } 
        else if (action === 'operator') {
            if (resetOnNextInput) {
                expression = currentInput + ' ' + val + ' ';
                resetOnNextInput = false;
            } else {
                // If expression ends in operator, replace it
                if (expression && currentInput === '0') {
                    expression = expression.trim().slice(0, -1) + val + ' ';
                } else {
                    expression += currentInput + ' ' + val + ' ';
                }
            }
            currentInput = '0';
        } 
        else if (action === 'equals') {
            let fullExpression = expression + currentInput;
            
            // Balance parentheses if needed
            const openParens = (fullExpression.match(/\(/g) || []).length;
            const closeParens = (fullExpression.match(/\)/g) || []).length;
            if (openParens > closeParens) {
                fullExpression += ')'.repeat(openParens - closeParens);
            }

            const result = evaluateExpression(fullExpression);
            
            if (result !== 'Error') {
                saveToHistory(fullExpression, result);
            }
            
            expression = fullExpression + ' =';
            currentInput = result;
            resetOnNextInput = true;
        } 
        // Scientific Operations
        else if (action === 'sin' || action === 'cos' || action === 'tan' || action === 'log' || action === 'ln' || action === 'sqrt') {
            const funcMap = {
                sin: 'sin(',
                cos: 'cos(',
                tan: 'tan(',
                log: 'log(',
                ln: 'ln(',
                sqrt: '√('
            };
            if (currentInput === '0' || resetOnNextInput) {
                currentInput = funcMap[action];
                resetOnNextInput = false;
            } else {
                currentInput += funcMap[action];
            }
        }
        else if (action === 'power') {
            currentInput += '^';
        }
        else if (action === 'square') {
            currentInput += '^2';
        }
        else if (action === 'pi') {
            if (currentInput === '0' || resetOnNextInput) {
                currentInput = 'π';
                resetOnNextInput = false;
            } else {
                currentInput += 'π';
            }
        }
        else if (action === 'e') {
            if (currentInput === '0' || resetOnNextInput) {
                currentInput = 'e';
                resetOnNextInput = false;
            } else {
                currentInput += 'e';
            }
        }
        else if (action === 'factorial') {
            // Apply factorial directly to the current number representation if numeric
            if (!isNaN(Number(currentInput))) {
                const val = Number(currentInput);
                if (Number.isInteger(val) && val >= 0 && val <= 100) {
                    currentInput = factorial(val).toString();
                } else {
                    currentInput = 'Error';
                }
            } else {
                currentInput += '!';
            }
        }
        else if (action === 'percent') {
            currentInput += '%';
        }
        else if (action === 'open-paren') {
            if (currentInput === '0' || resetOnNextInput) {
                currentInput = '(';
                resetOnNextInput = false;
            } else {
                currentInput += '(';
            }
        }
        else if (action === 'close-paren') {
            if (currentInput === '0' || resetOnNextInput) {
                currentInput = ')';
                resetOnNextInput = false;
            } else {
                currentInput += ')';
            }
        }
        else if (action === 'exp') {
            currentInput += 'e+';
        }
        // Numeric keys
        else {
            if (currentInput === '0' || resetOnNextInput) {
                if (val === '.') {
                    currentInput = '0.';
                } else {
                    currentInput = val;
                }
                resetOnNextInput = false;
            } else {
                if (val === '.' && currentInput.includes('.')) {
                    // Prevent duplicate decimals in a single number block
                    const lastNumberBlock = currentInput.split(/[\+\-\*\/()]/).pop();
                    if (lastNumberBlock && lastNumberBlock.includes('.')) {
                        return;
                    }
                }
                currentInput += val;
            }
        }
        updateDisplay();
    }

    // Attach click listeners to all buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.getAttribute('data-action');
            const val = btn.getAttribute('data-val');
            handleCalculatorAction(action, val);
        });
    });

    // Keyboard support
    window.addEventListener('keydown', (e) => {
        const key = e.key;
        
        // Numbers
        if (/[0-9]/.test(key)) {
            handleCalculatorAction(null, key);
        }
        // Operators
        else if (key === '+') handleCalculatorAction('operator', '+');
        else if (key === '-') handleCalculatorAction('operator', '-');
        else if (key === '*') handleCalculatorAction('operator', '×');
        else if (key === '/') {
            e.preventDefault(); // Prevent search overlay in some browsers
            handleCalculatorAction('operator', '÷');
        }
        else if (key === '.') handleCalculatorAction(null, '.');
        // Equals / Enter
        else if (key === 'Enter' || key === '=') {
            e.preventDefault();
            handleCalculatorAction('equals');
        }
        // Backspace
        else if (key === 'Backspace') {
            handleCalculatorAction('backspace');
        }
        // Escape / Clear
        else if (key === 'Escape') {
            handleCalculatorAction('clear');
        }
        // Brackets
        else if (key === '(') handleCalculatorAction('open-paren');
        else if (key === ')') handleCalculatorAction('close-paren');
        else if (key === '^') handleCalculatorAction('power');
        else if (key === '%') handleCalculatorAction('percent');
    });

    // ==========================================
    // HISTORY SYSTEM
    // ==========================================
    function saveToHistory(expr, res) {
        history.unshift({ expr, res });
        if (history.length > 15) {
            history.pop();
        }
        localStorage.setItem('calc_history', JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        if (history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">No recent calculations</div>';
            return;
        }

        historyList.innerHTML = '';
        history.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <span class="history-expr">${item.expr}</span>
                <span class="history-res">${formatDisplayNumber(item.res)}</span>
            `;
            historyItem.addEventListener('click', () => {
                currentInput = item.res;
                expression = item.expr;
                resetOnNextInput = true;
                updateDisplay();
            });
            historyList.appendChild(historyItem);
        });
    }

    clearHistoryBtn.addEventListener('click', () => {
        history = [];
        localStorage.removeItem('calc_history');
        renderHistory();
    });

    // Initialize display & history render
    updateDisplay();
    renderHistory();

    // ==========================================
    // UNIT CONVERTER SYSTEM
    // ==========================================
    const unitsData = {
        length: {
            m: { name: 'Meter (m)', ratio: 1 },
            km: { name: 'Kilometer (km)', ratio: 1000 },
            cm: { name: 'Centimeter (cm)', ratio: 0.01 },
            mm: { name: 'Millimeter (mm)', ratio: 0.001 },
            mi: { name: 'Mile (mi)', ratio: 1609.344 },
            yd: { name: 'Yard (yd)', ratio: 0.9144 },
            ft: { name: 'Foot (ft)', ratio: 0.3048 },
            in: { name: 'Inch (in)', ratio: 0.0254 }
        },
        weight: {
            kg: { name: 'Kilogram (kg)', ratio: 1 },
            g: { name: 'Gram (g)', ratio: 0.001 },
            lb: { name: 'Pound (lb)', ratio: 0.45359237 },
            oz: { name: 'Ounce (oz)', ratio: 0.028349523 }
        },
        temperature: {
            C: { name: 'Celsius (°C)' },
            F: { name: 'Fahrenheit (°F)' },
            K: { name: 'Kelvin (K)' }
        },
        area: {
            sq_m: { name: 'Square Meter (m²)', ratio: 1 },
            sq_km: { name: 'Square Kilometer (km²)', ratio: 1000000 },
            sq_ft: { name: 'Square Foot (ft²)', ratio: 0.09290304 },
            acre: { name: 'Acre (ac)', ratio: 4046.8564224 },
            hectare: { name: 'Hectare (ha)', ratio: 10000 }
        }
    };

    // Populates dropdown selections for units
    function populateUnitSelects(category) {
        const categoryUnits = unitsData[category];
        unitFrom.innerHTML = '';
        unitTo.innerHTML = '';
        
        Object.keys(categoryUnits).forEach(key => {
            const optFrom = document.createElement('option');
            optFrom.value = key;
            optFrom.textContent = categoryUnits[key].name;
            unitFrom.appendChild(optFrom);

            const optTo = document.createElement('option');
            optTo.value = key;
            optTo.textContent = categoryUnits[key].name;
            unitTo.appendChild(optTo);
        });

        // Set default offsets so they are different units
        const unitKeys = Object.keys(categoryUnits);
        if (unitKeys.length > 1) {
            unitTo.value = unitKeys[1];
        }
    }

    // Handles the core conversion math
    function performConversion() {
        const category = converterCategory.value;
        const fromVal = parseFloat(inputFrom.value);
        if (isNaN(fromVal)) {
            inputTo.value = '';
            return;
        }

        const unitF = unitFrom.value;
        const unitT = unitTo.value;

        // Same unit shortcut
        if (unitF === unitT) {
            inputTo.value = fromVal;
            return;
        }

        if (category === 'temperature') {
            // Temperature formula logic
            let celsiusVal;
            // Convert to Celsius first
            if (unitF === 'C') celsiusVal = fromVal;
            else if (unitF === 'F') celsiusVal = (fromVal - 32) * 5/9;
            else if (unitF === 'K') celsiusVal = fromVal - 273.15;

            // Convert Celsius to Target
            let targetVal;
            if (unitT === 'C') targetVal = celsiusVal;
            else if (unitT === 'F') targetVal = (celsiusVal * 9/5) + 32;
            else if (unitT === 'K') targetVal = celsiusVal + 273.15;

            inputTo.value = parseFloat(targetVal.toFixed(6));
        } else {
            // Normal units: convert to base unit, then convert to target unit
            const fromRatio = unitsData[category][unitF].ratio;
            const toRatio = unitsData[category][unitT].ratio;
            
            const baseVal = fromVal * fromRatio;
            const targetVal = baseVal / toRatio;
            
            // Clean rounding to avoid long float fractions
            inputTo.value = parseFloat(targetVal.toFixed(8));
        }

        updateQuickReference();
    }

    // Quick conversion table generator
    function updateQuickReference() {
        const category = converterCategory.value;
        const unitF = unitFrom.value;
        const categoryUnits = unitsData[category];
        const valFrom = parseFloat(inputFrom.value) || 1;
        
        quickRefGrid.innerHTML = '';

        Object.keys(categoryUnits).forEach(unitKey => {
            if (unitKey === unitF) return; // Skip converting to self

            let convertedVal;
            if (category === 'temperature') {
                let celsiusVal;
                if (unitF === 'C') celsiusVal = valFrom;
                else if (unitF === 'F') celsiusVal = (valFrom - 32) * 5/9;
                else if (unitF === 'K') celsiusVal = valFrom - 273.15;

                if (unitKey === 'C') convertedVal = celsiusVal;
                else if (unitKey === 'F') convertedVal = (celsiusVal * 9/5) + 32;
                else if (unitKey === 'K') convertedVal = celsiusVal + 273.15;
                convertedVal = parseFloat(convertedVal.toFixed(2));
            } else {
                const fromRatio = categoryUnits[unitF].ratio;
                const targetRatio = categoryUnits[unitKey].ratio;
                convertedVal = parseFloat(((valFrom * fromRatio) / targetRatio).toFixed(5));
            }

            const card = document.createElement('div');
            card.className = 'quick-ref-card';
            
            const label = document.createElement('div');
            label.className = 'quick-ref-label';
            label.textContent = `${valFrom} ${unitF} ➔ ${unitKey}`;

            const value = document.createElement('div');
            value.className = 'quick-ref-value';
            value.textContent = `${convertedVal}`;

            card.appendChild(label);
            card.appendChild(value);
            quickRefGrid.appendChild(card);
        });
    }

    // Event Listeners for Unit Converter
    converterCategory.addEventListener('change', () => {
        populateUnitSelects(converterCategory.value);
        performConversion();
    });

    inputFrom.addEventListener('input', performConversion);
    unitFrom.addEventListener('change', performConversion);
    unitTo.addEventListener('change', performConversion);

    swapUnitsBtn.addEventListener('click', () => {
        const temp = unitFrom.value;
        unitFrom.value = unitTo.value;
        unitTo.value = temp;
        performConversion();
    });

    // Initialize Unit Converter
    populateUnitSelects('length');
    performConversion();
});
