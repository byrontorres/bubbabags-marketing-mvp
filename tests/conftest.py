"""Fixtures para pytest."""
import pytest
import pandas as pd


@pytest.fixture
def sample_campaign_data():
    return pd.DataFrame({
        "campaign_id": ["c1", "c2"],
        "campaign_name": ["Campaign A", "Campaign B"],
        "impressions": [10000, 15000],
        "clicks": [200, 450],
        "cost": [500, 750],
        "revenue": [2000, 3000]
    })
