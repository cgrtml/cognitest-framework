# CogniTest Framework

**LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📋 Overview

CogniTest is a production-ready cognitive software testing framework that integrates Large Language Models (LLMs) with automated testing pipelines. It enhances test case generation, bug classification, and log interpretation using Mistral-7B-Instruct as the core reasoning engine.

**Key Features:**
- 🤖 **Automated Test Generation** from natural language requirements
- 🔍 **Intelligent Bug Classification** with 91.7% accuracy
- 📊 **Log Interpretation** with human-readable explanations
- ⚡ **68.5% Time Reduction** in test creation
- 📈 **73.4% Coverage Improvement** over manual testing

## 🎓 Research Paper

This repository accompanies the IEEE conference paper:

**"LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI"**

*Author:* Cagri Temel, IEEE Senior Member  
*Affiliation:* Grand Canyon University & Hezarfen LLC  
*Contact:* CTemel@my.gcu.edu | cagritemel@ieee.org

**Abstract:** Modern software testing faces significant challenges in scalability, maintainability, and intelligent defect detection. CogniTest addresses these challenges through a novel four-phase cognitive testing pipeline that demonstrates 73.4% improvement in test coverage, 68.2% reduction in manual test creation time, and 91.7% accuracy in automated bug severity classification.

## 🏗️ Architecture
```
CogniTest Framework
├── Test Generation (Phase 1)
│   └── Natural language → Executable pytest tests
├── Intelligent Execution (Phase 2)
│   └── Test execution with detailed tracing
├── Log Interpretation (Phase 3)
│   └── Root cause analysis and remediation
└── Bug Classification (Phase 4)
    └── Automated severity classification
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- CUDA-capable GPU (recommended) or CPU
- 16GB RAM minimum (32GB recommended for GPU)

### Installation
```bash
# Clone the repository
git clone https://github.com/cgrtml/cognitest-framework.git
cd cognitest-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### First Run
```bash
# Start demo microservices (3 separate terminals)
python demo_app/user_service/main.py      # Port 8000
python demo_app/order_service/main.py     # Port 8001
python demo_app/payment_service/main.py   # Port 8002

# Generate tests from requirements
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

# Run generated tests
pytest tests/generated/ --cov=demo_app --verbose
```

## 📁 Project Structure
```
cognitest-framework/
├── cognitest/                    # Core framework
│   ├── core/
│   │   ├── llm_engine.py        # Mistral-7B integration
│   │   ├── test_generator.py    # Test generation engine
│   │   ├── bug_classifier.py    # Severity classification
│   │   └── log_interpreter.py   # Log analysis
│   └── utils/
│       ├── prompt_templates.py  # LLM prompts
│       └── metrics.py           # Metrics collection
├── demo_app/                     # Demo microservices
│   ├── user_service/            # User authentication
│   ├── order_service/           # Order management
│   └── payment_service/         # Payment processing
├── experiments/                  # Research experiments
│   ├── run_coverage_experiment.py
│   ├── run_time_experiment.py
│   └── run_classification_experiment.py
├── tests/
│   ├── test_manual_baseline.py  # Manual test baseline
│   └── generated/               # Auto-generated tests
└── data/
    ├── requirements/            # Requirement documents
    └── results/                 # Experiment results
```

## 🧪 Running Experiments

Reproduce the paper results:
```bash
# Experiment 1: Coverage Analysis
python experiments/run_coverage_experiment.py

# Experiment 2: Time Efficiency
python experiments/run_time_experiment.py

# Experiment 3: Bug Classification
python experiments/run_classification_experiment.py
```

Results are saved in `data/results/` directory.

## 📊 Key Results

| Metric | Manual Baseline | CogniTest | Improvement |
|--------|----------------|-----------|-------------|
| Line Coverage | 68.3% | 91.2% | +33.5% |
| Branch Coverage | 54.7% | 84.9% | +55.2% |
| Test Creation Time | 16.5 hours | 5.2 hours | -68.5% |
| Bug Classification Accuracy | N/A | 91.7% | - |
| Edge Cases Detected | 12 | 35 | +191.7% |

## 💡 Usage Examples

