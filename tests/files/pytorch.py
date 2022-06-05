import torch
from torch import nn
import torchnet as tnt
from collections import OrderedDict


class Test:
    x: int


model = torch.nn.Sequential(torch.nn.Flatten(0, 1))

loss = torch.nn.MSELoss(reduction="sum")

learning_rate = 1e-3
optim_rms = torch.optim.RMSprop(model.parameters(), lr=learning_rate)

optim_sgd = torch.optim.SGD(model.parameters(), lr=1e-8, momentum=0.9)

model2 = nn.Sequential(
    OrderedDict(
        [("conv1", torch.nn.Conv2d(1, 20, 5)), ("relu1", torch.nn.ReLU())]
    )
)


class Polynomial3(torch.nn.Module, Test):
    x: int

    def __init__(self):
        super().__init__()
        self.a = torch.nn.Parameter(torch.randn(()))
        self.linear = torch.nn.Linear(1, 0)

    def test(self):
        pass


data_source = tnt.dataset.TensorDataset()
