import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sklearn import tree


DT_MODEL_PATH = Path("Decision_Tree_model.pkl")
RF_MODEL_PATH = Path("fraud_detection_rf_model.pkl")
FEATURE_MAP = {
    "PAYMENT": 2,
    "TRANSFER": 4,
    "CASH_OUT": 1,
    "DEBIT": 5,
    "CASH_IN": 3,
}
FEATURE_NAMES = ["type", "amount", "old_balance", "new_balance"]


@st.cache_resource
def load_model(path: Path):
    with path.open("rb") as model_file:
        return pickle.load(model_file)


def format_prediction(model, value):
    classes = getattr(model, "classes_", None)
    if classes is None:
        return str(value)
    labels = list(classes)
    if value in labels:
        label = value
    else:
        try:
            label = labels[int(value)]
        except Exception:
            label = value
    if all(isinstance(cls, (int, np.integer)) for cls in labels):
        mapping = {0: "No fraud", 1: "Fraud"}
        return mapping.get(label, str(label))
    return str(label)


def show_tree(model, title):
    class_names = getattr(model, "classes_", None)
    if class_names is not None:
        class_names = class_names.astype(str)

    fig, ax = plt.subplots(figsize=(18, 9))
    tree.plot_tree(
        model,
        feature_names=FEATURE_NAMES,
        class_names=class_names,
        filled=True,
        rounded=True,
        fontsize=9,
        ax=ax,
    )
    ax.set_title(title)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def explain_path(model, sample):
    node_indicator = model.decision_path(sample)
    leaf_id = model.apply(sample)[0]
    feature = model.tree_.feature
    threshold = model.tree_.threshold

    explanation = []
    node_index = node_indicator.indices[
        node_indicator.indptr[0] : node_indicator.indptr[1]
    ]
    for node_id in node_index:
        if leaf_id == node_id:
            explanation.append(f"Reached leaf node {node_id}.")
            continue
        feature_index = feature[node_id]
        if feature_index == tree._tree.TREE_UNDEFINED:
            continue
        threshold_value = threshold[node_id]
        feature_name = FEATURE_NAMES[feature_index]
        comparator = "<=" if sample[0, feature_index] <= threshold_value else ">"
        explanation.append(
            f"{feature_name} ({sample[0, feature_index]:.2f}) "
            f"{comparator} {threshold_value:.2f}"
        )
    return explanation


st.set_page_config(page_title="Fraud Model Demo", page_icon="🌳", layout="centered")
st.title("Fraud Transaction Prediction and Tree Viewer")
st.write("Provide the four features used during training to view predictions and tree paths.")

missing = [p for p in (DT_MODEL_PATH, RF_MODEL_PATH) if not p.exists()]
if missing:
    st.error(f"Missing model file(s): {', '.join(str(p) for p in missing)}")
    st.stop()

try:
    decision_tree_model = load_model(DT_MODEL_PATH)
    random_forest_model = load_model(RF_MODEL_PATH)
except Exception as exc:
    st.error(f"Could not load models: {exc}")
    st.stop()

transaction_label = st.selectbox("Transaction Type", list(FEATURE_MAP.keys()))
amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
old_balance = st.number_input("Old Balance (Sender)", min_value=0.0, format="%.2f")
new_balance = st.number_input("New Balance (Sender)", min_value=0.0, format="%.2f")

if st.button("Predict with Both Models"):
    sample = np.array(
        [
            [
                FEATURE_MAP[transaction_label],
                amount,
                old_balance,
                new_balance,
            ]
        ],
        dtype=float,
    )

    try:
        dt_prediction = decision_tree_model.predict(sample)[0]
        dt_proba = decision_tree_model.predict_proba(sample)[0]
    except Exception as exc:
        st.error(f"Decision Tree prediction failed: {exc}")
    else:
        st.subheader("Decision Tree Result")
        st.success(f"Prediction: {format_prediction(decision_tree_model, dt_prediction)}")
        st.write("Probabilities:", dict(zip(decision_tree_model.classes_, dt_proba)))
        st.write("Decision path:")
        for step in explain_path(decision_tree_model, sample):
            st.write("- ", step)
        show_tree(decision_tree_model, "Decision Tree Structure")

    try:
        rf_prediction = random_forest_model.predict(sample)[0]
        rf_proba = random_forest_model.predict_proba(sample)[0]
    except Exception as exc:
        st.error(f"Random Forest prediction failed: {exc}")
    else:
        st.subheader("Random Forest Result")
        st.success(f"Prediction: {format_prediction(random_forest_model, rf_prediction)}")
        st.write("Probabilities:", dict(zip(random_forest_model.classes_, rf_proba)))
        st.write("Decision path (first tree in forest):")
        first_tree = random_forest_model.estimators_[0]
        for step in explain_path(first_tree, sample):
            st.write("- ", step)
        show_tree(first_tree, "Random Forest - Tree 1 Structure")

