import os
import matplotlib.pyplot as plt
import base64

def plot_bar_chart(investments, output_path):
    labels = [inv['name'] for inv in investments]
    gain_loss = [inv['gain_loss'] for inv in investments]
    plt.figure(figsize=(10, 6))
    plt.bar(labels, gain_loss, color='skyblue')
    plt.xlabel('Company')
    plt.ylabel('Gain/Loss ($)')
    plt.title('Gain/Loss for Each Investment')
    plt.xticks(rotation=45)
    plt.savefig(output_path)  

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def decode_base64_to_image(encoded_string, output_path):
    image_data = base64.b64decode(encoded_string)
    with open(output_path, "wb") as image_file:
        image_file.write(image_data)