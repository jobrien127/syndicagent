import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import base64
import io
import tempfile
import os

from app.utils.logger import LoggerMixin

class PlotlyVisualizer(LoggerMixin):
    """Creates interactive visualizations using Plotly"""
    
    def __init__(self):
        super().__init__()
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    def create_field_summary_chart(self, field_data: List[Dict[str, Any]]) -> str:
        """Create field summary chart"""
        try:
            if not field_data:
                return self._create_empty_chart("No field data available")
            
            # Extract data for visualization
            field_names = [field.get('name', 'Unknown') for field in field_data]
            field_areas = [field.get('area', 0) for field in field_data]
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=field_names,
                    y=field_areas,
                    text=field_areas,
                    textposition='auto',
                    marker_color=self.default_colors[0]
                )
            ])
            
            fig.update_layout(
                title="Field Areas",
                xaxis_title="Field Name",
                yaxis_title="Area (hectares)",
                showlegend=False,
                height=400
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            self.log_error(f"Failed to create field summary chart: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_activity_timeline(self, activity_data: List[Dict[str, Any]]) -> str:
        """Create activity timeline chart"""
        try:
            if not activity_data:
                return self._create_empty_chart("No activity data available")
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(activity_data)
            
            # Ensure date column exists and is properly formatted
            if 'date' not in df.columns:
                return self._create_error_chart("No date information in activity data")
            
            df['date'] = pd.to_datetime(df['date'])
            df['activity_type'] = df.get('type', 'Unknown')
            
            # Create timeline chart
            fig = px.timeline(
                df,
                x_start="date",
                x_end="date",
                y="activity_type",
                color="activity_type",
                title="Activity Timeline"
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Activity Type"
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            self.log_error(f"Failed to create activity timeline: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_crop_distribution_pie(self, crop_data: List[Dict[str, Any]]) -> str:
        """Create crop distribution pie chart"""
        try:
            if not crop_data:
                return self._create_empty_chart("No crop data available")
            
            # Count crop types
            crop_counts = {}
            for crop in crop_data:
                crop_type = crop.get('type', 'Unknown')
                crop_counts[crop_type] = crop_counts.get(crop_type, 0) + 1
            
            # Create pie chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(crop_counts.keys()),
                    values=list(crop_counts.values()),
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title="Crop Distribution",
                height=400
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            self.log_error(f"Failed to create crop distribution chart: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_dashboard(self, data: Dict[str, Any]) -> str:
        """Create comprehensive dashboard with multiple charts"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Field Areas', 'Activity Timeline', 'Crop Distribution', 'Summary'),
                specs=[[{"type": "bar"}, {"type": "scatter"}],
                       [{"type": "pie"}, {"type": "table"}]]
            )
            
            # Add field areas if available
            if 'fields' in data:
                field_data = data['fields']
                field_names = [f.get('name', 'Unknown') for f in field_data]
                field_areas = [f.get('area', 0) for f in field_data]
                
                fig.add_trace(
                    go.Bar(x=field_names, y=field_areas, name="Fields"),
                    row=1, col=1
                )
            
            # Add activity timeline if available
            if 'activities' in data:
                activity_data = data['activities']
                dates = [a.get('date', '') for a in activity_data]
                types = [a.get('type', 'Unknown') for a in activity_data]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=types, mode='markers', name="Activities"),
                    row=1, col=2
                )
            
            # Add crop distribution if available
            if 'crops' in data:
                crop_data = data['crops']
                crop_counts = {}
                for crop in crop_data:
                    crop_type = crop.get('type', 'Unknown')
                    crop_counts[crop_type] = crop_counts.get(crop_type, 0) + 1
                
                fig.add_trace(
                    go.Pie(labels=list(crop_counts.keys()), values=list(crop_counts.values())),
                    row=2, col=1
                )
            
            # Add summary table
            summary_data = [
                ["Total Fields", len(data.get('fields', []))],
                ["Total Crops", len(data.get('crops', []))],
                ["Total Activities", len(data.get('activities', []))],
                ["Last Updated", datetime.now().strftime('%Y-%m-%d %H:%M')]
            ]
            
            fig.add_trace(
                go.Table(
                    header=dict(values=['Metric', 'Value']),
                    cells=dict(values=[[row[0] for row in summary_data],
                                     [row[1] for row in summary_data]])
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=800, title_text="Agworld Data Dashboard")
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            self.log_error(f"Failed to create dashboard: {str(e)}")
            return self._create_error_chart(str(e))
    
    def _create_empty_chart(self, message: str) -> str:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="No Data Available",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig.to_html(include_plotlyjs='cdn')
    
    def _create_error_chart(self, error_message: str) -> str:
        """Create error chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Visualization Error",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig.to_html(include_plotlyjs='cdn')

class MatplotlibVisualizer(LoggerMixin):
    """Creates static visualizations using Matplotlib"""
    
    def __init__(self):
        super().__init__()
        plt.style.use('default')
    
    def create_activity_trend_chart(
        self,
        activity_data: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """Create activity trend chart and return file path"""
        try:
            if not activity_data:
                return self._create_empty_plot("No activity data available", output_path)
            
            # Convert to DataFrame
            df = pd.DataFrame(activity_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date and count activities
            daily_counts = df.groupby(df['date'].dt.date).size()
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2)
            ax.set_title('Daily Activity Trends', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Activities', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format dates on x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Save to file
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.png', prefix='activity_trend_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.log_info(f"Activity trend chart saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.log_error(f"Failed to create activity trend chart: {str(e)}")
            return self._create_empty_plot(f"Error: {str(e)}", output_path)
    
    def create_field_comparison_chart(
        self,
        field_data: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """Create field comparison chart"""
        try:
            if not field_data:
                return self._create_empty_plot("No field data available", output_path)
            
            field_names = [field.get('name', 'Unknown') for field in field_data]
            field_areas = [field.get('area', 0) for field in field_data]
            
            # Create horizontal bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(field_names, field_areas)
            
            # Add value labels on bars
            for i, (bar, area) in enumerate(zip(bars, field_areas)):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{area:.1f}', va='center', fontsize=10)
            
            ax.set_title('Field Area Comparison', fontsize=16, fontweight='bold')
            ax.set_xlabel('Area (hectares)', fontsize=12)
            ax.set_ylabel('Field Name', fontsize=12)
            ax.grid(True, axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            # Save to file
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.png', prefix='field_comparison_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.log_info(f"Field comparison chart saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.log_error(f"Failed to create field comparison chart: {str(e)}")
            return self._create_empty_plot(f"Error: {str(e)}", output_path)
    
    def _create_empty_plot(self, message: str, output_path: Optional[str] = None) -> str:
        """Create empty plot with message"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.png', prefix='empty_plot_'
            )
            output_path = temp_file.name
            temp_file.close()
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path

class VisualizationManager(LoggerMixin):
    """Manages different visualization types and formats"""
    
    def __init__(self):
        super().__init__()
        self.plotly_viz = PlotlyVisualizer()
        self.matplotlib_viz = MatplotlibVisualizer()
    
    def create_report_visualizations(
        self,
        data: Dict[str, Any],
        include_static: bool = True,
        include_interactive: bool = True
    ) -> Dict[str, Any]:
        """Create visualizations for reports"""
        try:
            visualizations = {
                "interactive": {},
                "static": {},
                "success": True,
                "errors": []
            }
            
            # Create interactive visualizations
            if include_interactive:
                try:
                    if 'fields' in data:
                        visualizations["interactive"]["field_summary"] = \
                            self.plotly_viz.create_field_summary_chart(data['fields'])
                    
                    if 'activities' in data:
                        visualizations["interactive"]["activity_timeline"] = \
                            self.plotly_viz.create_activity_timeline(data['activities'])
                    
                    if 'crops' in data:
                        visualizations["interactive"]["crop_distribution"] = \
                            self.plotly_viz.create_crop_distribution_pie(data['crops'])
                    
                    visualizations["interactive"]["dashboard"] = \
                        self.plotly_viz.create_dashboard(data)
                        
                except Exception as e:
                    self.log_error(f"Failed to create interactive visualizations: {str(e)}")
                    visualizations["errors"].append(f"Interactive viz error: {str(e)}")
            
            # Create static visualizations
            if include_static:
                try:
                    if 'activities' in data:
                        visualizations["static"]["activity_trend"] = \
                            self.matplotlib_viz.create_activity_trend_chart(data['activities'])
                    
                    if 'fields' in data:
                        visualizations["static"]["field_comparison"] = \
                            self.matplotlib_viz.create_field_comparison_chart(data['fields'])
                        
                except Exception as e:
                    self.log_error(f"Failed to create static visualizations: {str(e)}")
                    visualizations["errors"].append(f"Static viz error: {str(e)}")
            
            visualizations["success"] = len(visualizations["errors"]) == 0
            return visualizations
            
        except Exception as e:
            self.log_error(f"Failed to create visualizations: {str(e)}")
            return {
                "interactive": {},
                "static": {},
                "success": False,
                "errors": [str(e)]
            }

# Global visualizer instance
visualizer = VisualizationManager()
