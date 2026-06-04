from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import torch


class AsymTrackExportWrapper(torch.nn.Module):
    def __init__(self, network):
        super().__init__()
        self.network = network

    def forward(self, search, template):
        if hasattr(self.network.backbone, "tempinit"):
            self.network.backbone.tempinit = False
        if hasattr(self.network.backbone, "fuselist"):
            self.network.backbone.fuselist = []
        xz = self.network.forward_backbone([search, template], train=False)
        out_dict, _, _ = self.network.forward_head(xz=xz)
        return out_dict["pred_boxes"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="third_party/AsymTrack")
    parser.add_argument("--checkpoint", default="/home/mll/Downloads/AsymTrack_ep0500.pth.tar")
    parser.add_argument("--yaml-name", default="tiny")
    parser.add_argument("--output", default="models/asymtrack/asymtrack_tiny.onnx")
    parser.add_argument("--opset", type=int, default=17)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    device = torch.device(args.device if args.device == "cuda" and torch.cuda.is_available() else "cpu")

    repo_root = Path(args.repo_root).resolve()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(repo_root))

    old_cwd = os.getcwd()
    os.chdir(repo_root)
    try:
        from lib.config.AsymTrack.config import cfg, update_config_from_file
        from lib.models.AsymTrack import build_asymtrack

        update_config_from_file(str(repo_root / "experiments" / "AsymTrack" / f"{args.yaml_name}.yaml"))
        cfg.TEST_MODE = True
        network = build_asymtrack(cfg)
        checkpoint = torch.load(args.checkpoint, map_location="cpu")
        network.load_state_dict(checkpoint["net"], strict=True)
        network.backbone.switch_to_deploy()
        network = network.to(device).eval()
        wrapper = AsymTrackExportWrapper(network).to(device).eval()
    finally:
        os.chdir(old_cwd)

    search = torch.randn(1, 3, 256, 256, dtype=torch.float32, device=device)
    template = torch.randn(1, 3, 128, 128, dtype=torch.float32, device=device)
    with torch.no_grad():
        pred = wrapper(search, template)
    print("dummy output", tuple(pred.shape), pred.dtype)
    if hasattr(network.backbone, "tempinit"):
        network.backbone.tempinit = False
    if hasattr(network.backbone, "fuselist"):
        network.backbone.fuselist = []

    torch.onnx.export(
        wrapper,
        (search, template),
        str(output),
        input_names=["search", "template"],
        output_names=["pred_boxes"],
        opset_version=args.opset,
        do_constant_folding=True,
        dynamo=False,
    )
    print(f"exported {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
