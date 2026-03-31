# Animation patterns

Prefer:
- CSS transitions/keyframes for DOM UI motion
- animation-delay / transition-delay over setTimeout choreography
- requestAnimationFrame or proper Web APIs for imperative motion when required

Avoid:
- setInterval for audio fades
- brittle timeout chains for primary state transitions
- mixing multiple competing animation systems without a reason
