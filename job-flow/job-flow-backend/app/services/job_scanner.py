"""
Job Scanner Service - Automated job discovery on various platforms

This service uses Playwright to scan job boards and discover new opportunities.
It extracts job details, scores them based on user preferences, and saves them
to the database for user review.

Supported platforms:
- LinkedIn (with Easy Apply filter)
- Indeed (future)
- Glassdoor (future)
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import JobListing, UserProfile
from app.schemas.job import JobListingCreate


logger = logging.getLogger(__name__)


class JobScanner:
    """
    Automated job discovery service using Playwright browser automation.

    Features:
    - Scan multiple platforms for new jobs
    - Extract job details (title, company, location, etc.)
    - Score jobs based on user preferences
    - Detect Easy Apply availability
    - Avoid duplicates
    - Respect rate limits
    """

    def __init__(self, db: Session):
        self.db = db
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def __aenter__(self):
        """Context manager entry - initialize browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=[
                '--disable-blink-features=AutomationControlled',  # Avoid detection
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        # Create context with realistic headers
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def scan_all_platforms(
        self,
        user_profile: UserProfile,
        max_jobs_per_platform: int = 50
    ) -> Dict[str, int]:
        """
        Scan all supported platforms for new jobs.

        Args:
            user_profile: User profile with search preferences
            max_jobs_per_platform: Maximum jobs to fetch per platform

        Returns:
            Dictionary with platform names and job counts found
        """
        results = {}

        try:
            # LinkedIn
            linkedin_count = await self.scan_linkedin(
                user_profile=user_profile,
                max_jobs=max_jobs_per_platform
            )
            results['linkedin'] = linkedin_count
            logger.info(f"LinkedIn scan complete: {linkedin_count} jobs found")

        except Exception as e:
            logger.error(f"Error during job scanning: {str(e)}", exc_info=True)
            results['error'] = str(e)

        return results

    async def scan_linkedin(
        self,
        user_profile: UserProfile,
        max_jobs: int = 50
    ) -> int:
        """
        Scan LinkedIn for jobs matching user preferences.

        This method:
        1. Builds search URL based on user preferences
        2. Navigates to LinkedIn jobs search
        3. Applies Easy Apply filter
        4. Extracts job cards from search results
        5. Visits each job to get full details
        6. Scores and saves to database

        Args:
            user_profile: User profile with search criteria
            max_jobs: Maximum number of jobs to fetch

        Returns:
            Number of new jobs found and saved
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized. Use async context manager.")

        logger.info(f"Starting LinkedIn scan for user {user_profile.id}")

        # Build search URL based on user preferences
        search_url = self._build_linkedin_search_url(user_profile)
        logger.info(f"LinkedIn search URL: {search_url}")

        page = await self.context.new_page()

        try:
            # Navigate to search results
            await page.goto(search_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)  # Let page settle

            # Handle login if needed (future: add session persistence)
            if await self._is_linkedin_login_page(page):
                logger.warning("LinkedIn login required. Skipping scan. TODO: Add session persistence.")
                return 0

            # Extract job cards from search results
            job_listings = await self._extract_linkedin_job_cards(page, max_jobs)
            logger.info(f"Extracted {len(job_listings)} job cards")

            # Visit each job to get full details and save
            new_jobs_count = 0
            for i, job_data in enumerate(job_listings):
                try:
                    logger.info(f"Processing job {i+1}/{len(job_listings)}: {job_data.get('title')}")

                    # Check if job already exists
                    if self._job_exists(job_data.get('job_id')):
                        logger.debug(f"Job {job_data.get('job_id')} already exists, skipping")
                        continue

                    # Get full job details
                    full_details = await self._get_linkedin_job_details(page, job_data)

                    # Score job based on user preferences
                    match_score = self._score_job(full_details, user_profile)
                    full_details['match_score'] = match_score

                    # Save to database
                    self._save_job(full_details, user_profile.id)
                    new_jobs_count += 1

                    # Rate limiting
                    await asyncio.sleep(1.5)  # Be respectful to LinkedIn

                except Exception as e:
                    logger.error(f"Error processing job {i+1}: {str(e)}")
                    continue

            logger.info(f"LinkedIn scan complete: {new_jobs_count} new jobs saved")
            return new_jobs_count

        finally:
            await page.close()

    def _build_linkedin_search_url(self, user_profile: UserProfile) -> str:
        """
        Build LinkedIn search URL based on user preferences.

        Example: https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=San%20Francisco&f_AL=true
        """
        base_url = "https://www.linkedin.com/jobs/search/?"

        # Build query parameters
        params = {
            'f_AL': 'true',  # Easy Apply only
            'sortBy': 'DD',  # Sort by date (most recent)
        }

        # Add keywords from current title or preferences
        if user_profile.current_title:
            params['keywords'] = user_profile.current_title

        # Add location
        if user_profile.city and user_profile.state:
            params['location'] = f"{user_profile.city}, {user_profile.state}"
        elif user_profile.city:
            params['location'] = user_profile.city

        # Remote filter
        if user_profile.remote_preference == 'remote_only':
            params['f_WT'] = '2'  # Remote only
        elif user_profile.remote_preference == 'hybrid':
            params['f_WT'] = '1,2'  # Hybrid or remote

        return base_url + urlencode(params)

    async def _is_linkedin_login_page(self, page: Page) -> bool:
        """Check if we've been redirected to LinkedIn login"""
        current_url = page.url
        return 'linkedin.com/login' in current_url or 'linkedin.com/uas/login' in current_url

    async def _extract_linkedin_job_cards(self, page: Page, max_jobs: int) -> List[Dict[str, Any]]:
        """
        Extract job cards from LinkedIn search results page.

        LinkedIn job cards contain:
        - Job title
        - Company name
        - Location
        - Job ID
        - Easy Apply badge
        """
        job_listings = []

        try:
            # Wait for job cards to load
            await page.wait_for_selector('.jobs-search__results-list', timeout=10000)

            # Scroll to load more jobs
            for _ in range(3):  # Scroll 3 times to load ~30 jobs
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)

            # Extract job cards
            job_cards = await page.query_selector_all('li.jobs-search-results__list-item')
            logger.info(f"Found {len(job_cards)} job cards on page")

            for card in job_cards[:max_jobs]:
                try:
                    job_data = await self._parse_linkedin_job_card(card)
                    if job_data:
                        job_listings.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job card: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting job cards: {str(e)}")

        return job_listings

    async def _parse_linkedin_job_card(self, card) -> Optional[Dict[str, Any]]:
        """Parse individual LinkedIn job card"""
        try:
            # Extract job link and ID
            link_elem = await card.query_selector('a.job-card-list__title')
            if not link_elem:
                return None

            job_url = await link_elem.get_attribute('href')
            job_id = self._extract_linkedin_job_id(job_url)

            # Extract title
            title = await link_elem.inner_text()
            title = title.strip()

            # Extract company
            company_elem = await card.query_selector('.job-card-container__company-name')
            company = await company_elem.inner_text() if company_elem else 'Unknown'
            company = company.strip()

            # Extract location
            location_elem = await card.query_selector('.job-card-container__metadata-item')
            location = await location_elem.inner_text() if location_elem else 'Unknown'
            location = location.strip()

            # Check for Easy Apply
            easy_apply_elem = await card.query_selector('.job-card-container__apply-method')
            easy_apply = easy_apply_elem is not None

            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'url': f"https://www.linkedin.com/jobs/view/{job_id}",
                'platform': 'linkedin',
                'easy_apply': easy_apply,
                'posted_date': datetime.utcnow(),  # LinkedIn doesn't show exact date on cards
            }

        except Exception as e:
            logger.error(f"Error parsing job card: {str(e)}")
            return None

    def _extract_linkedin_job_id(self, url: str) -> str:
        """Extract job ID from LinkedIn job URL"""
        # URL format: https://www.linkedin.com/jobs/view/1234567890
        if '/jobs/view/' in url:
            return url.split('/jobs/view/')[1].split('?')[0]
        return url.split('/')[-1].split('?')[0]

    async def _get_linkedin_job_details(self, page: Page, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Visit individual job page to get full details.

        Extracts:
        - Full job description
        - Required skills
        - Experience level
        - Employment type
        - Salary range (if available)
        """
        try:
            # Navigate to job page
            await page.goto(job_data['url'], wait_until='networkidle', timeout=20000)
            await asyncio.sleep(1)

            # Extract job description
            description_elem = await page.query_selector('.jobs-description__content')
            description = ''
            if description_elem:
                description = await description_elem.inner_text()
                description = description.strip()

            # Extract criteria (experience level, employment type, etc.)
            criteria = {}
            criteria_items = await page.query_selector_all('.job-details-jobs-unified-top-card__job-insight')
            for item in criteria_items:
                text = await item.inner_text()
                # Parse criteria (e.g., "Mid-Senior level", "Full-time")
                if 'level' in text.lower():
                    criteria['experience_level'] = text
                elif 'time' in text.lower():
                    criteria['employment_type'] = text

            # Update job_data with full details
            job_data['description'] = description
            job_data['experience_level'] = criteria.get('experience_level', 'Not specified')
            job_data['employment_type'] = criteria.get('employment_type', 'Full-time')

            return job_data

        except Exception as e:
            logger.error(f"Error getting job details for {job_data['job_id']}: {str(e)}")
            return job_data  # Return with partial data

    def _score_job(self, job_data: Dict[str, Any], user_profile: UserProfile) -> float:
        """
        Score job based on user preferences.

        Scoring factors (0-100):
        - Location match (20 points)
        - Remote preference match (20 points)
        - Title/role match (30 points)
        - Experience level match (15 points)
        - Easy Apply availability (15 points)

        Returns:
            Score from 0-100
        """
        score = 0.0

        # Location match
        job_location = job_data.get('location', '').lower()
        user_location = f"{user_profile.city}, {user_profile.state}".lower() if user_profile.city and user_profile.state else ''

        if 'remote' in job_location:
            if user_profile.remote_preference in ['remote_only', 'hybrid']:
                score += 20
        elif user_location and user_location in job_location:
            score += 20
        elif user_profile.willing_to_relocate:
            score += 10

        # Remote preference match
        if user_profile.remote_preference == 'remote_only' and 'remote' in job_location:
            score += 20
        elif user_profile.remote_preference == 'hybrid':
            score += 15

        # Title/role match (basic keyword matching)
        job_title = job_data.get('title', '').lower()
        user_title = user_profile.current_title.lower() if user_profile.current_title else ''

        # Extract key terms
        title_keywords = ['engineer', 'developer', 'senior', 'staff', 'lead', 'manager', 'architect']
        matching_keywords = sum(1 for kw in title_keywords if kw in user_title and kw in job_title)
        score += min(matching_keywords * 10, 30)

        # Experience level match
        experience_level = job_data.get('experience_level', '').lower()
        user_years = user_profile.years_of_experience or 0

        if user_years >= 7 and 'senior' in experience_level:
            score += 15
        elif 3 <= user_years < 7 and 'mid' in experience_level:
            score += 15
        elif user_years < 3 and ('entry' in experience_level or 'junior' in experience_level):
            score += 15
        else:
            score += 5  # Partial credit

        # Easy Apply bonus
        if job_data.get('easy_apply', False):
            score += 15

        return min(score, 100.0)  # Cap at 100

    def _job_exists(self, job_id: str) -> bool:
        """Check if job already exists in database"""
        existing = self.db.query(JobListing).filter(
            JobListing.external_job_id == job_id
        ).first()
        return existing is not None

    def _save_job(self, job_data: Dict[str, Any], user_id: int) -> JobListing:
        """Save job to database"""
        try:
            job_listing = JobListing(
                user_id=user_id,
                platform=job_data['platform'],
                external_job_id=job_data['job_id'],
                job_url=job_data['url'],
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                description=job_data.get('description', ''),
                employment_type=job_data.get('employment_type'),
                experience_level=job_data.get('experience_level'),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                posted_date=job_data.get('posted_date'),
                easy_apply=job_data.get('easy_apply', False),
                match_score=job_data.get('match_score', 0),
                status='discovered',
                discovered_at=datetime.utcnow()
            )

            self.db.add(job_listing)
            self.db.commit()
            self.db.refresh(job_listing)

            logger.info(f"Saved job: {job_listing.title} at {job_listing.company} (score: {job_listing.match_score})")
            return job_listing

        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            self.db.rollback()
            raise


async def scan_jobs_for_user(db: Session, user_id: int, max_jobs: int = 50) -> Dict[str, int]:
    """
    Convenience function to scan jobs for a specific user.

    Usage:
        from app.services.job_scanner import scan_jobs_for_user

        results = await scan_jobs_for_user(db, user_id=1, max_jobs=50)
        print(f"Found {results['linkedin']} new jobs on LinkedIn")

    Args:
        db: Database session
        user_id: User ID to scan jobs for
        max_jobs: Maximum jobs to fetch per platform

    Returns:
        Dictionary with platform names and job counts
    """
    # Get user profile
    user_profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_profile:
        raise ValueError(f"User profile not found for user_id={user_id}")

    # Scan jobs
    async with JobScanner(db) as scanner:
        results = await scanner.scan_all_platforms(
            user_profile=user_profile,
            max_jobs_per_platform=max_jobs
        )

    return results
