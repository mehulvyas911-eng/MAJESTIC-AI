# MAJESTIC Campaign Mini-Game Plan

## Goal
Add a mobile-friendly, playable campaign experience to the existing MAJESTIC AI cybersecurity platform without changing the existing API contract. The game is served at `/game` and uses the repository's established blood-red, dark terminal aesthetic.

## Gameplay
- Title: **MAJESTIC // THREAT TRIAGE**.
- Mechanic: players tap the suspicious indicators in a grid of signal cards before the 20-second timer expires.
- Each round has six cards and three target indicators. Correct taps increase score and combo; incorrect taps trigger immediate visual feedback and a penalty.
- Progress is visible through round number, score, combo, target count, and timer.
- The short session has three rounds, with escalating card density and target count.
- Results show score, rank, reward placeholder, and optional email capture.

## Product structure
- `game/index.html`: three clear screens (welcome, play, results), semantic form controls, accessible status text, and a noscript fallback.
- `game/styles.css`: responsive terminal-inspired visual system, mobile-first layout, touch-sized controls, feedback states, and reduced-motion support.
- `game/game.js`: deterministic client-side game loop, round generation, scoring, feedback, result state, optional signup storage, and replay flow.
- `server.py`: static routes for `/game`, `/game/`, `/game/<asset>` and `/game/leads` placeholder response.
- `manus-routes.json`: route manifest for the game route.
- `README.md`: run and lead/reward setup notes.

## Design

### Style options sampled for this brief
- Cyberpunk incident console — probability 0.06.
- Tactical command dashboard — probability 0.08.
- Editorial security report — probability 0.04.

**Chosen style: Cyberpunk incident console.**

### Design movement
A focused SOC console translated into a campaign microsite: crisp type, red signal states, scanline texture, and a controlled sense of urgency.

### Core principles
1. Make the next action obvious on a phone.
2. Use red as a signal color, not a wall of decoration.
3. Pair dense terminal cues with generous touch targets.
4. Give every tap an immediate, legible response.

### Color philosophy
Near-black graphite creates the command-center base. MAJESTIC red carries brand recognition and alert energy; pale green and amber are reserved for positive/neutral telemetry so players can parse the system at a glance.

### Layout paradigm
A single-column incident console with a strong left-edge signal rail, floating stat chips, and cards that feel like live telemetry rather than a conventional tile grid.

### Signature elements
- Thin red signal rail and bracketed labels.
- Red glow used only for active threat states.
- Monospace telemetry paired with bold condensed display text.

### Interaction and animation
Cards lift on press, correct targets pulse green, wrong targets flash red, and the timer bar drains with urgency. Animations are short and are disabled or softened for reduced-motion preferences.

### Typography system
Use `Space Grotesk` for display and interface hierarchy, with `IBM Plex Mono` for telemetry and technical labels. The layout includes system fallbacks for offline use.

### Brand essence and voice
MAJESTIC is an AI-powered cybersecurity automation platform for security practitioners who want faster, more informed action. Personality: precise, vigilant, capable.

Voice examples: “Your next signal is waiting.” and “Triage complete. Keep moving.”

### Signature brand color
MAJESTIC red: `#ff2d3d`, derived from the existing repository's blood-red terminal identity.

## Reward and lead assumptions
No campaign reward code, destination link, email provider, privacy URL, or consent copy was supplied. The results screen therefore labels the reward as `REWARD_CODE_PLACEHOLDER` and the CTA as `Replace with your campaign CTA`. The email form saves a consented demo lead to browser `localStorage` only and explicitly explains that production capture requires wiring an approved provider/API and privacy policy.

## Serving and validation
The existing Flask API remains the root service. The game is static and is mounted without enabling a database or changing existing endpoints. Validate with Python compilation, route smoke tests, static asset checks, and a browser-independent JavaScript syntax check where available.
