import os
import matplotlib.pyplot as plt

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
