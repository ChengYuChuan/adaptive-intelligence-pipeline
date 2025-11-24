"""
Email Output Adapter - Week 2 Implementation
Send reports via email using SMTP
"""
from typing import Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.adapters.output.base import BaseOutputAdapter
from app.config import settings

# Import aiosmtplib only if needed
try:
    import aiosmtplib
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False
    logging.warning("aiosmtplib not installed. Install with: pip install aiosmtplib")

logger = logging.getLogger(__name__)


class EmailAdapter(BaseOutputAdapter):
    """
    Email output adapter using SMTP
    
    Suitable for:
    - Daily/weekly report delivery
    - Personal notifications
    - Team distribution lists
    
    Supported providers:
    - Gmail (smtp.gmail.com:587)
    - Outlook (smtp-mail.outlook.com:587)
    - SendGrid (smtp.sendgrid.net:587)
    - AWS SES (email-smtp.us-east-1.amazonaws.com:587)
    - Custom SMTP servers
    
    Gmail setup:
    1. Enable 2-factor authentication
    2. Generate App Password (not your regular password)
    3. Use App Password in SMTP_PASSWORD
    
    Configuration in .env:
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your-email@gmail.com
    SMTP_PASSWORD=your-app-password
    EMAIL_FROM=your-email@gmail.com
    EMAIL_TO=recipient@example.com
    """
    
    def __init__(self):
        """Initialize email adapter with SMTP settings"""
        if not SMTP_AVAILABLE:
            raise ImportError(
                "aiosmtplib is required for Email adapter. "
                "Install with: pip install aiosmtplib"
            )
        
        # Load SMTP settings
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_to = settings.EMAIL_TO
        
        # Validate configuration
        if not all([
            self.smtp_host, self.smtp_port, 
            self.smtp_username, self.smtp_password,
            self.email_from, self.email_to
        ]):
            raise ValueError(
                "Email adapter not fully configured. "
                "Please set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
                "SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO in environment."
            )
        
        logger.info(f"Email adapter initialized (SMTP: {self.smtp_host}:{self.smtp_port})")
    
    async def send(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send report via email
        
        Args:
            content: Report content (supports plain text and HTML)
            metadata: Email metadata
                - title: Email subject
                - recipients: List of additional recipients (optional)
                - cc: List of CC recipients (optional)
                - format: 'plain' or 'html' (default: 'plain')
                - priority: 'high', 'normal', 'low' (default: 'normal')
                
        Returns:
            Result dictionary with status and message
        """
        metadata = metadata or {}
        
        try:
            # Prepare email
            subject = metadata.get('title', f"Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            recipients = self._parse_recipients(metadata)
            cc_recipients = metadata.get('cc', [])
            email_format = metadata.get('format', 'plain')
            priority = metadata.get('priority', 'normal')
            
            # Create message
            message = self._create_message(
                subject=subject,
                content=content,
                recipients=recipients,
                cc_recipients=cc_recipients,
                email_format=email_format,
                priority=priority
            )
            
            # Send email
            await self._send_email(message, recipients + cc_recipients)
            
            logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")
            
            return {
                "status": "success",
                "message": f"Email sent to {len(recipients)} recipient(s)",
                "url": None,  # Email doesn't have URL
                "timestamp": datetime.now().isoformat(),
                "recipients": recipients
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return {
                "status": "failed",
                "message": f"Email sending failed: {str(e)}",
                "url": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_recipients(self, metadata: Dict[str, Any]) -> list:
        """Parse and validate recipient list"""
        recipients = metadata.get('recipients', [])
        
        # Add default recipient if not in list
        if self.email_to and self.email_to not in recipients:
            recipients = [self.email_to] + recipients
        
        # Validate email addresses (basic validation)
        valid_recipients = []
        for email in recipients:
            if '@' in email and '.' in email:
                valid_recipients.append(email)
            else:
                logger.warning(f"Invalid email address skipped: {email}")
        
        if not valid_recipients:
            raise ValueError("No valid recipient email addresses")
        
        return valid_recipients
    
    def _create_message(
        self,
        subject: str,
        content: str,
        recipients: list,
        cc_recipients: list,
        email_format: str,
        priority: str
    ) -> MIMEMultipart:
        """Create email message with proper formatting"""
        
        # Create message container
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.email_from
        message['To'] = ', '.join(recipients)
        
        if cc_recipients:
            message['Cc'] = ', '.join(cc_recipients)
        
        # Add priority header
        if priority == 'high':
            message['X-Priority'] = '1'
            message['Importance'] = 'high'
        elif priority == 'low':
            message['X-Priority'] = '5'
            message['Importance'] = 'low'
        
        # Add content
        if email_format == 'html':
            # Convert markdown-like content to HTML
            html_content = self._markdown_to_html(content)
            message.attach(MIMEText(html_content, 'html', 'utf-8'))
        else:
            # Plain text
            message.attach(MIMEText(content, 'plain', 'utf-8'))
        
        return message
    
    async def _send_email(self, message: MIMEMultipart, all_recipients: list):
        """Send email via SMTP"""
        
        # Create SMTP client
        async with aiosmtplib.SMTP(
            hostname=self.smtp_host,
            port=self.smtp_port,
            use_tls=False,  # We'll use STARTTLS
            timeout=30
        ) as smtp:
            # Connect and authenticate
            await smtp.connect()
            await smtp.starttls()  # Upgrade to TLS
            await smtp.login(self.smtp_username, self.smtp_password)
            
            # Send message
            await smtp.send_message(message)
            
            logger.debug(f"SMTP send completed to {all_recipients}")
    
    def _markdown_to_html(self, content: str) -> str:
        """
        Simple markdown to HTML conversion
        For production, consider using a proper markdown library
        """
        html = content
        
        # Convert headers
        html = html.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>')
        html = html.replace('\n### ', '\n<h3>').replace('\n#### ', '\n<h4>')
        
        # Convert bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert line breaks to paragraphs
        paragraphs = html.split('\n\n')
        html = ''.join([f'<p>{p}</p>' for p in paragraphs if p.strip()])
        
        # Wrap in HTML structure
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; border-bottom: 2px solid #eee; }}
                p {{ margin: 1em 0; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return html
    
    def get_output_name(self) -> str:
        """Return the output name"""
        return "Email"


# Helper functions for email testing

async def test_email_connection(adapter: EmailAdapter) -> bool:
    """
    Test SMTP connection without sending actual email
    
    Returns:
        True if connection successful
    """
    try:
        async with aiosmtplib.SMTP(
            hostname=adapter.smtp_host,
            port=adapter.smtp_port,
            use_tls=False,
            timeout=10
        ) as smtp:
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(adapter.smtp_username, adapter.smtp_password)
            
        logger.info("SMTP connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"SMTP connection test failed: {e}")
        return False


async def send_test_email(adapter: EmailAdapter) -> bool:
    """
    Send a test email
    
    Returns:
        True if email sent successfully
    """
    try:
        result = await adapter.send(
            content="""# Test Email

This is a test email from Adaptive Intelligence Pipeline.

If you receive this email, your email adapter is working correctly!

---
Sent at: {datetime.now().isoformat()}
""",
            metadata={
                "title": "AIP Test Email",
                "format": "plain"
            }
        )
        
        return result["status"] == "success"
        
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        return False