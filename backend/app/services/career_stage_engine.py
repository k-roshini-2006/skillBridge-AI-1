import re
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any

# Target Role Definitions with required core skills and recommended projects
TARGET_ROLES_DATABASE = {
    "full-stack-developer": {
        "id": "full-stack-developer",
        "name": "Full Stack Developer",
        "category": "Software Engineering",
        "description": "Designs and builds end-to-end web applications across client interfaces, backend APIs, and databases.",
        "required_skills": [
            "JavaScript", "React", "Node.js", "Express", "HTML/CSS", 
            "SQL", "REST APIs", "Git", "Database Design", "Authentication"
        ],
        "recommended_projects": [
            "Full-Stack E-Commerce or SaaS Dashboard with JWT auth, payment gateway integration, and relational database.",
            "Real-Time Collaborative Workspace with WebSockets, state management, and deployed microservices."
        ]
    },
    "software-engineer": {
        "id": "software-engineer",
        "name": "Software Development Engineer (SDE)",
        "category": "Software Engineering",
        "description": "Builds robust, scalable software systems, algorithms, and core services with high performance.",
        "required_skills": [
            "Data Structures", "Algorithms", "Java", "Python", "C++", 
            "Object-Oriented Programming", "Git", "SQL", "System Design", "Unit Testing"
        ],
        "recommended_projects": [
            "Distributed Key-Value Store or Cache with thread-safe concurrency and LRU eviction policy.",
            "Algorithm Visualizer or Compiler/Interpreter for a domain-specific mathematical grammar."
        ]
    },
    "frontend-developer": {
        "id": "frontend-developer",
        "name": "Frontend Developer",
        "category": "Web Development",
        "description": "Crafts responsive, accessible, and high-performance user interfaces and interactive web applications.",
        "required_skills": [
            "JavaScript", "TypeScript", "React", "HTML/CSS", "Tailwind CSS", 
            "Responsive Design", "State Management", "REST APIs", "Git", "Web Performance"
        ],
        "recommended_projects": [
            "Interactive Component Design System & UI Library with accessibility (ARIA) and theme switching.",
            "High-Performance Analytics Dashboard with dynamic charting, filtering, and offline PWA caching."
        ]
    },
    "backend-developer": {
        "id": "backend-developer",
        "name": "Backend Developer",
        "category": "Backend & Cloud",
        "description": "Architects server-side logic, database schemas, secure authentication, and scalable microservices.",
        "required_skills": [
            "Python", "Node.js", "SQL", "PostgreSQL", "REST APIs", 
            "Docker", "Redis", "Authentication", "Database Design", "Git"
        ],
        "recommended_projects": [
            "Scalable RESTful API Service with Rate Limiting, Redis Caching, and Dockerized Postgres DB.",
            "Event-Driven Notification or Messaging Service using message queues and background workers."
        ]
    },
    "ai-ml-engineer": {
        "id": "ai-ml-engineer",
        "name": "AI / Machine Learning Engineer",
        "category": "Artificial Intelligence",
        "description": "Develops, trains, evaluates, and deploys machine learning and deep learning models into production.",
        "required_skills": [
            "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", 
            "Scikit-Learn", "Pandas", "NumPy", "Data Preprocessing", "Git"
        ],
        "recommended_projects": [
            "End-to-End Predictive ML Pipeline with automated hyperparameter tuning and model tracking.",
            "RAG-Powered LLM Assistant with vector similarity search, embeddings, and API deployment."
        ]
    },
    "data-scientist": {
        "id": "data-scientist",
        "name": "Data Scientist",
        "category": "Data Science",
        "description": "Uncovers patterns, develops statistical models, and derives actionable business intelligence from data.",
        "required_skills": [
            "Python", "SQL", "Statistics", "Data Analysis", "Pandas", 
            "NumPy", "Machine Learning", "Data Visualization", "Feature Engineering", "Git"
        ],
        "recommended_projects": [
            "Customer Churn / Financial Risk Prediction with exploratory data analysis and feature attribution.",
            "Interactive Tableau/Streamlit Business Intelligence Dashboard backed by SQL data warehouse queries."
        ]
    },
    "cloud-devops-engineer": {
        "id": "cloud-devops-engineer",
        "name": "Cloud & DevOps Engineer",
        "category": "Infrastructure",
        "description": "Automates CI/CD deployment pipelines, provisions cloud infrastructure, and ensures system reliability.",
        "required_skills": [
            "Linux", "Docker", "Kubernetes", "AWS", "CI/CD", 
            "Git", "Python", "Bash", "Terraform", "Networking"
        ],
        "recommended_projects": [
            "Automated Multi-Stage CI/CD GitHub Actions Pipeline deploying containerized microservices to Kubernetes.",
            "Infrastructure-as-Code Terraform Repository automating cloud VPC, load balancer, and database provisioning."
        ]
    },
    "cybersecurity-analyst": {
        "id": "cybersecurity-analyst",
        "name": "Cybersecurity Analyst",
        "category": "Security",
        "description": "Protects digital assets, identifies vulnerabilities, monitors network traffic, and implements security controls.",
        "required_skills": [
            "Network Security", "Linux", "Cryptography", "Vulnerability Assessment", 
            "Python", "Wireshark", "Firewalls", "Security Protocols", "Git", "Penetration Testing"
        ],
        "recommended_projects": [
            "Network Intrusion Detection System analyzing live packet PCAP files with Python and alerting anomalies.",
            "Automated Vulnerability Scanner detecting open ports, outdated SSL ciphers, and misconfigured HTTP headers."
        ]
    }
}

