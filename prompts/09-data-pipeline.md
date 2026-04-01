# Phase 5: Data Pipeline Implementation

## Objective

Implement all data loading, preprocessing, and augmentation logic. Every dataset mentioned in the paper must have a corresponding implementation. The data pipeline must be CPU-testable with synthetic or mock data — it cannot require real dataset downloads to instantiate.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json` — datasets section, preprocessing, augmentations
- `analysis_workspace/architecture_plan.json` — which data files to create
- `analysis_workspace/implementation_checklist.json`

---

## Required Outputs

All in `code_workspace/{paper_short_name}/`:

- `src/data/` — all dataset classes, transforms, and data utilities
- `configs/` — dataset configuration files (paths, splits, hyperparameters)

Updated `analysis_workspace/implementation_checklist.json` — mark all data_pipeline rubric items as "implemented".

---

## Implementation Standards

### Standard 1: Mock Data Support

Every dataset class must support instantiation with mock/synthetic data for CPU testing. Add a `mock_root` parameter or `create_mock_dataset()` factory:

```python
class CIFAR10Dataset(Dataset):
    def __init__(self, root, split="train", transform=None, mock=False):
        """
        Args:
            root: Path to dataset root directory
            split: "train", "val", or "test"
            transform: Torchvision transforms
            mock: If True, use synthetic data (for CPU testing, no download needed)
        """
        if mock:
            self.data = torch.randn(100, 3, 32, 32)
            self.labels = torch.randint(0, 10, (100,))
        else:
            # Real dataset loading
            ...
```

### Standard 2: Standard Transforms Pattern

Implement transforms as composable functions following torchvision patterns:

```python
def get_train_transforms(image_size=32, normalize_mean=None, normalize_std=None):
    """Training transforms per paper Section 4.1."""
    normalize_mean = normalize_mean or [0.485, 0.456, 0.406]
    normalize_std = normalize_std or [0.229, 0.224, 0.225]
    return transforms.Compose([
        transforms.RandomCrop(image_size, padding=4),  # paper: Section 4.1
        transforms.RandomHorizontalFlip(),              # paper: Section 4.1
        transforms.ToTensor(),
        transforms.Normalize(mean=normalize_mean, std=normalize_std)
    ])
```

### Standard 3: get_dataloader() Factory

Always provide a `get_dataloader()` factory function that creates both dataset and dataloader:

```python
def get_dataloader(root, split, batch_size, num_workers=4, mock=False, **kwargs):
    """Creates dataloader per paper experimental setup.

    Reference: Section 4.1, Appendix B.
    """
    dataset = MainDataset(root=root, split=split, mock=mock)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=num_workers,
        pin_memory=True,
        **kwargs
    )
    return loader
```

### Standard 4: Config-Driven Paths

Never hardcode dataset paths. Use config files:

```yaml
# configs/default.yaml
data:
  dataset: cifar10
  root: ./data/cifar10
  num_workers: 4
  pin_memory: true
  train_batch_size: 128
  eval_batch_size: 256
```

---

## Per-Dataset Implementation Guide

For each dataset in `paper_analysis.json → datasets`:

1. **Standard datasets** (CIFAR-10, ImageNet, MNIST, etc.): Use `torchvision.datasets` or `huggingface/datasets` as the base. Only implement a custom wrapper if the paper specifies non-standard preprocessing.

2. **Paper-specific datasets**: Implement a full `Dataset` class with `__len__` and `__getitem__`. Add a `download()` method or `setup_instructions` if applicable.

3. **Text datasets**: Use HuggingFace `datasets` library. Implement tokenization as a preprocessing step that can be cached.

4. **Custom/proprietary datasets**: Implement the `Dataset` class with the expected interface. Add a `README` note explaining the dataset is not publicly available. Add a `mock=True` mode that generates synthetic data of the correct shape.

---

## Data Pipeline Pass Checklist

### After Pass 1:
- [ ] All datasets in `paper_analysis.json → datasets` have implementations in `src/data/`
- [ ] Every dataset class has `mock=True` support
- [ ] `get_dataloader()` factory exists for every dataset
- [ ] Config files have dataset paths and parameters

### After Pass 2:
- [ ] All preprocessing steps from the paper are implemented (with paper citations in docstrings)
- [ ] All augmentations from the paper are implemented
- [ ] Train vs. eval transforms are correctly separated
- [ ] No real data downloads are required for instantiation
- [ ] `implementation_checklist.json` updated for all data_pipeline items

---

## Dataset Not Available Handling

When a dataset cannot be obtained (proprietary, no longer publicly available, requires registration):

1. Implement the full `Dataset` class interface anyway (shapes, dtypes, everything)
2. Add a `create_synthetic()` class method that generates data of the correct distribution
3. Add a clear README section: "Dataset X is not publicly available. Contact [institution] or use synthetic data: `python -m src.data.{dataset} --create-synthetic --output-dir ./data/{dataset}`"
4. Mark the corresponding rubric items as `skip_reason: "requires proprietary dataset access"` in `rubric.json`
