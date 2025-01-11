"""
Email template management for the automation system
"""
from typing import Dict

class EmailTemplateManager:
    def __init__(self):
        self.templates = self._create_email_templates()
        
    def _create_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Create and store email templates for each company"""
        
        base_template = """
Dear {name},

I hope this email finds you well. My name is Sai Harsha Mummaneni, and I'm reaching out regarding potential data science opportunities at {company}.

I'm a Master's graduate from UC Berkeley in Operations Research with a specialization in Fintech. Currently working as a Senior Data Scientist at BNY Mellon's TSG AI Team, I've gained valuable experience in:

{company_specific_achievements}

I would be grateful for the opportunity to discuss how my skills and experience could contribute to {company}'s data science initiatives. I've attached my resume for your reference.

Thank you for your time and consideration.

Best regards,
Sai Harsha Mummaneni
341-732-7942
LinkedIn: https://www.linkedin.com/in/harsha-m-725a691a0/
"""

        reminder_template = """
Dear {name},

I hope you're doing well. I wanted to follow up on my previous email regarding data science opportunities at {company}.

Given my background in AI/ML and my current role leading AI development projects at BNY Mellon, I believe I could bring valuable expertise to {company}'s data science initiatives.

{company_specific_achievements}

I would welcome the opportunity to discuss how my experience aligns with your team's needs.

Best regards,
Sai Harsha Mummaneni
341-732-7942
"""

        # Company-specific achievements
        achievements = {
            'amazon': """• Created LLM-based reasoning engines improving compliance metrics by 30%
• Developed ML classification systems achieving 75% accuracy with distributed computing
• Built scalable ETL pipelines reducing processing time by 65%""",
            
            'meta': """• Engineered AI chatbots reducing query latency by 40% using ColBERT and cross-encoder reranking
• Implemented advanced embedding techniques for semantic search and document classification
• Led AI development teams increasing sprint velocity by 25%""",
            
            'google': """• Developed vector embedding systems for time series analysis using HNSW algorithm
• Created ML models with 88% accuracy in customer lifetime value prediction
• Implemented distributed computing solutions using Ray framework""",
            
            'apple': """• Built end-to-end A/B testing pipelines improving conversion by 23%
• Developed custom RAG systems with advanced chunking strategies
• Created ML-based notification systems increasing conversion rates by 15%"""
        }

        templates = {}
        for company in ['amazon', 'meta', 'google', 'apple']:
            templates[company] = {
                'initial': base_template.format(
                    name="{name}",
                    company=company.title(),
                    company_specific_achievements=achievements[company]
                ),
                'reminder': reminder_template.format(
                    name="{name}",
                    company=company.title(),
                    company_specific_achievements=achievements[company]
                )
            }
            
        return templates
    
    def get_template(self, company: str, template_type: str = 'initial') -> str:
        """
        Get specific email template
        
        Args:
            company: Company name
            template_type: 'initial' or 'reminder'
            
        Returns:
            str: Email template
        """
        company = company.lower()
        if company not in self.templates:
            raise ValueError(f"No template found for company: {company}")
            
        if template_type not in ['initial', 'reminder']:
            raise ValueError(f"Invalid template type: {template_type}")
            
        return self.templates[company][template_type]
        
    def format_template(self, template: str, **kwargs) -> str:
        """
        Format template with provided values
        
        Args:
            template: Email template
            kwargs: Values to format template with
            
        Returns:
            str: Formatted email content
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required template value: {e}")