# Snake Game — Session Log

## Last Session
2026-03-03 — Full build, deployment, and Railway/DNS troubleshooting. Live.

## Completed This Session (2026-03-03)

- Built Snake game — Python Flask backend, HTML5 Canvas frontend
- Initial architecture: server-side game loop over WebSocket (Flask-SocketIO + eventlet)
- Published to GitHub: https://github.com/iamdavebock/snake-game (public)
- Deployed to Railway via GraphQL API (no browser/CLI)
- Opened UFW port 5050 (LAN only) for local access at http://10.108.14.232:5050
- Configured custom domain snake.davebock.au via Railway API + Cloudflare DNS API
- Resolved Railway routing issues: created service domain first, added TXT verification record
- Rewrote game to client-side JS — eliminated WebSocket latency, smooth controls
- Enabled Cloudflare proxy (orange cloud) for SSL on snake.davebock.au
- Added footer: "visit davebock.au | Built on Ember"
- Set GitHub repo homepage to https://snake.davebock.au
- Created global credentials file: /mnt/agents/apps/.env
- Full docs: README.md, docs/architecture.md, docs/game-logic.md, LICENSE

## In Progress

None.

## Next Steps

None outstanding — project is complete and live.

Possible enhancements (not requested):
- High score persistence
- Speed increase as score grows
- Multiple difficulty levels

## Blockers

None.

## Access

| Resource | URL |
|----------|-----|
| Live game | https://snake.davebock.au |
| GitHub | https://github.com/iamdavebock/snake-game |
| Local (LAN) | http://10.108.14.232:5050 |
| Railway dashboard | https://railway.com (project: grateful-vitality) |
| Railway service domain | https://snake-game-production-f5d2.up.railway.app |
