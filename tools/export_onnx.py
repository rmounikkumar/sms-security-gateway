import sys, os
sys.stdout.reconfigure(encoding="utf-8")

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_id = "mrm8488/bert-tiny-finetuned-sms-spam-detection"
save_dir = os.path.join(os.path.dirname(__file__), "..", "onnx_model")
os.makedirs(save_dir, exist_ok=True)

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)
model.eval()

print("Exporting to ONNX...")
dummy = tokenizer("test", return_tensors="pt", padding=True, truncation=True, max_length=128)

torch.onnx.export(
    model,
    (dummy["input_ids"], dummy["attention_mask"]),
    os.path.join(save_dir, "model.onnx"),
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch", 1: "seq"},
        "attention_mask": {0: "batch", 1: "seq"},
        "logits": {0: "batch"},
    },
    opset_version=14,
)

tokenizer.save_pretrained(save_dir)
print(f"ONNX model exported to {save_dir}")
print(f"Files: {os.listdir(save_dir)}")
