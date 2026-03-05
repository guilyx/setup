# Diagram Snippets

Reusable Mermaid snippets for issue discussions, design docs, or PR descriptions.

## 1) Layered Architecture

```mermaid
graph TD
  A[Config YAML] --> B[CLI / Web UI]
  B --> C[Ansible Playbooks]
  C --> D[Roles]
  D --> E[Hosts]
```

## 2) Dev Setup Pipeline

```mermaid
graph LR
  A[run-dev.sh] --> B[setup_cli dev]
  B --> C[ansible-playbook playbooks/dev.yml]
  C --> D[common role]
  C --> E[dev role]
  C --> F[dotfiles role]
```

## 3) VPS Setup Pipeline

```mermaid
graph LR
  A[run-vps.sh] --> B[setup_cli vps]
  B --> C[ansible-playbook playbooks/vps.yml]
  C --> D[common role]
  C --> E[vps role]
  C --> F[reverse_proxy role]
```

## 4) Incident Response Loop

```mermaid
flowchart TD
  A[Failure observed] --> B[Check mode rerun]
  B --> C[Scope with --limit]
  C --> D[Fix config/inventory]
  D --> E[Re-apply]
  E --> F[Verify]
  F -->|not ok| B
  F -->|ok| G[Close incident]
```

## Optional Excalidraw Snippet Template

If you want a visual whiteboard style, paste this markdown block in docs and replace with an exported PNG/SVG from Excalidraw:

```markdown
![Setup architecture whiteboard](./assets/setup-architecture-excalidraw.svg)
```

Use this naming convention for assets:

- `docs/assets/<topic>-excalidraw.svg`
- `docs/assets/<topic>-excalidraw.png`
