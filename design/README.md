# Profile design source

The public profile uses self-contained SVG artwork, real repository links and a collapsible text version. Desktop and mobile are separate compositions selected with HTML picture elements. No scripts, external fonts or external image services run in the README.

Direction: graphite, silver and a muted sage accent, Manrope typography, semantic backend diagrams and real technology marks. The original dark phone reference sets the restrained tone. No fake metrics, badges, pipeline status or application screenshots.

Generate with Python and fontTools: `python design/generate_profile.py`. All text is outlined to preserve typography on GitHub. The generator checks line widths and records text bounds for inspection. Commit the generated assets with the README.

Manrope comes from Google Fonts, under the SIL Open Font License included in fonts/OFL.txt. Source: https://github.com/google/fonts/tree/main/ofl/manrope

Technology marks come from Simple Icons (CC0), https://github.com/simple-icons/simple-icons. Brand names and logos belong to their respective owners. Outline navigation and workflow glyphs follow Tabler Icons (MIT), https://github.com/tabler/tabler-icons.

Node.js, TypeScript, Express, Prisma, Docker and Vitest are supported by the reviewed public repositories. CI/CD is included as confirmed by Ariel; no successful pipeline or deployment is claimed. Jirah uses SQLite/libSQL, not PostgreSQL.
