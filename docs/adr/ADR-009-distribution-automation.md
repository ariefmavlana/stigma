# ADR-009: Multi-Platform Distribution Automation

## Status
Accepted

## Context
Writing a blog post is only half the battle. Distribution across social platforms usually takes significant manual effort (summarizing for Twitter, rewording for LinkedIn, drafting newsletter blurbs). To maximize the value of the Stigma platform, we need to automate this meta-content generation.

## Decision
We decided to integrate "Promotion Drafting" directly into the Content Editor's final task.

1. **Schema Expansion**: Added `social_twitter` (thread array), `social_linkedin` (long-form), and `newsletter_copy` (condensed) to the Editor's required JSON output.
2. **Tabbed UI**: Implemented a "Promotion Dashboard" in `status_done.html` using Hyperscript for client-side state management (tabs).
3. **Clipboard Integration**: Built-in "Copy to Clipboard" functionality for each distribution channel to facilitate one-click multi-platform publishing.

## Consequences
- **Zero-effort Promotion**: Editors receive ready-to-use social copy immediately after generation.
- **Consistency**: High-quality summaries that maintain the original post's voice.
- **Frontend Complexity**: Minor increase in Hyperscript usage for the tabbed interface, but kept lightweight without requiring a JS framework.
