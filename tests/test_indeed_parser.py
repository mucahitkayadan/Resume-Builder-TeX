"""Test Indeed parser module."""

import pytest

from src.parsers.indeed_parser import parse_indeed_job


def test_parse_indeed_job():
    """Test parsing Indeed job posting."""
    # Sample HTML content
    html_content = """
    <div>
        <h1 class="jobsearch-JobInfoHeader-title">Software Engineer</h1>
        <div class="jobsearch-InlineCompanyRating"><a>Example Company</a></div>
        <div class="jobsearch-JobInfoHeader-subtitle">New York, NY</div>
        <div id="jobDescriptionText">
            We are looking for a Software Engineer...
        </div>
        <span class="jobsearch-JobMetadataHeader-item">$100,000 - $150,000</span>
        <div class="jobsearch-JobMetadataHeader-item">Full-time</div>
        <span class="jobsearch-JobMetadataFooter-item">Posted 2 days ago</span>
    </div>
    """

    # Parse the job posting
    result = parse_indeed_job(html_content)

    # Assert the results
    assert result["title"] == "Software Engineer"
    assert result["company"] == "Example Company"
    assert result["location"] == "New York, NY"
    assert "looking for a Software Engineer" in result["description"]
    assert result["salary"] == "$100,000 - $150,000"
    assert result["job_type"] == "Full-time"
    assert result["posted_date"] == "Posted 2 days ago"


def test_parse_indeed_job_missing_fields():
    """Test parsing Indeed job posting with missing fields."""
    # Sample HTML content with missing fields
    html_content = """
    <div>
        <h1 class="jobsearch-JobInfoHeader-title">Software Engineer</h1>
        <div id="jobDescriptionText">
            We are looking for a Software Engineer...
        </div>
    </div>
    """

    # Parse the job posting
    result = parse_indeed_job(html_content)

    # Assert the results
    assert result["title"] == "Software Engineer"
    assert result["company"] is None
    assert result["location"] is None
    assert "looking for a Software Engineer" in result["description"]
    assert result["salary"] is None
    assert result["job_type"] is None
    assert result["posted_date"] is None


def test_parse_indeed_job_invalid_html():
    """Test parsing Indeed job posting with invalid HTML."""
    # Invalid HTML content
    html_content = "Not valid HTML"

    # Parse the job posting
    result = parse_indeed_job(html_content)

    # Assert all fields are None
    assert all(value is None for value in result.values())
