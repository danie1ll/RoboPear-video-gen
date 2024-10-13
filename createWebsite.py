import os
from typing import List
from pydantic import BaseModel
import openai
from jinja2 import Template
import base64
from dotenv import load_dotenv

load_dotenv()

class TargetAudienceInsights(BaseModel):
    age_groups: List[str]
    gender_distribution: List[str]
    locations: List[str]
    interests: List[str]
    mainimage: str
    images: List[str]
    product: str
    description: str


# Read OpenAI API key from file
openai.api_key = os.getenv('OPENAI_API_KEY')

# HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ product_name }} Landing Page</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { width: 80%; margin: auto; overflow: hidden; }
        header { background: {{background_color}}; color: white; padding-top: 30px; min-height: 70px; border-bottom: {{main_color}} 3px solid; }
        header a { color: #ffffff; text-decoration: none; text-transform: uppercase; font-size: 16px; }
        header #branding { float: left; }
        header #branding h1 { margin: 0; }
        header nav { float: right; margin-top: 10px; }
        header .highlight, header .current a { color: {{main_color}}; font-weight: bold; }
        header a:hover { color: #cccccc; font-weight: bold; }
        #showcase { min-height: 400px; background: url('{{ product_image }}') no-repeat center center/cover; text-align: center; color: #ffffff; }
        #showcase h1 { margin-top: 100px; font-size: 55px; margin-bottom: 10px; }
        #showcase p { font-size: 20px; }
        button { display: inline-block; height: 50px; padding: 0 30px; color: #ffffff; text-align: center; font-size: 18px; font-weight: 600; line-height: 50px; letter-spacing: .1rem; text-transform: uppercase; text-decoration: none; white-space: nowrap; background-color: {{main_color}}; border-radius: 4px; border: none; cursor: pointer; box-sizing: border-box; }
        #main-content { padding: 20px; }
        footer { padding: 20px; margin-top: 20px; color: #ffffff; background-color: #222; text-align: center; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div id="branding">
                <h1><span class="highlight">{{ product_name }}</span></h1>
            </div>
        </div>
    </header>

    <section id="showcase">
        <div class="container">
            <h1>{{ headline }}</h1>
            <p>{{ subheadline }}</p>
            <button onClick="alert('Thanks du Hengst')">Pre-Order Now</button>
        </div>
    </section>

    <section id="main-content">
        <div class="container">
            {{ main_content | safe }}
        </div>
    </section>

    <footer>
        <p>© 2024 {{ product_name }}. All rights reserved.</p>
        <p>Impressum: RoboPear, 123 Munich Street, San Francisco</p>
    </footer>
</body>
</html>
"""


class ResponseFormat(BaseModel):
    headline: str
    subheadline: str
    main_content: str
    main_color: str
    background_color: str

def generate_landing_page_content(insights: TargetAudienceInsights) -> ResponseFormat:
    prompt = f"""
    Create content for a landing page selling '{insights.product}'. The target audience has the following characteristics:
    - Age groups: {', '.join(insights.age_groups)}
    - Gender distribution: {', '.join(insights.gender_distribution)}
    - Locations: {', '.join(insights.locations)}
    - Interests: {', '.join(insights.interests)}

    Product Description: {insights.description}

    Provide the following elements:
    1. A main color and a background color using html color strings for the landing page. The background color must work with text in main color.
    2. A catchy headline (max 10 words)
    3. A subheadline (max 20 words)
    4. Main content (about 300 words) describing the product benefits and features, use HTML for formatting. Do not use links. Use these images [{', '.join(insights.images)}, {insights.mainimage}] (only if existing) decently in your html, remember to bound the max size of the images in pixels since you do not know the resolution. Be creative with the text formatting.
    
    """

    response = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a skilled webdev for creating landing pages. Your product is used directly without any further changes, so be sure to do not make any mistakes."},
            {"role": "user", "content": prompt}
        ],
        response_format=ResponseFormat,
    ).choices[0].message.parsed

    print(response)

    if response == None:
        raise Exception("Failed to generate content for the landing page.")

    return response

def create_landing_page(folder: str, insights: TargetAudienceInsights):
    # Generate content using OpenAI
    content = generate_landing_page_content(insights)

    # Prepare the template data
    template_data = {
        "product_name": insights.product,
        "product_image": insights.mainimage,
        "headline": content.headline,
        "subheadline": content.subheadline,
        "main_content": content.main_content,
        "main_color": content.main_color,
        "background_color": content.background_color,
    }

    # Render the HTML template
    template = Template(html_template)
    rendered_html = template.render(**template_data)

    # Save the rendered HTML to a file
    with open(f"./generatedWebsites/{folder}/landing_page.html", "w+") as file:
        file.write(rendered_html)

    print(f"Landing page for {insights.product} has been created.")

# Example usage
if __name__ == "__main__":

    
    insights = TargetAudienceInsights(
        age_groups=["5-9"],
        gender_distribution=["100% Male", "0% Female"],
        locations=["New York", "Los Angeles", "Chicago"],
        interests=["Football", "Soccer", "Sports"],
        mainimage="coke.jpeg",
        images=["coke2.jpeg", "coke3.jpeg"],
        product="Funnzball",
        description="A football that can make funny sounds when you shoot it",
    )

    create_landing_page('sessionid', insights)