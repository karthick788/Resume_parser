# Resume Parser

A Python-based resume parser that extracts structured information from resumes in PDF, DOCX, and TXT formats.

## Features

- Extracts key information from resumes including:
  - Name
  - Email
  - Phone number
  - Skills
  - Education
  - Work experience
  - Links (GitHub, LinkedIn, personal websites)
- Supports multiple file formats: PDF, DOCX, and TXT
- Uses NLP (spaCy) for entity recognition
- Simple command-line interface

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ResumeParser
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the spaCy English model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Command Line

```bash
python resume_parser.py path/to/your/resume.pdf
```

The script will output the parsed information in JSON format.

### Python Module

```python
from resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_resume("path/to/your/resume.pdf")
print(result)
```

## Output Format

The parser returns a dictionary with the following structure:

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1 (555) 123-4567",
  "skills": ["Python", "Machine Learning", "Docker"],
  "education": ["MS in Computer Science, Stanford University, 2020"],
  "experience": [
    {
      "duration": "Jan 2020 - Present",
      "details": "Software Engineer at Tech Company - Developed web applications using Python and React"
    }
  ],
  "links": ["github.com/johndoe", "linkedin.com/in/johndoe"],
  "raw_text": "First 500 characters of the resume..."
}
```

## Customization

You can extend the parser by:

1. Adding more skills to the `_load_skills_vocab` method
2. Enhancing the regex patterns for better extraction
3. Training a custom NER model with spaCy for better entity recognition

## Dependencies

- Python 3.7+
- pdfplumber
- python-docx
- spacy
- python-magic (with python-magic-bin on Windows)

## License

MIT