### Example 1: Generate Tests from Requirements
```python
from cognitest.core.test_generator import TestGenerator

generator = TestGenerator()

requirement = """
Users can create orders with product name, quantity, and shipping address.
Quantity must be between 1 and 1000.
Total price should be calculated automatically.
"""

test_code = generator.generate_from_requirement(
    requirement=requirement,
    api_endpoint="http://localhost:8001/api/orders",
    http_method="POST",
    output_file="tests/generated/test_orders.py"
)

print(f"Generated test with {len(test_code.split('\n'))} lines")
```

### Example 2: Classify Bug Severity
```python
from cognitest.core.bug_classifier import BugClassifier

classifier = BugClassifier()

result = classifier.classify(
    error_message="Database connection timeout after 30 seconds",
    test_context="test_user_registration - Cannot complete registration",
    endpoint="/api/users/register"
)

print(f"Severity: {result['severity']}")
print(f"Score: {result['weighted_score']:.2f}")
print(f"Reasoning: {result['reasoning']}")
```

### Example 3: Interpret Error Logs
```python
from cognitest.core.log_interpreter import LogInterpreter

interpreter = LogInterpreter()

error_log = """
AssertionError: assert 500 == 200
Full URL: POST http://localhost:8001/api/orders
Response: {"detail":"Internal Server Error"}
"""

interpretation = interpreter.interpret(
    error_log=error_log,
    service_name="Order Service"
)

print(interpreter.generate_report(interpretation))
```

## 🔧 Configuration

### LLM Model Settings

Edit `cognitest/core/llm_engine.py`:
```python
@dataclass
class LLMConfig:
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    temperature: float = 0.3          # Lower = more deterministic
    top_p: float = 0.85               # Nucleus sampling
    max_tokens: int = 2048            # Max response length
    repetition_penalty: float = 1.15  # Reduce repetition
    load_in_4bit: bool = True         # Memory optimization
```

### Demo Services Configuration

Services run on:
- **User Service**: http://localhost:8000
- **Order Service**: http://localhost:8001
- **Payment Service**: http://localhost:8002

Change ports in respective `main.py` files if needed.

## 📈 Performance Considerations

**GPU Requirements:**
- NVIDIA GPU with 8GB+ VRAM (recommended)
- CUDA 11.8 or higher
- 4-bit quantization reduces memory to ~4.1GB

**CPU Mode:**
- Supported but 10-20x slower
- Requires 16GB+ RAM
- Set `load_in_4bit=False` in config

**First Run:**
- Model downloads ~4.1GB (one-time)
- Cached in `~/.cache/huggingface/`
- Initial load takes 2-3 minutes

## 🧪 Testing
```bash
# Run all tests
pytest tests/ --verbose

# Run with coverage
pytest tests/ --cov=cognitest --cov=demo_app --cov-report=html

# Run specific test file
pytest tests/test_manual_baseline.py -v

# Run generated tests only
pytest tests/generated/ -v
```

## 📝 Citation

If you use CogniTest in your research, please cite:
```bibtex
@inproceedings{temel2025cognitest,
  title={LLM-Assisted Test Automation: A Cognitive Software Testing Framework Using Generative AI},
  author={Temel, Cagri},
  booktitle={Proceedings of the IEEE International Conference on Software Engineering},
  year={2025},
  organization={IEEE}
}
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mistral AI for the open-source Mistral-7B-Instruct model
- HuggingFace for the transformers library
- FastAPI and pytest communities

## 📧 Contact

**Çağrı Temel**  
- Email: CTemel@my.gcu.edu | cagritemel@ieee.org
- Affiliation: Grand Canyon University, Department of Computer Science
- Position: Chief Technology Officer, Hezarfen LLC
- IEEE Member: Senior Member

For questions, issues, or collaboration opportunities, please open an issue or contact via email.

## 🔗 Links

- [GitHub Repository](https://github.com/cgrtml/cognitest-framework)
- [Documentation](https://github.com/cgrtml/cognitest-framework/wiki)
- [Issues](https://github.com/cgrtml/cognitest-framework/issues)
- [Paper (arXiv)](https://arxiv.org/abs/...) *(Coming Soon)*

---

**⭐ Star this repository if you find it useful!**

**Repository:** https://github.com/cgrtml/cognitest-framework
