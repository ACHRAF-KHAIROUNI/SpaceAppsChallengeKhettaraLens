# How we work together

## Five rules
1. **One owner per folder.** Only add or change files in your own folder.
2. **One source of numbers:** `data-analysis/results/trend_results.csv`. Never retype a number by hand.
3. **Everything delivered is in English** (code comments, dashboard, slides, README).
4. **Every number has a source** (NASA product and period).
5. **Never commit secrets** (Earthdata password, Meteomatics login, tokens).

## Simple Git workflow (no command line needed)
1. Ask the repository owner to add you in *Settings → Collaborators*. Accept the email invitation.
2. On the repository page, choose a **branch** in the branch menu (create your own, for example `data-analysis`, by typing its name).
3. *Add file → Upload files* → drag your files → write a short message (for example `Add trend results`) → **Commit**.
4. When your work is ready, open a **Pull request** and ask the owner to merge.

## Using the command line (optional)
```bash
git clone https://github.com/ACHRAF-KHAIROUNI/SpaceAppsChallengeWebSite.git
cd SpaceAppsChallengeWebSite
git checkout -b data-analysis        # create your branch
# ... add or edit files ...
git add .
git commit -m "Add trend results"
git push -u origin data-analysis
git pull origin main                 # get others' work before pushing again
```

## Commit messages
Short and clear: `Add notebook EN`, `Update results after 2025 data`, `Fix typo in README`.
