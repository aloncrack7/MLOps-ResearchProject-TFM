# Examples & Notebooks

This folder contains example scripts and Jupyter notebooks demonstrating how to use the MLOps platform for model training, data exploration, and integration with the deployment system.

---

## 📁 Folder Structure

```
examples/
├── autoML_train.py                # Example: Automated ML training script
├── data_exploration.ipynb         # Jupyter notebook for data exploration
├── example.env                    # Example environment variables file
├── requirements.txt               # Python dependencies for examples
├── set_up_data_for_degradation.ipynb # Notebook for preparing data for degradation testing
├── train.py, train_2.py, ...      # Example model training scripts
├── WineQT.csv                     # Example dataset (Wine Quality)
```

---

## ✨ Main Examples

- **Model Training**: Scripts (`train.py`, `train_2.py`, etc.) show how to train models, log experiments, and register models with MLflow.
- **AutoML**: `autoML_train.py` demonstrates automated model selection and training.
- **Data Exploration**: `data_exploration.ipynb` provides an interactive notebook for exploring datasets.
- **Degradation Testing**: `set_up_data_for_degradation.ipynb` shows how to prepare and test data for model degradation scenarios.
- **Environment Setup**: `example.env` and `requirements.txt` help set up the environment for running examples.
- **Sample Data**: `WineQT.csv` is a sample dataset used in the examples.

---

## 🚀 Usage

1. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run any example script:
   ```bash
   python train.py
   ```
4. Open notebooks with Jupyter:
   ```bash
   jupyter notebook data_exploration.ipynb
   ```

---

## 📝 Notes

- Example scripts are designed to work with the MLflow tracking server and deployment backend.
- You can use the provided `.env` file as a template for your environment variables.
- The sample dataset can be replaced with your own data for experimentation.

---

## 🤝 Contributing

Pull requests and new example scripts/notebooks are welcome!

---
