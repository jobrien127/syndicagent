import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Template
import os
from app.config import settings
from app.utils.logger import LoggerMixin

class EmailNotifier(LoggerMixin):
    """Handles email notifications"""
    
    def __init__(self):
        super().__init__()
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USER
        self.password = settings.EMAIL_PASS
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email notification"""
        try:
            self.log_info(f"Sending email to {len(to_emails)} recipients")
            
            if not self.smtp_server or not self.username:
                self.log_warning("Email configuration incomplete, skipping email send")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.log_info("Email sent successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to send email: {str(e)}")
            return False
    
    def send_report_email(
        self,
        to_emails: List[str],
        report_data: Dict[str, Any],
        template_path: Optional[str] = None
    ) -> bool:
        """Send formatted report email"""
        try:
            # Use default template if none provided
            if not template_path:
                template_path = "app/templates/report.html"
            
            # Load and render template
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                template = Template(template_content)
                html_body = template.render(**report_data)
            else:
                html_body = self._create_default_report_html(report_data)
            
            # Create text version
            text_body = self._create_text_report(report_data)
            
            subject = f"Agworld Report - {report_data.get('title', 'Generated Report')}"
            
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                body=text_body,
                html_body=html_body
            )
            
        except Exception as e:
            self.log_error(f"Failed to send report email: {str(e)}")
            return False
    
    def _create_default_report_html(self, report_data: Dict[str, Any]) -> str:
        """Create basic HTML report when template is not available"""
        html = f"""
        <html>
        <head><title>Agworld Report</title></head>
        <body>
            <h1>{report_data.get('title', 'Agworld Report')}</h1>
            <p><strong>Generated:</strong> {report_data.get('created_at', 'Unknown')}</p>
            <p><strong>Status:</strong> {report_data.get('status', 'Unknown')}</p>
            <div>
                <h2>Content:</h2>
                <p>{report_data.get('content', 'No content available')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_text_report(self, report_data: Dict[str, Any]) -> str:
        """Create text version of report"""
        return f"""
Agworld Report
{'-' * 50}

Title: {report_data.get('title', 'Agworld Report')}
Generated: {report_data.get('created_at', 'Unknown')}
Status: {report_data.get('status', 'Unknown')}

Content:
{report_data.get('content', 'No content available')}

---
This is an automated report from Agworld Reporter.
        """.strip()

class NotificationManager(LoggerMixin):
    """Manages different types of notifications"""
    
    def __init__(self):
        super().__init__()
        self.email_notifier = EmailNotifier()
    
    def send_notification(
        self,
        notification_type: str,
        recipients: Dict[str, Any],
        data: Dict[str, Any]
    ) -> bool:
        """Send notification based on type"""
        try:
            if notification_type == "email":
                email_addresses = recipients.get("emails", [])
                if email_addresses:
                    return self.email_notifier.send_report_email(email_addresses, data)
            
            # Add other notification types here (SMS, Slack, etc.)
            
            self.log_warning(f"Unsupported notification type: {notification_type}")
            return False
            
        except Exception as e:
            self.log_error(f"Failed to send {notification_type} notification: {str(e)}")
            return False

# Global notifier instance
notifier = NotificationManager()
