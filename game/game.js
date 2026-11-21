(() => {
  const $ = (id) => document.getElementById(id);
  const screens = { welcome: $('welcomeScreen'), game: $('gameScreen'), results: $('resultsScreen') };
  const grid = $('signalGrid');
  const signals = [
    ['CRITICAL', 'Auth bypass', 'CVE-9X21'], ['NORMAL', 'Patch update', 'PKG-4.2.1'], ['CRITICAL', 'Token leak', 'ENV-0x44'],
    ['INFO', 'Bot heartbeat', 'NODE-17'], ['CRITICAL', 'Rogue process', 'PID-8841'], ['NORMAL', 'Clean deploy', 'BUILD-721'],
    ['INFO', 'Asset sync', 'EDGE-08'], ['NORMAL', 'Rate limit', 'API-200'], ['CRITICAL', 'Exposed key', 'KEY-771'],
    ['INFO', 'DNS update', 'NET-14'], ['NORMAL', 'User login', 'AUTH-22'], ['CRITICAL', 'Shell drop', 'PROC-0xF1']
  ];
  let state;
  const show = (name) => Object.entries(screens).forEach(([key, el]) => { el.hidden = key !== name; });
  const pad = (n, len = 4) => String(n).padStart(len, '0');
  const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

  function resetState() {
    state = { round: 1, score: 0, combo: 0, hits: 0, targets: 0, timeLeft: 20, roundStart: 0, raf: 0, roundTimer: 0, locked: false };
  }
  function startGame() { resetState(); show('game'); startRound(); }
  function startRound() {
    state.locked = false; state.timeLeft = 20; state.roundStart = performance.now();
    const count = state.round === 1 ? 6 : state.round === 2 ? 8 : 10;
    const targetCount = state.round === 1 ? 2 : state.round === 2 ? 3 : 4;
    const pool = shuffle(signals).slice(0, count);
    const targetIndexes = new Set(shuffle([...Array(count).keys()]).slice(0, targetCount));
    state.targets = targetCount; state.hits = 0;
    $('roundLabel').textContent = `ROUND 0${state.round}/03`;
    $('instruction').innerHTML = 'Find the indicators tagged <b>CRITICAL</b>.';
    $('feedback').className = 'feedback'; $('feedback').textContent = 'Awaiting input…';
    grid.innerHTML = '';
    pool.forEach((item, index) => {
      const card = document.createElement('button'); card.type = 'button'; card.className = 'signal-card';
      const isTarget = targetIndexes.has(index); card.dataset.target = isTarget ? 'true' : 'false';
      card.innerHTML = `<span class="signal-type">${item[0]}</span><span class="signal-name">${item[1]}</span><span class="signal-meta">${item[2]}</span>`;
      card.setAttribute('aria-label', `${item[0]} ${item[1]} ${item[2]}`); card.addEventListener('click', () => selectCard(card)); grid.appendChild(card);
    });
    updateStats(); cancelAnimationFrame(state.raf); state.raf = requestAnimationFrame(tick);
  }
  function tick(now) {
    if (state.locked) return;
    state.timeLeft = Math.max(0, 20 - (now - state.roundStart) / 1000); $('timerValue').textContent = `${state.timeLeft.toFixed(1)}s`; $('timerBar').style.width = `${state.timeLeft / 20 * 100}%`;
    if (state.timeLeft <= 0) { finishRound(true); return; } state.raf = requestAnimationFrame(tick);
  }
  function selectCard(card) {
    if (state.locked || card.disabled) return;
    card.disabled = true;
    if (card.dataset.target === 'true') {
      card.classList.add('is-hit'); state.hits++; state.combo++; state.score += 100 + state.combo * 25; $('feedback').className = 'feedback good'; $('feedback').textContent = state.combo > 1 ? `Confirmed. Combo x${state.combo}.` : 'Confirmed. Signal contained.';
      if (state.hits === state.targets) finishRound(false);
    } else {
      card.classList.add('is-miss'); state.combo = 0; state.score = Math.max(0, state.score - 40); $('feedback').className = 'feedback bad'; $('feedback').textContent = 'False positive. Signal lost — keep scanning.';
    }
    updateStats();
  }
  function finishRound(timeout) {
    if (state.locked) return; state.locked = true; cancelAnimationFrame(state.raf); document.querySelectorAll('.signal-card').forEach((c) => c.disabled = true);
    if (timeout) { state.combo = 0; $('feedback').className = 'feedback bad'; $('feedback').textContent = 'Window closed. Incomplete sweep.'; }
    if (state.round < 3) { $('feedback').className = 'feedback round'; $('feedback').textContent = timeout ? 'Recalibrating next round…' : 'Clean sweep. Escalating incident…'; state.roundTimer = window.setTimeout(() => { state.round++; startRound(); }, 900); }
    else window.setTimeout(showResults, timeout ? 650 : 500);
  }
  function updateStats() { $('scoreValue').textContent = pad(state.score); $('comboValue').textContent = `x${state.combo}`; $('targetValue').textContent = `${state.hits}/${state.targets}`; }
  function showResults() {
    show('results'); $('finalScore').textContent = pad(state.score); const rank = state.score >= 1150 ? 'SIGNAL ARCHITECT' : state.score >= 700 ? 'FIELD ANALYST' : 'ROOKIE OPERATOR'; $('rankValue').textContent = `FIELD RANK // ${rank}`; $('resultSummary').textContent = state.score >= 700 ? 'You kept the signal clean. The next move is yours.' : 'The signal got noisy, but every sweep builds sharper instincts.';
  }
  $('playButton').addEventListener('click', startGame); $('againButton').addEventListener('click', startGame);
  $('signupForm').addEventListener('submit', (event) => { event.preventDefault(); const email = $('emailInput').value.trim(); if (!email || !$('consentInput').checked) { $('signupNote').textContent = 'Enter a valid email and check consent to save your result.'; $('signupNote').style.color = 'var(--red)'; return; } const lead = { email, score: state.score, consentedAt: new Date().toISOString() }; const existing = JSON.parse(localStorage.getItem('majestic_demo_leads') || '[]'); existing.push(lead); localStorage.setItem('majestic_demo_leads', JSON.stringify(existing)); $('signupNote').textContent = 'Saved in demo mode. Connect your approved lead provider before launch.'; $('signupNote').style.color = 'var(--green)'; event.target.querySelector('button').textContent = 'Result saved ✓'; });
  show('welcome');
})();
