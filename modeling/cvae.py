##########################################
# Implementation from: https://github.com/lyeoni/pytorch-mnist-CVAE/blob/master/pytorch-mnist-CVAE.ipynb
##########################################

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class CVAE(nn.Module):
    def __init__(self, x_shape, h_dim1, h_dim2, z_dim, c_shape):
        super(CVAE, self).__init__()
        self.x_shape = x_shape
        self.c_shape = c_shape

        self.x_dim = int(torch.tensor(x_shape).prod().item())  # flatten: 150*2 = 300
        self.c_dim = int(torch.tensor(c_shape).prod().item())  # flatten: 150*2 = 300

        # encoder part
        self.fc1 = nn.Linear(self.x_dim + self.c_dim, h_dim1)
        self.fc2 = nn.Linear(h_dim1, h_dim2)
        self.fc31 = nn.Linear(h_dim2, z_dim)
        self.fc32 = nn.Linear(h_dim2, z_dim)
        # decoder part
        self.fc4 = nn.Linear(z_dim + self.c_dim, h_dim2)
        self.fc5 = nn.Linear(h_dim2, h_dim1)
        self.fc6 = nn.Linear(h_dim1, self.x_dim)

    def encoder(self, x, c):
        x = x.view(x.size(0), -1)  # (batch, flattened_input_dim)
        c = c.view(c.size(0), -1)  # (batch, flattened_target_dim)
        concat_input = torch.cat([x, c], dim=-1)
        h = F.relu(self.fc1(concat_input))
        h = F.relu(self.fc2(h))
        return self.fc31(h), self.fc32(h)

    def sampling(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return eps.mul(std).add(mu)  # return z sample

    def decoder(self, z, c):
        c = c.reshape(c.size(0), -1)  # flatten condition
        concat_input = torch.cat([z, c], dim=-1)
        h = F.relu(self.fc4(concat_input))
        h = F.relu(self.fc5(h))
        x_hat = torch.sigmoid(self.fc6(h))  # (batch, flattened_input_dim)
        return x_hat.view(-1, * self.x_shape)   # reshape back to (batch, (input_dim))

    def forward(self, x, c):
        mu, log_var = self.encoder(x.view(-1, self.x_dim), c)
        z = self.sampling(mu, log_var)
        return self.decoder(z, c), mu, log_var


