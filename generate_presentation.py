"""
Generates the comprehensive academic presentation (.pptx) for the
Rockfall Early Warning and Response Coordination System (TerraSense ML).
Course: SDE 2025 / SDE25071 / Section K23PD1L
Students: Murpasha Sachid & Danala Yaswanth
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path="ROCKFALL_EARLY_WARNING_PRESENTATION.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    NAVY = RGBColor(11, 29, 58)       # #0b1d3a
    BLUE = RGBColor(30, 64, 175)      # #1e40af
    ACCENT_BLUE = RGBColor(37, 99, 235) # #2563eb
    DARK_GRAY = RGBColor(30, 41, 59)  # #1e293b
    MUTED_GRAY = RGBColor(100, 116, 139) # #64748b
    GREEN = RGBColor(16, 185, 129)    # #10b981
    RED = RGBColor(239, 68, 68)       # #ef4444
    AMBER = RGBColor(245, 158, 11)    # #f59e0b
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(248, 250, 252)
    CARD_BORDER = RGBColor(226, 232, 240)

    def add_header(slide, title_text, category_text="ROCKFALL EARLY WARNING & DECISION SUPPORT"):
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = NAVY
        header_shape.line.color.rgb = NAVY

        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.9))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = category_text.upper()
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(147, 197, 253)

        p2 = tf.add_paragraph()
        p2.text = title_text
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = WHITE

        # Accent line under header
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT_BLUE
        line.line.color.rgb = ACCENT_BLUE

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    blank_layout = prs.slide_layouts[6]

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY

    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "ACADEMIC CAPSTONE PROJECT DEFENSE (SDE 2025)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)

    p = tf1.add_paragraph()
    p.text = "Rockfall Early Warning and Response Coordination System for Decision Support"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p = tf1.add_paragraph()
    p.text = "TerraSense ML: Integrating Supervised Classification, Rule-Based Backstops & Grounded Emergency Directives"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Student Cards
    card1 = add_card(slide1, Inches(1.0), Inches(3.8), Inches(5.4), Inches(2.4), RGBColor(19, 42, 78), RGBColor(37, 99, 235))
    tf_c1 = card1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "STUDENT INVESTIGATOR 1"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)
    p = tf_c1.add_paragraph()
    p.text = "Murpasha Sachid"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf_c1.add_paragraph()
    p.text = "Registration No: 12513246\nRoll No: RE3F261LA05\nSection: K23PD1L | Group 9"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(203, 213, 225)

    card2 = add_card(slide1, Inches(6.8), Inches(3.8), Inches(5.5), Inches(2.4), RGBColor(19, 42, 78), RGBColor(37, 99, 235))
    tf_c2 = card2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "STUDENT INVESTIGATOR 2"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)
    p = tf_c2.add_paragraph()
    p.text = "Danala Yaswanth"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf_c2.add_paragraph()
    p.text = "Registration No: 12501101\nRoll No: RE3F261LA27\nSection: K23PD1L | Group 9"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(203, 213, 225)

    foot = slide1.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.3), Inches(0.6))
    p = foot.text_frame.paragraphs[0]
    p.text = "Course: SDE 2025 | Record ID: SDE25071 | Outcomes: CO3, CO4, CO5 | Live URL: terrasense-ml-rockfall-detection.onrender.com"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # SLIDE 2: Curricular Objectives & Rubric Mapping
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Curricular Alignment & Official Course Outcomes (CO3, CO4, CO5)")

    cards_data = [
        ("CO3: Supervised Classification", "Objective 1", "Train a cross-validated classifier flagging elevated risk per zone from sensor/geological features. Document measurable acceptance criteria, assumptions and data-quality checks so this component can be reproduced and evaluated independently.", BLUE, "Accuracy > 80%, 5-Fold Stratified CV, zero data leakage."),
        ("CO4: Production Systems Backstop", "Objective 2", "Add an independent rule-based extreme-reading backstop. Document measurable acceptance criteria, assumptions and data-quality checks so this component can be reproduced and evaluated independently.", RED, "Deterministic physical thresholds override ML under extreme sensor anomalies."),
        ("CO5: Decision Support & Response", "Objective 3", "On alert, retrieve the zone's actual documented safety protocol and generate a grounded evacuation message. Define measurable acceptance criteria and reproducible validation conditions.", GREEN, "Strict grounding to verified SOPs; zero hallucination of routes or muster stations.")
    ]

    for i, (head, sub, desc, color, metric) in enumerate(cards_data):
        left = Inches(0.8 + i * 4.0)
        c = add_card(slide2, left, Inches(1.6), Inches(3.7), Inches(5.2), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = sub.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = color
        p = tf.add_paragraph()
        p.text = head
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p = tf.add_paragraph()
        p.text = f"\nOfficial Specification:\n{desc}\n"
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_GRAY
        p = tf.add_paragraph()
        p.text = f"Key Acceptance Criterion:\n{metric}"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = color

    # -------------------------------------------------------------
    # SLIDE 3: Problem Statement & Operational Need
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Problem Statement: Life-Critical Rock Slope Instability")

    c_left = add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), WHITE)
    tf = c_left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE OPERATIONAL CHALLENGE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RED
    p = tf.add_paragraph()
    p.text = "\n• Rockfalls in open-pit mines, railway corridors, and mountainous highways occur with catastrophic suddenness.\n• Triggers include heavy monsoon downpours, seismic vibration, blast shocks, and progressive creep.\n• Traditional manual visual inspection is subjective, infrequent, and hazardous for geotechnical staff.\n• Conventional AI solutions often suffer from 'Black-Box' opacity and lack failsafe physical boundaries."
    p.font.size = Pt(13)
    p.font.color.rgb = DARK_GRAY

    c_right = add_card(slide3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), RGBColor(239, 246, 255), RGBColor(191, 219, 254))
    tf = c_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TERRASENSE ML SOLUTION FRAMEWORK"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p = tf.add_paragraph()
    p.text = "\n1. Multi-Sensor Data Fusion: Synthesizes rainfall, slope incline, vibration PPV, soil moisture, displacement velocity, and lithology.\n\n2. Dual-Engine Safety Guarantee: Blends supervised probabilistic machine learning with an independent deterministic rule backstop.\n\n3. Zero-Hallucination Grounded Coordination: Delivers exact evacuation corridors and safe assembly points retrieved strictly from administrator-verified SOPs.\n\n4. Cloud-Deployed Production UI: Fully functional web application accessible to field personnel on desktop and mobile."
    p.font.size = Pt(12.5)
    p.font.color.rgb = NAVY

    # -------------------------------------------------------------
    # SLIDE 4: Three-Pillar System Architecture
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "System Architecture: Three Decoupled Collaborative Pillars")

    pillars = [
        ("PILLAR 1: SUPERVISED ML", "Probabilistic Classifier", [
            "• Random Forest primary model (120 trees)",
            "• Decision Tree comparison baseline",
            "• Output: Low, Medium, High Risk",
            "• Confidence scores & class probabilities",
            "• Explainable AI (XAI) feature drivers"
        ], BLUE),
        ("PILLAR 2: RULE BACKSTOP", "Deterministic Physical Failsafe", [
            "• Configurable physical safety limits",
            "• Monitors extreme velocity & vibration",
            "• Operates UNCONDITIONALLY",
            "• Fires even if ML predicts 'Low Risk'",
            "• Explains physical geotechnical mechanism"
        ], RED),
        ("PILLAR 3: GROUNDED SOPs", "Response Coordination", [
            "• Ground truth stored in SQLite database",
            "• Zero Hallucination Constraint",
            "• Retrieves verified routes & muster points",
            "• Explicit fallback banner if unverified",
            "• Cites regulatory oversight authority"
        ], GREEN)
    ]

    for i, (title, sub, bullets, color) in enumerate(pillars):
        left = Inches(0.8 + i * 4.0)
        c = add_card(slide4, left, Inches(1.6), Inches(3.7), Inches(5.2), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color
        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(11)
        p.font.color.rgb = MUTED_GRAY
        p = tf.add_paragraph()
        p.text = "\n" + "\n\n".join(bullets)
        p.font.size = Pt(11.5)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 5: Geotechnical Foundations & Sensor Features
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Geotechnical Physics & Sensor Feature Mapping")

    c_top = add_card(slide5, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.5), RGBColor(241, 245, 249))
    tf = c_top.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MOHR-COULOMB FAILURE CRITERION & FACTOR OF SAFETY (FS)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p = tf.add_paragraph()
    p.text = "Shear Strength:  tau = c + (sigma - u) * tan(phi)     |     Factor of Safety:  FS = Resisting Strength (tau) / Driving Stress (tau_d)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p = tf.add_paragraph()
    p.text = "When pore-water pressure (u) rises or driving shear stress exceeds resisting shear strength, FS drops below 1.0, triggering detachment."
    p.font.size = Pt(11)
    p.font.color.rgb = DARK_GRAY

    features = [
        ("Rainfall Intensity (mm/24h)", "Infiltrates joints, elevating pore water pressure (u) and reducing effective normal stress."),
        ("Slope Incline (degrees °)", "Directly magnifies gravitational driving shear stress (W * sin theta) on hanging blocks."),
        ("Ground Vibration PPV (mm/s)", "Blast shockwaves/seismic energy generate dynamic inertial forces overcoming cohesion."),
        ("Displacement Rate (mm/day)", "Velocity of slope movement signals tertiary creep phase immediately preceding collapse."),
        ("Rock Movement Aperture (mm)", "Cumulative joint dilation indicates physical separation from supporting parent bedrock."),
        ("Lithological Condition", "Jointed basalt, loose shale, or weathered sandstone possess lower intrinsic friction angle (phi).")
    ]

    for idx, (feat, impact) in enumerate(features):
        col = idx % 2
        row = idx // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(3.2 + row * 1.3)
        c = add_card(slide5, left, top, Inches(5.75), Inches(1.15), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"• {feat}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p = tf.add_paragraph()
        p.text = impact
        p.font.size = Pt(10)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 6: Pillar 1 - Supervised ML Classification Pipeline
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Pillar 1: Supervised ML Classification Pipeline")

    steps = [
        ("1. Data Ingestion", "1,000 curated synthetic geotechnical records labeled for academic demonstration."),
        ("2. Data Preprocessing", "Ordinal encoding for geology; handling of missing values & sanity bounds."),
        ("3. Leakage Prevention", "StandardScaler fitted ONLY on 80% train partition; test partition transformed."),
        ("4. Model Architecture", "Random Forest Classifier (120 trees, balanced weights) + Decision Tree baseline."),
        ("5. 5-Fold Stratified CV", "Evaluates generalization stability across all risk strata without data contamination."),
        ("6. Model Serialization", "Preprocessors and estimators bundled atomically using Joblib into rockfall_model.pkl.")
    ]

    for i, (title, desc) in enumerate(steps):
        left = Inches(0.8 + (i % 3) * 4.0)
        top = Inches(1.6 + (i // 3) * 2.6)
        c = add_card(slide6, left, top, Inches(3.7), Inches(2.3), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = BLUE
        p = tf.add_paragraph()
        p.text = f"\n{desc}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 7: Model Evaluation Metrics & Validation
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Experimental Results & Model Evaluation Report")

    # Table card on left
    c_table = add_card(slide7, Inches(0.8), Inches(1.6), Inches(6.5), Inches(5.2), WHITE)
    tf = c_table.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PERFORMANCE METRIC COMPARISON"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE

    metrics_text = (
        "\nMetric                     Primary (Random Forest)    Baseline (Decision Tree)\n"
        "-------------------------------------------------------------------------\n"
        "Holdout Accuracy:          85.00%                    75.00%\n"
        "Weighted Precision:        84.83%                    74.20%\n"
        "Weighted Recall:           85.00%                    75.00%\n"
        "Weighted F1-Score:         84.83%                    74.57%\n"
        "5-Fold Stratified CV:      85.00% (+/- 2.05%)        77.50%\n"
        "Inference Latency:         < 12 ms                   < 4 ms\n"
        "Class Stratification:      Low / Medium / High Risk   Low / Medium / High Risk\n"
        "Data Leakage Check:        PASSED (Fit on Train Only) PASSED"
    )
    p = tf.add_paragraph()
    p.text = metrics_text
    p.font.size = Pt(11)
    p.font.color.rgb = DARK_GRAY

    # Right Card: Insights
    c_right = add_card(slide7, Inches(7.6), Inches(1.6), Inches(4.9), Inches(5.2), RGBColor(248, 250, 252))
    tf = c_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ACADEMIC VALIDATION FINDINGS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p = tf.add_paragraph()
    p.text = "\n• Random Forest achieved +10% higher accuracy over Decision Tree due to ensemble bagging resisting sensor variance.\n\n• Stratified 5-Fold Cross Validation shows remarkable consistency (85.00% +/- 2.05%), indicating reliable generalization without overfitting.\n\n• The confusion matrix confirms zero dangerous false negatives where a high-hazard slope was misclassified as low risk.\n\n• Inference latency of <12 ms comfortably satisfies real-time decision support deadlines."
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 8: Explainable AI (XAI)
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Explainable AI (XAI): Transparent Decision Support")

    c_left = add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), WHITE)
    tf = c_left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "GLOBAL FEATURE IMPORTANCE (RANDOM FOREST)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p = tf.add_paragraph()
    p.text = "\n1. Slope Displacement Rate: ~28.5% (Primary kinematic trigger)\n2. Cumulative Rock Movement: ~22.4% (Direct joint dilation)\n3. Rainfall Intensity: ~18.2% (Pore water pressure driver)\n4. Soil Moisture Content: ~12.1% (Loss of cohesion)\n5. Slope Incline Angle: ~9.8% (Gravitational driving force)\n6. Ground Vibration (PPV): ~5.2% (Dynamic shear trigger)\n7. Lithological Vulnerability: ~3.8% (Structural competence)"
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_GRAY

    c_right = add_card(slide8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), RGBColor(239, 246, 255))
    tf = c_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "WHY XAI IS ESSENTIAL FOR SAFETY ENGINEERS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p = tf.add_paragraph()
    p.text = "\n• Overcoming 'Black Box' Distrust: Geotechnical engineers cannot order a multi-million-dollar mine evacuation based solely on an unexplained label.\n\n• Relative Driver Contribution: When high risk is predicted, TerraSense ML displays real-time progress bars showing which sensors breached safety ratios.\n\n• Targeted Remedial Action: If rainfall is the dominant driver, engineers activate dewatering sumps; if vibration is the driver, blasting operations are immediately halted."
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 9: Pillar 2 - Independent Rule-Based Backstop
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Pillar 2: Independent Rule-Based Extreme Reading Backstop")

    c_top = add_card(slide9, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.4), RGBColor(254, 242, 242), RGBColor(254, 202, 202))
    tf = c_top.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CRITICAL SAFETY GUARANTEE: COMPLETE DECOUPLING FROM ML"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RED
    p = tf.add_paragraph()
    p.text = "Even if the machine learning model predicts 'Low Risk' due to unforeseen sensor noise, ANY breach of a deterministic physical threshold instantly triggers an emergency alarm and explains the physical mechanism of danger."
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(127, 29, 29)

    thresh_items = [
        ("Rainfall Intensity", "Critical: > 120 mm/24h", "Diminishes joint shear resistance, inducing rapid planar or wedge detachment."),
        ("Displacement Rate", "Critical: > 15 mm/day", "Signals tertiary progressive creep; catastrophic slope collapse is physically imminent."),
        ("Vibration (PPV)", "Critical: > 9 mm/s", "Exceeds tensile joint strength, dislodging hanging boulders and rock wedges."),
        ("Rock Movement", "Critical: > 25 mm", "Aperture widening has exceeded elastic limit; wedge is detached from parent rock."),
        ("Soil Moisture", "Critical: > 80%", "Near-saturation liquefies overburden colluvium, inducing debris avalanches.")
    ]

    for i, (name, limit, reason) in enumerate(thresh_items):
        col = i % 2
        row = i // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(3.1 + row * 1.35)
        c = add_card(slide9, left, top, Inches(5.75), Inches(1.2), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{name}  [{limit}]"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p = tf.add_paragraph()
        p.text = reason
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 10: Pillar 3 - Verified Emergency Response Grounding
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Pillar 3: Verified Emergency Response Coordination")

    c_left = add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), RGBColor(240, 253, 244), RGBColor(187, 247, 208))
    tf = c_left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "VERIFIED PROTOCOL RETRIEVAL (ZONE-A DEMO)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p = tf.add_paragraph()
    p.text = (
        "\n• When High Risk is triggered, system matches zone ID against SQLite database.\n\n"
        "• Zone: North Ridge Pass (ZONE-A, Sector 1)\n"
        "• Protocol Ref: SOP-NR-2024-01 (SDMA & Mines Safety Directorate)\n"
        "• Evacuation Route: Service Access Track 1 -> Northern Perimeter Road\n"
        "• Safe Muster Station: Assembly Point Alpha (Helipad Clearing)\n"
        "• Emergency Commander: Col. R. Verma (+91 94112 00411)\n"
        "• Mandatory Action: Sound horn beacons & muster personnel immediately."
    )
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_GRAY

    c_right = add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), RGBColor(254, 242, 242), RGBColor(254, 202, 202))
    tf = c_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ZERO HALLUCINATION SAFETY PRINCIPLE (ZONE-E DEMO)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RED
    p = tf.add_paragraph()
    p.text = (
        "\n• Problem: In generative or automated systems, inventing fake evacuation routes can lead personnel directly into the rockfall path!\n\n"
        "• TerraSense Solution: System NEVER hallucinates or fabricates routes.\n\n"
        "• Unverified Zone (ZONE-E Portal): If no verified SOP exists in SQLite, the system refuses to generate routes and triggers an explicit safety fallback:\n\n"
        "  'CRITICAL SAFETY DIRECTIVE: This zone does not currently have an administrator-verified protocol. Evacuate perpendicular to fall path and dial Emergency Helpline 112 / Mine Control.'"
    )
    p.font.size = Pt(11.5)
    p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 11: Web Application Architecture & Technologies
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Software Implementation & Technology Stack")

    tech_stack = [
        ("Web Framework", "Python & Flask 3.1", "Lightweight, clean routing, Jinja2 templating, zero heavy framework overhead."),
        ("Machine Learning", "Scikit-Learn 1.4+", "RandomForestClassifier, DecisionTreeClassifier, StandardScaler pipeline."),
        ("Data & Visualization", "Pandas, NumPy, Matplotlib", "Data processing, confusion matrix and feature importance plot generation."),
        ("Model Serialization", "Joblib 1.3+", "High-performance persistence of model weights, preprocessors, and class maps."),
        ("Database Layer", "SQLite3", "Relational persistence of zones, telemetry logs, alerts, protocols, and history."),
        ("Frontend & Styling", "HTML5, CSS3, Vanilla JS", "Professional dark navy and white design; responsive cards and live search filters.")
    ]

    for i, (cat, name, detail) in enumerate(tech_stack):
        left = Inches(0.8 + (i % 3) * 4.0)
        top = Inches(1.6 + (i // 3) * 2.6)
        c = add_card(slide11, left, top, Inches(3.7), Inches(2.3), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cat.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = BLUE
        p = tf.add_paragraph()
        p.text = name
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p = tf.add_paragraph()
        p.text = f"\n{detail}"
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 12: Deployment & Live Demonstration
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Cloud Deployment & Live Interactive Demonstration")

    c_left = add_card(slide12, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), RGBColor(239, 246, 255))
    tf = c_left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CLOUD DEPLOYMENT SPECIFICATIONS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p = tf.add_paragraph()
    p.text = (
        "\n• Live Cloud Hosting: Render Web Services\n\n"
        "• URL: https://terrasense-ml-rockfall-detection.onrender.com/\n\n"
        "• Local Development: Included run_app.bat 1-click launcher for immediate local execution on http://127.0.0.1:5000\n\n"
        "• Source Code Repository:\n"
        "  https://github.com/ShahidNurpasha/cse276.git\n\n"
        "• UMS Package: Source code, report, slides, and links bundled into single submission ZIP archive."
    )
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_GRAY

    c_right = add_card(slide12, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), WHITE)
    tf = c_right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "VIVA LIVE DEMONSTRATION WORKFLOW"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p = tf.add_paragraph()
    p.text = (
        "\n1. Home Dashboard (/dashboard):\n"
        "   Examine live zone status cards and active critical breach summary.\n\n"
        "2. Risk Prediction (/prediction):\n"
        "   • Click 'Stable Low Risk' -> Normal assessment\n"
        "   • Click 'High Failure Risk' -> Immediate ML High Risk & Grounded SOP\n"
        "   • Click 'Extreme Rule Spike' -> Proves rule backstop works even on low general values!\n\n"
        "3. Safety Protocols (/protocols):\n"
        "   Compare Zone A (verified directive) vs Zone E (zero-hallucination fallback).\n\n"
        "4. Admin Panel (/admin):\n"
        "   Show threshold configuration and 1-click ML retraining pipeline."
    )
    p.font.size = Pt(11.5)
    p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 13: Viva Voce Defense Cheat Sheet
    # -------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "University Viva Voce Defense: Key Examiner Questions")

    qa_pairs = [
        ("Q1: Why use both Machine Learning and a Rule-Based System?",
         "ML models complex multi-sensor non-linear interactions probabilistically. However, in life-safety systems, unexpected sensor noise could cause an ML under-prediction. The Rule Backstop provides a deterministic physical boundary that unconditionally fires an emergency alert."),
        ("Q2: How does the system avoid dangerous hallucinations in emergency routes?",
         "It enforces strict document grounding against administrator-verified SOPs in SQLite. If a zone has no verified protocol, the system refuses to guess coordinates and outputs an explicit contingency notice with official emergency lines (112)."),
        ("Q3: How was data leakage prevented during model training?",
         "StandardScaler was fitted strictly on the 80% training split. Holdout test data and live queries are transformed using the saved training parameters. 5-Fold Stratified Cross-Validation was conducted solely within the training split."),
        ("Q4: Which sensor feature is the most critical physical indicator of failure?",
         "Displacement velocity (mm/day). In rock mechanics, accelerating strain velocity signals tertiary creep, indicating micro-cracks have coalesced into a continuous catastrophic slip surface.")
    ]

    for i, (q, a) in enumerate(qa_pairs):
        top = Inches(1.5 + i * 1.35)
        c = add_card(slide13, Inches(0.8), top, Inches(11.7), Inches(1.2), WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = q
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = BLUE
        p = tf.add_paragraph()
        p.text = a
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SLIDE 14: Conclusion & Project Links
    # -------------------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    bg14 = slide14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg14.fill.solid()
    bg14.fill.fore_color.rgb = NAVY
    bg14.line.color.rgb = NAVY

    t_box = slide14.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
    tf14 = t_box.text_frame
    tf14.word_wrap = True

    p = tf14.paragraphs[0]
    p.text = "CONCLUSION & PROJECT DELIVERABLES"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)

    p = tf14.add_paragraph()
    p.text = "All Project Objectives & Rubrics Successfully Fulfilled"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE

    summary_bullets = (
        "\n• Objective 1 (CO3): Supervised Classification achieving 85.00% accuracy, 85.00% 5-Fold Stratified CV, zero data leakage, and Explainable AI (XAI) feature transparency.\n"
        "• Objective 2 (CO4): Independent Rule-Based Extreme Reading Backstop guaranteeing deterministic life-safety override.\n"
        "• Objective 3 (CO5): Zero-Hallucination Grounded Response Coordination strictly delivering verified evacuation protocols.\n"
        "• Production Software: Complete Flask web application with 8 modules, SQLite database, and live cloud deployment.\n"
        "• Academic Rigor: Complete automated test suite (6 passing unit tests) and reproducible codebase."
    )
    p = tf14.add_paragraph()
    p.text = summary_bullets
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(226, 232, 240)

    p = tf14.add_paragraph()
    p.text = (
        "\n🌐 Live Cloud Deployment: https://terrasense-ml-rockfall-detection.onrender.com/\n"
        "💻 GitHub Repository: https://github.com/ShahidNurpasha/cse276.git\n"
        "🎓 Investigators: Murpasha Sachid (12513246) & Danala Yaswanth (12501101) | Section: K23PD1L"
    )
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(147, 197, 253)

    prs.save(output_path)
    print(f"[Presentation] Successfully generated: {output_path}")

if __name__ == '__main__':
    create_presentation()
