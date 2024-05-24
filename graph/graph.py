import os
import matplotlib.pyplot as plt
import base64

def plot_bar_chart(investments, output_path):
    labels = [inv['name'] for inv in investments]
    gain_loss = [inv['gain_loss'] for inv in investments]
    
    colors = ['red' if gl < 0 else 'darkgreen' for gl in gain_loss]
    
    net_gain_loss = sum(gain_loss)

    plt.figure(figsize=(12, 6))  
    plt.bar(labels, gain_loss, color=colors)
    plt.xlabel('Company')
    plt.ylabel('Gain/Loss ($)')
    plt.title('Gain/Loss for Each Investment')
    plt.xticks(rotation=45)
    
    plt.subplots_adjust(right=0.8)
    
    plt.annotate(f'Net Gain/Loss: ${net_gain_loss:.2f}', xy=(1, 0.5), xycoords='axes fraction',
                 fontsize=12, color='black', ha='left', va='center', bbox=dict(facecolor='white', edgecolor='none'))

    plt.savefig(output_path)  

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def decode_base64_to_image(encoded_string, output_path):
    image_data = base64.b64decode(encoded_string)
    with open(output_path, "wb") as image_file:
        image_file.write(image_data)
