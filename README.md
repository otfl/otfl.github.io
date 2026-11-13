# OTFL website

The website of the (Opto)electronics and Thin Films Laboratory, IIT Gandhinagar.

**Live site:** https://otfl.github.io

You never need to touch any code. All the words live in simple text files in the `data/` folder, and all the photos live in the `images/` folder. When you save a change on GitHub, the website rebuilds itself and goes live in about **1–2 minutes**.

---

## Where everything is

| What you want to change | File to edit | Photos go in |
|---|---|---|
| News | `data/news.yml` | – |
| People (PhD, MTech, staff, alumni, PI) | `data/team.yml` | `images/team/` |
| Journal papers, conference talks, patents | `data/publications.yml` | – |
| Grants | `data/grants.yml` | – |
| Student awards | `data/awards.yml` | – |
| Courses | `data/courses.yml` | – |
| Research areas + research highlight strip | `data/research.yml` | `images/highlights/` |
| Lab instruments | `data/facilities.yml` | `images/facilities/` |
| Gallery | `data/gallery.yml` | `images/gallery/` |
| About text, openings, address, email, big photos | `data/site.yml` | `images/site/` |

---

## How to edit text (example: add a news item)

1. Open the repository on GitHub and click the `data` folder, then `news.yml`.
2. Click the **pencil icon** (top right of the file) to edit.
3. At the top of the list, add a new entry in the same shape as the others:
   ```yaml
   - date: November 2026
     text: Dushyant Dabhi presented his work on NbN thin films at ICFAST 2026.
     link: https://example.com/optional-link
   ```
   The `link:` line is optional. Delete it if there is no link.
4. Click **Commit changes…** (green button), then **Commit changes** again.
5. Wait 1–2 minutes and refresh the website.

## How to add a photo (example: a new PhD student)

1. Go to `images/team/`, click **Add file → Upload files**, and drag the photo in.
   Name it simply, e.g. `abhinav-rana.jpg` (lowercase, dashes instead of spaces).
   Phone photos are fine: the site shrinks them automatically.
2. Click **Commit changes**.
3. Open `data/team.yml`, click the pencil, and add the person under `phd_scholars:`:
   ```yaml
   - name: New Student Name
     photo: new-student-name.jpg
     details:
     - PhD, Joined 2026
     - MSc, Physics, Some University, 2025
   ```
4. Commit. Done.

To add a **gallery** photo: upload it to `images/gallery/`, then add its file name as a new line at the top of `data/gallery.yml`, e.g. `- diwali-2026.jpg`.

To **replace** a photo without changing any text: upload a new photo with **exactly the same file name** into the same folder. GitHub will replace the old one.

## Common tasks

- **Student graduates:** in `data/team.yml`, cut their block from `phd_scholars:` and paste it under `alumni:`. Replace `details:` with a line like
  `note: PhD 2027; currently a Postdoc at …`
- **New paper:** in `data/publications.yml`, add at the top of `journal:`:
  ```yaml
  - year: 2026
    text: Author One, Author Two, Emila Panda. Title of the paper, Journal Name, volume, page, 2026.
    link: https://doi.org/10.xxxx/xxxxx
  ```
  Chemical formulas (TiO2, Sm2Co17, NbN…) get subscripts automatically, and "Emila Panda" is made bold automatically. The counts on the home page update automatically too.

## Rules that avoid mistakes

- **Indentation matters.** Keep the same spaces as the entries around yours. Use spaces, never the Tab key.
- Each list item starts with `- ` (dash + space).
- If your text contains a **colon followed by a space** (like `Title: subtitle`), wrap the whole text in quotes:
  `text: "Award: Best Poster at MRSI 2026"`
- Photo file names must match **exactly**, including `.jpg` vs `.jpeg` and capital letters.

## If something goes wrong

- Click the **Actions** tab at the top of the repository. A red ✗ means the last change had a mistake. Click it to see which file and which line. Fix it the same way you edited, and commit again.
- Every change is saved in history. To undo, open the file, click **History**, pick the earlier version, and copy its text back.
- The website keeps showing the last good version until the mistake is fixed, so a typo never takes the site down.

## For developers

- `template.html` is the page design (CSS + animations).
- `build.py` reads `data/*.yml`, fills the template, resizes images, and writes `_site/`.
- `.github/workflows/deploy.yml` runs the build and publishes to GitHub Pages on every push to `main`.
- To preview on your computer: `pip install pyyaml pillow && python build.py`, then open `_site/index.html`.
