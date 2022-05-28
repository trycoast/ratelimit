'''
Function decorator for rate limiting.
'''
from ratelimit.decorators import RateLimitDecorator
from ratelimit.exception import RateLimitException

ratelimit = RateLimitDecorator

__all__ = [
    'RateLimitException',
    'ratelimit',
]

__version__ = '0.0.1'
