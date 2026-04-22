import re


class DataStandardizer:
    """
    Standardization layer to unify Local (Vietnam) and Global job market data.
    """

    # Simple VND to USD conversion rate
    VND_USD_RATE = 25000

    # Mapping Local Vietnamese Titles to Global Categories
    TITLE_MAP = {
        # High-level specialized roles
        "machine learning": "Machine Learning Engineer",
        "data scientist": "Data Scientist",
        "data analyst": "Data Analyst",
        "ai scientist": "AI Research Scientist",
        "ai engineer": "AI Engineer",
        "solution architect": "Solution Architect",
        "cloud architect": "Cloud Architect",
        "cybersecurity": "Cybersecurity Specialist",
        "blockchain": "Blockchain Engineer",
        "game developer": "Game Developer",
        "unity": "Game Developer",
        "unreal": "Game Developer",
        
        # DevOps & Infrastructure
        "sre": "Site Reliability Engineer",
        "site reliability": "Site Reliability Engineer",
        "devops": "DevOps Engineer",
        "infrastructure": "DevOps Engineer",
        "cloud engineer": "Cloud & DevOps",
        "aws": "Cloud & DevOps",
        "azure": "Cloud & DevOps",
        "kubernetes": "Cloud & DevOps",
        "docker": "Cloud & DevOps",

        # Mobile Development
        "ios": "iOS Developer",
        "android": "Android Developer",
        "flutter": "Mobile Developer",
        "react native": "Mobile Developer",
        "mobile": "Mobile Developer",

        # Frontend Development
        "frontend": "Frontend Developer",
        "react": "Frontend Developer",
        "angular": "Frontend Developer",
        "vue": "Frontend Developer",
        "javascript": "Frontend Developer",
        "typescript": "Frontend Developer",
        "nextjs": "Frontend Developer",

        # Backend Development
        "backend": "Backend Developer",
        "java": "Java Backend Developer",
        "node": "Node.js Backend Developer",
        "golang": "Go Backend Developer",
        "python developer": "Python Backend Developer",
        "php": "PHP Backend Developer",
        "ruby": "Ruby Backend Developer",
        ".net": ".NET Backend Developer",
        "c#": ".NET Backend Developer",
        "c++": "C++ Engineer",
        "embedded": "Embedded Systems",
        "firmware": "Embedded Systems",
        "rust": "Systems Engineer",

        # Fullstack
        "fullstack": "Fullstack Developer",
        "full stack": "Fullstack Developer",

        # Management & Business
        "project manager": "Project Manager",
        "product manager": "Product Manager",
        "business analyst": "Business Analyst",
        "ba": "Business Analyst",
        "manager": "Engineering Management",
        "director": "Executive",
        "cto": "Executive",
        "pmo": "Project Manager",
        
        # QA & Testing
        "qa": "QA/QC Engineer",
        "qc": "QA/QC Engineer",
        "tester": "QA/QC Engineer",
        "automation test": "QA/QC Engineer",
    }

    @classmethod
    def standardize_title(cls, title):
        """Maps diverse job titles to a standard global category or cleans the original."""
        title_clean = title.strip()
        title_lower = title_clean.lower()
        
        # Sort keys by length descending to match longest/most specific patterns first
        sorted_keys = sorted(cls.TITLE_MAP.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            if key in title_lower:
                return cls.TITLE_MAP[key]
        
        # If no stack-specific keyword, clean the original title instead of being generic
        # Remove common noise words
        noise = [
            r"\bsenior\b", r"\bjunior\b", r"\bmiddle\b", r"\blead\b", 
            r"\bprincipal\b", r"\bstaff\b", r"\bassociate\b", r"\bexpert\b",
            r"\[.*?\]", r"\(.*?\)", r"\bvn\b", r"\bvietnam\b", r"\bhcm\b", r"\bhanoi\b"
        ]
        
        cleaned = title_lower
        for pattern in noise:
            cleaned = re.sub(pattern, "", cleaned)
            
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        
        if len(cleaned) > 3:
            return cleaned.title()
            
        return "Specialized Tech Role"

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
