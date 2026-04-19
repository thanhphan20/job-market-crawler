import re


class DataStandardizer:
    """
    Standardization layer to unify Local (Vietnam) and Global job market data.
    """

    # Simple VND to USD conversion rate
    VND_USD_RATE = 25000

    # Mapping Local Vietnamese Titles to Global Categories
    TITLE_MAP = {
        "unity": "Game Development/AR-VR",
        "java": "Backend Developer",
        "python": "Data & AI Engineer",
        "data": "Data Science/Analytics",
        "ml": "Machine Learning Engineer",
        "machine learning": "Machine Learning Engineer",
        "frontend": "Frontend Developer",
        "react": "Frontend Developer",
        "fullstack": "Fullstack Developer",
        "devops": "Cloud & DevOps",
        "mobile": "Mobile App Developer",
        "ios": "Mobile App Developer",
        "android": "Mobile App Developer",
        "bridge": "Project Management",
        "manager": "Management/Leadership",
        "lead": "Management/Leadership",
    }

    @classmethod
    def standardize_title(cls, title):
        """Maps diverse job titles to a standard global category."""
        title_lower = title.lower()
        for key, category in cls.TITLE_MAP.items():
            if key in title_lower:
                return category
        return "Software Engineering (Other)"

    @classmethod
    def parse_experience(cls, exp_str):
        """Converts strings like '2 nam', '1 - 3 years' to a numeric minimum."""
        if not exp_str or not isinstance(exp_str, str):
            return 0

        # Look for the first number in the string
        nums = re.findall(r"\d+", exp_str.lower())
        if nums:
            return int(nums[0])

        if "trainee" in exp_str.lower() or "intern" in exp_str.lower():
            return 0
        return 0

    @classmethod
    def parse_salary_vnd(cls, salary_str):
        """
        Parses Vietnam salary strings (e.g., '15 - 20 trieu', 'Thoa thuan')
        and converts to annual USD.
        """
        if not salary_str or not isinstance(salary_str, str):
            return None

        salary_str = salary_str.lower()

        if "tho thun" in salary_str or "negotiable" in salary_str:
            return None  # Should handle as missing data

        # Extract numbers (trieu = million)
        nums = re.findall(r"\d+", salary_str.replace(".", "").replace(",", ""))
        if not nums:
            return None

        # If it's a range, take the average or the minimum (we'll take min as conservative)
        val = int(nums[0])

        # Check if it's 'trieu' (million VND)
        if "tri" in salary_str or val < 1000:  # Usually trieu if < 1000
            monthly_vnd = val * 1_000_000
        else:
            monthly_vnd = val

        annual_usd = (monthly_vnd * 12) / cls.VND_USD_RATE
        return round(annual_usd, 2)
