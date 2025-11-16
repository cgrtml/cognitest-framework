# CogniTest Framework

**LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📋 Overview

**CogniTest** is a production-ready cognitive software testing framework that integrates Large Language Models (LLMs) with automated testing pipelines. It enables end-to-end intelligent test generation, bug classification, and log interpretation using Mistral-7B-Instruct as the core reasoning engine.

**Key Features:**
- 🤖 Automated Test Generation from natural language requirements  
- 🧠 Cognitive Bug Classification (89.2% accuracy)  
- 📊 Human-readable Log Interpretation  
- ⚡ 64.3% reduction in manual test creation time  
- 📈 22.8 percentage point improvement in coverage  
- 🧪 742 executable tests generated from requirement documents  

---

## 🎓 Research Paper

This repository accompanies the TechRxiv research preprint:

### **"LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI"**

**Author:** Çağrı Temel, IEEE Senior Member  
**Affiliation:** Grand Canyon University & Hezarfen LLC  
**Contact:** CTemel@my.gcu.edu • cagritemel@ieee.org  

📄 **Full Paper (TechRxiv):**  
https://doi.org/10.36227/techrxiv.176315879.96821044/v1

---

## 🏗️ Architecture

## CogniTest Framework Architecture
```
📋 Phase 1: Test Generation
   └─ Natural language → executable pytest tests

⚙️ Phase 2: Intelligent Execution
   └─ Test execution with detailed tracing

🔍 Phase 3: Log Interpretation
   └─ Root cause analysis & remediation hints

🏷️ Phase 4: Bug Classification
   └─ Automated severity scoring & explanation
```

CogniTest implements a four-phase cognitive testing pipeline:
Test Generation (Phase 1):
Parses natural language requirements
Generates executable pytest test cases
Uses structured prompts and domain constraints
Intelligent Execution (Phase 2):
Runs generated tests with pytest
Collects HTTP traces, DB state, and timing metrics
Reduces flaky behavior via isolation and state reset
Log Interpretation (Phase 3):
Processes stack traces and logs via LLM
Produces human-readable explanations and likely root causes
Bug Classification (Phase 4):
Assigns severity (Critical/High/Medium/Low) via multi-factor scoring
Incorporates impact, frequency, and recovery difficulty


---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (recommended)
- 16–32GB RAM

### Installation
```bash
git clone https://github.com/cgrtml/cognitest-framework.git
cd cognitest-framework
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


**First Run**
python demo_app/user_service/main.py
python demo_app/order_service/main.py
python demo_app/payment_service/main.py

python -c "
from cognitest.core.test_generator import TestGenerator
generator = TestGenerator()
generator.generate_from_requirement(
    requirement='Users must register with valid email and strong password',
    api_endpoint='http://localhost:8000/api/users/register',
    http_method='POST',
    output_file='tests/generated/test_example.py'
)
"

pytest tests/generated/ --cov=demo_app --verbose


**📁 Project Structure**

cognitest-framework/
├── cognitest/
│   ├── core/
│   │   ├── llm_engine.py
│   │   ├── test_generator.py
│   │   ├── bug_classifier.py
│   │   └── log_interpreter.py
│   └── utils/
│       ├── prompt_templates.py
│       └── metrics.py
├── demo_app/
├── experiments/
├── tests/
└── data/


**🧪 Running Experiments**
python experiments/run_coverage_experiment.py
python experiments/run_time_experiment.py
python experiments/run_classification_experiment.py


**📊 Key Results**

| Metric                      | Manual Baseline | CogniTest | Improvement |
| --------------------------- | --------------- | --------- | ----------- |
| Line Coverage               | 64.8%           | 87.6%     | +22.8%      |
| Branch Coverage             | 51.3%           | 79.7%     | +28.4%      |
| Test Creation Time          | 18.1 hours      | 6.5 hours | -64.3%      |
| Bug Classification Accuracy | N/A             | 89.2%     | -           |
| Edge Cases Detected         | 9               | 31        | +244%       |


**💡 Usage Examples**

Generate Tests

from cognitest.core.test_generator import TestGenerator
generator = TestGenerator()
requirement = """
Users can create orders with product name, quantity, and address.
Quantity must be between 1 and 1000.
"""
generator.generate_from_requirement(
    requirement=requirement,
    api_endpoint="http://localhost:8001/api/orders",
    http_method="POST",
    output_file="tests/generated/test_orders.py"
)

**Classify Bug Severity**
from cognitest.core.bug_classifier import BugClassifier
classifier = BugClassifier()
result = classifier.classify(
    error_message="Timeout connecting to database",
    endpoint="/api/orders"
)
print(result)

**Interpret Logs**
from cognitest.core.log_interpreter import LogInterpreter
interpreter = LogInterpreter()
report = interpreter.interpret(error_log="AssertionError: 500 != 200")
print(report)


**🔧 Configuration**

LLM Model

@dataclass
class LLMConfig:
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    temperature: float = 0.3
    top_p: float = 0.85
    max_tokens: int = 2048
    repetition_penalty: float = 1.15
    load_in_4bit: bool = True

**Demo Service Ports**

User Service → 8000
Order Service → 8001
Payment Service → 8002

**🧪 Testing**
pytest tests/ --verbose
pytest tests/ --cov=cognitest --cov=demo_app
pytest tests/generated/ -v


**📝 Citation**
If you use CogniTest, please cite:

@article{temel2025cognitest,
  title={LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI},
  author={Temel, Cagri},
  journal={TechRxiv Preprint},
  year={2025},
  doi={10.36227/techrxiv.176315879.96821044/v1},
  url={https://doi.org/10.36227/techrxiv.176315879.96821044/v1}
}


**🤝 Contributing**

Pull requests are welcome.
Fork
Create branch
Commit
Submit PR

**📄 License**

MIT License — see LICENSE.

**🙏 Acknowledgments**
Mistral AI
HuggingFace Transformers
FastAPI & pytest

**📧 Contact**

Çağrı Temel
CTemel@my.gcu.edu • cagritemel@ieee.org
CTO, Hezarfen LLC • IEEE Senior Member

**🔗 Links**

GitHub Repository: https://github.com/cgrtml/cognitest-framework
Documentation: https://github.com/cgrtml/cognitest-framework/wiki
Issues: https://github.com/cgrtml/cognitest-framework/issues
Paper (TechRxiv): https://doi.org/10.36227/techrxiv.176315879.96821044/v1

⭐ If you find this project useful, please consider starring the repository!
