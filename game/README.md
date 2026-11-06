# Super Gurtej World

A playable, dependency-free Mario fan mini-game. Collect coins, hit question blocks,
pick up a Super Mushroom for a protective power-up, stomp Goombas, jump across pits
and reach the flag. Includes a scrolling camera, three lives, timer, optional sound,
local best score, pause/restart and touch controls.

Download or clone the repository, then open `game/index.html` in your browser.
No build, install, API key or server is needed. GitHub displays source files and the
README animation; it cannot execute the interactive game inside a README.

- **Move:** Left / Right arrows or A / D
- **Jump:** Space, Up arrow or W; hold for a higher jump
- **Pause:** P or the Pause button; switching tabs pauses automatically
- **Restart:** R or the Restart button
- **Mobile:** On-screen direction and jump buttons
- **Sound:** Off initially; enable with the Sound button

The game is a fixed, handmade level. The README's separate contribution run uses
real GitHub data; this playable level does not claim to represent contributions.

## Profile artwork

Run these from the repository root with Python 3:

```sh
python3 scripts/build_profile.py
python3 scripts/generate_mario.py
```

`build_profile.py` rebuilds the five SVG scenes and `sprites.js` from shared pixel
art in `scripts/art.py`. The contribution generator reads GitHub's public calendar
locally or its GraphQL API when `GITHUB_TOKEN` is available. The scheduled workflow
refreshes `assets/mario-contributions.svg` daily at 00:17 UTC. Fetch failures leave
the last successful image intact. No fake contribution data is generated.

All SVGs are self-contained and support reduced motion. The retired Pac-Man
workflow is removed; the old `output` branch is no longer used by the profile.

## Checks

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/game.test.cjs
```

Original pixel drawings and code created for this profile. Unofficial fan project;
Mario and Super Mario are Nintendo trademarks.
