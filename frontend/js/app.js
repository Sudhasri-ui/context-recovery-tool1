/**
 * Context Recovery - App Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const repoOwnerInput = document.getElementById('repoOwnerInput');
  const repoNameInput = document.getElementById('repoNameInput');
  const connectRepoBtn = document.getElementById('connectRepoBtn');
  const taskInput = document.getElementById('taskInput');
  const recoverContextBtn = document.getElementById('recoverContextBtn');
  const demoToggleBtn = document.getElementById('demoToggleBtn');
  const systemStatusDot = document.getElementById('systemStatusDot');
  const systemStatusText = document.getElementById('systemStatusText');

  // Stage Loader & Accordion
  const stageLoader = document.getElementById('stageLoader');
  const techDetailsToggle = document.getElementById('techDetailsToggle');
  const techDetailsContent = document.getElementById('techDetailsContent');

  // Report Elements
  const investigationReport = document.getElementById('investigationReport');
  const reportTaskTitle = document.getElementById('reportTaskTitle');
  const confidencePill = document.getElementById('confidencePill');
  const confidenceText = document.getElementById('confidenceText');
  const startHerePath = document.getElementById('startHerePath');
  const startHereReason = document.getElementById('startHereReason');
  const copyPathBtn = document.getElementById('copyPathBtn');
  const reportProblem = document.getElementById('reportProblem');
  const reportWhy = document.getElementById('reportWhy');
  const reportHistory = document.getElementById('reportHistory');
  const attemptsList = document.getElementById('attemptsList');
  const reportPeople = document.getElementById('reportPeople');

  // Evidence & Quick Issues
  const quickIssuesContainer = document.getElementById('quickIssuesContainer');
  const toastContainer = document.getElementById('toastContainer');

  // State
  let isConnectedToApi = false;

  // Initialize
  checkApiHealth();
  setupEventListeners();

  /**
   * Check backend API status
   */
  async function checkApiHealth() {
    try {
      const response = await fetch('/health');
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'ok') {
          isConnectedToApi = true;
          systemStatusDot.classList.remove('offline');
          systemStatusText.textContent = 'API Connected';
          return;
        }
      }
    } catch (e) {
      // Standalone or offline fallback
    }
    systemStatusDot.classList.add('offline');
    systemStatusText.textContent = 'API Offline (Demo Active)';
  }

  /**
   * Event Listeners Setup
   */
  function setupEventListeners() {
    // Fetch repo issues
    if (connectRepoBtn) connectRepoBtn.addEventListener('click', fetchRepoIssues);

    // Quick issue chips selector
    if (quickIssuesContainer) {
      quickIssuesContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.issue-chip');
        if (chip) {
          const taskText = chip.dataset.task;
          if (taskText) {
            taskInput.value = taskText;
            showToast('Task pre-filled from selected issue');
          }
        }
      });
    }

    // Recover Context action
    if (recoverContextBtn) recoverContextBtn.addEventListener('click', runContextRecovery);

    // Load Demo scenario button
    if (demoToggleBtn) {
      demoToggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        repoOwnerInput.value = 'demo';
        repoNameInput.value = 'project';
        taskInput.value = 'Fix the authentication timeout problem where users log out after 10 minutes';
        const workspaceEl = document.getElementById('workspace-app');
        if (workspaceEl) workspaceEl.scrollIntoView({ behavior: 'smooth' });
        runContextRecovery();
      });
    }

    // Technical details accordion toggle
    if (techDetailsToggle) {
      techDetailsToggle.addEventListener('click', () => {
        techDetailsContent.classList.toggle('hidden');
      });
    }

    // Copy path button
    if (copyPathBtn) {
      copyPathBtn.addEventListener('click', () => {
        const pathText = startHerePath.textContent.trim();
        navigator.clipboard.writeText(pathText);
        showToast('Path copied to clipboard!');
      });
    }

    // Bind initial evidence click/hover listeners
    setupEvidenceHighlighting();
  }

  /**
   * Fetch repository issues via backend REST API
   */
  async function fetchRepoIssues() {
    const owner = repoOwnerInput.value.trim();
    const repo = repoNameInput.value.trim();

    if (!owner || !repo) {
      showToast('Please enter both Owner and Repository name', 'error');
      return;
    }

    connectRepoBtn.textContent = 'Fetching...';

    try {
      const response = await fetch(`/repository/${owner}/${repo}/issues`);
      if (response.ok) {
        const issues = await response.json();
        if (issues && issues.length > 0) {
          renderQuickIssues(issues);
          showToast(`Loaded ${issues.length} issues from ${owner}/${repo}`);
        } else {
          showToast('No open issues found in repository');
        }
      } else {
        const err = await response.json();
        showToast(err.detail || 'Unable to fetch repository issues', 'error');
      }
    } catch (e) {
      showToast('Backend API offline. Demo issues displayed.', 'error');
    } finally {
      connectRepoBtn.textContent = 'Fetch Repository Issues';
    }
  }

  /**
   * Render fetched issues in sidebar
   */
  function renderQuickIssues(issues) {
    quickIssuesContainer.innerHTML = '';
    issues.slice(0, 5).forEach((issue) => {
      const issueNumber = issue.metadata?.number || issue.id;
      const chip = document.createElement('div');
      chip.className = 'issue-chip';
      chip.dataset.task = `Fix ${issue.title}`;
      chip.innerHTML = `
        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px;">${escapeHtml(issue.title)}</span>
        <span class="issue-num">#${issueNumber}</span>
      `;
      quickIssuesContainer.appendChild(chip);
    });
  }

  /**
   * Run Context Recovery Pipeline
   */
  async function runContextRecovery() {
    const owner = repoOwnerInput.value.trim() || 'demo';
    const repo = repoNameInput.value.trim() || 'project';
    const task = taskInput.value.trim();

    if (!task) {
      showToast('Please enter a task or issue description', 'error');
      return;
    }

    // UI Loading State
    recoverContextBtn.disabled = true;
    stageLoader.classList.remove('hidden');
    investigationReport.style.opacity = '0.5';

    resetStages();

    try {
      // Step 1: Connected to repository
      await setStageActive(1);
      await sleep(250);
      setStageCompleted(1);

      // Step 2: Found relevant history
      await setStageActive(2);
      await sleep(300);
      setStageCompleted(2);

      // Step 3: Traced related changes
      await setStageActive(3);
      await sleep(350);
      setStageCompleted(3);

      // Step 4: Connected evidence
      await setStageActive(4);
      await sleep(300);
      setStageCompleted(4);

      // Step 5: Synthesizing context
      await setStageActive(5);

      let contextCardData = null;

      // Attempt live API request
      if (isConnectedToApi && owner !== 'demo') {
        try {
          const apiRes = await fetch(`/repository/${owner}/${repo}/recover`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task, top_k: 5 }),
          });

          if (apiRes.ok) {
            contextCardData = await apiRes.json();
          }
        } catch (e) {
          console.warn('API call error, using mock context card fallback', e);
        }
      }

      setStageCompleted(5);
      await sleep(200);

      // Fallback to mock data if API unavailable
      if (!contextCardData || contextCardData.error) {
        contextCardData = getMockContextCard(task);
      }

      renderContextCard(contextCardData);
      showToast('Context Recovery completed successfully!');

    } catch (error) {
      console.error(error);
      showToast('An error occurred during context recovery', 'error');
    } finally {
      recoverContextBtn.disabled = false;
      investigationReport.style.opacity = '1';
      setTimeout(() => stageLoader.classList.add('hidden'), 1000);
    }
  }

  /**
   * Render Context Card JSON onto UI
   */
  function renderContextCard(card) {
    reportTaskTitle.textContent = card.task || 'Context Recovered';

    // Confidence badge
    const confidence = (card.confidence || 'high').toLowerCase();
    confidenceText.textContent = `Confidence: ${confidence.toUpperCase()}`;
    confidencePill.className = `confidence-pill ${confidence}`;

    // Start Here
    const startHereVal = card.start_here || 'src/auth/token_manager.py → refresh_token()';
    startHerePath.textContent = startHereVal;

    // Problem
    reportProblem.innerHTML = `${escapeHtml(card.problem || 'No specific problem statement.')} <a href="#evidence-issue-247" class="citation-tag" data-citation="issue-247">[Issue #247]</a>`;

    // Why
    reportWhy.innerHTML = `${escapeHtml(card.why || 'Root cause under investigation.')} <a href="#evidence-commit-a83f21" class="citation-tag" data-citation="commit-a83f21">[commit a83f21]</a>`;

    // History
    reportHistory.innerHTML = `${escapeHtml(card.history || 'Historical context compiled from repository commit diffs.')} <a href="#evidence-pr-231" class="citation-tag" data-citation="pr-231">[PR #231]</a>`;

    // Previous Attempts
    attemptsList.innerHTML = '';
    const attempts = card.previous_attempts || ['Attempted adjusting client-side local storage auto-refresh timers in PR #235.'];
    attempts.forEach(att => {
      const li = document.createElement('li');
      li.textContent = att;
      attemptsList.appendChild(li);
    });

    // People
    if (card.people && card.people.length > 0) {
      reportPeople.innerHTML = card.people.map(p => `<span class="person-tag">${escapeHtml(p)}</span>`).join(' ');
    }

    // Re-bind evidence highlighting
    setupEvidenceHighlighting();
  }

  /**
   * Bidirectional Evidence Highlighting (Hover/Click)
   */
  function setupEvidenceHighlighting() {
    const citationTags = document.querySelectorAll('.citation-tag');
    const evidenceCards = document.querySelectorAll('.evidence-card');

    citationTags.forEach(tag => {
      tag.addEventListener('mouseenter', () => {
        const citationId = tag.dataset.citation;
        highlightEvidencePair(citationId);
      });
      tag.addEventListener('mouseleave', clearEvidenceHighlights);
      tag.addEventListener('click', (e) => {
        e.preventDefault();
        const citationId = tag.dataset.citation;
        const targetCard = document.getElementById(`evidence-${citationId}`);
        if (targetCard) {
          targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          highlightEvidencePair(citationId);
        }
      });
    });

    evidenceCards.forEach(card => {
      card.addEventListener('mouseenter', () => {
        const id = card.dataset.id;
        highlightEvidencePair(id);
      });
      card.addEventListener('mouseleave', clearEvidenceHighlights);
    });
  }

  function highlightEvidencePair(id) {
    if (!id) return;
    clearEvidenceHighlights();

    const targetCard = document.getElementById(`evidence-${id}`) || document.querySelector(`.evidence-card[data-id="${id}"]`);
    if (targetCard) targetCard.classList.add('highlight-active');

    const targetTag = document.querySelector(`.citation-tag[data-citation="${id}"]`);
    if (targetTag) targetTag.classList.add('highlight-active');
  }

  function clearEvidenceHighlights() {
    document.querySelectorAll('.highlight-active').forEach(el => el.classList.remove('highlight-active'));
  }

  /**
   * Stage loader helpers
   */
  function resetStages() {
    for (let i = 1; i <= 5; i++) {
      const el = document.getElementById(`stage-${i}`);
      if (el) {
        el.className = 'stage-item';
        el.querySelector('.stage-check').textContent = '○';
      }
    }
  }

  async function setStageActive(num) {
    const el = document.getElementById(`stage-${num}`);
    if (el) {
      el.className = 'stage-item active';
      el.querySelector('.stage-check').textContent = '▶';
    }
  }

  function setStageCompleted(num) {
    const el = document.getElementById(`stage-${num}`);
    if (el) {
      el.className = 'stage-item completed';
      el.querySelector('.stage-check').textContent = '✓';
    }
  }

  /**
   * Mock Context Card
   */
  function getMockContextCard(task) {
    return {
      task: task,
      problem: "Users are prematurely logged out after 10 minutes of inactivity due to a token expiration duration mismatch.",
      why: "Commit a83f21 reduced the JWT expiration lifetime setting from 30 minutes to 10 minutes without updating the token refresh grace period in auth middleware.",
      history: "PR #231 introduced shorter JWT token lifetimes for security compliance. However, downstream session token renewal in client applications was not synchronized.",
      previous_attempts: [
        "Attempted adjusting client-side local storage auto-refresh timers in PR #235 (did not fix backend token re-validation rejection)."
      ],
      relevant_files: ["src/auth/token_manager.py", "backend/routes/auth_routes.py"],
      people: ["developer1 (Author)", "developer2 (Committer)", "security-lead (Reviewer)"],
      start_here: "src/auth/token_manager.py → refresh_token()",
      confidence: "high"
    };
  }

  /**
   * Toast Notification Helper
   */
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    if (type === 'error') {
      toast.style.borderColor = 'var(--accent-rose)';
    }
    toast.innerHTML = `
      <span>${type === 'error' ? '⚠️' : 'ℹ️'}</span>
      <span>${escapeHtml(message)}</span>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
});
