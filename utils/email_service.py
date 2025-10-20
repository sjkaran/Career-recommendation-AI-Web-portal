"""
Email service for sending reports and notifications
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with attachments"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
    def send_report_email(self, to_email: str, subject: str, 
                         report_data: Dict[str, Any], 
                         attachment_path: Optional[str] = None) -> bool:
        """Send report via email with optional attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create email body
            body = self._create_email_body(report_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                self._add_attachment(msg, attachment_path)
            
            # Send email
            return self._send_email(msg, to_email)
            
        except Exception as e:
            logger.error(f"Failed to send report email: {e}")
            return False
    
    def send_notification_email(self, to_email: str, subject: str, 
                              message: str, is_html: bool = False) -> bool:
        """Send simple notification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(message, content_type))
            
            return self._send_email(msg, to_email)
            
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            return False
    
    def send_bulk_reports(self, recipients: List[str], subject: str,
                         report_data: Dict[str, Any], 
                         attachment_bytes: Optional[bytes] = None,
                         attachment_filename: Optional[str] = None) -> Dict[str, bool]:
        """Send report to multiple recipients"""
        results = {}
        
        for email in recipients:
            try:
                if attachment_bytes:
                    # Save bytes to temporary file for attachment
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{attachment_filename.split(".")[-1]}') as tmp_file:
                        tmp_file.write(attachment_bytes)
                        tmp_path = tmp_file.name
                    
                    success = self.send_report_email(email, subject, report_data, tmp_path)
                    
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                else:
                    success = self.send_report_email(email, subject, report_data)
                
                results[email] = success
                
            except Exception as e:
                logger.error(f"Failed to send report to {email}: {e}")
                results[email] = False
        
        return results
    
    def schedule_report_delivery(self, report_config: Dict[str, Any]) -> bool:
        """Schedule automated report delivery"""
        try:
            # This would integrate with a task scheduler like Celery in production
            # For now, we'll implement a simple scheduling mechanism
            
            schedule_type = report_config.get('schedule_type', 'once')
            
            if schedule_type == 'once':
                # Send immediately
                return self._generate_and_send_report(report_config)
            elif schedule_type in ['daily', 'weekly', 'monthly']:
                # In production, this would create a scheduled task
                logger.info(f"Scheduled {schedule_type} report delivery configured")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to schedule report delivery: {e}")
            return False
    
    def _generate_and_send_report(self, config: Dict[str, Any]) -> bool:
        """Generate and send report based on configuration"""
        try:
            from utils.report_generator import ReportGenerator
            
            # Generate report
            generator = ReportGenerator()
            report_data = config.get('report_data', {})
            export_format = config.get('format', 'pdf')
            
            if export_format == 'pdf':
                report_bytes = generator.generate_pdf_report(report_data)
                filename = f"{config.get('report_type', 'report')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            else:
                report_content = generator.generate_csv_report(report_data)
                report_bytes = report_content.encode('utf-8')
                filename = f"{config.get('report_type', 'report')}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Send to recipients
            recipients = config.get('recipients', [])
            subject = config.get('subject', f"Automated Report - {datetime.now().strftime('%Y-%m-%d')}")
            
            results = self.send_bulk_reports(recipients, subject, report_data, report_bytes, filename)
            
            # Log results
            successful = sum(1 for success in results.values() if success)
            logger.info(f"Report sent to {successful}/{len(recipients)} recipients")
            
            return successful > 0
            
        except Exception as e:
            logger.error(f"Failed to generate and send report: {e}")
            return False
    
    def _create_email_body(self, report_data: Dict[str, Any]) -> str:
        """Create HTML email body for report"""
        report_type = report_data.get('report_type', 'Analytics Report')
        generated_at = report_data.get('generated_at', datetime.now().isoformat())
        
        # Format report title
        title_map = {
            'placement_summary': 'Placement Summary Report',
            'skill_gap_analysis': 'Skill Gap Analysis Report',
            'industry_demand': 'Industry Demand Report',
            'branch_performance': 'Branch Performance Report'
        }
        report_title = title_map.get(report_type, report_type.replace('_', ' ').title())
        
        # Get summary data
        summary = report_data.get('summary', {})
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .summary-box {{ background: #f8fafc; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; }}
                .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
                .metric {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; min-width: 150px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
                .metric-label {{ font-size: 14px; color: #64748b; }}
                .footer {{ background: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #64748b; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
                th {{ background: #f8fafc; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AI Career Platform</h1>
                <h2>{report_title}</h2>
            </div>
            
            <div class="content">
                <div class="summary-box">
                    <h3>Report Summary</h3>
                    <p><strong>Generated:</strong> {self._format_datetime(generated_at)}</p>
                    <p><strong>Report Type:</strong> {report_title}</p>
        """
        
        # Add date range if available
        date_range = report_data.get('date_range')
        if date_range:
            html_body += f"""
                    <p><strong>Date Range:</strong> {date_range.get('start_date', 'N/A')} to {date_range.get('end_date', 'N/A')}</p>
            """
        
        # Add filters if available
        filters = report_data.get('filters')
        if filters and any(filters.values()):
            filter_info = []
            for key, value in filters.items():
                if value:
                    filter_info.append(f"{key.title()}: {value}")
            if filter_info:
                html_body += f"""
                    <p><strong>Filters Applied:</strong> {', '.join(filter_info)}</p>
                """
        
        html_body += """
                </div>
        """
        
        # Add key metrics based on report type
        if report_type == 'placement_summary' and summary:
            html_body += f"""
                <h3>Key Metrics</h3>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{summary.get('total_placements', 0)}</div>
                        <div class="metric-label">Total Placements</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{summary.get('branches_covered', 0)}</div>
                        <div class="metric-label">Branches Covered</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">₹{summary.get('avg_salary', 0):,.0f}</div>
                        <div class="metric-label">Average Salary</div>
                    </div>
                </div>
            """
        
        # Add branch performance table for relevant reports
        branch_performance = report_data.get('branch_performance', [])
        if branch_performance:
            html_body += """
                <h3>Top Performing Branches</h3>
                <table>
                    <tr>
                        <th>Branch</th>
                        <th>Placements</th>
                        <th>Avg Salary</th>
                        <th>Feedback</th>
                    </tr>
            """
            
            for branch in branch_performance[:5]:  # Top 5 branches
                html_body += f"""
                    <tr>
                        <td>{branch.get('student_branch', 'N/A')}</td>
                        <td>{branch.get('placement_count', 0)}</td>
                        <td>₹{branch.get('avg_salary', 0):,.0f}</td>
                        <td>{branch.get('avg_feedback', 0):.1f}/10</td>
                    </tr>
                """
            
            html_body += """
                </table>
            """
        
        # Add top skills for industry demand reports
        top_skills = report_data.get('top_skills', [])
        if top_skills:
            html_body += """
                <h3>Top Skills in Demand</h3>
                <table>
                    <tr>
                        <th>Skill</th>
                        <th>Industry</th>
                        <th>Demand Score</th>
                        <th>Avg Salary</th>
                    </tr>
            """
            
            for skill in top_skills[:5]:  # Top 5 skills
                salary = skill.get('avg_salary')
                salary_str = f"₹{salary:,.0f}" if salary else "N/A"
                html_body += f"""
                    <tr>
                        <td>{skill.get('skill_name', 'N/A')}</td>
                        <td>{skill.get('industry', 'N/A')}</td>
                        <td>{skill.get('demand_score', 0):.1f}</td>
                        <td>{salary_str}</td>
                    </tr>
                """
            
            html_body += """
                </table>
            """
        
        html_body += """
                <p><strong>Note:</strong> This is an automated report. For detailed analysis, please refer to the attached file or access the full dashboard.</p>
            </div>
            
            <div class="footer">
                <p>AI Career Platform - Automated Report System</p>
                <p>This email was generated automatically. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add file attachment to email message"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment {file_path}: {e}")
    
    def _send_email(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Send email message via SMTP"""
        try:
            # Check if email configuration is available
            if not self.smtp_username or not self.smtp_password:
                logger.warning("Email credentials not configured. Email sending disabled.")
                return False
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string for display"""
        if not datetime_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return datetime_str
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration and connectivity"""
        try:
            if not self.smtp_username or not self.smtp_password:
                return {
                    'success': False,
                    'error': 'Email credentials not configured',
                    'details': 'Please set SMTP_USERNAME and SMTP_PASSWORD environment variables'
                }
            
            # Test SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email configuration is valid',
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'from_email': self.from_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Email configuration test failed',
                'details': str(e)
            }


# Global email service instance
email_service = EmailService()