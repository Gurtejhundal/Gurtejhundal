# The Kingdom You Built

Your last twelve GitHub activity weeks become a playable Mario world:

- Each week is one stage, in date order.
- Each active day adds exactly one brick row to that stage.
- Each contribution becomes one coin. A bundle labelled `+50` contains exactly
  50 contributions from that week; it is collected only once.
- Weeks with no activity remain flat ground with no reward to collect.
- Collect all weekly bundles, then reach the flag. If you miss one, move left
  and retrieve it. There is no timer or invented score bonus.

The profile's SVG is a 26-second automatic replay of this same world. Its Mario
route, bundle amounts, coin counter, terrain and final total are generated from
real activity. The previous independent calendar grid and arbitrary obstacle
course have been replaced. The README cannot execute keyboard-controlled games.

Download or clone the repository and open `game/index.html` in a browser.
No build, install, API key or server is required.

**Move:** Left / Right or A / D. **Jump:** Space, Up or W. **Pause/resume:** P.
**Restart:** R. Touch controls are available on mobile. Sound is optional.

## Rebuild

```sh
python3 scripts/build_profile.py
python3 scripts/generate_mario.py
```

`build_profile.py` regenerates the five surrounding profile scenes and shared
sprite data. `generate_mario.py` writes both `assets/mario-contributions.svg` and
`game/activity-level.js` from one calendar snapshot. The scheduled workflow
refreshes both together daily at 00:17 UTC using GitHub GraphQL. Local builds can
use the public calendar without a token. Fetch failures leave the previous files
untouched. An optional `--input calendar.json` supports reproducible local builds.

The window includes the current Sunday-start week (marked `*` while incomplete)
and the eleven weeks before it. Totals describe this displayed period rather than
the entire year. Dates and exact weekly values are included in the SVG's accessible
description. Reduced motion shows a static overview with all bundles visible.

## Checks

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/game.test.cjs
```

Original pixel drawings and code for this profile. Unofficial fan project;
Mario and Super Mario are Nintendo trademarks.
