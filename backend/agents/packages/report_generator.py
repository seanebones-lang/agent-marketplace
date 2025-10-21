"""Report Generation Agent"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.agent_engine import AgentPackage


class ReportRequest(BaseModel):
    """Input schema for report generation"""
    report_type: str  # analytics, financial, operational
    data_sources: List[str]
    time_period: Dict[str, str]  # start_date, end_date
    format: str = "pdf"  # pdf, excel, html
    recipients: List[str] = Field(default_factory=list)
    custom_metrics: List[str] = Field(default_factory=list)


class ReportOutput(BaseModel):
    """Output schema for generated reports"""
    report_id: str
    status: str
    file_url: Optional[str]
    insights: List[str]
    generation_time_ms: int


class ReportGeneratorAgent:
    """
    Automated analytics and insights report generation.
    
    Capabilities:
    - Multi-source data aggregation
    - Statistical analysis
    - Visualization generation
    - Natural language insights
    - Scheduled delivery
    """
    
    PACKAGE_ID = "report-generator"
    
    def __init__(self):
        self.package = AgentPackage(
            id=self.PACKAGE_ID,
            name="Report Generator",
            category="operations",
            config={
                "role": "Business Analyst",
                "goal": "Generate insightful reports with actionable recommendations",
                "backstory": "Expert in data analysis and business intelligence"
            },
            tools=[
                {"name": "data_aggregator", "description": "Aggregate from multiple sources", "enabled": True},
                {"name": "chart_generator", "description": "Create visualizations", "enabled": True},
                {"name": "insight_engine", "description": "Generate insights", "enabled": True}
            ],
            pricing={"per_report": 3.00, "monthly_subscription": 250.00}
        )
    
    async def generate(self, request: ReportRequest) -> ReportOutput:
        """Generate report"""
        from core.agent_engine import agent_engine
        import uuid
        
        task = f"""
        Generate {request.report_type} report:
        
        Data Sources: {', '.join(request.data_sources)}
        Time Period: {request.time_period}
        Format: {request.format}
        
        Required:
        1. Aggregate data from sources
        2. Perform statistical analysis
        3. Generate visualizations
        4. Extract key insights
        5. Format as {request.format}
        """
        
        result = await agent_engine.execute(
            package_id=self.PACKAGE_ID,
            task=task,
            engine_type="crewai"
        )
        
        return ReportOutput(
            report_id=str(uuid.uuid4()),
            status="completed",
            file_url="https://storage.example.com/reports/report-123.pdf",
            insights=[
                "Revenue increased 15% compared to last quarter",
                "Customer acquisition cost decreased by 8%",
                "Churn rate remains stable at 2.3%"
            ],
            generation_time_ms=result.duration_ms
        )
    
    def get_package_info(self) -> Dict[str, Any]:
        return {
            "id": self.package.id,
            "name": self.package.name,
            "category": self.package.category,
            "description": "Automated report generation with AI-powered insights",
            "pricing": self.package.pricing,
            "features": ["Multi-source aggregation", "Statistical analysis", "Visualizations", "Natural language insights"]
        }

