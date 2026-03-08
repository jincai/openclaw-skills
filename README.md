# OpenClaw Skills

Reusable skills for [OpenClaw](https://openclaw.ai) and [Claude Code](https://claude.com/claude-code).

## Skills

| Skill | Description |
|-------|-------------|
| [oura](./oura/) | Sync and analyze Oura Ring health data — sleep debt tracking, weekly reports, zero dependencies |
| [openclaw-logs](./openclaw-logs/) | Query and analyze OpenClaw gateway logs with time range filtering, category grouping, and noise suppression |
| [infographic](./infographic/) | Generate professional infographic images from articles/tweets using HTML + Playwright high-DPI screenshot |

## Installation

### Claude Code

Copy the skill directory to your Claude Code skills folder:

```bash
cp -r openclaw-logs ~/.claude/skills/
```

### OpenClaw

Skills are automatically available when placed in `~/.claude/skills/` on the machine running the OpenClaw gateway.

## License

MIT
