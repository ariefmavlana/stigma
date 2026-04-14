"""
Management command: seed_data
──────────────────────────────
Populates the database with sample categories and posts for development.

Usage:
    uv run python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Category, Post


SAMPLE_CATEGORIES = [
    ("Technology", "Explorations at the frontier of software and systems."),
    ("Culture", "Ideas, society, and the world we're building."),
    ("Science", "The natural world, explained and wondered at."),
    ("Opinion", "Perspectives, arguments, and considered takes."),
    ("Design", "The craft of making things good."),
]

SAMPLE_POSTS = [
    {
        "title": "The Quiet Revolution in Database Design",
        "excerpt": "For decades, we chose between SQL and NoSQL. A new generation of databases refuses the distinction.",
        "body": """## The False Dichotomy

For a decade, we were told to choose: relational databases for structure, NoSQL for scale. The dichotomy was clean, marketable, and largely wrong.

The friction wasn't really SQL vs. document stores. It was **schema rigidity vs. query power**. And somewhere between 2018 and 2022, a handful of databases quietly solved both.

## What Changed

The shift happened in three waves:

1. **PostgreSQL grew up** — JSON columns, full-text search, LISTEN/NOTIFY. Postgres didn't become a NoSQL database; it became the only database most teams need.
2. **NewSQL emerged** — CockroachDB, PlanetScale, Neon. Horizontal scaling with ACID guarantees. The promise of the 2010s, finally delivered.
3. **The edge arrived** — SQLite on Fly.io, Turso, Cloudflare D1. The oldest database in the world turned out to be perfectly suited for the newest compute model.

## The Lesson

The best technology decisions aren't about picking winners. They're about understanding *what problem you actually have*. Most teams don't have a Google-scale data problem. They have a **complexity management** problem.

Pick the database that makes your queries readable, your migrations survivable, and your 3am incidents rare. In 2025, that's probably still Postgres.
""",
        "category_name": "Technology",
        "tags": ["databases", "postgres", "engineering"],
        "is_ai_generated": False,
    },
    {
        "title": "On the Aesthetics of Error Messages",
        "excerpt": "A compiler error is a piece of writing. Most are bad. A few are extraordinary. What separates them?",
        "body": """## Error as Communication

Nobody reads documentation until they're stuck. Error messages, then, are the most important prose a software team produces — and the most neglected.

Consider the Elm compiler, famous for error messages like:

> *I was expecting to see a closing parenthesis next, like this: `)`. Maybe you want to add it?*

Compare this to the genre of error that reads:

> `NullPointerException at line 847`

The first treats the programmer as a confused person who deserves an explanation. The second treats them as a machine that failed a checksum.

## What Good Looks Like

The best error messages share three qualities:

**They say what happened.** Not a code, not a stack trace. A sentence. "The connection timed out after 30 seconds."

**They say why it matters.** "This means your changes were not saved."

**They suggest what to do.** "Check your network connection and try again, or contact support at support@example.com."

Rust's borrow checker errors are the gold standard of this form. They're verbose — sometimes embarrassingly so — but they're *correct*, and they treat compiler output as a teaching opportunity.

## The Uncomfortable Truth

Most bad error messages aren't the result of ignorance. They're the result of **prioritisation**. Error copy is written last, by engineers who are tired, and reviewed by nobody.

The fix isn't technical. It's cultural: treat error messages as product copy. Run them through the same review as your marketing page. Your users will notice.
""",
        "category_name": "Design",
        "tags": ["ux", "writing", "developer-experience"],
        "is_ai_generated": False,
    },
    {
        "title": "Why We Overestimate AI and Underestimate Spreadsheets",
        "excerpt": "The most powerful productivity tool in the world isn't a language model. It's a 40-year-old grid.",
        "body": """## The Grid Endures

Every few years, something is going to kill the spreadsheet. Databases in the 90s. Specialized software in the 00s. AI in the 20s. And yet: there are an estimated 1.1 billion spreadsheet users in the world.

Why does the spreadsheet survive?

## Legibility as Superpower

A spreadsheet is radically legible. Every formula is visible. Every dependency is traceable. There are no black boxes. When something is wrong, you can see where the number came from.

This is not a primitive quality. It is an *extremely rare* quality. Most software is opaque by design — the logic is hidden in classes and database calls and API requests. The spreadsheet puts the logic in the cell.

## What AI Gets Wrong About Productivity

The current wave of AI productivity tools optimizes for output — *generate more, faster*. Spreadsheets optimise for something different: **understanding**.

When you build a financial model in Excel, you don't just produce a number. You develop an intuition about the relationships in the model. You see what's sensitive to what. You know the answer because you built the machine that produced it.

AI can generate a financial model faster than any analyst. But it produces understanding in neither the machine nor the person who prompted it.

## The Coexistence

The lesson isn't that AI is bad. It's that tools optimised for **understanding** and tools optimised for **generation** serve different purposes — and we need both.

The spreadsheet will outlast the current AI cycle, just as it outlasted every previous cycle. Not because it's better at generating output. Because nothing else is as good at building the mental model that makes output trustworthy.
""",
        "category_name": "Opinion",
        "tags": ["ai", "productivity", "spreadsheets", "tools"],
        "is_ai_generated": False,
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample categories and blog posts."

    def handle(self, *args, **kwargs):
        # Get or create a superuser to attribute posts to
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(
                self.style.WARNING(
                    "No superuser found. Run 'python manage.py createsuperuser' first."
                )
            )
            return

        # Create categories
        created_categories = {}
        for name, desc in SAMPLE_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            created_categories[name] = cat
            if created:
                self.stdout.write(f"  Created category: {name}")

        # Create posts
        for post_data in SAMPLE_POSTS:
            if Post.objects.filter(title=post_data["title"]).exists():
                self.stdout.write(f"  Skipped (exists): {post_data['title']}")
                continue

            post = Post(
                title=post_data["title"],
                excerpt=post_data["excerpt"],
                body=post_data["body"],
                author=admin,
                category=created_categories.get(post_data["category_name"]),
                status=Post.Status.PUBLISHED,
                is_ai_generated=post_data.get("is_ai_generated", False),
                published_at=timezone.now(),
            )
            post.save()
            post.tags.add(*post_data.get("tags", []))
            self.stdout.write(self.style.SUCCESS(f"  Created post: {post.title}"))

        self.stdout.write(self.style.SUCCESS("\n✓ Seed data loaded successfully."))
