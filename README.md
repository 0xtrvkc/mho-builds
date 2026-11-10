# Outlanders Armor Planner

A single-file, dark-mode armor build planner for **Monster Hunter Outlanders**. Type up to three priority skills and the planner shows complete, side-by-side loadouts that trade one skill against another, without wasting levels over the cap.

No build step, no dependencies, no server. Open `index.html` in a browser.

## Features

- **Priority skills:** type up to 3 skills (P1, P2, P3). Each can have a target level; leave it empty to aim for the skill's max.
- **Build options:** every option is a full loadout (Head, Chest, Arms, Waist, Legs) with progress bars per skill, so you can compare trade-offs such as Capacity Boost 7 / Fire Damage Up 2 against 5 / 4.
- **No overcap:** the optimizer checks every combination and prefers builds that waste no levels, then use the fewest pieces, then have the most defense.
- **Real skill caps:** every skill uses its actual max level.
- **Color coding:** each priority skill has its own color across inputs, chips, bars and totals.
- **Details on hover (desktop) or tap (mobile):** piece stats, every skill with level and max, and the set skill with its effect.
- **Skill details:** description and max level for each priority skill, with a link to the level-by-level effects.
- **Set skills:** pieces needed, the skill each one grants, and its effect.
- **Manual swapping:** pin any piece in "Swap pieces manually" and the options are recalculated around it.
- **Data stamp:** the header shows when the data was built, how many pieces and skills it has, and turns amber after 14 days.
- **Mobile friendly:** swipeable build cards, large tap targets, and a bottom sheet for piece details.

## How the options are chosen

The planner searches all combinations (one piece per slot) and keeps the ones where no skill can improve without lowering another (the Pareto frontier). Among builds with the same skill levels, it picks the one with the least overcap, then the fewest pieces, then the highest defense. Up to six options are shown, labeled *Favors P1*, *Balanced* or *Trade-off*.

Limits to be aware of:

- Options compare **skill levels**, not real damage. How percentages combine in the game is not modeled.
- Set skills are shown as progress only. They are **not** added to skill levels and are not used when choosing pieces.
- Piece skills are taken at max rarity, as listed in the data source.

## Run locally

```bash
git clone <your-repo-url>
cd <your-repo>
open index.html        # or double-click it
```

## Deploy on GitHub Pages

1. Push `index.html` (and the other files) to your repository.
2. Go to **Settings > Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`, then save.
4. Your site appears at `https://<username>.github.io/<repo>/`.

## Updating the data

The armor data lives inside `index.html`, between the `DATA_START` and `DATA_END` markers.

1. Get an updated spreadsheet with these columns, in this order, with a header row:

   | Name | Part | Set | Rarity | Defense | Skills | Set Skill |
   |---|---|---|---|---|---|---|

   `Skills` looks like `Ammo Enhancement Lv2; Windproof Lv1`. A skill without `Lv` counts as Lv1. `Part` must be one of Head, Chest, Arms, Waist, Legs.

2. Run the updater:

   ```bash
   pip install openpyxl
   python update_data.py MHO_armor_list.xlsx index.html
   ```

   It rewrites the armor data and sets the data date to today. It also prints any skill missing a max level and any set skill missing from the set table.

3. If it reports missing items, add them to the tables near the top of the script in `index.html`:

   | Table | What it holds |
   |---|---|
   | `MAXL` | Max level of each skill |
   | `SETS` | Pieces needed for each set skill and the skill it grants |
   | `SETFX` | Effect text of each set skill |
   | `DESC` | One-line skill descriptions |

   A skill missing from `MAXL` has no cap. A set skill missing from `SETS` is treated as needing 2 pieces.

4. Commit and push.

To change when the amber warning appears, edit `STALE_DAYS` (default 14) in `index.html`.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app: markup, styles, script and data |
| `update_data.py` | Rebuilds the armor data in `index.html` from a spreadsheet |
| `README.md` | This file |

## Data source

Armor, skill and set skill data comes from [GamesWith's Monster Hunter Outlanders database](https://gamewith.ai/monster-hunter-outlanders/en/armor). Compare the piece count in the header with that page to check whether the data is current. The app cannot check the source by itself.

## Disclaimer

This is an unofficial fan project. It is not affiliated with or endorsed by Capcom or the Monster Hunter Outlanders developers. Monster Hunter is a trademark of Capcom. Game data belongs to its respective owners and is used here for reference.

## License

Choose a license before publishing (for example MIT) and add a `LICENSE` file. Check the terms of your data source before redistributing its data.
