import io
import matplotlib.pyplot as plt

def generate_training_plot(series_id: str, version: str, timestamps: list, values: list) -> bytes:
    print(f"Plotting training data for {series_id}_{version}")
    plt.figure(figsize=(8, 4))
    plt.plot(timestamps, values, marker="o")
    plt.title(f"Training Data - {series_id} ({version})")
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.read()