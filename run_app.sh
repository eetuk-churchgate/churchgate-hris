# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install the required dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit app
streamlit run app.py
