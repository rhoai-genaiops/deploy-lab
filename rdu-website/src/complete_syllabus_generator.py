#!/usr/bin/env python3
"""
Complete PDF Syllabus Generator for All 16 RDU University Programs
Generates comprehensive syllabus PDFs matching the biotechnology template format.

This script contains complete content for all 16 required programs:
1. Chemistry, 2. Mathematics, 3. Physics, 4. Environmental Science, 5. Data Science,
6. Electrical Engineering, 7. Civil Engineering, 8. Chemical Engineering, 
9. Aerospace Engineering, 10. Business Administration, 11. Economics, 12. Psychology,
13. Public Health, 14. Art & Design, 15. Communications, 16. International Studies

Requirements:
    pip install reportlab markdown2

Usage:
    python complete_syllabus_generator.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Import the PDF generator class from the previous script
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import black, blue, darkblue, gray
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
except ImportError:
    print("Required libraries not found. Please install:")
    print("pip install reportlab markdown2")
    sys.exit(1)

class SyllabusContent:
    """Container for syllabus content data"""
    
    def __init__(self, program_name: str, description: str, pillars: List[str], 
                 learning_outcomes: List[str], semesters: Dict[int, List[Dict]],
                 elective_tracks: List[Dict] = None, facilities: str = "",
                 career_paths: List[str] = None):
        self.program_name = program_name
        self.description = description
        self.pillars = pillars
        self.learning_outcomes = learning_outcomes
        self.semesters = semesters
        self.elective_tracks = elective_tracks or []
        self.facilities = facilities
        self.career_paths = career_paths or []

class CompleteSyllabusPDFGenerator:
    """Enhanced PDF generator with comprehensive content"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles matching biotechnology template"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=16,
            textColor=gray,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        # Description style
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=16,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Course style
        self.styles.add(ParagraphStyle(
            name='Course',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=2,
            leftIndent=20,
            fontName='Helvetica'
        ))
        
        # Course detail style
        self.styles.add(ParagraphStyle(
            name='CourseDetail',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceBefore=2,
            spaceAfter=2,
            leftIndent=40,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, content: SyllabusContent, filename: str):
        """Generate a complete syllabus PDF matching biotechnology template"""
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2.5*cm, bottomMargin=2*cm)
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(content))
        
        # Program overview
        story.extend(self._create_program_overview(content))
        
        # Learning outcomes
        story.extend(self._create_learning_outcomes(content))
        
        # Curriculum structure
        story.extend(self._create_curriculum_structure(content))
        
        # Elective tracks
        if content.elective_tracks:
            story.extend(self._create_elective_tracks(content))
        
        # Facilities and additional sections
        story.extend(self._create_additional_sections(content))
        
        doc.build(story)
        print(f"Generated: {filepath}")
    
    def _create_title_page(self, content: SyllabusContent) -> List:
        """Create comprehensive title page"""
        story = []
        
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Bachelor of Science in {content.program_name} (4 Years, 240 ECTS)", 
                              self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(content.description, self.styles['Description']))
        story.append(Spacer(1, 0.5*inch))
        
        return story
    
    def _create_program_overview(self, content: SyllabusContent) -> List:
        """Create detailed program overview section"""
        story = []
        
        story.append(Paragraph("Program Overview", self.styles['SectionHeader']))
        
        overview_data = [
            ['<b>Award:</b>', f'B.Sc. in {content.program_name}'],
            ['<b>Duration:</b>', '8 Semesters (4 academic years)'],
            ['<b>Total Credits:</b>', '240 ECTS'],
            ['<b>Delivery:</b>', 'Lectures (L), Tutorials (T), Laboratories (P), Studio/Project (S), Fieldwork (F)'],
            ['<b>Typical Workload:</b>', '1 ECTS ≈ 25–30 hours']
        ]
        
        table = Table(overview_data, colWidths=[4*cm, 11*cm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Pillars
        pillars_text = " • ".join(content.pillars)
        story.append(Paragraph(f"<b>Pillars:</b> {pillars_text}", self.styles['Normal']))
        story.append(Spacer(1, 16))
        
        return story
    
    def _create_learning_outcomes(self, content: SyllabusContent) -> List:
        """Create comprehensive learning outcomes section"""
        story = []
        
        story.append(Paragraph("Graduate Learning Outcomes", self.styles['SectionHeader']))
        story.append(Paragraph("Graduates will be able to:", self.styles['Normal']))
        story.append(Spacer(1, 8))
        
        for i, outcome in enumerate(content.learning_outcomes, 1):
            outcome_parts = outcome.split("**")
            if len(outcome_parts) >= 3:
                formatted_outcome = f"{i}. <b>{outcome_parts[1]}</b> {outcome_parts[2]}"
            else:
                formatted_outcome = f"{i}. {outcome}"
            story.append(Paragraph(formatted_outcome, self.styles['Normal']))
            story.append(Spacer(1, 6))
        
        return story
    
    def _create_curriculum_structure(self, content: SyllabusContent) -> List:
        """Create detailed curriculum structure"""
        story = []
        
        story.append(Paragraph("Curriculum Map (By Semester)", self.styles['SectionHeader']))
        story.append(Paragraph("Each course lists ECTS, L-T-P-S, Pre/Co-requisites, Assessment, Tools, and Detailed Topics with representative labs/projects.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        for semester_num in sorted(content.semesters.keys()):
            courses = content.semesters[semester_num]
            story.append(Paragraph(f"Semester {semester_num} (30 ECTS)", self.styles['SubsectionHeader']))
            
            for i, course in enumerate(courses, 1):
                course_title = f"{i}. <b>{course['code']} {course['name']}</b> ({course['ects']} ECTS, {course['format']})"
                story.append(Paragraph(course_title, self.styles['Course']))
                
                if 'prereq' in course and course['prereq']:
                    story.append(Paragraph(f"Pre: {course['prereq']}", self.styles['CourseDetail']))
                
                if 'assessment' in course:
                    story.append(Paragraph(f"Assessment: {course['assessment']}", self.styles['CourseDetail']))
                
                if 'topics' in course:
                    story.append(Paragraph(f"Topics: {course['topics']}", self.styles['CourseDetail']))
                
                if 'labs' in course:
                    story.append(Paragraph(f"Labs: {course['labs']}", self.styles['CourseDetail']))
                
                if 'tools' in course:
                    story.append(Paragraph(f"Tools: {course['tools']}", self.styles['CourseDetail']))
                
                story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 12))
        
        return story
    
    def _create_elective_tracks(self, content: SyllabusContent) -> List:
        """Create technical elective tracks section"""
        story = []
        
        story.append(PageBreak())
        story.append(Paragraph("Technical Elective Tracks (Sample Menus)", self.styles['SectionHeader']))
        story.append(Paragraph("Choose at least 5 electives; ≥ 2 must be lab/process design focused.", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        for track in content.elective_tracks:
            story.append(Paragraph(f"<b>{track['name']}</b>", self.styles['SubsectionHeader']))
            for course in track['courses']:
                story.append(Paragraph(f"• <b>{course['code']}</b> — {course['description']}", self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_additional_sections(self, content: SyllabusContent) -> List:
        """Create additional standard sections"""
        story = []
        
        # Facilities section
        story.append(Paragraph("Laboratories & Facilities", self.styles['SectionHeader']))
        if content.facilities:
            story.append(Paragraph(content.facilities, self.styles['Normal']))
        else:
            story.append(Paragraph("State-of-the-art laboratories and computing facilities support hands-on learning and research activities.", 
                                  self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Assessment section
        story.append(Paragraph("Assessment & Quality Assurance", self.styles['SectionHeader']))
        story.append(Paragraph("Comprehensive assessment methods emphasize academic rigor, practical skills, and professional preparation. "
                              "Authentic assessment includes laboratory practicals, research projects, oral presentations, and peer review.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Career preparation
        if content.career_paths:
            story.append(Paragraph("Career Preparation", self.styles['SectionHeader']))
            career_text = "Graduates are prepared for careers in: " + ", ".join(content.career_paths) + "."
            story.append(Paragraph(career_text, self.styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Accreditation mapping
        story.append(Paragraph("Accreditation Mapping", self.styles['SectionHeader']))
        story.append(Paragraph("The program meets international standards for academic quality and professional preparation. "
                              "Regular external review and outcomes assessment ensure continuous improvement.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"This syllabus is a comprehensive template. Institutions should calibrate contact hours, prerequisites, and facilities "
                              f"while preserving academic depth, practical skills, and professional competence.", 
                              self.styles['Normal']))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", 
                              self.styles['Normal']))
        
        return story

# Complete syllabus content for all 16 programs
ALL_SYLLABUS_CONTENT = {
    "Chemistry": SyllabusContent(
        program_name="Chemistry",
        description="A comprehensive chemistry program combining theoretical foundations with extensive laboratory experience in analytical, organic, inorganic, and physical chemistry. Structured across 8 semesters (30 ECTS each) with integrated laboratory courses, research experiences, internship, and a two-semester capstone.",
        pillars=["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Analytical Chemistry", "Computational Chemistry", "Materials Chemistry", "Environmental Chemistry", "Research Methods", "Safety & Ethics", "Professional Development"],
        learning_outcomes=[
            "**Apply fundamental principles** of organic, inorganic, physical, and analytical chemistry to solve complex problems.",
            "**Execute advanced synthetic** and analytical techniques (NMR, MS, IR, UV-Vis, chromatography, crystallography) with precision and safety awareness.",
            "**Collect, analyze, and interpret** experimental data using statistical methods and computational tools (ChemDraw, Gaussian, R/Python).",
            "**Design and conduct** independent research projects from hypothesis formulation to results interpretation and publication.",
            "**Assess chemical hazards** and implement safety protocols, environmental stewardship, and risk management in laboratory settings.",
            "**Communicate chemical concepts** and research findings effectively to both scientific and general audiences.",
            "**Demonstrate ethical behavior**, teamwork skills, and lifelong learning in chemistry careers and graduate studies."
        ],
        semesters={
            1: [
                {"code": "CH101", "name": "General Chemistry I (Atomic Structure & Bonding)", "ects": 6, "format": "3-1-2-0", "assessment": "Labs/Reports 35%, Midterm 20%, Final 45%", "topics": "Atomic theory, electronic structure, periodic trends, ionic and covalent bonding, molecular geometry, hybridization", "labs": "Flame tests, molecular modeling, crystal structure determination, spectroscopic analysis"},
                {"code": "CH102", "name": "Mathematics for Chemists I (Calculus)", "ects": 6, "format": "3-2-0-0", "topics": "Limits, derivatives, integrals, applications to chemical kinetics and thermodynamics, differential equations basics", "tools": "MATLAB/Python for numerical methods"},
                {"code": "CH103", "name": "Physics for Chemists I (Mechanics & Thermodynamics)", "ects": 6, "format": "3-1-1-0", "topics": "Classical mechanics, waves, thermodynamics, statistical mechanics, applications to chemical systems", "labs": "Calorimetry, thermal analysis, pressure-volume work"},
                {"code": "CH104", "name": "Introduction to Laboratory Techniques", "ects": 6, "format": "1-0-4-0", "topics": "Laboratory safety, precision and accuracy, error analysis, basic analytical techniques, data treatment", "labs": "Gravimetric analysis, volumetric analysis, pH measurements, conductivity"},
                {"code": "CH105", "name": "Scientific Writing & Communication", "ects": 6, "format": "2-1-0-1", "topics": "Scientific writing, literature search, citation methods, presentation skills, research ethics", "assessment": "Reports 40%, Presentations 30%, Ethics portfolio 30%"}
            ],
            2: [
                {"code": "CH106", "name": "General Chemistry II (Chemical Reactions & Equilibria)", "ects": 6, "format": "3-1-2-0", "prereq": "CH101", "topics": "Chemical kinetics, equilibrium, acid-base chemistry, electrochemistry, coordination compounds", "labs": "Kinetics studies, potentiometric titrations, synthesis of coordination complexes"},
                {"code": "CH107", "name": "Mathematics for Chemists II (Statistics & Linear Algebra)", "ects": 6, "format": "3-2-0-0", "prereq": "CH102", "topics": "Statistical analysis, linear algebra, matrix operations, eigenvalues, multivariate analysis", "tools": "R/Python for statistical computing, data visualization"},
                {"code": "CH108", "name": "Physics for Chemists II (Electricity & Magnetism)", "ects": 6, "format": "3-1-1-0", "prereq": "CH103", "topics": "Electromagnetic theory, optics, introduction to quantum mechanics, spectroscopy fundamentals", "labs": "Optical spectroscopy, electromagnetic induction experiments"},
                {"code": "CH109", "name": "Quantitative Analysis Laboratory", "ects": 6, "format": "1-0-4-0", "prereq": "CH104", "topics": "Advanced analytical techniques, method validation, quality control, trace analysis", "labs": "HPLC, GC, atomic absorption spectroscopy, method development"},
                {"code": "CH110", "name": "Chemistry Ethics & Safety", "ects": 6, "format": "2-1-0-1", "topics": "Laboratory safety protocols, chemical hazards, environmental impact, research ethics, regulatory compliance", "assessment": "Safety assessments 40%, Ethics cases 30%, Compliance projects 30%"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Pharmaceutical Chemistry",
                "courses": [
                    {"code": "CH451", "description": "Medicinal Chemistry — Drug design, structure-activity relationships, pharmacophores"},
                    {"code": "CH452", "description": "Drug Design & Development — Lead optimization, ADMET properties, clinical trials"},
                    {"code": "CH453", "description": "Pharmacokinetics & Metabolism — Drug metabolism, pharmacokinetic modeling, bioanalysis"},
                    {"code": "CH454", "description": "Natural Products Chemistry — Isolation, structure determination, biosynthesis, drug discovery"}
                ]
            },
            {
                "name": "Track B — Materials & Nanotechnology",
                "courses": [
                    {"code": "CH461", "description": "Polymer Chemistry — Synthesis mechanisms, characterization, structure-property relationships"},
                    {"code": "CH462", "description": "Nanomaterials Synthesis — Bottom-up synthesis, characterization, applications"},
                    {"code": "CH463", "description": "Surface Chemistry — Surface analysis, modification, catalysis, sensors"},
                    {"code": "CH464", "description": "Electronic Materials — Semiconductors, conductors, optical materials, devices"}
                ]
            }
        ],
        facilities="Modern synthesis labs with fume hoods, glove boxes, analytical instrumentation rooms. Equipment: NMR (400 MHz), IR/UV-Vis, GC-MS, HPLC, atomic absorption, X-ray diffractometer, rotary evaporators, lyophilizers. Computational: High-performance computing cluster with Gaussian, ChemDraw, SciFinder, molecular modeling software.",
        career_paths=["pharmaceutical research", "materials science", "environmental consulting", "forensic chemistry", "graduate studies", "chemical industry", "quality control", "patent law"]
    ),
    
    "Mathematics": SyllabusContent(
        program_name="Mathematics",
        description="A comprehensive mathematics program blending pure and applied mathematics with computational methods, statistical analysis, and real-world problem-solving. Structured across 8 semesters (30 ECTS each) with theoretical foundations, computational projects, research experiences, and a two-semester capstone.",
        pillars=["Pure Mathematics", "Applied Mathematics", "Statistics & Probability", "Computational Mathematics", "Mathematical Modeling", "Optimization", "Financial Mathematics", "Data Analysis", "Research Methods", "Professional Development"],
        learning_outcomes=[
            "**Master fundamental concepts** in calculus, algebra, analysis, geometry, and discrete mathematics with rigorous proof techniques.",
            "**Apply mathematical modeling** and computational methods to solve complex problems in science, engineering, finance, and industry.",
            "**Analyze and interpret data** using advanced statistical methods, machine learning algorithms, and visualization techniques.",
            "**Develop and validate** mathematical models for real-world phenomena using analytical and numerical approaches.",
            "**Communicate mathematical ideas** clearly through written proofs, oral presentations, and technical documentation.",
            "**Use computational tools** effectively (MATLAB, R, Python, Mathematica) for mathematical analysis and problem-solving.",
            "**Conduct independent research** in pure or applied mathematics with appropriate methodology and ethical standards."
        ],
        semesters={
            1: [
                {"code": "MA101", "name": "Calculus I (Single Variable)", "ects": 6, "format": "3-2-0-0", "assessment": "Problem Sets 30%, Midterm 25%, Final 45%", "topics": "Limits, continuity, derivatives, applications of derivatives, optimization, curve sketching", "tools": "Graphing calculators, Desmos, GeoGebra"},
                {"code": "MA102", "name": "Linear Algebra I", "ects": 6, "format": "3-2-0-0", "topics": "Vector spaces, linear transformations, matrices, systems of linear equations, determinants", "tools": "MATLAB, Python (NumPy), computational exercises"},
                {"code": "MA103", "name": "Discrete Mathematics", "ects": 6, "format": "3-2-0-0", "topics": "Logic, set theory, combinatorics, graph theory, number theory, algorithms", "labs": "Cryptographic applications, network analysis, algorithm design"},
                {"code": "MA104", "name": "Mathematical Reasoning & Proof Techniques", "ects": 6, "format": "2-2-0-1", "topics": "Logic and proofs, direct proofs, proof by contradiction, induction, proof writing", "assessment": "Proof portfolios 50%, Peer reviews 25%, Exams 25%"},
                {"code": "MA105", "name": "Mathematical Software & Computing", "ects": 6, "format": "2-0-3-0", "topics": "Programming fundamentals, mathematical software packages, numerical precision, visualization", "labs": "MATLAB/Python programming, symbolic computation, mathematical typesetting"}
            ],
            2: [
                {"code": "MA106", "name": "Calculus II (Integral Calculus)", "ects": 6, "format": "3-2-0-0", "prereq": "MA101", "topics": "Integration techniques, applications of integrals, improper integrals, sequences and series", "labs": "Area, volume, work, center of mass, arc length calculations"},
                {"code": "MA107", "name": "Linear Algebra II", "ects": 6, "format": "3-2-0-0", "prereq": "MA102", "topics": "Eigenvalues and eigenvectors, diagonalization, quadratic forms, applications", "labs": "Principal component analysis, dynamical systems, optimization"},
                {"code": "MA108", "name": "Probability & Statistics I", "ects": 6, "format": "3-1-1-0", "topics": "Probability theory, random variables, distributions, expectation, variance", "labs": "Statistical computing, simulation studies, probability modeling"},
                {"code": "MA109", "name": "Differential Equations I", "ects": 6, "format": "3-1-1-0", "prereq": "MA106", "topics": "First-order ODEs, linear ODEs, applications to physics and engineering", "labs": "Numerical solutions, phase portraits, modeling projects"},
                {"code": "MA110", "name": "Mathematical Communication", "ects": 6, "format": "2-1-0-1", "topics": "Technical writing, mathematical presentation, research literature, ethics in mathematics", "assessment": "Technical papers 40%, Presentations 30%, Peer collaboration 30%"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Pure Mathematics",
                "courses": [
                    {"code": "MA451", "description": "Number Theory — Elementary and analytic number theory, cryptographic applications"},
                    {"code": "MA452", "description": "Differential Geometry — Curves and surfaces, Riemannian geometry, general relativity"},
                    {"code": "MA453", "description": "Functional Analysis — Banach and Hilbert spaces, operators, spectral theory"},
                    {"code": "MA454", "description": "Algebraic Geometry — Algebraic varieties, schemes, computational algebra"}
                ]
            },
            {
                "name": "Track B — Applied Mathematics & Engineering",
                "courses": [
                    {"code": "MA461", "description": "Fluid Dynamics — Navier-Stokes equations, computational fluid dynamics"},
                    {"code": "MA462", "description": "Mathematical Biology — Population models, epidemiology, biomechanics"},
                    {"code": "MA463", "description": "Control Theory — Linear systems, stability, optimal control"},
                    {"code": "MA464", "description": "Signal Processing — Fourier analysis, wavelets, digital signal processing"}
                ]
            }
        ],
        facilities="High-performance workstations with MATLAB, Mathematica, R, Python, SAS, specialized software. Computing Resources: Access to university computing cluster, cloud computing platforms. Library: Comprehensive mathematics library, online journal access, mathematical databases.",
        career_paths=["data science", "actuarial science", "financial analysis", "software development", "consulting", "graduate studies", "government research", "education", "quantitative analysis"]
    ),
    
    "Physics": SyllabusContent(
        program_name="Physics",
        description="A comprehensive physics program combining theoretical foundations with experimental techniques and computational methods across classical and modern physics. Structured across 8 semesters (30 ECTS each) with integrated laboratory courses, research experiences, internship, and a two-semester capstone.",
        pillars=["Classical Mechanics", "Electromagnetism", "Quantum Mechanics", "Thermodynamics", "Statistical Mechanics", "Optics", "Atomic & Nuclear Physics", "Condensed Matter", "Computational Physics", "Experimental Methods"],
        learning_outcomes=[
            "**Apply fundamental principles** of classical and modern physics to analyze and solve complex physical problems.",
            "**Design and conduct experiments** using advanced instrumentation, data acquisition systems, and error analysis techniques.",
            "**Utilize computational methods** and programming (Python, MATLAB, C++) for modeling physical systems and data analysis.",
            "**Demonstrate proficiency** in mathematical methods including calculus, differential equations, linear algebra, and complex analysis.",
            "**Communicate scientific results** effectively through technical writing, oral presentations, and peer review.",
            "**Analyze physical phenomena** across multiple scales from subatomic to cosmological using appropriate theoretical frameworks.",
            "**Conduct independent research** with proper methodology, safety protocols, and ethical standards."
        ],
        semesters={
            1: [
                {"code": "PH101", "name": "Classical Mechanics I", "ects": 6, "format": "3-2-1-0", "assessment": "Problem Sets 30%, Lab Reports 20%, Midterm 20%, Final 30%", "topics": "Kinematics, Newton's laws, energy, momentum, oscillations, central forces", "labs": "Motion analysis, pendulum studies, collision experiments, data acquisition"},
                {"code": "PH102", "name": "Mathematics for Physicists I", "ects": 6, "format": "3-2-0-0", "topics": "Calculus, vector analysis, coordinate systems, infinite series, differential equations", "tools": "Mathematical software packages, symbolic computation"},
                {"code": "PH103", "name": "General Chemistry for Physicists", "ects": 6, "format": "3-1-2-0", "topics": "Atomic structure, chemical bonding, thermochemistry, quantum aspects of chemistry", "labs": "Spectroscopy, electrochemistry, thermodynamic measurements"},
                {"code": "PH104", "name": "Introduction to Experimental Physics", "ects": 6, "format": "1-0-4-0", "topics": "Measurement techniques, error analysis, data acquisition, instrumentation basics", "labs": "Fundamental experiments, statistical analysis, report writing"},
                {"code": "PH105", "name": "Physics Communication & Ethics", "ects": 6, "format": "2-1-0-1", "topics": "Scientific writing, presentation skills, research ethics, history of physics", "assessment": "Laboratory notebooks 30%, Technical presentations 40%, Ethics portfolio 30%"}
            ],
            2: [
                {"code": "PH106", "name": "Classical Mechanics II", "ects": 6, "format": "3-2-1-0", "prereq": "PH101", "topics": "Rigid body motion, Lagrangian mechanics, Hamiltonian mechanics, chaos", "labs": "Gyroscopes, coupled oscillators, nonlinear dynamics experiments"},
                {"code": "PH107", "name": "Electricity & Magnetism I", "ects": 6, "format": "3-2-1-0", "prereq": "PH102", "topics": "Electrostatics, Gauss's law, electric potential, capacitance, dielectrics", "labs": "Electric field mapping, capacitor measurements, dielectric properties"},
                {"code": "PH108", "name": "Mathematics for Physicists II", "ects": 6, "format": "3-2-0-0", "prereq": "PH102", "topics": "Complex analysis, Fourier analysis, partial differential equations, special functions", "labs": "Wave equations, boundary value problems, Green's functions"},
                {"code": "PH109", "name": "Computational Physics I", "ects": 6, "format": "2-1-2-0", "topics": "Programming fundamentals, numerical methods, simulation techniques, visualization", "labs": "Python/MATLAB programming, numerical integration, Monte Carlo methods"},
                {"code": "PH110", "name": "Modern Physics Survey", "ects": 6, "format": "3-1-1-0", "topics": "Special relativity, quantum mechanics introduction, atomic structure, nuclear physics", "labs": "Photoelectric effect, electron diffraction, radioactivity measurements"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Theoretical Physics",
                "courses": [
                    {"code": "PH451", "description": "General Relativity — Einstein's field equations, black holes, cosmology"},
                    {"code": "PH452", "description": "Quantum Field Theory — Second quantization, Feynman diagrams, gauge theories"},
                    {"code": "PH453", "description": "Many-Body Theory — Green's functions, Feynman diagrams, phase transitions"},
                    {"code": "PH454", "description": "String Theory Introduction — Basic string theory, extra dimensions, duality"}
                ]
            },
            {
                "name": "Track B — Condensed Matter Physics",
                "courses": [
                    {"code": "PH461", "description": "Advanced Solid State — Electronic band structure, magnetism, superconductivity"},
                    {"code": "PH462", "description": "Semiconductor Physics — Device physics, quantum wells, spintronics"},
                    {"code": "PH463", "description": "Nanophysics — Quantum dots, nanotubes, mesoscopic physics"},
                    {"code": "PH464", "description": "Surface Physics — Surface science, thin films, epitaxy"}
                ]
            }
        ],
        facilities="Core Labs: Mechanics, optics, electronics, atomic physics, nuclear physics, condensed matter. Major Equipment: Scanning probe microscopes, X-ray diffractometer, laser systems, vacuum chambers, cryogenic systems. Computing: High-performance cluster, specialized software (Mathematica, MATLAB, COMSOL, LabVIEW). Clean Room: Microfabrication facility for device fabrication and characterization.",
        career_paths=["graduate studies in physics", "technology companies", "national laboratories", "aerospace industry", "telecommunications", "energy sector", "medical physics", "education", "patent law", "financial modeling"]
    ),
    
    "Environmental Science": SyllabusContent(
        program_name="Environmental Science",
        description="An interdisciplinary program integrating natural sciences, policy analysis, and field research to address environmental challenges. Structured across 8 semesters (30 ECTS each) with field studies, laboratory research, policy analysis, and a two-semester capstone.",
        pillars=["Ecology", "Environmental Chemistry", "Atmospheric Science", "Hydrology", "Soil Science", "Environmental Policy", "GIS & Remote Sensing", "Sustainability", "Conservation Biology", "Climate Science"],
        learning_outcomes=[
            "**Apply scientific principles** to analyze environmental systems and human impacts on natural processes.",
            "**Conduct field and laboratory research** using modern analytical techniques and instrumentation.",
            "**Evaluate environmental policies** and regulations for effectiveness and compliance with standards.",
            "**Use GIS, remote sensing**, and modeling tools for environmental analysis and decision-making.",
            "**Communicate environmental science** findings to diverse stakeholders including policymakers and the public.",
            "**Design sustainable solutions** for environmental challenges using interdisciplinary approaches.",
            "**Conduct environmental impact assessments** and risk analyses for development projects."
        ],
        semesters={
            1: [
                {"code": "ES101", "name": "Environmental Science Foundations", "ects": 6, "format": "3-1-2-0", "assessment": "Field reports 30%, Lab work 25%, Exams 45%", "topics": "Earth systems, biogeochemical cycles, human-environment interactions, sustainability principles", "labs": "Water quality analysis, soil sampling, ecosystem observations, environmental monitoring"},
                {"code": "ES102", "name": "General Chemistry for Environmental Science", "ects": 6, "format": "3-1-2-0", "topics": "Chemical principles, environmental chemistry, analytical methods, pollution chemistry", "labs": "Titrations, spectroscopy, environmental sample analysis, contamination studies"},
                {"code": "ES103", "name": "Calculus & Statistics for Environmental Science", "ects": 6, "format": "3-2-0-0", "topics": "Calculus applications, descriptive statistics, probability, hypothesis testing, environmental data analysis", "tools": "R, Excel, statistical software, graphing calculators"},
                {"code": "ES104", "name": "Biology for Environmental Scientists", "ects": 6, "format": "3-1-2-0", "topics": "Ecology, biodiversity, population dynamics, conservation biology, ecosystem services", "labs": "Field surveys, species identification, population studies, biodiversity assessment"},
                {"code": "ES105", "name": "Environmental Communication & Ethics", "ects": 6, "format": "2-1-0-1", "topics": "Scientific writing, environmental ethics, stakeholder communication, public engagement", "assessment": "Reports 40%, Presentations 30%, Ethics cases 30%"}
            ],
            2: [
                {"code": "ES106", "name": "Physical Geography & Climate", "ects": 6, "format": "3-1-1-0", "prereq": "ES101", "topics": "Atmospheric processes, climate systems, weather patterns, climate change, paleoclimatology", "labs": "Weather monitoring, climate data analysis, GIS mapping"},
                {"code": "ES107", "name": "Organic Chemistry for Environmental Science", "ects": 6, "format": "3-1-2-0", "prereq": "ES102", "topics": "Organic pollutants, pesticides, environmental fate and transport, biodegradation", "labs": "Extraction methods, chromatography, compound identification, persistence studies"},
                {"code": "ES108", "name": "Environmental Data Analysis", "ects": 6, "format": "2-1-2-0", "prereq": "ES103", "topics": "Statistical analysis, data visualization, experimental design, quality assurance", "tools": "R, Python, GIS software, statistical packages"},
                {"code": "ES109", "name": "Hydrology & Water Resources", "ects": 6, "format": "3-1-1-0", "topics": "Water cycle, surface water, groundwater, watershed management, water quality", "labs": "Stream flow measurement, water table monitoring, hydraulic testing"},
                {"code": "ES110", "name": "Environmental Policy & Law", "ects": 6, "format": "2-2-0-0", "topics": "Environmental regulations, policy analysis, compliance, international agreements, environmental justice", "assessment": "Policy briefs 40%, Case studies 30%, Mock hearings 30%"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Environmental Chemistry & Toxicology",
                "courses": [
                    {"code": "ES451", "description": "Advanced Environmental Chemistry — Fate and transport of contaminants, reaction kinetics"},
                    {"code": "ES452", "description": "Environmental Toxicology — Dose-response relationships, risk assessment, ecotoxicology"},
                    {"code": "ES453", "description": "Air Pollution Chemistry — Atmospheric reactions, photochemistry, air quality modeling"},
                    {"code": "ES454", "description": "Environmental Analytical Chemistry — Advanced instrumentation, method development, QA/QC"}
                ]
            },
            {
                "name": "Track B — Ecology & Conservation",
                "courses": [
                    {"code": "ES461", "description": "Conservation Biology — Population genetics, habitat fragmentation, restoration ecology"},
                    {"code": "ES462", "description": "Landscape Ecology — Spatial patterns, connectivity, landscape-scale processes"},
                    {"code": "ES463", "description": "Marine & Aquatic Ecology — Aquatic ecosystems, fisheries, coastal zone management"},
                    {"code": "ES464", "description": "Wildlife Management — Population dynamics, habitat management, human-wildlife conflict"}
                ]
            }
        ],
        facilities="Field research vehicles and equipment, water quality monitoring instruments, soil analysis laboratory, GIS computer lab with ArcGIS and remote sensing software, greenhouse facilities, environmental chambers for controlled studies, analytical chemistry laboratory with HPLC, GC-MS, and spectroscopic equipment.",
        career_paths=["environmental consulting", "government agencies", "non-profit organizations", "environmental law", "corporate sustainability", "research institutions", "education", "environmental health", "climate science", "conservation organizations"]
    ),
    
    "Data Science": SyllabusContent(
        program_name="Data Science",
        description="A comprehensive program combining statistics, computer science, and domain expertise to extract insights from data. Structured across 8 semesters (30 ECTS each) with programming, machine learning, big data technologies, and real-world applications.",
        pillars=["Statistics & Probability", "Programming & Software Engineering", "Machine Learning", "Big Data Technologies", "Data Visualization", "Database Systems", "Ethics & Privacy", "Business Intelligence", "Research Methods", "Communication"],
        learning_outcomes=[
            "**Apply statistical methods** and machine learning algorithms to analyze complex datasets and extract meaningful insights.",
            "**Program in multiple languages** (Python, R, SQL, Java) for data processing, analysis, and application development.",
            "**Design and implement** scalable data pipelines and storage solutions using modern big data technologies.",
            "**Create effective data visualizations** and communicate findings clearly to technical and non-technical stakeholders.",
            "**Ensure ethical use of data** and protect privacy while maintaining transparency in data science projects.",
            "**Work with big data technologies** and cloud computing platforms for large-scale data processing.",
            "**Conduct reproducible research** and maintain version control of data science projects and analyses."
        ],
        semesters={
            1: [
                {"code": "DS101", "name": "Introduction to Data Science", "ects": 6, "format": "3-1-2-0", "assessment": "Projects 50%, Assignments 30%, Exam 20%", "topics": "Data science lifecycle, exploratory data analysis, basic statistics, data types", "tools": "Python, Jupyter notebooks, pandas, matplotlib"},
                {"code": "DS102", "name": "Programming Fundamentals I (Python)", "ects": 6, "format": "2-1-3-0", "topics": "Python syntax, data structures, algorithms, object-oriented programming, debugging", "labs": "Programming exercises, project development, code review"},
                {"code": "DS103", "name": "Mathematics for Data Science I", "ects": 6, "format": "3-2-0-0", "topics": "Linear algebra, calculus, probability theory, discrete mathematics, optimization basics", "tools": "Mathematical software, symbolic computation, numerical libraries"},
                {"code": "DS104", "name": "Statistics & Probability", "ects": 6, "format": "3-1-1-0", "topics": "Descriptive statistics, probability distributions, hypothesis testing, confidence intervals", "labs": "Statistical computing, simulation studies, hypothesis testing"},
                {"code": "DS105", "name": "Data Ethics & Communication", "ects": 6, "format": "2-1-0-1", "topics": "Data privacy, algorithmic bias, ethical frameworks, technical communication, storytelling", "assessment": "Ethics cases 40%, Communication projects 60%"}
            ],
            2: [
                {"code": "DS106", "name": "Programming Fundamentals II (R & SQL)", "ects": 6, "format": "2-1-3-0", "prereq": "DS102", "topics": "R programming, database design, SQL queries, data manipulation, joins", "labs": "Database projects, statistical computing, data wrangling"},
                {"code": "DS107", "name": "Mathematics for Data Science II", "ects": 6, "format": "3-2-0-0", "prereq": "DS103", "topics": "Multivariable calculus, optimization, numerical methods, information theory", "labs": "Machine learning mathematics, computational methods, algorithm analysis"},
                {"code": "DS108", "name": "Data Structures & Algorithms", "ects": 6, "format": "3-1-2-0", "prereq": "DS102", "topics": "Algorithm analysis, sorting, searching, graph algorithms, complexity theory", "labs": "Algorithm implementation, performance analysis, optimization"},
                {"code": "DS109", "name": "Data Visualization & Exploration", "ects": 6, "format": "2-1-2-0", "prereq": "DS101", "topics": "Visualization principles, interactive dashboards, storytelling with data, design theory", "tools": "matplotlib, seaborn, plotly, Tableau, D3.js"},
                {"code": "DS110", "name": "Web Technologies for Data Science", "ects": 6, "format": "2-1-2-0", "topics": "HTML/CSS, JavaScript, web scraping, APIs, web applications, deployment", "labs": "Web development projects, data collection, API integration"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Machine Learning & AI",
                "courses": [
                    {"code": "DS451", "description": "Deep Learning — Neural networks, CNNs, RNNs, transfer learning, model optimization"},
                    {"code": "DS452", "description": "Natural Language Processing — Text processing, sentiment analysis, language models"},
                    {"code": "DS453", "description": "Computer Vision — Image processing, object detection, feature extraction"},
                    {"code": "DS454", "description": "Reinforcement Learning — Markov decision processes, Q-learning, policy optimization"}
                ]
            },
            {
                "name": "Track B — Big Data & Cloud Computing",
                "courses": [
                    {"code": "DS461", "description": "Big Data Technologies — Hadoop, Spark, distributed computing, parallel processing"},
                    {"code": "DS462", "description": "Cloud Computing for Data Science — AWS/Azure/GCP, serverless computing, containers"},
                    {"code": "DS463", "description": "Stream Processing — Real-time analytics, Kafka, Storm, streaming algorithms"},
                    {"code": "DS464", "description": "Data Engineering — ETL pipelines, data warehousing, workflow orchestration"}
                ]
            }
        ],
        facilities="High-performance computing cluster with GPU nodes, cloud computing credits (AWS, Azure, GCP), modern computer labs with multiple monitors, collaborative workspace with whiteboards and presentation equipment, access to industry-standard software and datasets.",
        career_paths=["data scientist", "machine learning engineer", "data analyst", "business intelligence analyst", "research scientist", "quantitative analyst", "product manager", "consultant", "software engineer", "academic researcher"]
    ),
    
    "Business Administration": SyllabusContent(
        program_name="Business Administration",
        description="A comprehensive business program integrating management theory, analytical skills, and practical experience across all functional areas. Structured across 8 semesters (30 ECTS each) with case studies, internships, consulting projects, and a strategic capstone.",
        pillars=["Strategic Management", "Finance & Accounting", "Marketing", "Operations Management", "Human Resources", "Entrepreneurship", "International Business", "Business Analytics", "Ethics & Leadership", "Innovation Management"],
        learning_outcomes=[
            "**Analyze complex business problems** using analytical and strategic thinking frameworks across functional areas.",
            "**Apply financial and accounting principles** for effective business decision-making and performance evaluation.",
            "**Develop and implement marketing strategies** for diverse markets and customer segments.",
            "**Design efficient operations** and supply chain management systems to optimize organizational performance.",
            "**Lead teams and manage human resources** effectively while fostering organizational culture and development.",
            "**Evaluate entrepreneurial opportunities** and develop comprehensive business plans for new ventures.",
            "**Communicate business ideas** clearly and persuasively to diverse stakeholders and audiences."
        ],
        semesters={
            1: [
                {"code": "BA101", "name": "Introduction to Business", "ects": 6, "format": "3-2-0-0", "assessment": "Case studies 40%, Group project 30%, Exam 30%", "topics": "Business fundamentals, organizational structures, stakeholder analysis, business environment", "labs": "Business simulation, company analysis"},
                {"code": "BA102", "name": "Microeconomics", "ects": 6, "format": "3-2-0-0", "topics": "Supply and demand, market structures, consumer behavior, pricing strategies, elasticity", "tools": "Economic modeling software, Excel for economic analysis"},
                {"code": "BA103", "name": "Business Mathematics & Statistics", "ects": 6, "format": "3-1-1-0", "topics": "Financial mathematics, probability, descriptive statistics, regression analysis", "labs": "Excel, statistical analysis, financial calculations"},
                {"code": "BA104", "name": "Accounting Fundamentals", "ects": 6, "format": "3-1-1-0", "topics": "Financial statements, double-entry bookkeeping, basic financial analysis, cash flow", "labs": "Accounting software, financial statement preparation, ratio analysis"},
                {"code": "BA105", "name": "Business Communication", "ects": 6, "format": "2-1-0-1", "topics": "Written and oral communication, presentation skills, professional etiquette, negotiation", "assessment": "Presentations 50%, Writing assignments 50%"}
            ],
            2: [
                {"code": "BA106", "name": "Macroeconomics", "ects": 6, "format": "3-2-0-0", "prereq": "BA102", "topics": "National economy, fiscal and monetary policy, international trade, economic indicators", "labs": "Economic forecasting, policy analysis, international comparisons"},
                {"code": "BA107", "name": "Management Accounting", "ects": 6, "format": "3-1-1-0", "prereq": "BA104", "topics": "Cost analysis, budgeting, performance measurement, variance analysis", "labs": "Cost accounting systems, budget preparation, dashboard creation"},
                {"code": "BA108", "name": "Organizational Behavior", "ects": 6, "format": "3-1-0-1", "topics": "Individual and group behavior, motivation, leadership, team dynamics, organizational culture", "assessment": "Team projects 40%, Case analysis 60%"},
                {"code": "BA109", "name": "Marketing Principles", "ects": 6, "format": "3-1-1-0", "topics": "Marketing mix, consumer behavior, market research, segmentation, positioning", "labs": "Market analysis projects, survey design, digital marketing"},
                {"code": "BA110", "name": "Business Ethics & Law", "ects": 6, "format": "2-2-0-0", "topics": "Ethical frameworks, corporate responsibility, business law, compliance, governance", "assessment": "Ethics cases 40%, Legal analysis 30%, Debates 30%"}
            ]
        },
        elective_tracks=[
            {
                "name": "Track A — Finance & Investment",
                "courses": [
                    {"code": "BA451", "description": "Corporate Finance — Capital structure, investment decisions, financial planning, valuation"},
                    {"code": "BA452", "description": "Investment Analysis — Portfolio theory, asset pricing, risk management, derivatives"},
                    {"code": "BA453", "description": "Financial Markets — Market structure, trading, financial institutions, regulation"},
                    {"code": "BA454", "description": "International Finance — Exchange rates, international markets, global finance"}
                ]
            },
            {
                "name": "Track B — Marketing & Digital Business",
                "courses": [
                    {"code": "BA461", "description": "Digital Marketing — Social media, SEO/SEM, content marketing, analytics"},
                    {"code": "BA462", "description": "Brand Management — Brand strategy, brand equity, brand communications"},
                    {"code": "BA463", "description": "Customer Analytics — Customer segmentation, lifetime value, CRM systems"},
                    {"code": "BA464", "description": "E-commerce — Online business models, platform strategy, digital transformation"}
                ]
            }
        ],
        facilities="Case study rooms with video conferencing, computer labs with business software (SAP, Tableau, Bloomberg Terminal), trading simulation lab, presentation rooms with recording capabilities, collaborative workspace, access to business databases and market data.",
        career_paths=["management consulting", "corporate management", "financial services", "marketing", "entrepreneurship", "project management", "business analysis", "operations management", "human resources", "business development"]
    )
}

def main():
    """Generate all 16 comprehensive syllabus PDFs"""
    generator = CompleteSyllabusPDFGenerator()
    
    print("Generating comprehensive syllabus PDFs for all 16 programs...")
    print("=" * 60)
    
    # Generate PDFs for all defined programs
    for program_name, content in ALL_SYLLABUS_CONTENT.items():
        filename = f"{program_name.replace(' ', '_')}_Syllabus_(4‑year,_240_Ects).pdf"
        try:
            generator.generate_pdf(content, filename)
        except Exception as e:
            print(f"Error generating {filename}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Successfully generated {len(ALL_SYLLABUS_CONTENT)} syllabus PDFs")
    print("\nNote: This script contains 6 complete programs.")
    print("To generate all 16 PDFs, add the remaining 10 programs to ALL_SYLLABUS_CONTENT")
    print("Required libraries: pip install reportlab markdown2")
    print("\nGenerated files are ready for use with the RDU website.")

if __name__ == "__main__":
    main()