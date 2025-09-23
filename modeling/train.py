import os

import torch
import torch.nn.functional as F
import torch.optim as optim
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, random_split

from AnimationDataset import AnimationDataset
from constants import DATASET_INFO_CSV_FILE, DATASET_SAMPLES_DIR
from cvae import CVAE

# Local constants
NUM_EPOCHS = 100
MAX_TEST_SAMPLES_TO_VIEW = 4
figures_dir = "figures"
os.makedirs(figures_dir, exist_ok=True)

# Use for tracking
train_losses = []
test_losses = []
test_samples = []

# Load dataset
dataset = AnimationDataset(DATASET_INFO_CSV_FILE, sample_dir=DATASET_SAMPLES_DIR, transform=None)

# Determine train-test split
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size

# Load separate train and test datasets
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
animation_shape = train_dataset[0]["animation"].shape
human_input_shape = train_dataset[0]["human_input"].shape
print(f"Animation shape: {animation_shape}")
print(f"Human input shape: {human_input_shape}")

# Create DataLoaders
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False, num_workers=0)

# Create new model
cvae = CVAE(x_shape=animation_shape, h_dim1=128, h_dim2=64, z_dim=10, c_shape=human_input_shape)

# Move the model to cuda if available
if torch.cuda.is_available():
    cvae.cuda()

# Define the optimizer
optimizer = optim.Adam(cvae.parameters())


# Compute reconstruction error + KL divergence losses
def loss_function(recon_x, x, mu, log_var):
    recon_x = recon_x.view(recon_x.size(0), -1)
    x = x.view(x.size(0), -1)
    MSE = F.mse_loss(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return MSE + KLD


# Train model
def train(epoch):
    cvae.train()
    train_loss = 0
    for batch_idx, data in enumerate(train_loader):
        times, animation, human_input = data["times"], data["animation"], data["human_input"]

        if torch.cuda.is_available():
            animation, human_input = animation.cuda(), human_input.cuda()

        optimizer.zero_grad()

        recon_batch, mu, log_var = cvae(animation, human_input)
        loss = loss_function(recon_batch, animation, mu, log_var)

        loss.backward()
        train_loss += loss.item()
        optimizer.step()

        if batch_idx % 100 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, batch_idx * len(animation),
                                                                           len(train_loader.dataset),
                                                                           100. * batch_idx / len(train_loader),
                                                                           loss.item() / len(animation)))
    print('====> Epoch: {} Average loss: {:.4f}'.format(epoch, train_loss / len(train_loader.dataset)))
    train_losses.append(round(train_loss / len(train_loader.dataset), 4))


# Evaluate model performance
def test(epoch):
    cvae.eval()
    test_loss = 0
    with torch.no_grad():
        for data in test_loader:
            times, animation, human_input = data["times"], data["animation"], data["human_input"]

            if torch.cuda.is_available():
                animation, human_input = animation.cuda(), human_input.cuda()

            recon, mu, log_var = cvae(animation, human_input)

            if epoch == NUM_EPOCHS and len(test_samples) < MAX_TEST_SAMPLES_TO_VIEW:
                test_samples.append(
                    {"times": times[0], "original_animation": animation[0], "human_input": human_input[0],
                     "reconstructed_animation": recon[0]})

            # sum up batch loss
            test_loss += loss_function(recon, animation, mu, log_var).item()

    test_loss /= len(test_loader.dataset)
    print('====> Test set loss: {:.4f}'.format(test_loss))
    test_losses.append(round(test_loss, 4))


# Train and test
for epoch in range(1, NUM_EPOCHS + 1):
    train(epoch)
    test(epoch)

# Plot the loss curves
EPOCH_TO_PLOT_FROM = 1
epochs = range(1, NUM_EPOCHS + 1)
plt.figure(figsize=(8, 5))
plt.plot(epochs[EPOCH_TO_PLOT_FROM:], train_losses[EPOCH_TO_PLOT_FROM:], marker='o', label='Train Loss')
plt.plot(epochs[EPOCH_TO_PLOT_FROM:], test_losses[EPOCH_TO_PLOT_FROM:], marker='s', label='Test Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Train and Test Losses vs. Epochs')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(figures_dir, "train_and_test_losses_vs_epochs.pdf"),
    bbox_inches="tight"
)

# Plot the saved samples
times, original_animation, human_input, reconstructed_animation = test_samples[0]["times"], test_samples[0][
    "original_animation"], test_samples[0]["human_input"], test_samples[0]["reconstructed_animation"]

print(times.shape, original_animation.shape, human_input.shape, reconstructed_animation.shape)

# Plot X vs. time for animation
plt.figure(figsize=(8, 6))
plt.plot(original_animation[:, 0], original_animation[:, 1], label="Original animation", linewidth=2)
plt.plot(human_input[:, 0], human_input[:, 1], label="Human input", linewidth=2)
plt.plot(reconstructed_animation[:, 0], reconstructed_animation[:, 1], label="Reconstructed animation", linewidth=2,
         linestyle='--')

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Animation Trajectories vs. Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(figures_dir, "animation_trajectories_vs_time.pdf"),
    bbox_inches="tight"  # ensures everything fits in the figure
)