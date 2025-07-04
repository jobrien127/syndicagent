from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import tempfile
from app.utils.logger import LoggerMixin
from app.services.processor import processor

# Import notifier with fallback
try:
    from app.services.notifier import notifier
except ImportError:
    notifier = None
    print("Notifier not available, email sending will be disabled")

# Try to import reportlab, fall back to simple text reports if not available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("ReportLab not available, PDF generation will be disabled")
    REPORTLAB_AVAILABLE = False

class PDFReportGenerator(LoggerMixin):
    """Generates PDF reports using ReportLab"""
    
    def __init__(self):
        super().__init__()
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self.title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            self.header_style = ParagraphStyle(
                'CustomHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            )
        else:
            self.styles = None
            self.title_style = None
            self.header_style = None
    
    def generate_pdf_report(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Generate PDF report and return file path"""
        if not REPORTLAB_AVAILABLE:
            # Fallback to text report
            return self.generate_text_report(report_data, output_path)
            
        try:
            # Create output file if no output path provided
            if not output_path:
                # Use /app/output directory (mounted to host) instead of /tmp
                output_dir = "/app/output"
                os.makedirs(output_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"agworld_report_{timestamp}.pdf"
                output_path = os.path.join(output_dir, filename)
            
            self.log_info(f"Generating PDF report: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title
            title = Paragraph(
                report_data.get('title', 'Agworld Report'),
                self.title_style
            )
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add metadata
            meta_data = [
                ['Generated:', report_data.get('created_at', 'Unknown')],
                ['Status:', report_data.get('status', 'Unknown')],
                ['Type:', report_data.get('report_type', 'Custom')]
            ]
            
            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 20))
            
            # Add content
            content_header = Paragraph("Report Content", self.header_style)
            story.append(content_header)
            
            content_text = report_data.get('content', 'No content available')
            content_para = Paragraph(content_text, self.styles['Normal'])
            story.append(content_para)
            
            # Build PDF
            doc.build(story)
            
            self.log_info(f"PDF report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.log_error(f"Error generating PDF report: {str(e)}")
            raise
    
    def generate_text_report(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Generate text report as fallback when PDF is not available"""
        try:
            # Create temporary file if no output path provided
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.txt',
                    prefix='agworld_report_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            self.log_info(f"Generating text report: {output_path}")
            
            with open(output_path, 'w') as f:
                f.write("=" * 50 + "\n")
                f.write(f"{report_data.get('title', 'Agworld Report')}\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Generated: {report_data.get('created_at', 'Unknown')}\n")
                f.write(f"Status: {report_data.get('status', 'Unknown')}\n")
                f.write(f"Type: {report_data.get('report_type', 'Custom')}\n\n")
                
                f.write("CONTENT:\n")
                f.write("-" * 20 + "\n")
                f.write(f"{report_data.get('content', 'No content available')}\n\n")
                
                if 'data' in report_data:
                    f.write("DATA:\n")
                    f.write("-" * 20 + "\n")
                    f.write(str(report_data['data']))
            
            self.log_info(f"Text report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.log_error(f"Error generating text report: {str(e)}")
            raise
    
    def _add_data_summary(self, story: List, data: Dict[str, Any]):
        """Add data summary section to PDF"""
        try:
            summary_title = Paragraph('Data Summary', self.styles['Heading2'])
            story.append(summary_title)
            story.append(Spacer(1, 10))
            
            if isinstance(data, dict):
                # Convert dict to table format
                table_data = [['Field', 'Value']]
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    table_data.append([str(key), str(value)])
                
                if len(table_data) > 1:
                    data_table = Table(table_data, colWidths=[2*inch, 4*inch])
                    data_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(data_table)
            
        except Exception as e:
            self.log_error(f"Error adding data summary to PDF: {str(e)}")

class ReportManager(LoggerMixin):
    """Manages report generation and distribution"""
    
    def __init__(self):
        super().__init__()
        self.pdf_generator = PDFReportGenerator()
    
    def generate_report(
        self,
        report_data: Dict[str, Any],
        format_type: str = "both",  # pdf, email, both
        recipients: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate and optionally send report"""
        try:
            self.log_info(f"Generating {format_type} report")
            
            result = {
                "success": False,
                "pdf_path": None,
                "email_sent": False,
                "errors": []
            }
            
            # Generate PDF if requested
            if format_type in ["pdf", "both"]:
                try:
                    pdf_path = self.pdf_generator.generate_pdf_report(report_data)
                    result["pdf_path"] = pdf_path
                    self.log_info(f"PDF generated: {pdf_path}")
                except Exception as e:
                    result["errors"].append(f"PDF generation failed: {str(e)}")
            
            # Send email if requested and recipients provided
            if format_type in ["email", "both"] and recipients:
                try:
                    if notifier:
                        email_sent = notifier.send_notification("email", recipients, report_data)
                        result["email_sent"] = email_sent
                        if email_sent:
                            self.log_info("Report email sent successfully")
                        else:
                            result["errors"].append("Email sending failed")
                    else:
                        result["errors"].append("Email notifier not available")
                except Exception as e:
                    result["errors"].append(f"Email sending failed: {str(e)}")
            
            result["success"] = len(result["errors"]) == 0
            return result
            
        except Exception as e:
            self.log_error(f"Report generation failed: {str(e)}")
            return {
                "success": False,
                "errors": [str(e)],
                "pdf_path": None,
                "email_sent": False
            }
    
    def create_summary_report(self, processed_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary report from processed data"""
        try:
            # Aggregate data
            aggregated_data = processor.aggregate_data(processed_data_list)
            
            # Create report structure
            report_data = {
                "title": f"Agworld Data Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "report_type": "summary",
                "content": self._create_summary_content(aggregated_data),
                "data": aggregated_data
            }
            
            return report_data
            
        except Exception as e:
            self.log_error(f"Failed to create summary report: {str(e)}")
            raise
    
    def _create_summary_content(self, aggregated_data: Dict[str, Any]) -> str:
        """Create human-readable summary content"""
        try:
            content_lines = [
                f"Data Summary Report",
                f"Generated: {aggregated_data.get('aggregated_at', 'Unknown')}",
                f"",
                f"Total Records Processed: {aggregated_data.get('total_records', 0)}",
                f""
            ]
            
            # Add data type breakdown
            data_types = aggregated_data.get('data_types', {})
            if data_types:
                content_lines.append("Data Types:")
                for data_type, count in data_types.items():
                    content_lines.append(f"  - {data_type}: {count} records")
                content_lines.append("")
            
            # Add summaries
            summaries = aggregated_data.get('summaries', [])
            if summaries:
                content_lines.append("Record Summaries:")
                for i, summary in enumerate(summaries[:10], 1):  # Limit to first 10
                    content_lines.append(f"  {i}. {summary}")
                
                if len(summaries) > 10:
                    content_lines.append(f"  ... and {len(summaries) - 10} more records")
            
            return "\n".join(content_lines)
            
        except Exception as e:
            self.log_error(f"Error creating summary content: {str(e)}")
            return "Error generating summary content"

# Global reporter instance
reporter = ReportManager()
