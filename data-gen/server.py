import json
import uuid
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Employee-Future-Jobs-Data-Gen")


# File paths - absolute to avoid read-only issue
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_FILE = os.path.join(CURRENT_DIR, "resources.xlsx")  # Current employee skills  
REQUESTS_FILE = os.path.join(CURRENT_DIR, "requests.xlsx")    # Future job competencies

# Data Models
class Employee(BaseModel):
    """Current employee with skills (Resources)"""
    employee_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str
    current_role: str
    department: str
    years_experience: int
    skills: Dict[str, int]  # skill_name -> level (1-10)
    competencies: Dict[str, int]  # competency_name -> level (1-10)

class FutureJob(BaseModel):
    """Future job opportunity with requirements (Requests)"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    title: str
    department: str
    level: str  # Junior, Mid, Senior, Lead, Executive
    required_skills: Dict[str, int]  # skill_name -> required_level (1-10)
    required_competencies: Dict[str, int]  # competency_name -> required_level (1-10)

# Global storage
talent_data = {
    "employees": {},
    "future_jobs": {}
}

# Core skills and competencies - every employee/job gets ALL of these
ALL_SKILLS = [
    "System Architecture", "Cloud Architecture", "Solution Design", "Enterprise Integration",
    "Technical Documentation", "Stakeholder Management", "Infrastructure Design",
    "Security Architecture", "Data Architecture", "API Design"
]

ALL_COMPETENCIES = [
    "Strategic Planning", "Technical Leadership", "Communication", "Decision Making",
    "Enterprise Thinking", "Innovation", "Risk Management", "Business Acumen",
    "Change Management", "Mentorship"
]

DEPARTMENTS = [
    "Enterprise Architecture", "Solution Architecture", "Cloud Architecture",
    "Security Architecture", "Data Architecture", "Integration Architecture",
    "Infrastructure Architecture", "Business Architecture"
]

INDUSTRIES = [
    "Financial Services", "Healthcare", "Government", "Telecommunications",
    "Manufacturing", "Retail", "Energy", "Transportation",
    "Education", "Insurance", "Technology", "Consulting"
]

FUTURE_JOB_TITLES = [
    "Enterprise Architect", "Chief Architect", "Principal Architect",
    "Lead Solution Architect", "Senior Cloud Architect", "Data Architecture Lead",
    "Security Architecture Lead", "Integration Architect", "Infrastructure Architect",
    "Business Solutions Architect", "Digital Transformation Architect",
    "Technical Architecture Consultant", "Architecture Governance Lead"
]


# Excel file operations
def load_employees_from_excel() -> Dict[str, Employee]:
    """Load employees from Resources.xlsx"""
    try:
        df = pd.read_excel(RESOURCES_FILE)
        employees = {}
        for _, row in df.iterrows():
            # Parse skills and competencies from Excel columns
            skills = {}
            competencies = {}
            
            for col in df.columns:
                if col.startswith("skill_") and pd.notna(row[col]):
                    skill_name = col.replace("skill_", "").replace("_", " ").title()
                    skills[skill_name] = int(row[col])
                elif col.startswith("comp_") and pd.notna(row[col]):
                    comp_name = col.replace("comp_", "").replace("_", " ").title()
                    competencies[comp_name] = int(row[col])
            
            employee = Employee(
                employee_id=row.get("employee_id", str(uuid.uuid4())[:12]),
                name=row["name"],
                current_role=row["current_role"],
                department=row["department"],
                years_experience=int(row["years_experience"]),
                skills=skills,
                competencies=competencies
            )
            employees[employee.employee_id] = employee
        return employees
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading employees: {e}")
        return {}

def save_employees_to_excel(employees: Dict[str, Employee]):
    """Save employees to Resources.xlsx"""
    if not employees:
        return
    
    try:
        data = []
        all_skills = set()
        all_competencies = set()
        
        for emp in employees.values():
            all_skills.update(emp.skills.keys())
            all_competencies.update(emp.competencies.keys())
        
        # Create rows
        for emp in employees.values():
            row = {
                "employee_id": emp.employee_id,
                "name": emp.name,
                "current_role": emp.current_role,
                "department": emp.department,
                "years_experience": emp.years_experience
            }
            
            # Add skills columns
            for skill in sorted(all_skills):
                row[f"skill_{skill.lower().replace(' ', '_')}"] = emp.skills.get(skill, 0)
            
            # Add competency columns
            for comp in sorted(all_competencies):
                row[f"comp_{comp.lower().replace(' ', '_')}"] = emp.competencies.get(comp, 0)
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Ensure directory is writable and file can be created
        os.makedirs(CURRENT_DIR, exist_ok=True)
        
        df.to_excel(RESOURCES_FILE, index=False, engine='openpyxl')
        print(f"Successfully saved {len(employees)} employees to {RESOURCES_FILE}")
        
    except PermissionError as e:
        print(f"Permission error writing to {RESOURCES_FILE}: {e}")
        temp_file = f"/tmp/resources_backup.xlsx"
        df.to_excel(temp_file, index=False, engine='openpyxl')
        print(f"Saved to temporary location: {temp_file}")
    except Exception as e:
        print(f"Error saving employees to Excel: {e}")
        raise

def load_future_jobs_from_excel() -> Dict[str, FutureJob]:
    """Load future jobs from requests.xlsx"""
    try:
        df = pd.read_excel(REQUESTS_FILE)
        jobs = {}
        for _, row in df.iterrows():
            # Parse required skills and competencies
            required_skills = {}
            required_competencies = {}
            
            for col in df.columns:
                if col.startswith("req_skill_") and pd.notna(row[col]):
                    skill_name = col.replace("req_skill_", "").replace("_", " ").title()
                    required_skills[skill_name] = int(row[col])
                elif col.startswith("req_comp_") and pd.notna(row[col]):
                    comp_name = col.replace("req_comp_", "").replace("_", " ").title()
                    required_competencies[comp_name] = int(row[col])
            
            job = FutureJob(
                job_id=row.get("job_id", str(uuid.uuid4())[:12]),
                title=row["title"],
                department=row["department"],
                level=row["level"],
                required_skills=required_skills,
                required_competencies=required_competencies
            )
            jobs[job.job_id] = job
        return jobs
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading future jobs: {e}")
        return {}

def save_future_jobs_to_excel(jobs: Dict[str, FutureJob]):
    """Save future jobs to requests.xlsx"""
    if not jobs:
        return
    
    try:
        data = []
        all_skills = set()
        all_competencies = set()
        
        for job in jobs.values():
            all_skills.update(job.required_skills.keys())
            all_competencies.update(job.required_competencies.keys())
        
        for job in jobs.values():
            row = {
                "job_id": job.job_id,
                "title": job.title,
                "department": job.department,
                "level": job.level
            }
            
            for skill in sorted(all_skills):
                row[f"req_skill_{skill.lower().replace(' ', '_')}"] = job.required_skills.get(skill, 0)
            
            for comp in sorted(all_competencies):
                row[f"req_comp_{comp.lower().replace(' ', '_')}"] = job.required_competencies.get(comp, 0)
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        os.makedirs(CURRENT_DIR, exist_ok=True)
        
        df.to_excel(REQUESTS_FILE, index=False, engine='openpyxl')
        print(f"Successfully saved {len(jobs)} future jobs to {REQUESTS_FILE}")
        
    except PermissionError as e:
        print(f"Permission error writing to {REQUESTS_FILE}: {e}")
        temp_file = f"/tmp/requests_backup.xlsx"
        df.to_excel(temp_file, index=False, engine='openpyxl')
        print(f"Saved to temporary location: {temp_file}")
    except Exception as e:
        print(f"Error saving future jobs to Excel: {e}")
        raise

# Data Generation Functions
def create_random_employee() -> Employee:
    """Create a random employee with ALL skills and competencies rated 1-10"""
    skills = {}
    for skill in ALL_SKILLS:
        skills[skill] = random.randint(1, 10)
    
    competencies = {}
    for competency in ALL_COMPETENCIES:
        competencies[competency] = random.randint(1, 10)
    
    # Generate other attributes
    names = [
        "Alex Rivera", "Sam Chen", "Jordan Martinez", "Taylor Johnson", "Casey Park",
        "Morgan Davis", "Riley Thompson", "Cameron Lee", "Avery Garcia", "Dakota Kim"
    ]
    
    roles = [
        "Architecture Analyst", "Associate Architect", "Solution Architect",
        "Senior Solution Architect", "Lead Architect", "Principal Architect",
        "Enterprise Architect", "Chief Architect"
    ]
    
    return Employee(
        name=random.choice(names),
        current_role=random.choice(roles),
        department=random.choice(DEPARTMENTS),
        years_experience=random.randint(1, 15),
        skills=skills,
        competencies=competencies
    )

def create_random_future_job() -> FutureJob:
    """Create a random future job with requirements for ALL skills and competencies rated 1-10"""
    required_skills = {}
    for skill in ALL_SKILLS:
        required_skills[skill] = random.randint(1, 7) 
    
    required_competencies = {}
    for competency in ALL_COMPETENCIES:
        required_competencies[competency] = random.randint(1, 7) 
    
    levels = ["Junior", "Mid", "Senior", "Lead", "Principal", "Executive"]
    
    return FutureJob(
        title=random.choice(FUTURE_JOB_TITLES),
        department=random.choice(DEPARTMENTS),
        level=random.choice(levels),
        required_skills=required_skills,
        required_competencies=required_competencies
    )

# MCP Tools
@mcp.tool()
async def generate_resources(count: int = 5) -> Dict[str, Any]:
    """
    Generate current employee profiles and save to Resources.xlsx
    
    Args:
        count: Number of employees to generate (1-20)
        
    Returns:
        Dictionary with generated employees and metadata
    """
    if count < 1 or count > 20:
        return {"error": "Count must be between 1 and 20"}
    
    # Load existing employees
    existing_employees = load_employees_from_excel()
    
    # Generate new employees
    new_employees = []
    for i in range(count):
        employee = create_random_employee()
        existing_employees[employee.employee_id] = employee
        new_employees.append(employee)
        talent_data["employees"][employee.employee_id] = employee
    
    # Save to Excel
    save_employees_to_excel(existing_employees)
    
    return {
        "generated_employees": [emp.model_dump() for emp in new_employees],
        "count": len(new_employees),
        "total_in_database": len(existing_employees),
        "saved_to": RESOURCES_FILE,
        "status": "success"
    }

@mcp.tool()
async def generate_requests(count: int = 3) -> Dict[str, Any]:
    """
    Generate future job opportunities and save to requests.xlsx
    
    Args:
        count: Number of future jobs to generate (1-15)
        
    Returns:
        Dictionary with generated future jobs and metadata
    """
    if count < 1 or count > 15:
        return {"error": "Count must be between 1 and 15"}
    
    # Load existing jobs
    existing_jobs = load_future_jobs_from_excel()
    
    # Generate new jobs
    new_jobs = []
    for i in range(count):
        job = create_random_future_job()
        existing_jobs[job.job_id] = job
        new_jobs.append(job)
        talent_data["future_jobs"][job.job_id] = job
    
    # Save to Excel
    save_future_jobs_to_excel(existing_jobs)
    
    return {
        "generated_jobs": [job.model_dump() for job in new_jobs],
        "count": len(new_jobs),
        "total_in_database": len(existing_jobs),
        "saved_to": REQUESTS_FILE,
        "status": "success"
    }

@mcp.tool()
async def lookup_employee_by_name(name: str) -> Dict[str, Any]:
    """
    Look up employee information by name
    
    Args:
        name: Employee name to search for (case-insensitive, partial matches allowed)
        
    Returns:
        Dictionary with matching employee(s) and their complete information
    """
    employees = load_employees_from_excel()
    
    if not employees:
        return {"error": "No employees found in database", "matches": []}
    
    # Search for matches (case-insensitive, partial matching)
    matches = []
    search_name = name.lower().strip()
    
    for employee in employees.values():
        if search_name in employee.name.lower():
            matches.append(employee.model_dump())
    
    if not matches:
        return {
            "searched_name": name,
            "matches": [],
            "match_count": 0,
            "message": f"No employees found with name containing '{name}'"
        }
    
    return {
        "searched_name": name,
        "matches": matches,
        "match_count": len(matches),
        "status": "success"
    }

@mcp.tool()
async def lookup_job_by_title(title: str) -> Dict[str, Any]:
    """
    Look up job information by title
    
    Args:
        title: Job title to search for (case-insensitive, partial matches allowed)
        
    Returns:
        Dictionary with matching job(s) and their complete information
    """
    jobs = load_future_jobs_from_excel()
    
    if not jobs:
        return {"error": "No jobs found in database", "matches": []}
    
    # Search for matches (case-insensitive, partial matching)
    matches = []
    search_title = title.lower().strip()
    
    for job in jobs.values():
        if search_title in job.title.lower():
            matches.append(job.model_dump())
    
    if not matches:
        return {
            "searched_title": title,
            "matches": [],
            "match_count": 0,
            "message": f"No jobs found with title containing '{title}'"
        }
    
    return {
        "searched_title": title,
        "matches": matches,
        "match_count": len(matches),
        "status": "success"
    }

@mcp.tool()
async def get_talent_overview() -> Dict[str, Any]:
    """
    Get overview of all employees and future jobs in the system
    
    Returns:
        Dictionary with complete database overview
    """
    employees = load_employees_from_excel()
    jobs = load_future_jobs_from_excel()
    
    return {
        "resources": {
            "count": len(employees),
            "file": RESOURCES_FILE,
            "employees": [emp.model_dump() for emp in employees.values()]
        },
        "requests": {
            "count": len(jobs),
            "file": REQUESTS_FILE, 
            "future_jobs": [job.model_dump() for job in jobs.values()]
        },
        "skill_scale": "1-10 (1=Beginner, 10=Expert)",
        "status": "success"
    }

if __name__ == "__main__":
    print("Starting Employee-Future Jobs Data Generation MCP Server...")
    print("Available tools:")
    print("- generate_resources: Create current employee profiles → resources.xlsx")
    print("- generate_requests: Create future job opportunities → requests.xlsx") 
    print("- get_talent_overview: View all data from both files")
    print("- lookup_employee_by_name: Find employee information by name")
    print("- lookup_job_by_title: Find job information by title")
    print(f"Skill/Competency Scale: 1-10")
    
    # Run the server
    mcp.run()
