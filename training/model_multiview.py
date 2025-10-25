import torch
import torch.nn as nn
import torchvision.models as models


class MultiViewResNet(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()

        self.feature_extractor = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        in_feat = self.feature_extractor.fc.in_features
        self.feature_extractor.fc = nn.Identity()

        fusion_feat = in_feat * 3  # front, spine, back

        self.corner = nn.Linear(fusion_feat, num_classes)
        self.cover = nn.Linear(fusion_feat, num_classes)
        self.dirty = nn.Linear(fusion_feat, num_classes)
        self.damage = nn.Linear(fusion_feat, num_classes)

    def forward(self, front, spine, back):
        f1 = self.feature_extractor(front)
        f2 = self.feature_extractor(spine)
        f3 = self.feature_extractor(back)
        fused = torch.cat([f1, f2, f3], dim=1)

        return {
            "corner": self.corner(fused),
            "cover": self.cover(fused),
            "dirty": self.dirty(fused),
            "damage": self.damage(fused),
        }