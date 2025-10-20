"""
Report generation utilities for PDF and CSV export
"""
import csv
import io
import json
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from flask import make_response


class ReportGenerator:
    """Utility class for generating reports in various formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )
    
    def generate_pdf_report(self, report_data: Dict[str, Any], filename: str = None) -> bytes:
        """Generate PDF report from report data"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.pdf"
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build story (content)
        story = []
        
        # Add title
        report_type = report_data.get('report_type', 'Analytics Report')
        title = self._format_report_title(report_type)
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # Add generation info
        generated_at = report_data.get('generated_at', datetime.now().isoformat())
        info_text = f"Generated on: {self._format_datetime(generated_at)}"
        story.append(Paragraph(info_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add content based on report type
        if report_type == 'placement_summary':
            self._add_placement_summary_content(story, report_data)
        elif report_type == 'skill_gap_analysis':
            self._add_skill_gap_content(story, report_data)
        elif report_type == 'industry_demand':
            self._add_industry_demand_content(story, report_data)
        elif report_type == 'branch_performance':
            self._add_branch_performance_content(story, report_data)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_csv_report(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """Generate CSV report from report data with Excel compatibility"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.csv"
        
        # Create CSV buffer with UTF-8 BOM for Excel compatibility
        output = io.StringIO()
        output.write('\ufeff')  # UTF-8 BOM for Excel
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        
        # Add header information
        report_type = report_data.get('report_type', 'Analytics Report')
        writer.writerow([f"Report Type: {self._format_report_title(report_type)}"])
        writer.writerow([f"Generated: {self._format_datetime(report_data.get('generated_at'))}"])
        
        # Add date range if available
        date_range = report_data.get('date_range')
        if date_range:
            writer.writerow([f"Date Range: {date_range.get('start_date', 'N/A')} to {date_range.get('end_date', 'N/A')}"])
        
        # Add filters if available
        filters = report_data.get('filters')
        if filters:
            filter_info = []
            for key, value in filters.items():
                if value:
                    filter_info.append(f"{key.title()}: {value}")
            if filter_info:
                writer.writerow([f"Filters: {', '.join(filter_info)}"])
        
        writer.writerow([])  # Empty row
        
        # Add content based on report type
        if report_type == 'placement_summary':
            self._add_placement_summary_csv(writer, report_data)
        elif report_type == 'skill_gap_analysis':
            self._add_skill_gap_csv(writer, report_data)
        elif report_type == 'industry_demand':
            self._add_industry_demand_csv(writer, report_data)
        elif report_type == 'branch_performance':
            self._add_branch_performance_csv(writer, report_data)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def _format_report_title(self, report_type: str) -> str:
        """Format report type into readable title"""
        title_map = {
            'placement_summary': 'Placement Summary Report',
            'skill_gap_analysis': 'Skill Gap Analysis Report',
            'industry_demand': 'Industry Demand Report',
            'branch_performance': 'Branch Performance Report'
        }
        return title_map.get(report_type, report_type.replace('_', ' ').title())
    
    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string for display"""
        if not datetime_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return datetime_str
    
    def _add_placement_summary_content(self, story: List, report_data: Dict):
        """Add placement summary content to PDF"""
        summary = report_data.get('summary', {})
        
        # Summary section
        story.append(Paragraph("Executive Summary", self.heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Placements', str(summary.get('total_placements', 0))],
            ['Branches Covered', str(summary.get('branches_covered', 0))],
            ['Industries Covered', str(summary.get('industries_covered', 0))],
            ['Average Salary', f"₹{summary.get('avg_salary', 0):,.2f}"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Branch performance
        branch_performance = report_data.get('branch_performance', [])
        if branch_performance:
            story.append(Paragraph("Branch Performance", self.heading_style))
            
            branch_data = [['Branch', 'Placements', 'Avg Salary', 'Avg Feedback']]
            for branch in branch_performance[:10]:  # Top 10 branches
                branch_data.append([
                    branch.get('student_branch', 'N/A'),
                    str(branch.get('placement_count', 0)),
                    f"₹{branch.get('avg_salary', 0):,.2f}",
                    f"{branch.get('avg_feedback', 0):.1f}/10"
                ])
            
            branch_table = Table(branch_data)
            branch_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(branch_table)
    
    def _add_skill_gap_content(self, story: List, report_data: Dict):
        """Add skill gap analysis content to PDF"""
        story.append(Paragraph("Skill Gap Analysis by Branch", self.heading_style))
        
        branch_analysis = report_data.get('branch_analysis', [])
        
        for branch_data in branch_analysis:
            branch_name = branch_data.get('branch', 'Unknown')
            student_count = branch_data.get('student_count', 0)
            top_gaps = branch_data.get('top_gaps', [])
            
            # Branch header
            story.append(Paragraph(f"{branch_name} ({student_count} students)", 
                                 self.styles['Heading3']))
            
            if top_gaps:
                gap_data = [['Skill', 'Demand Score', 'Avg Salary']]
                for gap in top_gaps[:5]:  # Top 5 gaps per branch
                    salary = gap.get('avg_salary')
                    salary_str = f"₹{salary:,.0f}" if salary else "N/A"
                    gap_data.append([
                        gap.get('skill_name', 'N/A'),
                        f"{gap.get('demand_score', 0):.1f}",
                        salary_str
                    ])
                
                gap_table = Table(gap_data)
                gap_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(gap_table)
            else:
                story.append(Paragraph("No skill gaps identified.", self.styles['Normal']))
            
            story.append(Spacer(1, 15))
    
    def _add_industry_demand_content(self, story: List, report_data: Dict):
        """Add industry demand content to PDF"""
        story.append(Paragraph("Top Skills in Demand", self.heading_style))
        
        top_skills = report_data.get('top_skills', [])
        
        if top_skills:
            skill_data = [['Skill', 'Industry', 'Demand Score', 'Job Count', 'Avg Salary']]
            for skill in top_skills[:15]:  # Top 15 skills
                salary = skill.get('avg_salary')
                salary_str = f"₹{salary:,.0f}" if salary else "N/A"
                skill_data.append([
                    skill.get('skill_name', 'N/A'),
                    skill.get('industry', 'N/A'),
                    f"{skill.get('demand_score', 0):.1f}",
                    str(skill.get('job_count', 0)),
                    salary_str
                ])
            
            skill_table = Table(skill_data)
            skill_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(skill_table)
        
        # Trending skills section
        trending_skills = report_data.get('trending_skills', [])
        if trending_skills:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Trending Skills (High Growth)", self.heading_style))
            
            trending_data = [['Skill', 'Growth Rate', 'Current Demand']]
            for skill in trending_skills[:10]:
                trending_data.append([
                    skill.get('skill_name', 'N/A'),
                    f"{skill.get('growth_rate', 0):.1f}%",
                    f"{skill.get('demand_score', 0):.1f}"
                ])
            
            trending_table = Table(trending_data)
            trending_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(trending_table)
    
    def _add_branch_performance_content(self, story: List, report_data: Dict):
        """Add branch performance content to PDF"""
        story.append(Paragraph("Branch Performance Analysis", self.heading_style))
        
        branch_performance = report_data.get('branch_performance', [])
        
        if branch_performance:
            # Add chart if we have data
            if len(branch_performance) > 1:
                chart = self._create_branch_performance_chart(branch_performance)
                if chart:
                    story.append(chart)
                    story.append(Spacer(1, 20))
            
            perf_data = [['Branch', 'Placements', 'Avg Salary', 'Min Salary', 'Max Salary', 'Feedback']]
            for branch in branch_performance:
                perf_data.append([
                    branch.get('student_branch', 'N/A'),
                    str(branch.get('placement_count', 0)),
                    f"₹{branch.get('avg_salary', 0):,.0f}",
                    f"₹{branch.get('min_salary', 0):,.0f}",
                    f"₹{branch.get('max_salary', 0):,.0f}",
                    f"{branch.get('avg_feedback', 0):.1f}/10"
                ])
            
            perf_table = Table(perf_data)
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1abc9c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(perf_table)
    
    def _create_branch_performance_chart(self, branch_performance):
        """Create a bar chart for branch performance"""
        try:
            drawing = Drawing(400, 200)
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 50
            chart.height = 125
            chart.width = 300
            
            # Prepare data (top 8 branches to avoid overcrowding)
            top_branches = branch_performance[:8]
            chart.data = [[branch.get('placement_count', 0) for branch in top_branches]]
            chart.categoryAxis.categoryNames = [branch.get('student_branch', 'N/A')[:10] for branch in top_branches]
            
            # Style the chart
            chart.bars[0].fillColor = colors.HexColor('#3498db')
            chart.valueAxis.valueMin = 0
            chart.categoryAxis.labels.angle = 45
            chart.categoryAxis.labels.fontSize = 8
            
            drawing.add(chart)
            return drawing
        except Exception:
            # Return None if chart creation fails
            return None
    
    def _create_pie_chart(self, data_dict, title=""):
        """Create a pie chart from dictionary data"""
        try:
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            
            # Prepare data (top 6 items to avoid overcrowding)
            items = list(data_dict.items())[:6]
            pie.data = [item[1] for item in items]
            pie.labels = [f"{item[0][:15]}: {item[1]}" for item in items]
            
            # Style the pie chart
            colors_list = [colors.HexColor('#3498db'), colors.HexColor('#e74c3c'), 
                          colors.HexColor('#2ecc71'), colors.HexColor('#f39c12'),
                          colors.HexColor('#9b59b6'), colors.HexColor('#1abc9c')]
            
            for i, color in enumerate(colors_list[:len(items)]):
                pie.slices[i].fillColor = color
            
            drawing.add(pie)
            return drawing
        except Exception:
            return None
    
    def _add_placement_summary_csv(self, writer, report_data: Dict):
        """Add placement summary data to CSV"""
        summary = report_data.get('summary', {})
        
        writer.writerow(['EXECUTIVE SUMMARY'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Placements', summary.get('total_placements', 0)])
        writer.writerow(['Branches Covered', summary.get('branches_covered', 0)])
        writer.writerow(['Industries Covered', summary.get('industries_covered', 0)])
        writer.writerow(['Average Salary (₹)', f"{summary.get('avg_salary', 0):,.2f}"])
        writer.writerow([])
        
        # Branch performance
        writer.writerow(['BRANCH PERFORMANCE'])
        writer.writerow(['Branch', 'Placements', 'Avg Salary (₹)', 'Min Salary (₹)', 'Max Salary (₹)', 'Avg Feedback (1-10)'])
        
        branch_performance = report_data.get('branch_performance', [])
        for branch in branch_performance:
            writer.writerow([
                branch.get('student_branch', 'N/A'),
                branch.get('placement_count', 0),
                f"{branch.get('avg_salary', 0):,.2f}",
                f"{branch.get('min_salary', 0):,.2f}",
                f"{branch.get('max_salary', 0):,.2f}",
                f"{branch.get('avg_feedback', 0):.1f}"
            ])
        
        writer.writerow([])
        
        # Industry distribution
        industry_stats = report_data.get('industry_distribution', [])
        if industry_stats:
            writer.writerow(['INDUSTRY DISTRIBUTION'])
            writer.writerow(['Industry', 'Placements', 'Avg Salary (₹)', 'Min Salary (₹)', 'Max Salary (₹)'])
            
            for industry in industry_stats:
                writer.writerow([
                    industry.get('job_category', 'N/A'),
                    industry.get('placement_count', 0),
                    f"{industry.get('avg_salary', 0):,.2f}",
                    f"{industry.get('min_salary', 0):,.2f}",
                    f"{industry.get('max_salary', 0):,.2f}"
                ])
    
    def _add_skill_gap_csv(self, writer, report_data: Dict):
        """Add skill gap analysis data to CSV"""
        writer.writerow(['SKILL GAP ANALYSIS SUMMARY'])
        writer.writerow(['Branch', 'Student Count', 'Top 3 Missing Skills', 'Avg Gap Score'])
        
        branch_analysis = report_data.get('branch_analysis', [])
        for branch_data in branch_analysis:
            branch_name = branch_data.get('branch', 'Unknown')
            student_count = branch_data.get('student_count', 0)
            top_gaps = branch_data.get('top_gaps', [])
            
            # Get top 3 missing skills
            top_skills = [gap.get('skill_name', '') for gap in top_gaps[:3]]
            skills_str = ', '.join(top_skills) if top_skills else 'None'
            
            # Calculate average gap score
            avg_gap_score = 0
            if top_gaps:
                avg_gap_score = sum(gap.get('demand_score', 0) for gap in top_gaps[:5]) / min(len(top_gaps), 5)
            
            writer.writerow([branch_name, student_count, skills_str, f"{avg_gap_score:.1f}"])
        
        writer.writerow([])
        writer.writerow(['DETAILED SKILL GAPS BY BRANCH'])
        writer.writerow(['Branch', 'Missing Skill', 'Demand Score (1-100)', 'Avg Salary (₹)', 'Priority Level'])
        
        for branch_data in branch_analysis:
            branch_name = branch_data.get('branch', 'Unknown')
            top_gaps = branch_data.get('top_gaps', [])
            
            for gap in top_gaps[:10]:  # Top 10 gaps per branch
                demand_score = gap.get('demand_score', 0)
                priority = 'High' if demand_score >= 80 else 'Medium' if demand_score >= 60 else 'Low'
                
                writer.writerow([
                    branch_name,
                    gap.get('skill_name', 'N/A'),
                    f"{demand_score:.1f}",
                    f"{gap.get('avg_salary', 0):,.0f}" if gap.get('avg_salary') else 'N/A',
                    priority
                ])
    
    def _add_industry_demand_csv(self, writer, report_data: Dict):
        """Add industry demand data to CSV"""
        writer.writerow(['TOP SKILLS IN DEMAND'])
        writer.writerow(['Rank', 'Skill', 'Industry', 'Demand Score (1-100)', 'Job Count', 'Avg Salary (₹)', 'Market Status'])
        
        top_skills = report_data.get('top_skills', [])
        for idx, skill in enumerate(top_skills[:25], 1):  # Top 25 skills
            demand_score = skill.get('demand_score', 0)
            market_status = 'Hot' if demand_score >= 90 else 'High' if demand_score >= 70 else 'Moderate'
            
            writer.writerow([
                idx,
                skill.get('skill_name', 'N/A'),
                skill.get('industry', 'N/A'),
                f"{demand_score:.1f}",
                skill.get('job_count', 0),
                f"{skill.get('avg_salary', 0):,.0f}" if skill.get('avg_salary') else 'N/A',
                market_status
            ])
        
        writer.writerow([])
        writer.writerow(['TRENDING SKILLS (HIGH GROWTH)'])
        writer.writerow(['Rank', 'Skill', 'Growth Rate (%)', 'Current Demand Score', 'Trend Direction', 'Opportunity Level'])
        
        trending_skills = report_data.get('trending_skills', [])
        for idx, skill in enumerate(trending_skills[:15], 1):  # Top 15 trending
            growth_rate = skill.get('growth_rate', 0)
            trend_direction = 'Rising Fast' if growth_rate >= 20 else 'Rising' if growth_rate >= 10 else 'Stable'
            opportunity = 'Excellent' if growth_rate >= 15 else 'Good' if growth_rate >= 8 else 'Fair'
            
            writer.writerow([
                idx,
                skill.get('skill_name', 'N/A'),
                f"{growth_rate:.1f}%",
                f"{skill.get('demand_score', 0):.1f}",
                trend_direction,
                opportunity
            ])
    
    def _add_branch_performance_csv(self, writer, report_data: Dict):
        """Add branch performance data to CSV"""
        writer.writerow(['BRANCH PERFORMANCE OVERVIEW'])
        writer.writerow(['Rank', 'Branch', 'Total Placements', 'Avg Salary (₹)', 'Min Salary (₹)', 'Max Salary (₹)', 'Avg Feedback (1-10)', 'Performance Grade'])
        
        branch_performance = report_data.get('branch_performance', [])
        
        # Sort by placement count for ranking
        sorted_branches = sorted(branch_performance, key=lambda x: x.get('placement_count', 0), reverse=True)
        
        for idx, branch in enumerate(sorted_branches, 1):
            placement_count = branch.get('placement_count', 0)
            avg_salary = branch.get('avg_salary', 0)
            avg_feedback = branch.get('avg_feedback', 0)
            
            # Calculate performance grade
            grade = 'A+' if placement_count >= 50 and avg_salary >= 500000 else \
                   'A' if placement_count >= 30 and avg_salary >= 400000 else \
                   'B+' if placement_count >= 20 and avg_salary >= 300000 else \
                   'B' if placement_count >= 10 else 'C'
            
            writer.writerow([
                idx,
                branch.get('student_branch', 'N/A'),
                placement_count,
                f"{avg_salary:,.2f}",
                f"{branch.get('min_salary', 0):,.2f}",
                f"{branch.get('max_salary', 0):,.2f}",
                f"{avg_feedback:.1f}",
                grade
            ])
        
        writer.writerow([])
        writer.writerow(['PERFORMANCE METRICS SUMMARY'])
        writer.writerow(['Metric', 'Value'])
        
        if branch_performance:
            total_placements = sum(b.get('placement_count', 0) for b in branch_performance)
            avg_salary_all = sum(b.get('avg_salary', 0) for b in branch_performance) / len(branch_performance)
            top_performer = max(branch_performance, key=lambda x: x.get('placement_count', 0))
            
            writer.writerow(['Total Branches Analyzed', len(branch_performance)])
            writer.writerow(['Total Placements Across All Branches', total_placements])
            writer.writerow(['Average Salary Across All Branches (₹)', f"{avg_salary_all:,.2f}"])
            writer.writerow(['Top Performing Branch', top_performer.get('student_branch', 'N/A')])
            writer.writerow(['Top Branch Placements', top_performer.get('placement_count', 0)])


def create_pdf_response(pdf_bytes: bytes, filename: str) -> 'Response':
    """Create Flask response for PDF download"""
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def create_csv_response(csv_content: str, filename: str) -> 'Response':
    """Create Flask response for CSV download"""
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response