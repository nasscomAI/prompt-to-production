let history = '';
let currentInput = '0';
let resetNextInput = false;

const displayEl = document.getElementById('display');
const historyEl = document.getElementById('history');

function updateDisplay() {
    displayEl.textContent = currentInput;
    historyEl.textContent = history;
}

function appendValue(val) {
    if (currentInput === '0' || resetNextInput) {
        currentInput = val;
        resetNextInput = false;
    } else {
        currentInput += val;
    }
    updateDisplay();
}

function setOperator(op) {
    if (resetNextInput && history !== '') {
        // Change operator if already evaluated
        history = history.slice(0, -1) + op;
        updateDisplay();
        return;
    }

    if (history === '') {
        history = currentInput + ' ' + op + ' ';
    } else {
        // If there's an ongoing operation, compute it
        compute();
        history += currentInput + ' ' + op + ' ';
    }
    resetNextInput = true;
    updateDisplay();
}

function handleAction(action) {
    switch(action) {
        case 'clear-all':
            history = '';
            currentInput = '0';
            break;
        case 'clear-entry':
            currentInput = '0';
            break;
        case 'backspace':
            if (resetNextInput) break;
            currentInput = currentInput.slice(0, -1);
            if (currentInput === '' || currentInput === '-') currentInput = '0';
            break;
        case 'neg':
            if (currentInput !== '0') {
                currentInput = currentInput.startsWith('-') ? currentInput.substring(1) : '-' + currentInput;
            }
            break;
        case 'trig':
            // E.g., handling tan, sin, cos via separate logic or combined
            // Will map to specific trig functions
            break;
        case 'inv':
            if (parseFloat(currentInput) !== 0) {
                currentInput = (1 / parseFloat(currentInput)).toString();
            } else {
                currentInput = "DivByZeroError";
            }
            resetNextInput = true;
            break;
        case 'abs':
            currentInput = Math.abs(parseFloat(currentInput)).toString();
            resetNextInput = true;
            break;
        case 'sqrt':
            if (parseFloat(currentInput) >= 0) {
                currentInput = Math.sqrt(parseFloat(currentInput)).toString();
            } else {
                currentInput = "InvalidInput";
            }
            resetNextInput = true;
            break;
        case 'power2':
            currentInput = Math.pow(parseFloat(currentInput), 2).toString();
            resetNextInput = true;
            break;
        case 'power10':
            currentInput = Math.pow(10, parseFloat(currentInput)).toString();
            resetNextInput = true;
            break;
        case 'log':
            currentInput = Math.log10(parseFloat(currentInput)).toString();
            resetNextInput = true;
            break;
        case 'ln':
            currentInput = Math.log(parseFloat(currentInput)).toString();
            resetNextInput = true;
            break;
        case 'fact':
            currentInput =  factorial(parseFloat(currentInput)).toString();
            resetNextInput = true;
            break;
        case 'compute':
            compute();
            history = '';
            break;
    }
    updateDisplay();
}

function handleTrig(trigFunc) {
     let val = parseFloat(currentInput);
     // Convert to radians for Math trig functions
     if(trigFunc === 'sin') {
         currentInput = Math.sin(val).toString();
     } else if(trigFunc === 'cos') {
         currentInput = Math.cos(val).toString();
     } else if(trigFunc === 'tan') {
         currentInput = Math.tan(val).toString();
     }
     resetNextInput = true;
     updateDisplay();
}

function factorial(n) {
    if (n < 0 || !Number.isInteger(n)) return NaN;
    if (n === 0 || n === 1) return 1;
    let res = 1;
    for(let i=2; i<=n; i++) res *= i;
    return res;
}

function compute() {
    if (history === '' || resetNextInput) return;
    
    let expr = history + currentInput;
    // Replace operators with JS readable ones
    expr = expr.replace(/×/g, '*').replace(/÷/g, '/').replace(/−/g, '-');
    expr = expr.replace(/\^/g, '**').replace(/Mod/g, '%');

    try {
        // Safe evaluation strategy since input only comes from our buttons
        // For a mathematical calculator, evaluating sanitized strings via Function constructor works well
        const computeFunc = new Function('return (' + expr + ')');
        const res = computeFunc();
        currentInput = parseDisplayResult(res);
        history = '';
        resetNextInput = true;
    } catch(e) {
        currentInput = "Error";
    }
    updateDisplay();
}

function parseDisplayResult(res) {
    if (!isFinite(res)) {
        return "DivisionByZeroError";
    }
    // Handle floating point precision issues
    return parseFloat(res.toPrecision(12)).toString();
}


document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const val = e.target.getAttribute('data-val');
        const action = e.target.getAttribute('data-action');
        const innerText = e.target.innerText;

        if (btn.classList.contains('num')) {
            appendValue(val);
        } else if (btn.classList.contains('op')) {
            // Need to insert corresponding string
            const opSign = e.target.innerText;
            if(val === '(' || val === ')') {
                 appendValue(val);
            } else if (val === '^' || val === '%') {
                 setOperator(val);
            } else {
                 setOperator(opSign);
            }
        } else if (action === 'trig') {
             handleTrig(innerText);
        } else if (action) {
            handleAction(action);
        }
    });
});

// Keypress logic
document.addEventListener('keydown', (e) => {
    e.preventDefault(); // Stop default browser actions
    if (e.key >= '0' && e.key <= '9' || e.key === '.') {
        appendValue(e.key);
    } else if (['+', '-', '*', '/'].includes(e.key)) {
        let displayOp = e.key;
        if(e.key === '*') displayOp = '×';
        if(e.key === '/') displayOp = '÷';
        if(e.key === '-') displayOp = '−';
        setOperator(displayOp);
    } else if (e.key === 'Enter' || e.key === '=') {
        handleAction('compute');
    } else if (e.key === 'Backspace') {
        handleAction('backspace');
    } else if (e.key === 'Escape') {
        handleAction('clear-all');
    }
});
