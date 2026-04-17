# ADR-008: Auto-Internal Linking via Custom Django Tools

## Status
Accepted

## Context
A key requirement for the Stigma platform is SEO-optimised content. Internal linking (linking between related posts) is a crucial SEO best practice that keeps readers on the site longer. Manually finding relevant posts during AI generation is inefficient.

## Decision
We decided to empower the `content_editor` agent with a custom CrewAI tool that has read-only access to the internal blog database.

1. **Custom Tool**: We implemented `SearchBlogTool` in `ai_crew/tools.py` using Django's ORM.
2. **Safety**: The tool strictly filters for `status=Post.Status.PUBLISHED` to ensure the AI never links to private drafts.
3. **Integration**: The tool is attached to the Editor agent, who uses it during the final "Edit & Finalise" task.
4. **Markdown Formatting**: The AI is instructed to use standard Markdown links `[Title](/posts/slug/)` which are compatible with our routing system.

## Consequences
- **Improved SEO**: Automated discovery of relevant content for every new post.
- **Dynamic Awareness**: The AI is no longer "blind" to the existing archive; it becomes a self-aware editorial system.
- **Resource Usage**: Slight overhead of database queries during the Editor's execution phase, but negligible compared to LLM inference.
