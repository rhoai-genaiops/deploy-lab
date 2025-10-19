#!/usr/bin/env python3
"""
PDF Syllabus Generator for RDU University Programs
Generates comprehensive syllabus PDFs from structured content.

Requirements:
    pip install reportlab markdown2

Usage:
    python generate_syllabus_pdfs.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import black, blue, darkblue, gray
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    import markdown2
except ImportError:
    print("Required libraries not found. Please install:")
    print("pip install reportlab markdown2")
    sys.exit(1)

class SyllabusContent:
    """Container for syllabus content data"""
    
    def __init__(self, program_name: str, description: str, pillars: List[str], 
                 learning_outcomes: List[str], semesters: Dict[int, List[Dict]]):
        self.program_name = program_name
        self.description = description
        self.pillars = pillars
        self.learning_outcomes = learning_outcomes
        self.semesters = semesters

class SyllabusPDFGenerator:
    """Generates comprehensive syllabus PDFs in the style of the biotechnology template"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=darkblue,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=gray,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=8,
            textColor=darkblue
        ))
        
        # Course style
        self.styles.add(ParagraphStyle(
            name='Course',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=20
        ))
    
    def generate_pdf(self, content: SyllabusContent, filename: str):
        """Generate a complete syllabus PDF"""
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(content))
        story.append(PageBreak())
        
        # Program overview
        story.extend(self._create_program_overview(content))
        
        # Learning outcomes
        story.extend(self._create_learning_outcomes(content))
        
        # Curriculum structure
        story.extend(self._create_curriculum_structure(content))
        
        # Additional sections
        story.extend(self._create_additional_sections(content))
        
        doc.build(story)
        print(f"Generated: {filepath}")
    
    def _create_title_page(self, content: SyllabusContent) -> List:
        """Create the title page"""
        story = []
        
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Bachelor of Science in {content.program_name}", self.styles['CustomTitle']))
        story.append(Paragraph("(4 Years, 240 ECTS)", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(content.description, self.styles['Normal']))
        
        return story
    
    def _create_program_overview(self, content: SyllabusContent) -> List:
        """Create program overview section"""
        story = []
        
        story.append(Paragraph("Program Overview", self.styles['SectionHeader']))
        
        overview_data = [
            ['Award:', f'B.Sc. in {content.program_name}'],
            ['Duration:', '8 Semesters (4 academic years)'],
            ['Total Credits:', '240 ECTS'],
            ['Delivery:', 'Lectures (L), Tutorials (T), Laboratories (P), Studio/Project (S), Fieldwork (F)'],
            ['Typical Workload:', '1 ECTS ≈ 25–30 hours']
        ]
        
        table = Table(overview_data, colWidths=[3*cm, 12*cm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Pillars
        pillars_text = " • ".join(content.pillars)
        story.append(Paragraph(f"<b>Pillars:</b> {pillars_text}", self.styles['Normal']))
        
        return story
    
    def _create_learning_outcomes(self, content: SyllabusContent) -> List:
        """Create learning outcomes section"""
        story = []
        
        story.append(Paragraph("Graduate Learning Outcomes", self.styles['SectionHeader']))
        story.append(Paragraph("Graduates will be able to:", self.styles['Normal']))
        story.append(Spacer(1, 6))
        
        for i, outcome in enumerate(content.learning_outcomes, 1):
            story.append(Paragraph(f"{i}. {outcome}", self.styles['Normal']))
            story.append(Spacer(1, 4))
        
        return story
    
    def _create_curriculum_structure(self, content: SyllabusContent) -> List:
        """Create curriculum structure section"""
        story = []
        
        story.append(Paragraph("Curriculum Map (By Semester)", self.styles['SectionHeader']))
        story.append(Paragraph("Each course lists ECTS, L-T-P-S, Pre/Co-requisites, Assessment, Tools, and Detailed Topics with representative labs/projects.", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        for semester_num in sorted(content.semesters.keys()):
            courses = content.semesters[semester_num]
            story.append(Paragraph(f"Semester {semester_num} (30 ECTS)", self.styles['Heading3']))
            
            for course in courses:
                course_title = f"{course['code']} {course['name']} ({course['ects']} ECTS, {course['format']})"
                story.append(Paragraph(course_title, self.styles['Course']))
                
                if 'prereq' in course and course['prereq']:
                    story.append(Paragraph(f"Pre: {course['prereq']}", self.styles['Course']))
                
                if 'assessment' in course:
                    story.append(Paragraph(f"Assessment: {course['assessment']}", self.styles['Course']))
                
                if 'topics' in course:
                    story.append(Paragraph(f"Topics: {course['topics']}", self.styles['Course']))
                
                if 'labs' in course:
                    story.append(Paragraph(f"Labs: {course['labs']}", self.styles['Course']))
                
                story.append(Spacer(1, 8))
        
        return story
    
    def _create_additional_sections(self, content: SyllabusContent) -> List:
        """Create additional standard sections"""
        story = []
        
        # Technical Electives section
        story.append(PageBreak())
        story.append(Paragraph("Technical Elective Tracks", self.styles['SectionHeader']))
        story.append(Paragraph("Choose at least 5 electives; focus on one track for specialization.", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Facilities section
        story.append(Paragraph("Laboratories & Facilities", self.styles['SectionHeader']))
        story.append(Paragraph("State-of-the-art laboratories and computing facilities support hands-on learning and research activities.", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Assessment section
        story.append(Paragraph("Assessment & Quality Assurance", self.styles['SectionHeader']))
        story.append(Paragraph("Comprehensive assessment methods ensure academic rigor and professional preparation.", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        
        return story

# Comprehensive syllabus content for all 16 programs
SYLLABUS_CONTENT = {
    "Environmental Science": SyllabusContent(
        program_name="Environmental Science",
        description="An interdisciplinary program integrating natural sciences, policy analysis, and field research to address environmental challenges. Structured across 8 semesters with field studies, laboratory research, policy analysis, and a two-semester capstone.",
        pillars=["Ecology", "Environmental Chemistry", "Atmospheric Science", "Hydrology", "Soil Science", "Environmental Policy", "GIS & Remote Sensing", "Sustainability", "Conservation Biology", "Climate Science"],
        learning_outcomes=[
            "Apply scientific principles to analyze environmental systems and human impacts",
            "Conduct field and laboratory research using modern analytical techniques",
            "Evaluate environmental policies and regulations for effectiveness and compliance",
            "Use GIS, remote sensing, and modeling tools for environmental analysis",
            "Communicate environmental science findings to diverse stakeholders",
            "Design sustainable solutions for environmental challenges",
            "Conduct environmental impact assessments and risk analyses"
        ],
        semesters={
            1: [
                {"code": "ES101", "name": "Environmental Science Foundations", "ects": 6, "format": "3-1-2-0", "topics": "Earth systems, biogeochemical cycles, human-environment interactions", "labs": "Water quality analysis, soil sampling, ecosystem observations"},
                {"code": "ES102", "name": "General Chemistry for Environmental Science", "ects": 6, "format": "3-1-2-0", "topics": "Chemical principles, environmental chemistry, analytical methods", "labs": "Titrations, spectroscopy, environmental sample analysis"},
                {"code": "ES103", "name": "Calculus & Statistics for Environmental Science", "ects": 6, "format": "3-2-0-0", "topics": "Calculus applications, descriptive statistics, probability, hypothesis testing", "tools": "R, Excel, statistical software"},
                {"code": "ES104", "name": "Biology for Environmental Scientists", "ects": 6, "format": "3-1-2-0", "topics": "Ecology, biodiversity, population dynamics, conservation biology", "labs": "Field surveys, species identification, population studies"},
                {"code": "ES105", "name": "Environmental Communication & Ethics", "ects": 6, "format": "2-1-0-1", "topics": "Scientific writing, environmental ethics, stakeholder communication", "assessment": "Reports 40%, Presentations 30%, Ethics cases 30%"}
            ],
            2: [
                {"code": "ES106", "name": "Physical Geography & Climate", "ects": 6, "format": "3-1-1-0", "prereq": "ES101", "topics": "Atmospheric processes, climate systems, weather patterns, climate change", "labs": "Weather monitoring, climate data analysis"},
                {"code": "ES107", "name": "Organic Chemistry for Environmental Science", "ects": 6, "format": "3-1-2-0", "prereq": "ES102", "topics": "Organic pollutants, pesticides, environmental fate and transport", "labs": "Extraction methods, chromatography, compound identification"},
                {"code": "ES108", "name": "Environmental Data Analysis", "ects": 6, "format": "2-1-2-0", "prereq": "ES103", "topics": "Statistical analysis, data visualization, experimental design", "tools": "R, Python, GIS software"},
                {"code": "ES109", "name": "Hydrology & Water Resources", "ects": 6, "format": "3-1-1-0", "topics": "Water cycle, surface water, groundwater, watershed management", "labs": "Stream flow measurement, water table monitoring"},
                {"code": "ES110", "name": "Environmental Policy & Law", "ects": 6, "format": "2-2-0-0", "topics": "Environmental regulations, policy analysis, compliance, international agreements", "assessment": "Policy briefs, case studies, mock hearings"}
            ]
        }
    ),
    
    "Data Science": SyllabusContent(
        program_name="Data Science",
        description="A comprehensive program combining statistics, computer science, and domain expertise to extract insights from data. Structured across 8 semesters with programming, machine learning, big data technologies, and real-world applications.",
        pillars=["Statistics & Probability", "Programming & Software Engineering", "Machine Learning", "Big Data Technologies", "Data Visualization", "Database Systems", "Ethics & Privacy", "Business Intelligence", "Research Methods", "Communication"],
        learning_outcomes=[
            "Apply statistical methods and machine learning algorithms to analyze complex datasets",
            "Program in multiple languages (Python, R, SQL, Java) for data processing and analysis",
            "Design and implement scalable data pipelines and storage solutions",
            "Create effective data visualizations and communicate findings to stakeholders",
            "Ensure ethical use of data and protect privacy in data science projects",
            "Work with big data technologies and cloud computing platforms",
            "Conduct reproducible research and maintain version control of projects"
        ],
        semesters={
            1: [
                {"code": "DS101", "name": "Introduction to Data Science", "ects": 6, "format": "3-1-2-0", "topics": "Data science lifecycle, exploratory data analysis, basic statistics", "tools": "Python, Jupyter notebooks, pandas"},
                {"code": "DS102", "name": "Programming Fundamentals I (Python)", "ects": 6, "format": "2-1-3-0", "topics": "Python syntax, data structures, algorithms, object-oriented programming", "labs": "Programming exercises, project development"},
                {"code": "DS103", "name": "Mathematics for Data Science I", "ects": 6, "format": "3-2-0-0", "topics": "Linear algebra, calculus, probability theory, discrete mathematics", "tools": "Mathematical software, symbolic computation"},
                {"code": "DS104", "name": "Statistics & Probability", "ects": 6, "format": "3-1-1-0", "topics": "Descriptive statistics, probability distributions, hypothesis testing", "labs": "Statistical computing, simulation studies"},
                {"code": "DS105", "name": "Data Ethics & Communication", "ects": 6, "format": "2-1-0-1", "topics": "Data privacy, algorithmic bias, ethical frameworks, technical communication", "assessment": "Ethics cases 40%, Communication projects 60%"}
            ],
            2: [
                {"code": "DS106", "name": "Programming Fundamentals II (R & SQL)", "ects": 6, "format": "2-1-3-0", "prereq": "DS102", "topics": "R programming, database design, SQL queries, data manipulation", "labs": "Database projects, statistical computing"},
                {"code": "DS107", "name": "Mathematics for Data Science II", "ects": 6, "format": "3-2-0-0", "prereq": "DS103", "topics": "Multivariable calculus, optimization, numerical methods", "applications": "Machine learning mathematics, computational methods"},
                {"code": "DS108", "name": "Data Structures & Algorithms", "ects": 6, "format": "3-1-2-0", "prereq": "DS102", "topics": "Algorithm analysis, sorting, searching, graph algorithms, complexity", "labs": "Algorithm implementation, performance analysis"},
                {"code": "DS109", "name": "Data Visualization & Exploration", "ects": 6, "format": "2-1-2-0", "prereq": "DS101", "topics": "Visualization principles, interactive dashboards, storytelling with data", "tools": "matplotlib, seaborn, plotly, Tableau"},
                {"code": "DS110", "name": "Web Technologies for Data Science", "ects": 6, "format": "2-1-2-0", "topics": "HTML/CSS, JavaScript, web scraping, APIs, web applications", "labs": "Web development projects, data collection"}
            ]
        }
    ),
    
    # Add more programs as needed...
    
    "Business Administration": SyllabusContent(
        program_name="Business Administration",
        description="A comprehensive business program integrating management theory, analytical skills, and practical experience across all functional areas. Structured across 8 semesters with case studies, internships, consulting projects, and a strategic capstone.",
        pillars=["Strategic Management", "Finance & Accounting", "Marketing", "Operations Management", "Human Resources", "Entrepreneurship", "International Business", "Business Analytics", "Ethics & Leadership", "Innovation Management"],
        learning_outcomes=[
            "Analyze complex business problems using analytical and strategic thinking",
            "Apply financial and accounting principles for business decision-making",
            "Develop and implement marketing strategies for diverse markets",
            "Design efficient operations and supply chain management systems",
            "Lead teams and manage human resources effectively",
            "Evaluate entrepreneurial opportunities and develop business plans",
            "Communicate business ideas clearly and persuasively to stakeholders"
        ],
        semesters={
            1: [
                {"code": "BA101", "name": "Introduction to Business", "ects": 6, "format": "3-2-0-0", "topics": "Business fundamentals, organizational structures, stakeholder analysis", "assessment": "Case studies 40%, Exam 60%"},
                {"code": "BA102", "name": "Microeconomics", "ects": 6, "format": "3-2-0-0", "topics": "Supply and demand, market structures, consumer behavior, pricing", "tools": "Economic modeling software"},
                {"code": "BA103", "name": "Business Mathematics & Statistics", "ects": 6, "format": "3-1-1-0", "topics": "Financial mathematics, probability, descriptive statistics, regression", "labs": "Excel, statistical analysis"},
                {"code": "BA104", "name": "Accounting Fundamentals", "ects": 6, "format": "3-1-1-0", "topics": "Financial statements, double-entry bookkeeping, basic analysis", "labs": "Accounting software, financial statement preparation"},
                {"code": "BA105", "name": "Business Communication", "ects": 6, "format": "2-1-0-1", "topics": "Written and oral communication, presentation skills, professional etiquette", "assessment": "Presentations 50%, Writing assignments 50%"}
            ],
            2: [
                {"code": "BA106", "name": "Macroeconomics", "ects": 6, "format": "3-2-0-0", "prereq": "BA102", "topics": "National economy, fiscal and monetary policy, international trade", "applications": "Economic forecasting, policy analysis"},
                {"code": "BA107", "name": "Management Accounting", "ects": 6, "format": "3-1-1-0", "prereq": "BA104", "topics": "Cost analysis, budgeting, performance measurement", "labs": "Cost accounting systems, variance analysis"},
                {"code": "BA108", "name": "Organizational Behavior", "ects": 6, "format": "3-1-0-1", "topics": "Individual and group behavior, motivation, leadership, team dynamics", "assessment": "Team projects 40%, Case analysis 60%"},
                {"code": "BA109", "name": "Marketing Principles", "ects": 6, "format": "3-1-1-0", "topics": "Marketing mix, consumer behavior, market research, segmentation", "labs": "Market analysis projects, survey design"},
                {"code": "BA110", "name": "Business Ethics & Law", "ects": 6, "format": "2-2-0-0", "topics": "Ethical frameworks, corporate responsibility, business law, compliance", "assessment": "Ethics cases, legal analysis, debates"}
            ]
        }
    )
}

def main():
    """Generate all syllabus PDFs"""
    generator = SyllabusPDFGenerator()
    
    # Generate PDFs for the content we have defined
    for program_name, content in SYLLABUS_CONTENT.items():
        filename = f"{program_name.replace(' ', '_')}_Syllabus_(4‑year,_240_Ects).pdf"
        generator.generate_pdf(content, filename)
    
    print(f"\nGenerated {len(SYLLABUS_CONTENT)} syllabus PDFs")
    print("\nTo generate all 16 PDFs, please:")
    print("1. Install required libraries: pip install reportlab markdown2")
    print("2. Add the remaining program content to SYLLABUS_CONTENT dictionary")
    print("3. Run this script: python generate_syllabus_pdfs.py")

if __name__ == "__main__":
    main()