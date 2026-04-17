from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from django.db.models import Q
from blog.models import Post

class SearchBlogInput(BaseModel):
    """Input schema for SearchBlogTool."""
    query: str = Field(..., description="The search query to find relevant blog posts.")

class SearchBlogTool(BaseTool):
    name: str = "search_blog_tool"
    description: str = (
        "Search the internal blog database for existing published posts. "
        "Returns a list of matching post titles and their internal URLs. "
        "Use this for internal linking only."
    )
    args_schema: Type[BaseModel] = SearchBlogInput

    def _run(self, query: str) -> str:
        # We only want published posts to avoid linking to drafts
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(body__icontains=query) |
            Q(excerpt__icontains=query),
            status=Post.Status.PUBLISHED
        ).only('title', 'slug')[:5]

        if not posts.exists():
            return "No relevant internal posts found for this query."

        results = []
        for post in posts:
            results.append(f"- Title: {post.title} | URL: /posts/{post.slug}/")
        
        return "\n".join(results)
