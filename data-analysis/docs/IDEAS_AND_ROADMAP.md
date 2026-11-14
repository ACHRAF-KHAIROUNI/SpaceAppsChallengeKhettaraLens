# Ideas and roadmap

## The investigation story
1. **Wind** transports sand.
2. **Dry soil** makes it mobile; moist soil helps plants.
3. **Rain** brings water: rare but sometimes extreme.
4. **Heat** dries and stresses young plants.
5. **Bare soil / vegetation** (BSI, NDVI) shows how the land responds.

## Solutions we propose
1. **Stop the sand:** windbreak fences (palm fronds, straw) across the dominant wind.
2. **Capture water:** zaï pits and half-moons (Sahel, Morocco), water pans and sand dams (flash floods), traditional khettaras and matfiyas; fog nets and wind-pumped boreholes for regions with almost no rain (Namib, Kalahari).
3. **Plant native shrubs** in those pits (to validate with local botanical expertise). Avoid invasive species such as *Prosopis juliflora*.
4. **Choose the timing:** in the monthly rain data the wettest months are September-November and March-April; June-July are very dry. This is a hypothesis, not a rule.
5. **Monitor:** BSI should go down, NDVI up; field visit before any real planting.

## Data we could add (by priority)
| Priority | Data | Why | Effort |
|---|---|---|---|
| 1 | NDVI (MODIS via Earth Engine) | Measures vegetation and planting success | Medium |
| 2 | Hourly wind (Meteomatics) | Sand-transport direction, barrier placement | Medium |
| 3 | GPM IMERG daily rain | Better resolution for flash floods | Medium |
| 4 | SMAP soil moisture | Cross-check GLDAS with a satellite measurement | Medium |
| 5 | Land cover (MODIS MCD12Q1) | Where sand, crops and oases are | Easy |
| 6 | Elevation (NASADEM) | Where water runs off (place half-moons, pans) | Medium |
| 7 | Landsat / Sentinel maps (10-30 m) | Exact placement of plantations | Heavy |

## What we do not claim
- NASA cells are 25-50 km: regional climate, not exact planting spots.
- A trend is not a cause: it does not prove by itself that sand encroachment increases.
- Rain → BSI link is weak in our first numbers (r about -0.15); the 2024 drop after heavy rain is a lead.

## Checklist for submission
- [ ] Project summary in English
- [ ] Notebook + repository with READMEs
- [ ] Dashboard in English
- [ ] Slides / video if required
- [ ] Data list with versions (`data_provenance.csv`)
- [ ] AI-use statement if the rules ask for it
