import  torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
from dgl.nn.pytorch.conv import GATConv
from onmt.GAT import *

class GATGATE(nn.Module):
    def __init__(self, in_feats, out_feats, edge_dim, num_heads):
        super(GATGATE, self).__init__()
        self.in_feats = in_feats
        self.out_feats = out_feats
        self.GATLayers = nn.ModuleList([])
        self.GATLayers.append(MultiHeadGATLayer(in_feats, out_feats, edge_dim, num_heads))
        self.GATLayers.append(MultiHeadGATLayer(out_feats, out_feats, edge_dim, num_heads))
        self.GATLayers.append(MultiHeadGATLayer(out_feats, out_feats, edge_dim, num_heads))
        self.seq_fc1 = nn.Linear(out_feats, out_feats)
        self.seq_fc2 = nn.Linear(out_feats, out_feats)
        self.bias = nn.Parameter(torch.rand(1, out_feats))
        torch.nn.init.uniform_(self.bias, a=-0.2, b=0.2)
        
    def forward(self, g, features):
        n = features.size(0)
        
        for i in range(len(self.GATLayers)):
            h = self.GATLayers[i](g, features)  # N * Heads * D
            if i < len(self.GATLayers)-1:
                h = F.elu(h)
           # h = torch.mean(h, dim = 1)  # N * D
           # print(i, ' layer', h.size())
            if i==0:
                features = h
                continue
            z = torch.sigmoid(self.seq_fc1(h) + self.seq_fc2(features) + self.bias.expand(n, self.out_feats))
            features = z * h + (1 - z) * features
        
        return features

