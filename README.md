# English Listening Agent V6

Cloud version of the user's V5 workflow: BBC RSS headlines/brief summaries → British English Sonia voice MP3 + aligned English SRT → GitHub Pages → ntfy iPhone notification. No OpenAI API key. The public website and MP3s are accessible to anyone with the link. Only use public, non-sensitive material.

## Deploy (new public repository with README already created)
1. Ensure **Settings → Secrets and variables → Actions** has repository secret `NTFY_TOPIC` matching the topic subscribed to on iPhone. Never commit this value.
2. Extract the ZIP. Open the repository **Code → Add file → Upload files** and upload `build.py`, `notify.py`, `README.md`, `.gitignore`, and the `site` folder (including `site/index.html`). **GitHub's web uploader may not preserve hidden `.github` directories reliably**: create workflow files separately via **Add file → Create new file**, typing exactly `.github/workflows/build.yml` and `.github/workflows/notify.yml`, then paste their contents from the ZIP. You may instead use git on your Mac to upload the full tree.
3. **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. **Settings → Actions → General → Workflow permissions → Read and write permissions** (if selectable). This allows the build to commit public generated files to main. Workflow `permissions` are also declared in YAML. If org policy blocks this, the push will fail.
5. Open **Actions → Build listening lesson and publish Pages → Run workflow → target: today**. Wait for a green result and Pages URL. First deployment requires Pages to be enabled.
6. Open the Pages URL and verify that the player loads MP3, SRT and source links. Press play (iPhone autoplay is intentionally not attempted).
7. Open **Actions → Push daily lesson to iPhone → Run workflow**. Confirm iPhone receives the MP3 and tapping notification opens the Pages player. Do this only after today's build succeeds.

## Daily schedule (Asia/Shanghai)
- 22:05: build **tomorrow's** lesson, commit up to 14 days of public MP3/SRT/text, deploy Pages.
- 08:30: send MP3 attachment with a Click URL for the static player.

GitHub Actions cron is **best effort**: scheduled runs can be delayed or dropped, especially around load peaks. The notify job refuses to send an outdated lesson. The system is independent of your Mac being on, but it does **not guarantee an exact 08:30 delivery**. Schedules use UTC cron, and assume Beijing time is UTC+8 year-round.

## Limitations
- RSS source material is *headlines and brief descriptions*, not full articles. It uses simple keyword ranking, not an LLM. English text and subtitles only; no Chinese translation or autonomous AI reasoning.
- `edge-tts` contacts Microsoft's online TTS service. No OpenAI tokens, but it may be rate-limited or change availability.
- GitHub Pages is public. GitHub commits permanently record published text/audio even after later deletion from the current site. Do not add private user uploads or credentials.
- ntfy.sh is third-party, not end-to-end private. Topic is a hard-to-guess routing name, not strong authentication. Public ntfy service can impose attachment size/retention limits.
- Scheduled workflows in public repos can be disabled after extended inactivity. GitHub billing/free tier policies can change.
- If the daily build fails or GitHub Pages deploy fails, the morning notification may not contain fresh material; inspect Actions logs.
- Existing V5 local launchd jobs remain installed on Mac and may send duplicate notifications if the Mac wakes at those times. Disable V5 jobs when V6 is verified.

## Developer tests
`python -m py_compile build.py notify.py` and `node --check` on extracted JS are useful static checks. Full RSS/edge-tts/ntfy/Pages end-to-end requires GitHub network access and user's secret.
