"""
mock-jutsu — Social Media Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Format rules:
  username / handle — Twitter/X spec: 4-15 chars, [a-z0-9_], no leading/trailing underscore
  hashtag           — # + [a-zA-Z][a-zA-Z0-9]{1,29} (no spaces, no special chars)
  bio               — max 160 chars (Twitter bio limit)
  follower_count    — realistic distribution (power law: most accounts have few followers)
"""

import secrets
import string

# ── Word pools ────────────────────────────────────────────────────────────────

_ADJECTIVES = [
    'cool', 'real', 'official', 'the', 'pro', 'dev', 'tech', 'digital',
    'creative', 'smart', 'bold', 'swift', 'sharp', 'deep', 'fast',
]

_NOUNS = [
    'dev', 'coder', 'maker', 'builder', 'hacker', 'pilot', 'ninja',
    'guru', 'wolf', 'fox', 'hawk', 'bear', 'eagle', 'tiger', 'lion',
    'pixel', 'byte', 'node', 'stack', 'loop', 'query', 'cache',
]

_TOPICS = [
    'AI', 'Tech', 'Code', 'Data', 'Cloud', 'Web', 'Mobile', 'Security',
    'Design', 'Product', 'Startup', 'Finance', 'Crypto', 'Gaming', 'Music',
    'Travel', 'Food', 'Fitness', 'Science', 'Space', 'Nature', 'Art',
]

_BIO_TEMPLATES = [
    "Building the future one line of code at a time.",
    "Developer, maker, and coffee enthusiast.",
    "Turning ideas into products since day one.",
    "Passionate about technology and design.",
    "Open source advocate. Always learning.",
    "Entrepreneur | Engineer | Dreamer.",
    "Making the web a better place.",
    "Data nerd. Problem solver. Cat person.",
    "Exploring the intersection of AI and creativity.",
    "Full-stack developer by day, gamer by night.",
    "Startup founder. Failed fast, learned faster.",
    "Minimalist. Futurist. Software craftsman.",
    "I ship products people actually use.",
    "Code. Coffee. Repeat.",
    "Engineering manager who still loves to code.",
]


# ── Generator ─────────────────────────────────────────────────────────────────

class SocialGenerator:
    """Username, handle, hashtag, bio, follower_count — Twitter/X spec compliant."""

    def generate(self, data_type: str, **kwargs):
        dt = data_type.lower().strip()

        if dt == 'username':
            return self._username()
        if dt == 'handle':
            return '@' + self._username()
        if dt == 'hashtag':
            return self._hashtag()
        if dt == 'bio':
            return secrets.choice(_BIO_TEMPLATES)
        if dt == 'follower_count':
            return str(self._follower_count())

        return f"ERROR: Unknown DataType '{dt}'"

    # ── Username ──────────────────────────────────────────────────────────────

    def _username(self) -> str:
        """Twitter/X compliant: 4-15 chars, [a-z0-9_], no leading/trailing underscore."""
        strategy = secrets.randbelow(3)

        if strategy == 0:
            # adj + noun: e.g. "cooldev", "realninja"
            base = secrets.choice(_ADJECTIVES) + secrets.choice(_NOUNS)
        elif strategy == 1:
            # noun + 2-4 digits: e.g. "dev42", "coder2025"
            base = secrets.choice(_NOUNS) + str(secrets.randbelow(9000) + 1000)
        else:
            # adj + noun + 2 digits: e.g. "boldcoder77"
            base = (secrets.choice(_ADJECTIVES) + secrets.choice(_NOUNS)
                    + str(secrets.randbelow(90) + 10))

        # Clamp to 15 chars, ensure at least 4
        base = base[:15]
        if len(base) < 4:
            base = base + str(secrets.randbelow(90) + 10)
        return base

    # ── Hashtag ───────────────────────────────────────────────────────────────

    def _hashtag(self) -> str:
        """# + topic word + optional digits. Only [a-zA-Z0-9], starts with letter."""
        topic = secrets.choice(_TOPICS)
        if secrets.randbelow(2) == 0:
            suffix = str(secrets.randbelow(9000) + 1000)
            return '#' + topic + suffix
        return '#' + topic

    # ── Follower count ────────────────────────────────────────────────────────

    def _follower_count(self) -> int:
        """Realistic power-law distribution: most accounts small, few large."""
        tier = secrets.randbelow(100)
        if tier < 40:
            return secrets.randbelow(500)           # 0–499 (micro)
        if tier < 65:
            return secrets.randbelow(4500) + 500    # 500–4999
        if tier < 80:
            return secrets.randbelow(45000) + 5000  # 5k–49k
        if tier < 92:
            return secrets.randbelow(450000) + 50000    # 50k–499k
        if tier < 98:
            return secrets.randbelow(4500000) + 500000  # 500k–4.99M
        return secrets.randbelow(45000000) + 5000000    # 5M–49M
