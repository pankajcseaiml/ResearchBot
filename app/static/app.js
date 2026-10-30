/**
 * ResearchBot Frontend Application Logic
 * Handles user interactions, API communication, progress states,
 * safe Markdown rendering, HTML sanitization, and error handling.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const form = document.getElementById('research-form');
  const questionInput = document.getElementById('question-input');
  const charCount = document.getElementById('char-count');
  const btnSubmit = document.getElementById('btn-submit');
  const btnClear = document.getElementById('btn-clear');
  const btnSpinner = btnSubmit.querySelector('.btn-spinner');
  const btnText = btnSubmit.querySelector('.btn-text');

  const alertBanner = document.getElementById('alert-banner');
  const alertTitle = document.getElementById('alert-title');
  const alertMessage = document.getElementById('alert-message');
  const alertClose = document.getElementById('alert-close');
  const alertIcon = document.getElementById('alert-icon');

  const statusPill = document.getElementById('system-status-pill');
  const statusText = document.getElementById('system-status-text');
  const modelTag = document.getElementById('model-tag');

  const progressSection = document.getElementById('progress-section');
  const pipeStep1 = document.getElementById('pipe-step-1');
  const pipeStep2 = document.getElementById('pipe-step-2');
  const pipeStep3 = document.getElementById('pipe-step-3');

  const resultsSection = document.getElementById('results-section');
  const displayQuestion = document.getElementById('display-question');
  const reportOutput = document.getElementById('report-output');
  const sourcesList = document.getElementById('sources-list');
  const sourcesCount = document.getElementById('sources-count');
  const disclaimerText = document.getElementById('disclaimer-text');

  const btnCopy = document.getElementById('btn-copy');
  const copyText = document.getElementById('copy-text');
  const btnNewResearch = document.getElementById('btn-new-research');
  const topicChips = document.querySelectorAll('.topic-chip');

  let currentMarkdownAnswer = '';
  let progressInterval = null;

  // Initialize
  checkSystemHealth();
  updateCharCount();

  // Event Listeners
  questionInput.addEventListener('input', updateCharCount);

  questionInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!btnSubmit.disabled) {
        form.dispatchEvent(new Event('submit', { cancelable: true }));
      }
    }
  });

  btnClear.addEventListener('click', () => {
    questionInput.value = '';
    updateCharCount();
    questionInput.focus();
    hideAlert();
  });

  alertClose.addEventListener('click', hideAlert);

  btnNewResearch.addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    questionInput.value = '';
    updateCharCount();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    questionInput.focus();
  });

  btnCopy.addEventListener('click', () => {
    if (!currentMarkdownAnswer) return;
    navigator.clipboard.writeText(currentMarkdownAnswer).then(() => {
      copyText.textContent = 'Copied!';
      btnCopy.classList.add('btn-primary');
      setTimeout(() => {
        copyText.textContent = 'Copy Report';
        btnCopy.classList.remove('btn-primary');
      }, 2000);
    }).catch(() => {
      showAlert('Notice', 'Unable to copy report automatically.', 'warning');
    });
  });

  topicChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      if (query) {
        questionInput.value = query;
        updateCharCount();
        questionInput.focus();
        hideAlert();
      }
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rawQuestion = questionInput.value.trim();

    if (!rawQuestion) {
      showAlert('Input Required', 'Please enter a research question before submitting.', 'warning');
      questionInput.focus();
      return;
    }

    if (rawQuestion.length > 5000) {
      showAlert('Question Too Long', 'Question exceeds the maximum allowed length of 5,000 characters.', 'warning');
      return;
    }

    await executeResearch(rawQuestion);
  });

  // System Health Check
  async function checkSystemHealth() {
    try {
      const res = await fetch('/health');
      if (!res.ok) throw new Error(`Health check returned status ${res.status}`);
      const data = await res.json();

      modelTag.textContent = data.model || 'llama-3.3-70b-versatile';

      if (data.status === 'healthy' && data.groq_configured) {
        statusPill.className = 'status-pill status-ready';
        statusText.textContent = 'Ready & Grounded';
        statusPill.title = 'Groq API configured. Curated research library loaded.';
      } else {
        statusPill.className = 'status-pill status-degraded';
        statusText.textContent = 'Degraded (No API Key)';
        statusPill.title = 'Groq API key missing in .env. Model inference disabled.';
        showAlert(
          'API Key Unconfigured',
          'Groq API key is not configured. Set GROQ_API_KEY in your .env file to enable live agent coordination.',
          'warning'
        );
      }
    } catch (err) {
      statusPill.className = 'status-pill status-degraded';
      statusText.textContent = 'Offline';
      statusPill.title = 'Could not contact backend service.';
    }
  }

  // Character Counter
  function updateCharCount() {
    const len = questionInput.value.length;
    charCount.textContent = `${len.toLocaleString()} / 5,000`;
    if (len > 5000) {
      charCount.style.color = 'var(--error-text)';
      btnSubmit.disabled = true;
    } else {
      charCount.style.color = 'var(--text-muted)';
      btnSubmit.disabled = false;
    }
  }

  // Alert helpers
  function showAlert(title, message, type = 'error') {
    alertBanner.className = `alert-banner alert-${type}`;
    alertTitle.textContent = title;
    alertMessage.textContent = message;
    alertIcon.textContent = type === 'warning' ? '⚠️' : type === 'success' ? '✅' : '❌';
    alertBanner.classList.remove('hidden');
    alertBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function hideAlert() {
    alertBanner.classList.add('hidden');
  }

  // Progress Pipeline Simulation
  function startProgressIndicator() {
    progressSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    hideAlert();

    // Reset steps
    pipeStep1.className = 'pipeline-step step-active';
    pipeStep2.className = 'pipeline-step';
    pipeStep3.className = 'pipeline-step';

    let elapsedSeconds = 0;
    progressInterval = setInterval(() => {
      elapsedSeconds += 1;
      if (elapsedSeconds === 2) {
        pipeStep1.className = 'pipeline-step step-complete';
        pipeStep2.className = 'pipeline-step step-active';
      } else if (elapsedSeconds === 5) {
        pipeStep2.className = 'pipeline-step step-complete';
        pipeStep3.className = 'pipeline-step step-active';
      }
    }, 1000);
  }

  function stopProgressIndicator() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    progressSection.classList.add('hidden');
  }

  // Main Research Execution
  async function executeResearch(question) {
    // UI state: loading
    btnSubmit.disabled = true;
    btnClear.disabled = true;
    btnSpinner.classList.remove('hidden');
    btnText.textContent = 'Investigating...';
    startProgressIndicator();

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        throw new Error(text || `Server returned status ${response.status}`);
      }

      if (!response.ok) {
        const errorMsg = data.message || data.detail || `Request failed with status ${response.status}`;
        if (response.status === 503) {
          showAlert('Configuration Required', `${errorMsg} (Please check your local .env file).`, 'warning');
        } else if (response.status === 504) {
          showAlert('Request Timeout', 'The multi-agent research workflow timed out. Try refining your question.', 'error');
        } else if (response.status === 422) {
          showAlert('Invalid Request', errorMsg, 'warning');
        } else {
          showAlert('Research Error', errorMsg, 'error');
        }
        return;
      }

      // Success
      renderResults(data);
    } catch (err) {
      showAlert('Connection Failure', `Could not complete request: ${err.message}`, 'error');
    } finally {
      stopProgressIndicator();
      btnSubmit.disabled = false;
      btnClear.disabled = false;
      btnSpinner.classList.add('hidden');
      btnText.textContent = 'Investigate Question';
    }
  }

  // Results Rendering
  function renderResults(data) {
    currentMarkdownAnswer = data.answer || '';
    displayQuestion.textContent = data.question || '';

    // Render Sources
    sourcesList.innerHTML = '';
    const sources = data.sources || [];
    sourcesCount.textContent = `${sources.length} ${sources.length === 1 ? 'source' : 'sources'}`;

    if (sources.length > 0) {
      sources.forEach((s) => {
        const li = document.createElement('li');
        li.className = 'source-item';
        
        // Extract identifier if present e.g. "sample-rag-001 — ..."
        const parts = s.split('—');
        if (parts.length > 1) {
          const badge = document.createElement('span');
          badge.className = 'source-badge';
          badge.textContent = parts[0].trim();
          li.appendChild(badge);

          const titleSpan = document.createElement('span');
          titleSpan.textContent = parts.slice(1).join('—').trim();
          li.appendChild(titleSpan);
        } else {
          li.textContent = s;
        }
        sourcesList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.className = 'source-item';
      li.textContent = 'No matching documents from the curated local research library were cited for this query.';
      sourcesList.appendChild(li);
    }

    // Render Markdown safely
    renderSafeMarkdown(reportOutput, currentMarkdownAnswer);

    // Disclaimer
    if (data.disclaimer) {
      disclaimerText.textContent = data.disclaimer;
    }

    // Reveal results
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Safe Markdown rendering with DOMPurify and fallback
  function renderSafeMarkdown(targetElement, markdownText) {
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
      try {
        marked.setOptions({
          gfm: true,
          breaks: true,
        });
        const rawHtml = marked.parse(markdownText);
        const cleanHtml = DOMPurify.sanitize(rawHtml);
        targetElement.innerHTML = cleanHtml;
        return;
      } catch (err) {
        console.warn('Marked/DOMPurify parsing failed, falling back to safe renderer', err);
      }
    }

    // Resilient fallback: sanitize text and parse basic markdown structure
    targetElement.innerHTML = parseMarkdownFallback(markdownText);
  }

  // Lightweight fallback renderer that never executes scripts
  function parseMarkdownFallback(text) {
    // Escape HTML special characters
    const escapeHtml = (str) =>
      str.replace(/[&<>'"]/g, (tag) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;',
      }[tag] || tag));

    const escaped = escapeHtml(text);
    return escaped
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/`([^`]+)`/gim, '<code>$1</code>')
      .replace(/\n\n+/g, '</p><p>')
      .replace(/^-(.*$)/gim, '<ul><li>$1</li></ul>')
      .replace(/<\/ul>\s*<ul>/g, '');
  }
});
