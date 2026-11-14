#  Dune Detective — Space Apps Challenge 2026

**Challenge:** *Be an Earth System Trend Detective* (NASA International Space Apps Challenge 2026)
**Goal:** fight **sand encroachment** in Africa (pilot site: **Merzouga, Morocco**) by understanding how the local climate is changing, then proposing where, when and how to plant.

## The idea in one minute
Sand moves when **wind** is strong and the **soil is dry and bare**. We look for trends in:

| Clue | Why it matters | Data |
|---|---|---|
| Wind at 10 m | It transports the sand | NASA MERRA-2 |
| Soil moisture | Dry soil = mobile sand; moist soil = plants survive | NASA GLDAS |
| Rainfall (incl. extreme days) | Water for planting; flash floods can be harvested | NASA GLDAS, NASA POWER |
| Surface / soil temperature | Heat dries soil and stresses young plants | NASA MERRA-2, GLDAS |
| Bare Soil Index (BSI) / NDVI | How the land responds; how we measure planting success | MODIS |

For each variable and site we answer the four questions of the challenge: **what** changes, **where**, **by how much**, and **is it statistically significant**.

## From data to action
| Finding | Action |
|---|---|
| Wind direction and strength | Place sand barriers (palm-frond fences) across the dominant wind |
| Rare, strong rain events | Harvest runoff: zaï pits, half-moons, water pans, sand dams |
| Soil moisture and temperature | Choose native species suited to each site; mulch and shade |
| BSI / NDVI | Monitor results: BSI should fall, NDVI should rise |

## Repository map
```
README.md                      <- you are here
data-analysis/                 <- DATA part (notebook, data, results)
  README.md                    <- start here for the data work
  notebooks/                   <- the Colab notebook
  data/                        <- team data files + data dictionary
  results/                     <- outputs: trends, charts, dashboard
  docs/
    CONTRIBUTING.md            <- how we work together in Git
    IDEAS_AND_ROADMAP.md       <- ideas, extra data, next steps
```
Other parts of the project (website, slides, plant/water research) go in **their own folders** so nobody overwrites anybody.

## Team (fill in)
| Role | Person | Folder |
|---|---|---|
| DATA (notebook, trends) | Ouiam | `data-analysis/` |
| Dashboard / website | _to fill_ | _to fill_ |
| Water harvesting and plants | _to fill_ | _to fill_ |
| Story and pitch | _to fill_ | _to fill_ |

## Honest limits
- NASA grid cells are about 25-50 km: they describe the **regional climate**, not exact planting spots.
- A trend is **not** a cause. "No demonstrated trend" is a valid result.
- The BSI is a *change proxy only*. Location of the team CSV files must be confirmed.

## Data and AI use
All data comes from NASA (Earthdata, POWER) and MODIS products, listed with versions in `data-analysis/results/data_provenance.csv` after running the notebook. AI tools were used to help write code and documentation, as allowed by the hackathon.
