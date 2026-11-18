# Profile design source

The public profile uses self-contained SVG artwork, real repository links, a collapsible public-language panel and a text version. Desktop and mobile are separate compositions selected with HTML picture elements. SVG animation traces data flow and weekly activity, with static reduced-motion alternatives. No scripts, external fonts or external image services run in the README.

Direction: cohesive black and graphite surfaces, restrained cyan/blue highlights, Manrope typography, semantic backend diagrams and real technology marks in brand colors. The original dark phone reference sets the restrained tone. PostgreSQL is a first-class stack item; SQLite/libSQL is specific to the Jirah project. No fake metrics, badges, pipeline status or application screenshots.

Refresh public data with `python design/update_activity.py`, then render with `python design/generate_profile.py` and validate with `python design/check_profile.py`. Python plus fonttools 4.65.0 is required. All text is outlined to preserve typography on GitHub. The generator checks line widths and records text bounds for inspection. Commit the generated assets with the README.

The profile-activity workflow runs daily at 09:17 UTC, and also supports manual refresh. It reads only public repositories, public language byte counts and GitHub's public contribution calendars. Each source calendar's tooltip sum must match GitHub's heading; the complete rolling-year date window must be present before a snapshot can replace the previous one. The calendar is in UTC; the refresh date is displayed in Ecuador time. Private data that is not publicly visible is excluded. A failed refresh leaves the last committed assets intact. Statistics are dated snapshots refreshed by the workflow, not browser-side live counters.

The language breakdown measures code bytes across owned public non-fork repositories, excluding this profile. It is not a measure of proficiency. Repository cards and the activity chart link to GitHub's actual interfaces; the native Pinned and Contributions sections retain GitHub's own styling.

Manrope comes from Google Fonts, under the SIL Open Font License included in fonts/OFL.txt. Source: https://github.com/google/fonts/tree/main/ofl/manrope

Technology marks come from Simple Icons (CC0), https://github.com/simple-icons/simple-icons. Brand names and logos belong to their respective owners. Outline navigation and workflow glyphs follow Tabler Icons (MIT), https://github.com/tabler/tabler-icons.

Node.js, TypeScript, Express, Prisma, Docker and Vitest are supported by the reviewed public repositories. CI/CD is included as confirmed by Ariel; no successful pipeline or deployment is claimed. Jirah uses SQLite/libSQL, not PostgreSQL.
