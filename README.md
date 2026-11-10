# claude-plugins

Personal Claude Code plugin marketplace.

| Plugin | Skill | What it does |
| --- | --- | --- |
| `book-doc` | `book-doc` | Book-style technical guides as HTML and LaTeX/PDF |
| `python-style` | `python-style` | Python code style conventions |
| `isaaclab-style` | `isaaclab-config` | Isaac Lab configclass conventions |

## Install

```bash
claude plugin marketplace add gunnxx/claude-plugins

# everywhere
claude plugin install book-doc@gunnxx-plugins
claude plugin install python-style@gunnxx-plugins

# per project, from inside an Isaac Lab repo
claude plugin install isaaclab-style@gunnxx-plugins --scope project
```

## Update

Bump `version` in the plugin's `.claude-plugin/plugin.json`, push, then on each machine:

```bash
claude plugin marketplace update gunnxx-plugins
claude plugin update <plugin>@gunnxx-plugins
```
