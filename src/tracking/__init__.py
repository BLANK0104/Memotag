"""
MemoTag Longitudinal Tracking Module

This module provides tools for tracking speech patterns over time,
establishing personalized baselines, and detecting cognitive changes.
"""

from .longitudinal_tracker import LongitudinalTracker

__version__ = '1.0.0'
__all__ = ['LongitudinalTracker']

# Constants
DEFAULT_BASELINE_MIN_SAMPLES = 3
DEFAULT_ALERT_THRESHOLD_MILD = 1.5  # Standard deviations
DEFAULT_ALERT_THRESHOLD_MODERATE = 2.0
DEFAULT_ALERT_THRESHOLD_SEVERE = 3.0
