from __future__ import annotations

from typing import List

from .models import Provider

DEFAULT_PROVIDERS: List[Provider] = [
    Provider(
        name="github",
        pattern="https://github.com/{username}",
        kind="username",
        description="GitHub profile",
    ),
    Provider(
        name="twitter",
        pattern="https://x.com/{username}",
        kind="username",
        description="X/Twitter profile",
    ),
    Provider(
        name="instagram",
        pattern="https://www.instagram.com/{username}/",
        kind="username",
        description="Instagram profile",
    ),
    Provider(
        name="linkedin",
        pattern="https://www.linkedin.com/in/{username}",
        kind="username",
        description="LinkedIn profile",
    ),
    Provider(
        name="reddit",
        pattern="https://www.reddit.com/user/{username}",
        kind="username",
        description="Reddit profile",
    ),
    Provider(
        name="youtube",
        pattern="https://www.youtube.com/@{username}",
        kind="username",
        description="YouTube channel",
    ),
    Provider(
        name="mastodon",
        pattern="https://mastodon.social/@{username}",
        kind="username",
        description="Mastodon profile",
    ),
    Provider(
        name="tumblr",
        pattern="https://{username}.tumblr.com/",
        kind="username",
        description="Tumblr profile",
    ),
    Provider(
        name="medium",
        pattern="https://medium.com/@{username}",
        kind="username",
        description="Medium profile",
    ),
    Provider(
        name="stackoverflow",
        pattern="https://stackoverflow.com/users/{username}",
        kind="username",
        description="Stack Overflow profile",
    ),
    Provider(
        name="hackernews",
        pattern="https://news.ycombinator.com/user?id={username}",
        kind="username",
        description="Hacker News profile",
    ),
    Provider(
        name="gitlab",
        pattern="https://gitlab.com/{username}",
        kind="username",
        description="GitLab profile",
    ),
]

EMAIL_PROVIDERS: List[Provider] = [
    Provider(
        name="search_google",
        pattern="https://www.google.com/search?q={email}",
        kind="email",
        description="Google search for the email address",
    ),
    Provider(
        name="search_duckduckgo",
        pattern="https://duckduckgo.com/?q={email}",
        kind="email",
        description="DuckDuckGo search for the email address",
    ),
    Provider(
        name="haveibeenpwned",
        pattern="https://haveibeenpwned.com/unifiedsearch/{email}",
        kind="email",
        description="Have I Been Pwned search",
    ),
    Provider(
        name="github_email",
        pattern="https://github.com/search?q={email}&type=users",
        kind="email",
        description="GitHub search for the email address",
    ),
]
