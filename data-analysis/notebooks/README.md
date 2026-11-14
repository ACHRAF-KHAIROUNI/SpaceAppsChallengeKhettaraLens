# Notebook: `dune_detective_trends_EN.ipynb`

## Open it in Google Colab
**Option A — from GitHub (repository must be public, or you must be logged in with access):**
Colab → *File → Open notebook → GitHub* tab → paste the repository URL → choose the notebook.

**Option B — upload:** download the `.ipynb` from GitHub, then Colab → *File → Upload notebook*.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ACHRAF-KHAIROUNI/SpaceAppsChallengeWebSite/blob/main/data-analysis/notebooks/dune_detective_trends_EN.ipynb)
*(badge link assumes branch `main`; change `main` to the branch name if different)*

## Before running
- NASA Earthdata account with **NASA GESDISC DATA ARCHIVE** authorised.
- Team CSV files: in Colab's **Files** panel create a folder named `team_data` and drop the three files from `data-analysis/data/team_data/` into it. Without them step 6b is simply skipped.
- Optional: a Google Earth Engine project (for NDVI).

## Run order
Run the cells **one by one**. Step 4 (MERRA-2) takes 5-15 minutes the first time. Keep the browser tab open.

## Settings you may change (Step 2)
| Setting | Meaning |
|---|---|
| `SITES` | Study sites as `name: (latitude, longitude)`. Add a line to study a new region. |
| `START_WIND`, `END_WIND` | Years for MERRA-2 (set `START_WIND = 1990` for a longer history, slower). |
| `START_SOIL`, `END_SOIL` | Years for GLDAS (data exists since 2000). |
| `BOX_HALF_WIDTH` | Size in degrees of the box averaged around each site. |
| `TEAM_SITE` (step 6b) | Name of the site covered by the team CSV files. |
| `USE_GEE`, `EE_PROJECT` | Enable NDVI via Earth Engine. |

## After running
Download `outputs_trends` from Colab (cell "zip", or Files panel) and upload its content to `data-analysis/results/` on GitHub.