# Skill aliases and normalizer for robust regex matching in resumes
SKILLS_TAXONOMY = {
    "JavaScript": [r"\bjavascript\b", r"\bjs\b", r"\bes6\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "Java": [r"\bjava\b(?!script)"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],
    "React": [r"\breact\b", r"\breact\.js\b", r"\breactjs\b"],
    "Node.js": [r"\bnode\.js\b", r"\bnodejs\b", r"\bnode\b"],
    "Express": [r"\bexpress\b", r"\bexpress\.js\b", r"\bexpressjs\b"],
    "HTML/CSS": [r"\bhtml\b", r"\bcss\b", r"\bhtml5\b", r"\bcss3\b"],
    "Tailwind CSS": [r"\btailwind\b", r"\btailwindcss\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bsqlite\b"],
    "PostgreSQL": [r"\bpostgres\b", r"\bpostgresql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "Docker": [r"\bdocker\b", r"\bcontainer\b", r"\bcontainers\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b", r"\bec2\b", r"\bs3\b"],
    "CI/CD": [r"\bci/cd\b", r"\bcicd\b", r"\bgithub actions\b", r"\bjenkins\b"],
    "Linux": [r"\blinux\b", r"\bubuntu\b", r"\bbash\b", r"\bshell\b"],
    "REST APIs": [r"\brest\b", r"\brestful\b", r"\bapi\b", r"\bapis\b"],
    "Data Structures": [r"\bdata structures\b", r"\bdsa\b", r"\barrays\b", r"\btrees\b", r"\bgraphs\b"],
    "Algorithms": [r"\balgorithms\b", r"\balgorithmic\b", r"\bbinary search\b", r"\bbfs\b", r"\bdfs\b"],
    "Object-Oriented Programming": [r"\boop\b", r"\boops\b", r"\bobject-oriented\b"],
    "System Design": [r"\bsystem design\b", r"\bscalability\b", r"\barchitecture\b"],
    "Unit Testing": [r"\bunit testing\b", r"\bjest\b", r"\bpytest\b", r"\bjunit\b", r"\btesting\b"],
    "Responsive Design": [r"\bresponsive\b", r"\bmobile-first\b"],
    "State Management": [r"\bredux\b", r"\bzustand\b", r"\bcontext api\b", r"\bstate management\b"],
    "Web Performance": [r"\bweb performance\b", r"\blighthouse\b", r"\blazy loading\b"],
    "Database Design": [r"\bdatabase design\b", r"\bschema\b", r"\bnormalization\b", r"\ber diagram\b"],
    "Authentication": [r"\bjwt\b", r"\boauth\b", r"\bauthentication\b", r"\bauth\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning": [r"\bdeep learning\b", r"\bneural networks\b", r"\bdl\b"],
    "PyTorch": [r"\bpytorch\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b", r"\bkeras\b"],
    "Scikit-Learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Data Preprocessing": [r"\bdata preprocessing\b", r"\bfeature engineering\b", r"\bcleaning\b"],
    "Data Analysis": [r"\bdata analysis\b", r"\beda\b", r"\bexploratory data\b"],
    "Statistics": [r"\bstatistics\b", r"\bstatistical\b", r"\bprobability\b", r"\bhypothesis testing\b"],
    "Data Visualization": [r"\bdata visualization\b", r"\bmatplotlib\b", r"\bseaborn\b", r"\btableau\b", r"\bpower bi\b"],
    "Feature Engineering": [r"\bfeature engineering\b", r"\bfeature selection\b"],
    "Network Security": [r"\bnetwork security\b", r"\bcybersecurity\b", r"\bfirewall\b"],
    "Cryptography": [r"\bcryptography\b", r"\bencryption\b", r"\bhashing\b"],
    "Vulnerability Assessment": [r"\bvulnerability\b", r"\bvulnerability assessment\b", r"\bowasp\b"],
    "Security Protocols": [r"\btls\b", r"\bssl\b", r"\bhttps\b", r"\bssh\b"],
    "Penetration Testing": [r"\bpenetration testing\b", r"\bpentest\b", r"\bethical hacking\b"],
    "Wireshark": [r"\bwireshark\b", r"\bnmap\b", r"\bpacket analysis\b"],
    "Terraform": [r"\bterraform\b", r"\biac\b", r"\binfrastructure as code\b"],
    "Bash": [r"\bbash\b", r"\bshell scripting\b"],
    "Networking": [r"\btcp/ip\b", r"\bdns\b", r"\bhttp\b", r"\bnetworking\b"]
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text content from uploaded PDF resume bytes using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        return ""


def extract_skills(text: str) -> List[str]:
    """Finds all demonstrated skills from the skills taxonomy present in the resume text."""
    lower_text = text.lower()
    matched = []
    for skill_name, patterns in SKILLS_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, lower_text):
                matched.append(skill_name)
                break
    return matched


def extract_projects_count(text: str) -> Tuple[int, List[str]]:
    """
    Detects projects mentioned in the resume by looking for Project sections,
    bullet points, GitHub links, and title markers.
    """
    lower = text.lower()
    project_indicators = [
        r"project[s]?:?", r"academic projects", r"personal projects", 
        r"github\.com/[\w\-]+", r"deployed at", r"live demo"
    ]
    
    # Check for dedicated Projects section
    lines = text.split("\n")
    in_project_section = False
    project_titles = []
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if re.match(r"^(projects|academic projects|technical projects|key projects)\b", cleaned.lower()):
            in_project_section = True
            continue
        elif in_project_section and re.match(r"^(experience|education|skills|certifications|achievements)\b", cleaned.lower()):
            in_project_section = False
            
        if in_project_section and len(cleaned) > 5:
            # Bullet point or bold title indicating a project
            if cleaned.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")) or (len(cleaned) < 50 and not cleaned.endswith(".")):
                if not any(k in cleaned.lower() for k in ["github", "tech stack", "tools:", "technologies:"]):
                    project_titles.append(cleaned.lstrip("-*•12345. "))

    # Count deduplicated plausible project headers
    count = max(len(set(project_titles[:6])), 0)
    
    # Fallback heuristic: count github repositories or 'built a' occurrences if section wasn't labeled
    if count == 0:
        github_links = len(re.findall(r"github\.com/[\w\-]+/[\w\-]+", lower))
        built_occurrences = len(re.findall(r"\b(developed|built|created|designed and deployed|implemented a)\b", lower))
        count = min(5, max(github_links, built_occurrences // 2))

    return max(0, count), project_titles[:4]


def extract_experience_months(text: str) -> Tuple[int, List[str]]:
    """
    Detects work experience, internships, or freelance roles in the resume.
    Returns estimated months and identified role snippets.
    """
    lower = text.lower()
    roles = []
    
    # Check for internship keywords
    intern_matches = re.findall(r"\b(intern|internship|trainee|apprentice|software engineering intern|frontend intern|backend intern)\b", lower)
    fulltime_matches = re.findall(r"\b(junior developer|associate engineer|software engineer|developer at|employed by)\b", lower)
    freelance_matches = re.findall(r"\b(freelance|consultant|contractor|open source contributor)\b", lower)

    months = 0
    if fulltime_matches:
        months += len(fulltime_matches) * 6
        roles.append(f"Professional/Developer Experience ({len(fulltime_matches)} position(s))")
    if intern_matches:
        months += len(intern_matches) * 3
        roles.append(f"Internship Experience ({len(intern_matches)} internship(s))")
    if freelance_matches and not fulltime_matches and not intern_matches:
        months += 2
        roles.append("Freelance / Open Source Contributions")

    return months, roles


def extract_education_level(text: str) -> Dict[str, Any]:
    """Detects degree, engineering branch, and graduation timeline."""
    lower = text.lower()
    has_cs_degree = bool(re.search(r"\b(computer science|information technology|software engineering|cse|it|data science|ai)\b", lower))
    has_btech = bool(re.search(r"\b(b\.?tech|b\.?e\.?|bachelor|b\.?s\.?|bca|mca)\b", lower))
    has_cert = bool(re.search(r"\b(certified|certification|aws certified|coursera|udemy|hackathon)\b", lower))
    
    return {
        "relevant_degree": has_cs_degree or has_btech,
        "certifications_detected": has_cert
    }


def assess_career_stage(
    resume_text: str, 
    target_role_id: str = "full-stack-developer",
    custom_job_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core Career Stage Assessment Algorithm.
    Evaluates student career readiness stage (1 to 5) relative to the target role.
    
    Stages:
      Stage 1 – Beginner (Score 0-29): Basic knowledge, few demonstrated skills, little/no practical projects.
      Stage 2 – Learner (Score 30-49): Learning relevant technologies, foundational skills or small projects.
      Stage 3 – Project Builder (Score 50-69): Has completed practical projects and can demonstrate some job-relevant skills.
      Stage 4 – Internship Ready (Score 70-84): Relevant projects, demonstrated technical skills, practical experience/internship ready.
      Stage 5 – Job Ready (Score 85-100): Strong alignment with selected role through skills, complex projects, and experience.
    """
    if not resume_text or len(resume_text.strip()) < 20:
        return {
            "career_stage": 1,
            "stage_name": "Beginner",
            "readiness_score": 0.0,
            "match_percentage": 0.0,
            "stage_reason": "Insufficient resume text provided to detect demonstrated skills or technical projects.",
            "strengths": [],
            "missing_skills": [],
            "demonstrated_skills": [],
            "score_breakdown": {"skills": 0, "projects": 0, "experience": 0, "education": 0},
            "recommendations": ["Upload a complete resume detailing technical skills, GitHub projects, and coursework."],
            "progression_plan": {}
        }

    # 1. Determine Target Role Requirements
    role_info = TARGET_ROLES_DATABASE.get(target_role_id)
    if not role_info:
        role_info = TARGET_ROLES_DATABASE["full-stack-developer"]

    target_skills = list(role_info["required_skills"])
    
    # If custom job description provided, extract skills from it
    if custom_job_description and len(custom_job_description.strip()) > 30:
        custom_skills = extract_skills(custom_job_description)
        if len(custom_skills) >= 4:
            target_skills = custom_skills

    # 2. Extract Evidence from Resume
    resume_skills = extract_skills(resume_text)
    projects_count, project_samples = extract_projects_count(resume_text)
    exp_months, exp_roles = extract_experience_months(resume_text)
    edu_info = extract_education_level(resume_text)

    # 3. Compare Skills against Target Role
    resume_skills_set = set(resume_skills)
    demonstrated_target_skills = [s for s in target_skills if s in resume_skills_set]
    missing_target_skills = [s for s in target_skills if s not in resume_skills_set]
    additional_strengths = [s for s in resume_skills if s not in demonstrated_target_skills]

    match_pct = (len(demonstrated_target_skills) / len(target_skills)) * 100 if target_skills else 0.0

    # 4. Transparent Multi-Dimensional Readiness Scoring (0 to 100 pts)
    # Dimension A: Target Skills Match (Max 40 points)
    skills_score = round(min(40.0, (len(demonstrated_target_skills) / max(1, len(target_skills))) * 40.0), 1)

    # Dimension B: Practical Project Depth (Max 30 points)
    # 0 projects: 0 pts | 1 project: 12 pts | 2 projects: 22 pts | 3+ projects: 30 pts
    if projects_count >= 3:
        projects_score = 30.0
    elif projects_count == 2:
        projects_score = 22.0
    elif projects_count == 1:
        projects_score = 12.0
    else:
        projects_score = 4.0 if len(resume_skills) >= 3 else 0.0

    # Dimension C: Practical Experience & Internships (Max 20 points)
    # 0 months: 0-5 pts (small freelance/open source) | 3 mos internship: 14 pts | 6+ mos: 20 pts
    if exp_months >= 6:
        exp_score = 20.0
    elif exp_months >= 3:
        exp_score = 14.0
    elif exp_months > 0 or exp_roles:
        exp_score = 8.0
    else:
        exp_score = 0.0

    # Dimension D: Foundational Education & Credentials (Max 10 points)
    edu_score = 0.0
    if edu_info["relevant_degree"]:
        edu_score += 7.0
    if edu_info["certifications_detected"]:
        edu_score += 3.0

    total_readiness_score = round(skills_score + projects_score + exp_score + edu_score, 1)

    # 5. Career Stage Determination (1 to 5)
    # Rigorous rules ensuring stage reflects practical ability for the specific target role
    if total_readiness_score >= 85 and len(demonstrated_target_skills) >= 7 and projects_count >= 2 and exp_months >= 3:
        stage_num = 5
        stage_name = "Job Ready"
        stage_reason = (
            f"Demonstrates strong, verified alignment with the {role_info['name']} role. "
            f"Matches {len(demonstrated_target_skills)}/{len(target_skills)} core technical skills, "
            f"features {projects_count} substantial project(s), and demonstrates practical internship/work experience."
        )
    elif total_readiness_score >= 68 and len(demonstrated_target_skills) >= 5 and projects_count >= 2:
        stage_num = 4
        stage_name = "Internship Ready"
        stage_reason = (
            f"Possesses the technical foundation and multi-project portfolio required to contribute effectively in an internship. "
            f"Demonstrates {len(demonstrated_target_skills)} core role skills and {projects_count} project(s), "
            f"with a clear path to bridge remaining advanced skills ({', '.join(missing_target_skills[:3])})."
        )
    elif total_readiness_score >= 48 and len(demonstrated_target_skills) >= 3 and projects_count >= 1:
        stage_num = 3
        stage_name = "Project Builder"
        stage_reason = (
            f"Has successfully transitioned from basic theory to practical application with {projects_count} completed project(s). "
            f"Matches {round(match_pct)}% of target role requirements. Needs to expand practical project depth to become internship ready."
        )
    elif total_readiness_score >= 25 and len(demonstrated_target_skills) >= 2:
        stage_num = 2
        stage_name = "Learner"
        stage_reason = (
            f"Actively acquiring relevant technologies for {role_info['name']} ({', '.join(demonstrated_target_skills[:4])}) "
            f"with foundational familiarity. Needs 1-2 end-to-end portfolio projects to advance to the Project Builder stage."
        )
    else:
        stage_num = 1
        stage_name = "Beginner"
        stage_reason = (
            f"Early in the technical journey for {role_info['name']}. "
            f"Currently demonstrates {len(demonstrated_target_skills)} core role skill(s) and little or no demonstrated practical project experience in this domain."
        )


    # 6. Actionable Recommendations to Reach Next Stage
    next_stage_map = {
        1: "Stage 2 (Learner)",
        2: "Stage 3 (Project Builder)",
        3: "Stage 4 (Internship Ready)",
        4: "Stage 5 (Job Ready)",
        5: "Industry Mastery & Advanced Specialization"
    }

    recommendations = []
    if missing_target_skills:
        recommendations.append(f"Master top priority missing skills for {role_info['name']}: {', '.join(missing_target_skills[:3])}.")
    if projects_count < 2:
        recommendations.append("Build and deploy a full-featured, standalone portfolio project with a public GitHub repository and live demo.")
    if exp_months == 0:
        recommendations.append("Contribute to open-source repositories or complete a real-world client/hackathon project to gain practical team experience.")
    recommendations.append("Take SkillBridge AI competency diagnostics on core Data Structures and algorithms to validate algorithmic problem-solving.")

    # 7. Step-by-Step Progression Plan
    skills_to_learn = [
        {
            "skill": skill,
            "priority": "High" if idx < 2 else "Medium",
            "impact": f"Required for {role_info['name']} role qualification",
            "study_topic": "Data Structures & Core CS" if skill in ["Data Structures", "Algorithms"] else f"{skill} Concepts & Patterns"
        }
        for idx, skill in enumerate(missing_target_skills[:5])
    ]

    projects_to_build = [
        {
            "title": proj_idea.split(" with ")[0],
            "description": proj_idea,
            "skills_involved": demonstrated_target_skills[:3] + missing_target_skills[:2],
            "target_stage_unlock": next_stage_map.get(stage_num, "Stage 5")
        }
        for proj_idea in role_info.get("recommended_projects", [])[:2]
    ]

    assessments_to_take = [
        {
            "type": "diagnostic",
            "title": "Data Structures Comprehensive Diagnostic",
            "benefit": "Identifies foundational memory and algorithm gaps before technical interviews."
        },
        {
            "type": "mastery",
            "title": f"{role_info['name']} Core Competency Gate",
            "benefit": "Tests algorithmic invariants and edge cases at ≥ 80% threshold."
        }
    ]

    score_breakdown = {
        "skills": {
            "score": skills_score,
            "max": 40,
            "description": f"Demonstrated {len(demonstrated_target_skills)} of {len(target_skills)} target role skills"
        },
        "projects": {
            "score": projects_score,
            "max": 30,
            "description": f"Detected {projects_count} practical project(s) in resume"
        },
        "experience": {
            "score": exp_score,
            "max": 20,
            "description": f"Detected ~{exp_months} months internship/practical experience"
        },
        "education": {
            "score": edu_score,
            "max": 10,
            "description": "Relevant computer science/engineering degree & certifications"
        }
    }

    return {
        "target_role": role_info["name"],
        "target_role_id": role_info["id"],
        "career_stage": stage_num,
        "stage_name": stage_name,
        "next_stage_name": next_stage_map.get(stage_num, "Stage 5"),
        "readiness_score": total_readiness_score,
        "match_percentage": round(match_pct, 1),
        "stage_reason": stage_reason,
        "strengths": [f"Demonstrated: {s}" for s in demonstrated_target_skills[:5]] + [f"Complementary: {s}" for s in additional_strengths[:3]],
        "missing_skills": missing_target_skills,
        "demonstrated_skills": demonstrated_target_skills,
        "score_breakdown": score_breakdown,
        "recommendations": recommendations,
        "progression_plan": {
            "skills_to_learn": skills_to_learn,
            "projects_to_build": projects_to_build,
            "assessments_to_take": assessments_to_take
        },
        "extracted_skills": resume_skills,
        "extracted_projects_count": projects_count,
        "extracted_experience_months": exp_months
    }
